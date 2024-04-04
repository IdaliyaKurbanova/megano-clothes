"""
Модуль с представлениями для работы с платежами.
"""

from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogs.models import Product, Sale
from order.models import Order, OrderProduct, Status
from .models import PaymentItem


class PaymentView(APIView):
    """
    API-класс с методом для валидации и создания платежа.
    """

    def post(self, request: Request, id: int) -> Response:
        # поменяли payment.js, строка 10, т.к. не отправлялся введенный номер карты на бэкэнд

        number = "".join(request.data["number"].split(" "))

        # если введенный пользователем номер карты отсутствует, а также если номер карты нечетный или заканчивается
        # на ноль, то возвращается ответ со статусом 400 и сообщением об ошибке
        if number:
            number = int(number)
            if number % 2 != 0 or number % 10 == 0:
                return Response(
                    {"error": "Ошибка оплаты - некорректный номер карты"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Ошибка оплаты - отсутствует номер карты"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        month = request.data["month"]
        year = request.data["year"]

        # возвращается ответ со статусом 400 и сообщением об ошибке, если:
        # 1) год и месяц действия карты не введены пользователем
        # 2) если год и месяц - не числа
        # 3) если некорректное количество символов в месяце или годе
        # 4) если срок действия карты истек
        # 5) если число месяца больше 12

        if (
            (month and year)
            and (len(year) == 2 or len(year) == 4)
            and len(month) == 2
            and year.isdigit()
            and month.isdigit()
        ):
            month = int(month)
            if len(year) == 2:
                year = int("20" + year)
            else:
                year = int(year)

            if month > 12:
                return Response(
                    {
                        "error": "Ошибка оплаты - некорректный месяц срока действия карты"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                if datetime.now().year > year:
                    return Response(
                        {"error": "Ошибка оплаты - срок действия карты истек"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif datetime.now().year == year:
                    if datetime.now().month > month:
                        return Response(
                            {"error": "Ошибка оплаты - срок действия карты истек"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
        else:
            return Response(
                {
                    "error": "Ошибка оплаты - отсутствует срок действия карты или он некорректен"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = request.data["code"]

        # возвращается ответ со статусом 400 и сообщением об ошибке,
        # если код отсутствует, он не является числом или его длина больше 3-х
        if code:
            if not code.isdigit() or len(code) != 3:
                return Response(
                    {"error": "Ошибка - код CVV введен некорректно"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"error": "Ошибка - отсутствует код CVV"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.filter(pk=id).first()

        # если у заказа иной статус, кроме "Ожидает оплаты", то возвращается сообщение об ошибке и статус 400
        # в ином случае создается платеж PaymentItem
        if order.status.title == "Ожидает оплаты":
            PaymentItem.objects.create(
                profile=request.user.profile,
                order=order,
                number=number,
                year=year,
                month=month,
                code=code,
            )
        else:
            return Response(
                {"error": "Заказ уже оплачен"}, status=status.HTTP_400_BAD_REQUEST
            )

        order_products = (
            OrderProduct.objects.filter(order=order)
            .exclude(product__description__iregex="доставка")
            .all()
        )

        # после платежа заказу присваивается новый статус "Оплачен"
        new_status = Status.objects.filter(title="Оплачен").first()
        order.status = new_status
        order.save()

        # для каждого товара в заказе в связи OrderProduct добавляется финальная цена,
        # чтобы понимать, по какой итоговой цене продукт был продан.
        # а также для каждого продукта обновляется количество на складе с учетом продажи
        for ord_product in order_products:
            try:
                sale = Sale.objects.get(
                    product_id=ord_product.product.pk,
                    dateFrom__lte=datetime.now(),
                    dateTo__gte=datetime.now(),
                )
                ord_product.final_price = sale.salePrice
            except ObjectDoesNotExist:
                ord_product.final_price = ord_product.product.price
            ord_product.save()
            Product.objects.filter(pk=ord_product.product.pk).update(
                count=F("count") - ord_product.quantity
            )

        return Response(status=status.HTTP_200_OK)
