from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Case, When, DecimalField, F, Sum

from catalogs.models import Product, Sale
from profile_user.models import Profile


class Delivery(models.Model):
    """
    Модель для типа доставки
    """

    type = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    min_amount_for_free = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        return f"{self.type} - {self.price}, {self.description}"


class Payment(models.Model):
    """
    Модель для типа оплаты
    """

    type = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.type}"


class Status(models.Model):
    """
    Модель для статуса заказа
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title}"


class Order(models.Model):
    """
    Модель для заказа. Один заказ может быть связан с несколькими продуктами через связь OrderProduct,
    и один продукт может быть связан с несколькими заказами.
    """

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, related_name="orders", null=True
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    fullName = models.CharField(null=True, blank=True, max_length=200)
    email = models.EmailField(null=True, blank=True, max_length=50)
    phone = models.CharField(null=True, blank=True, max_length=15)
    deliveryType = models.ForeignKey(
        Delivery,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="orders",
        null=True,
    )
    paymentType = models.ForeignKey(
        Payment,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="orders",
        null=True,
    )
    status = models.ForeignKey(
        Status, on_delete=models.DO_NOTHING, related_name="orders"
    )
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    products = models.ManyToManyField(
        Product, through="OrderProduct", related_name="orders"
    )

    def totalCost(self) -> int:
        """
        Метод для подсчета общей стоимости заказа. Если у товара есть акционная цена,
        то она участвует в расчете, иначе - обычная цена.

        :return: общая стоимость заказа
        """
        order_products = self.orderproduct_set.annotate(
            sale_price=Case(
                When(
                    product__sales__isnull=False,
                    product__sales__dateFrom__lte=datetime.now(),
                    product__sales__dateTo__gte=datetime.now(),
                    then="product__sales__salePrice",
                ),
                default="product__price",
                output_field=DecimalField(),
            )
        ).annotate(cost=F("sale_price") * F("quantity"))

        total_cost = order_products.aggregate(total=Sum("cost"))["total"]

        return total_cost

    def __str__(self):
        return f"Заказ №{self.pk}"


class OrderProduct(models.Model):
    """
    Модель для связи одного заказа с одним продуктом.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        return f"{self.product.title} - {self.quantity} шт."
