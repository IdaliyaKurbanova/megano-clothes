import json

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from basket.models import Basket, BasketProduct
from basket.views import BasketView
from catalogs.models import Product
from order.models import Order, OrderProduct, Status, Delivery, Payment
from order.serializers import OrderSerializer, OrderProductSerializer
from profile_user.models import Profile


def remains_checking(product_list) -> tuple[bool, list]:
    """
    Функция для проверки наличия на складе достаточного количества товаров.
    Возвращает ответ (True или False), хватает ли всех проверяемых товаров на складе,
    а также список недостающих товаров.

    :param product_list: список с id продуктов, наличие которых на складе необходимо проверить
    :return: is_enough - ответ, хватает ли всех товаров в необходимом количестве
             products_not_enough - список с товарами, которых не хватает частично или полностью
    """
    products_not_enough: list = []
    is_enough: bool = True
    for prod in product_list:
        product = Product.objects.filter(pk=prod["id"]).first()
        if product.count < prod["count"]:
            products_not_enough.append(product)

    if products_not_enough:
        is_enough: bool = False

    return is_enough, products_not_enough


class OrdersView(APIView):
    """
    API-класс с методами для работы с заказами (создание нового заказа и просмотр всех заказов пользователя)
    """

    def post(self, request: Request) -> Response:
        """
        Метод для создания нового заказа.

        :return: Response со словарем, в котором содержится номер созданного в БД заказа
        """

        is_enough, products_not_enough = remains_checking(request.data)

        # если какого-то товара не хватает, то осуществляются изменения в составе корзины
        # согласно имеющемуся количеству на складе и возвращается ответ 400.
        if not is_enough:
            response = Response(
                {"error": "Часть товара могла закончится, проверьте корзину"},
                status=status.HTTP_400_BAD_REQUEST,
            )

            # если пользователь аутентифицирован, то изменения производятся в корзине пользователя в базе данных
            if request.user.is_authenticated:
                basket = Basket.objects.filter(user=request.user).first()
                for product in products_not_enough:
                    basket_product = BasketProduct.objects.filter(
                        basket=basket, product=product
                    ).first()
                    if product.count == 0:
                        basket_product.delete()
                    else:
                        basket_product.quantity = product.count
                        basket_product.save()

            # если пользователь не аутентифицирован, то изменяется количество товаров корзины в куки
            else:
                basket_in_cookies = request.COOKIES.get("basket", 0)
                if isinstance(basket_in_cookies, str):
                    basket_in_cookies = json.loads(basket_in_cookies)
                    print(basket_in_cookies)
                    for product in products_not_enough:
                        if product.count == 0:
                            basket_in_cookies.pop(f"{product.pk}")
                        else:
                            basket_in_cookies[f"{product.pk}"] = product.count
                    print(basket_in_cookies)
                response.set_cookie(key="basket", value=json.dumps(basket_in_cookies))
            return response

        # если для создания заказа всех товаров хватает, то создается новый заказ, а товары в корзине удаляются
        else:
            order_status = Status.objects.filter(title="Создан").first()
            order = Order.objects.create(status=order_status)
            response = Response({"orderId": order.pk})

            if request.user.is_authenticated:
                profile, created = Profile.objects.get_or_create(user=request.user)
                order.profile = profile
                order.save()
                basket = Basket.objects.filter(user=request.user).first()
                basket_products = BasketProduct.objects.filter(basket=basket)
                basket_products.delete()
            else:
                response.set_cookie(key="orderId", value=order.pk)
                response.set_cookie(key="basket", value={})

            # каждый продукт, который был в корзине переносится в заказ путем создания связи OrderProduct
            for product_data in request.data:
                product = Product.objects.filter(pk=product_data["id"]).first()
                if product.count > 0:
                    OrderProduct.objects.create(
                        product=product, order=order, quantity=product_data["count"]
                    )

            # также проверяется количесто товаров с платной досставкой в составе заказа
            not_free_order_products = OrderProduct.objects.filter(
                order=order, product__freeDelivery=False
            ).all()

            ordinary_type = Delivery.objects.get(type="ordinary")
            # если сумма заказа меньше минимально необходимой для бесплатной доставки и в составе заказа
            # есть хотя бы один товар с платной доставкой, то в состав заказа также добавляется стоимость обычной доставки
            if (
                order.totalCost() < ordinary_type.min_amount_for_free
                and len(not_free_order_products) > 0
            ):
                ordinary_delivery = Product.objects.filter(title="ordinary").first()
                OrderProduct.objects.create(
                    product=ordinary_delivery, order=order, quantity=1
                )

            return response

    def get(self, request: Request):
        """
        Метод для получения информации о заказах аутентифицированного пользователя.

        :return: Response со списком заказов пользователя
        """

        # получаем заказ из куки, если он там есть
        cookie_order = int(request.COOKIES.get("orderId", 0))

        # если в куки хранится номер заказа, то переносим информацию о нем на пользователя, а сами куки очищаем
        if cookie_order != 0:
            order = Order.objects.get(pk=cookie_order)
            order.profile = request.user.profile
            order.save()

        # получаем их БД все заказы пользователя и, используя сериализатор, отправляем на фронтэнд
        orders = (
            Order.objects.filter(profile=request.user.profile)
            .order_by("-createdAt")
            .prefetch_related("status")
            .prefetch_related("deliveryType")
            .prefetch_related("paymentType")
        ).all()

        serialized = OrderSerializer(orders, many=True)
        response = Response(serialized.data)
        response.set_cookie(key="orderId", value=0)
        return response


