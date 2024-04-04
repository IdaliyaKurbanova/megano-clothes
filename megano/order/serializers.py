from rest_framework import serializers

from .models import Order, OrderProduct
from catalogs.serializers import ProductSerializer


class OrderProductSerializer(ProductSerializer):
    """
    Сериализатор для отражения информации о продукте в заказе. Наследуется от базового сериализатора товара.
    """

    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        """
        Метод для получения количества товара в заказе через заказ, переданный в контексте.

        :return: количество товара в заказе
        """
        order = self.context.get("order")
        order_product = OrderProduct.objects.filter(order=order, product=obj).first()
        return order_product.quantity


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отражения информации о заказе.
    """

    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    deliveryType = serializers.SerializerMethodField()
    paymentType = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        ]

    def get_fullName(self, obj):
        """
        Метод для получения полного имени пользователя, создавшего заказ, через его профиль, связанный с заказом.

        :return: полное имя пользователя
        """
        if obj.fullName:
            return obj.fullName
        return obj.profile.fullName

    def get_email(self, obj):
        """
        Метод для получения почты пользователя, создавшего заказ, через его профиль, связанный с заказом.

        :return: эл.почта пользователя
        """
        if obj.email:
            return obj.email
        return obj.profile.email

    def get_phone(self, obj):
        """
        Метод для получения телефона пользователя, создавшего заказ, через его профиль, связанный с заказом.

        :return: телефон пользователя
        """
        if obj.phone:
            return obj.phone
        return obj.profile.phone

    def get_status(self, obj):
        """
        Метод получения названия статуса заказа

        :return: название статуса заказа
        """
        return obj.status.title

    def get_createdAt(self, obj):
        """
        Метод для получения даты создания заказа в виде строки.

        :return: Дата создания заказа в виде строки.
        """
        return obj.createdAt.strftime("%d-%m-%Y %H:%M")

    def get_products(self, obj):
        """
        Получение отсериализованных данных о продуктах в заказе.

        :return: Отсериализованный список продуктов в заказе
        """
        serialized = OrderProductSerializer(
            obj.products, many=True, context={"order": obj}
        )
        return serialized.data

    def get_deliveryType(self, obj):
        """
        Получение названия типа доставки заказа

        :return: название типа доставки
        """
        if obj.deliveryType:
            return obj.deliveryType.type

    def get_paymentType(self, obj):
        """
        Получение названия типа оплаты

        :return: название типа оплаты
        """
        if obj.paymentType:
            return obj.paymentType.type
