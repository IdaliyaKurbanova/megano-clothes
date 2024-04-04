from django.contrib.auth.models import User
from django.db import models
from catalogs.models import Product


class Basket(models.Model):
    """
    Модель, представляющая собой корзину. Корзина может быть связана только с одним пользователем.
    Корзина имеет связь со многими продуктами через модель BasketProduct,
    и каждый продукт может иметь связь сразу с несколькими корзинами в БД.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    session_key = models.CharField(max_length=32, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(
        Product, through="BasketProduct", related_name="baskets"
    )

    def __str__(self):
        return f"Корзина №{self.pk}"


class BasketProduct(models.Model):
    """
    Модель, представляющая собой связь одного продукта с одной корзиной.
    """

    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.title} - {self.quantity} шт."
