from rest_framework import serializers
from .models import BasketProduct
from catalogs.serializers import ProductSerializer


class BasketSerializer(ProductSerializer):
    """
    Сериализатор для товара в корзине. Наследуется от базового сериализатора для товара.
    """

    count: int = serializers.SerializerMethodField()

    def get_count(self, obj):
        """
        Метод, переопределяющий метод базового класса по представлению количества товара.
        Возвращает не общее количество товара на складе, а количество товара именно в корзине.

        :return: количество товара в корзине
        """

        # получаем данные о корзине, которые передаются в контекст сериализатора:
        # объект basket(если аутентифицированный пользователь) или словарь (если корзина хранится в куки)

        basket = self.context.get("basket")
        if not isinstance(basket, dict):
            basket_product = BasketProduct.objects.filter(
                basket=basket, product=obj
            ).first()
            return basket_product.quantity
        else:
            count: int = basket[f"{obj.pk}"]
            return count
