from datetime import datetime
from rest_framework import serializers
from .models import Category, Product, ProductImage, Tag, Review, Specification, Sale
from rest_framework_recursive.fields import RecursiveField
from django.core.exceptions import ObjectDoesNotExist


class ImageFieldSerializer(serializers.Field):
    """
    Сериализатор для отображения данных о картинке в поле модели.
    """

    def to_representation(self, value):
        return {
            "src": value.url,
            "alt": value.name,
        }


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о фото товара(отдельная модель).
    """

    def to_representation(self, instance: ProductImage):
        return {
            "src": instance.image.url,
            "alt": instance.image.name,
        }


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели тэга товара.
    """

    class Meta:
        model = Tag
        fields = ["id", "name"]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели отзыва.
    """

    class Meta:
        model = Review
        fields = ["author", "email", "text", "rate", "date"]


class SpecificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели спецификации.
    """

    class Meta:
        model = Specification
        fields = ["name", "value"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели категории. Подкатегории выводятся на основе рекурсивного метода.
    """

    image = ImageFieldSerializer()
    subcategories = RecursiveField(many=True)

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели продукта (менее детальная). В основном используется при передаче на фронтэнд списка товаров.
    Для фото товара и тэгов товара как отдельных моделей используются отдельные сериализаторы.
    """

    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        ]

    def get_count(self, obj):
        return obj.count

    def get_price(self, obj):
        """
        Метод для отображения цены товара. Если у товара есть действующая акции,
        то возвращаетя цена по акции. В ином случае, обычная цена.
        :param obj: экземпляр модели продукта
        :return: цена продукта
        """
        try:
            sale = Sale.objects.get(
                product_id=obj.pk,
                dateFrom__lte=datetime.now(),
                dateTo__gte=datetime.now(),
            )
        except ObjectDoesNotExist:
            return obj.price
        return sale.salePrice

    def get_reviews(self, instance):
        """
        Метод, который подсчитывает и возвращает количество отзывов, связанных с товаров.
        :param instance: экземпляр модели продукта
        :return: количество отзывов у продукта
        """
        return instance.reviews.count()


class AloneProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели товара (детальная информация).
    Используется при передаче на фронтэнд информации об отдельном товаре.
    Для фото, тэга, спецификации и отзыва товара как отдельных моделей используются отдельные сериализаторы.
    """

    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        ]

    def get_price(self, obj):
        """
        Метод для отображения цены товара. Если у товара есть действующая акции,
        то возвращаетя цена по акции. В ином случае, обычная цена.
        :param obj: экземпляр модели продукта
        :return: цена продукта
        """
        try:
            sale = Sale.objects.get(
                product_id=obj.pk,
                dateFrom__lte=datetime.now(),
                dateTo__gte=datetime.now(),
            )
        except ObjectDoesNotExist:
            return obj.price
        return sale.salePrice


class SaleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для акции на товар.
    """

    id = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]

    def get_id(self, obj):
        """
        Метод для получения id товара через связанный с акцией товар.
        :param obj: экземпляр модели акции
        :return: id товара
        """
        id = obj.product.pk
        return id

    def get_price(self, obj):
        """
        Метод для получения обычной цены товара через связанный с моделью товар.
        :param obj: экземпляр модели акции
        :return: цена товара
        """
        price = obj.product.price
        return price

    def get_title(self, obj):
        """
        Метод для получения названия товара через связанный с моделью товар.
        :param obj: экземпляр модели акции
        :return: название товара
        """
        title = obj.product.title
        return title

    def get_images(self, obj):
        """
        Метод для получения всех фото товара через связанный с моделью товар.
        :param obj: экземпляр модели акции
        :return: фото товара
        """
        images = obj.product.images.all()
        return ProductImageSerializer(images, many=True).data
