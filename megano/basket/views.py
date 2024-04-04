import json
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, BaseParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from ast import literal_eval

from .serializers import BasketSerializer

from catalogs.models import Product
from .models import Basket, BasketProduct


class PlainTextParser(BaseParser):
    """
    Парсер для преобразования в байты полученные данные в виде простого текста (а не в json-формате).
    """

    media_type = "text/plain;charset=UTF-8"

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()


class BasketView(APIView):
    """
    API-класс с методами по работе с корзиной покупок.
    Если пользователь аутентифицирован, то информация о его корзине хранится в БД.
    В ином случае, информация с товарами корзины хранится в куках.
    """

    parser_classes = [JSONParser, FormParser, PlainTextParser]

    def get(self, request: Request) -> Response:
        """
        Метод для получения информации о товарах в корзине.
        :return: Response со списком отсериализованных товаров в корзине
        """
        # Получаем из куки информацию о товарах в корзине
        basket_in_cookies: dict | 0 = request.COOKIES.get("basket", 0)

        # Если информация в виде строки, то преобразуем ее в словарь
        if isinstance(basket_in_cookies, str):
            basket_in_cookies = json.loads(basket_in_cookies)

        # Если пользователь аутентифицировался, то достаем из БД его корзину. Если ее нет, то создаем для него корзину.
        if request.user.is_authenticated:
            basket = Basket.objects.filter(user=request.user).first()

            if not basket:
                basket = Basket.objects.create(user=request.user)

            # Если в куках хранится информация о товарах корзины,
            # то мы переносим эти товары в корзину из базы данных и затем очищаем куки.
            # Теперь вся информация о товарах хранится в корзине БД
            if basket_in_cookies:
                for product_id, product_count in basket_in_cookies.items():

                    # для каждого id продукта в корзине из куки мы получаем продукт и его наличие в корзине
                    # (связь BasketProduct)
                    # если продукт уже есть в корзине БД, то мы просто к нему добавляем количество из куки,
                    # а если нет - то создаем его в корзине (BasketProduct для данного продукта)
                    product = Product.objects.filter(pk=product_id).first()
                    product_in_basket = BasketProduct.objects.filter(
                        product=product, basket=basket
                    ).first()

                    if not product_in_basket:
                        product_in_basket = BasketProduct.objects.create(
                            product=product, basket=basket, quantity=product_count
                        )
                    else:
                        product_in_basket.quantity += product_count

            # Если в корзине из БД есть продукты, то мы их сериализуем и отправляем на фронтэнд.
            # Если товаров в корзине нет, то вернется просто ответ со статусом 200.
            if basket.products.all():
                products_in_basket = basket.products.all()
                serialized = BasketSerializer(
                    products_in_basket, context={"basket": basket}, many=True
                )
                response = Response(serialized.data)
                response.set_cookie(key="basket", value={}, max_age=360000000)
                return response

        # else - описывает случай, если пользователь неаутентифицирован.
        else:

            # если в куках еще нет информации о корзине, то пустая корзина добавляется в куки
            if not isinstance(basket_in_cookies, dict):
                response = Response()
                response.set_cookie(key="basket", value={}, max_age=360000000)
                return response

            # если в куках есть информация о продуктах в корзине,
            # то получаем эти продукты из БД и отправляем их на фронтэнд
            else:
                products = Product.objects.filter(pk__in=basket_in_cookies.keys()).all()
                serialized = BasketSerializer(
                    products, context={"basket": basket_in_cookies}, many=True
                )
                return Response(serialized.data)

        # возвращается пустой ответ со статусом 200 во всех других случаях
        return Response(status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """
        Метод для добавления в корзину выбранного товара
        :return: Response со списком отсериализованных товаров в корзине
        """

        # получаем из БД товар, который необходимо добавить в корзину
        product = Product.objects.filter(pk=request.data["id"]).first()
        quantity: int = request.data["count"]

        # если добавляемого товара не осталось на складе, то ничего не делаем и сразу переходим к методу get
        if product.count == 0:
            return self.get(request)

        # если пользователь аутентифицирован, то достаем из БД корзину и меняем или добавляем количество товара
        if request.user.is_authenticated:
            basket = Basket.objects.filter(user=request.user).first()
            basket_product = BasketProduct.objects.filter(
                basket=basket, product=product
            ).first()
            if basket_product:
                if basket_product.quantity + quantity <= product.count:
                    basket_product.quantity += quantity
                else:
                    basket_product.quantity = product.count
                basket_product.save()

            else:
                if quantity <= product.count:
                    basket.products.add(
                        product.pk, through_defaults={"quantity": quantity}
                    )
                else:
                    basket.products.add(
                        product.pk, through_defaults={"quantity": product.count}
                    )
                    basket.save()

            products_in_basket = basket.products.all()
            serialized = BasketSerializer(
                products_in_basket, context={"basket": basket}, many=True
            )
            return Response(serialized.data)

        # если пользователь не аутентифицирован, то информацию о корзине достаем из куки
        else:
            basket_in_cookies = request.COOKIES.get("basket", 0)

            if isinstance(basket_in_cookies, str):
                basket_in_cookies = json.loads(basket_in_cookies)

            # если корзины еще нет, то создаем ее
            if not isinstance(basket_in_cookies, dict):

                basket_in_cookies = {}
                if quantity <= product.count:
                    basket_in_cookies[f"{product.pk}"] = quantity
                else:
                    basket_in_cookies[f"{product.pk}"] = product.count

            # если корзина уже есть в куки
            else:
                product_in_basket_count = basket_in_cookies.get(f"{product.pk}", False)

                # если в корзине уже есть текущий товар, то изменяем его количество
                if product_in_basket_count:
                    if product_in_basket_count + quantity <= product.count:
                        basket_in_cookies[f"{product.pk}"] = (
                            product_in_basket_count + quantity
                        )
                    else:
                        basket_in_cookies[f"{product.pk}"] = product.count

                # если товара нет, то добавляем его в корзину
                else:
                    if quantity <= product.count:
                        basket_in_cookies[f"{product.pk}"] = quantity
                    else:
                        basket_in_cookies[f"{product.pk}"] = product.count

            # получаем объекты товара из БД, сериализуем и возвращаем на фронтэнд
            products = Product.objects.filter(pk__in=basket_in_cookies.keys()).all()
            serialized = BasketSerializer(
                products, context={"basket": basket_in_cookies}, many=True
            )
            response = Response(serialized.data)
            response.set_cookie(
                key="basket", value=json.dumps(basket_in_cookies), max_age=360000000
            )
            return response

    def delete(self, request: Request) -> Response:
        """
        Метод для удаления или уменьшения количества выбранного товара в корзине пользователя

        :return: Response со списком отсериализованных товаров в корзине
        """

        # т.к. в методе delete данные отправляются на бэкэнд в виде plain text вместо json,
        # то сначала преобразовываем полученные через парсер данные в байтах в стоковый формат

        req_dict: bytes = request.data
        dict_str: str = req_dict.decode()
        data_dict: dict = literal_eval(dict_str)
        count_to_delete: int = data_dict["count"]

        product = Product.objects.filter(pk=data_dict["id"]).first()

        # если пользователь аутентифицирован, то достаем из БД корзину и меняем количество выбранного товара:
        if request.user.is_authenticated:
            basket = Basket.objects.filter(user=request.user).first()
            basket_product = BasketProduct.objects.filter(
                basket=basket, product=product
            ).first()
            if count_to_delete >= basket_product.quantity:
                basket_product.delete()
            else:
                basket_product.quantity -= count_to_delete
                basket_product.save()
            products_in_basket = basket.products.all()
            serialized = BasketSerializer(
                products_in_basket, context={"basket": basket}, many=True
            )
            return Response(serialized.data)

        # если пользователь не аутентифицирован, то достаем корзину из куки и меняем количество товара в ней
        else:
            basket_in_cookies = request.COOKIES.get("basket", 0)

            if isinstance(basket_in_cookies, str):
                basket_in_cookies = json.loads(basket_in_cookies)

            if count_to_delete >= basket_in_cookies[f"{product.pk}"]:
                basket_in_cookies.pop(f"{product.pk}")
            else:
                basket_in_cookies[f"{product.pk}"] = (
                    basket_in_cookies[f"{product.pk}"] - count_to_delete
                )

            # возвращаем отсериализованные данные о продуктах корзины на фронтэнд

            products = Product.objects.filter(pk__in=basket_in_cookies.keys()).all()
            serialized = BasketSerializer(
                products, context={"basket": basket_in_cookies}, many=True
            )
            response = Response(serialized.data)
            response.set_cookie(
                key="basket", value=json.dumps(basket_in_cookies), max_age=360000000
            )
            return response