class SingleOrderView(APIView):
    """
    API-класс с методами по работе с заказом (получение информация об отдельном заказе и подтверждение определенного заказа)
    """

    def get(self, request: Request, id: int) -> Response:
        """
        Метод для получения информации об определенном заказе.

        :param id: pk-номер заказа в БД, информацию о котором необходимо получить
        :return: Response с информацией об отдельном заказе
        """

        order = (
            Order.objects.filter(pk=id)
            .prefetch_related("products")
            .prefetch_related("status")
            .prefetch_related("deliveryType")
            .prefetch_related("paymentType")
            .first()
        )

        serialized = OrderSerializer(order)

        return Response(serialized.data)

    def post(self, request: Request, id: int) -> Response:
        """Метод для подтверждения и изменения информации в заказе"""

        # получаем их БД объект заказа, и если он в статусе "Оплачен" или "Принят",
        # то его уже нельзя изменить, поэтому возвращает ответ со статусом 400.
        order = Order.objects.filter(pk=id).first()
        if (order.status is not None) and order.status.title in ["Оплачен", "Принят"]:
            return Response(
                {"error": "Заказ уже оплачен, и поэтому не может быть изменен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # получаем продукты в заказе и проверяем, всех ли товаров достаточно на складе для подтверждения заказа
        products_in_order = OrderProductSerializer(
            order.products.all(), many=True, context={"order": order}
        )
        is_enough, products_not_enough = remains_checking(products_in_order.data)

        # если каких-либо товаров недостаточно, то переносим товары из заказа в максимально возможном количестве в
        # корзину, а сам заказ удаляем и возвращаем ответ со статусом 400 и сообщением об ошибке
        if not is_enough:
            basket = Basket.objects.filter(user=request.user).first()
            order_products = (
                OrderProduct.objects.filter(order=order)
                .exclude(product__description__iregex="доставка")
                .all()
            )
            for order_product in order_products:
                if order_product.product.count > 0:
                    basket_product = BasketProduct.objects.filter(
                        basket=basket, product=order_product.product
                    ).first()
                    if not basket_product:
                        BasketProduct.objects.create(
                            basket=basket,
                            product=order_product.product,
                            quantity=min(
                                order_product.product.count, order_product.quantity
                            ),
                        )
                    else:
                        max_addition: int = min(
                            (order_product.product.count - basket_product.quantity),
                            order_product.quantity,
                        )
                        basket_product.quantity += max_addition
                        basket_product.save()

            order.delete()

            return Response(
                {
                    "error": "Часть товара могла закончится, заказ отменен, проверьте корзину"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # если всех товаров достаточно, то проверяем, указал ли пользователь адрес, в ином случае возвращаем статус 400
        if request.data["city"] == None or request.data["address"] == None:
            return Response(
                {"error": "Город и адрес доставки не указаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.fullName = request.data["fullName"]
        order.phone = request.data["phone"]
        order.email = request.data["email"]
        order.city = request.data["city"]
        order.address = request.data["address"]

        delivery = Delivery.objects.filter(type=request.data["deliveryType"]).first()
        payment = Payment.objects.filter(type=request.data["paymentType"]).first()

        new_status = Status.objects.filter(title="Ожидает оплаты").first()
        order.status = new_status

        # если тип доставки выбран не был, то автоматически доставка устанавливается на обычную
        if not delivery:
            delivery = Delivery.objects.filter(type="ordinary").first()

        order.deliveryType = delivery

        # если тип оплаты выбран не был, то автоматически оплата устанавливается на онлайн
        if not payment:
            payment = Payment.objects.filter(type="online").first()

        order.paymentType = payment

        order.save()

        # если тип доставки был выбран express, то мы определяем текущую доставку и меняем на express
        if delivery.type == "express":
            product = Product.objects.filter(title="express").first()
            current_delivery = OrderProduct.objects.filter(
                order=order, product__description__iregex="доставка"
            ).first()

            if not current_delivery:
                OrderProduct.objects.create(order=order, product=product, quantity=1)

            elif current_delivery.product.title == "ordinary":
                current_delivery.delete()
                OrderProduct.objects.create(order=order, product=product, quantity=1)

        # если была выбрана обычная доставка, то определяем текущую доставку и заменяем ее на обычную
        # при замене также учитываем общую сумму заказа и есть ли в составе заказа товары с платной доставкой
        else:
            product = Product.objects.filter(title="ordinary").first()
            current_delivery = OrderProduct.objects.filter(
                order=order, product__description__iregex="доставка"
            ).first()
            if current_delivery and current_delivery.product.title == "express":
                current_delivery.delete()
                not_free_order_products = OrderProduct.objects.filter(
                    order=order, product__freeDelivery=False
                ).all()
                ordinary_type = Delivery.objects.get(type="ordinary")
                if (
                    order.totalCost() < ordinary_type.min_amount_for_free
                    and len(not_free_order_products) > 0
                ):
                    OrderProduct.objects.create(
                        order=order, product=product, quantity=1
                    )

        return Response({"orderId": order.pk})
