from django.contrib import admin
from .models import Category, Product, ProductImage, Review, Specification, Tag, Sale


class ProductImageInline(admin.TabularInline):
    """
    Класс для просмотра и загрузки фото товара внутри деталей товара в админ-панели.
    """

    model = ProductImage


class TagInline(admin.StackedInline):
    """
    Класс для просмотра тэгов товара внутри деталей товара в админ-панели.
    """

    model = Product.tags.through


class SpecificationInline(admin.TabularInline):
    """
    Класс для просмотра спецификаций товара внутри деталей товара в админ-панели.
    """

    model = Product.specifications.through


class ReviewInline(admin.TabularInline):
    """
    Класс для просмотра отзывов товара внутри деталей товара в админ-панели.
    """

    model = Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Класс для отображения объектов Категории в админ-панели
    """

    list_display = "pk", "title", "image"
    list_display_links = "pk", "title"

    def get_queryset(self, request):
        """
        Метод для отображения внутри категории также дочерних подкатегорий
        """
        return Category.objects.prefetch_related("subcategories")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Класс для отображения объектов товара в админ-панели
    """

    inlines = (
        ProductImageInline,
        TagInline,
        SpecificationInline,
        ReviewInline,
    )
    list_display = "pk", "title", "category", "description", "price", "count", "rating"
    list_display_links = "pk", "title", "price"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Класс для отображения объектов отзыва в админ-панели
    """

    list_display = "pk", "author", "email", "rate", "text"
    list_display_links = "author", "rate"


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    """
    Класс для отображения объектов спецификаций в админ-панели
    """

    list_display = (
        "pk",
        "name",
        "value",
    )
    list_display_links = "name", "value"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Класс для отображения объектов Тэга в админ-панели
    """

    list_display = (
        "pk",
        "name",
    )
    list_display_links = ("name",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """
    Класс для отображения акций на товары в админ-панели
    """

    list_display = (
        "pk",
        "product_name",
        "product_price",
        "salePrice",
        "dateFrom",
        "dateTo",
        "discount_percentage",
    )
    list_display_links = "pk", "product_name", "salePrice", "dateFrom", "dateTo"

    def product_price(self, obj: Sale):
        """
        Метод для отображения обычной цены товара по акции
        """
        return obj.product.price

    def product_name(self, obj: Sale):
        """
        Метод для отображения названия товара по акции
        """
        return obj.product.title
