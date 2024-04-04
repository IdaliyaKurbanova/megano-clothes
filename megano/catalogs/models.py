from datetime import datetime
from django.utils.timezone import now
from django.db import models
from django.db.models import Avg
from profile_user.models import Profile


def get_category_file_name(instance: "Category", filename) -> str:
    """
    Функция для создания названия пути для файла с фото категории.
    :param instance: объект класса Category
    :param filename: имя загруженного файла
    :return: наименование пути файла в папке uploads
    """
    return "categories/category_{title}/{filename}".format(
        title=instance.title, filename=filename
    )


def get_product_image_name(instance: "ProductImage", filename) -> str:
    """
    Функция для создания названия пути для файла с фото товара.
    :param instance: объект класса ProductImage
    :param filename: имя загруженного файла
    :return: наименование пути файла в папке uploads
    """
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk, filename=filename
    )


class Category(models.Model):
    """
    Модель для хранения в БД категории товара.
    """

    title = models.CharField(max_length=250)
    level = models.IntegerField(null=False, blank=False, default=0)
    image = models.ImageField(null=True, blank=True, upload_to=get_category_file_name)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="subcategories",
    )

    def __str__(self) -> str:
        return f"Категория {self.title!r}, №{self.pk}"


class Product(models.Model):
    """
    Модель для хранения в БД товара.
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="product",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.CharField(blank=True, max_length=300)
    fullDescription = models.TextField(blank=True)
    freeDelivery = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    limited_edition = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.title}, №{self.pk}, цена - {self.price}"

    @property
    def avg_rating(self) -> int:
        """
        Геттер для получения средней оценки всех отзывов товара.
        :return: среднее значение всех отзывов товара
        """
        return self.reviews.aggregate(Avg("rate")).get("rate__avg", 0)

    @avg_rating.setter
    def avg_rating(self, value) -> None:
        """
        Сеттер для обновления значения рейтинга товара.
        :param value: новое значение рейтинга
        """
        self.rating = value
        self.save()


class ProductImage(models.Model):
    """
    Модель, представляющая 1 фото товара. У товара может быть сразу несколько фото.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(null=True, blank=True, upload_to=get_product_image_name)


class Tag(models.Model):
    """
    Модель, представляющая тэг товара. У одного товара может быть несколько тэгов.
    А также один тэг может быть прикреплен сразу к нескольким товарам.
    """

    products = models.ManyToManyField(Product, related_name="tags", blank=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"#{self.name}"


class Specification(models.Model):
    """
    Модель представляющая спецификацию товара. У одного товара может быть несколько спецификаций.
    А также одна спецификация может быть прикреплена сразу к нескольким товарам.
    """

    product = models.ManyToManyField(Product, related_name="specifications", blank=True)
    name = models.CharField(max_length=150)
    value = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.value}"


class Review(models.Model):
    """
    Модель представляющая отзыв. Один отзыв может быть прикреплен только к одному пользователю и к одному товару, но
    у одного товара может быть несколько отзывов, и у одного пользователя может быть несколько отзывов.
    """

    profile = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="reviews"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.CharField(max_length=150)
    email = models.CharField(max_length=150, null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    rate = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.rate} {self.date} {self.author}"


class Sale(models.Model):
    """
    Модель, представляющая акцию на товар. Одна акция на товар sale может быть связана только с одним товаром.
    Но у одного товара может быть несколько акций.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales")
    salePrice = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    dateFrom = models.DateField(default=now)
    dateTo = models.DateField(default=now)

    def __str__(self) -> str:
        return f"{self.product} {self.salePrice} c {self.dateFrom} по {self.dateTo}"

    def discount_percentage(self):
        """
        Метод, который возвращает процент скидки на акционный товар.
        :return: int - процент скидки
        """
        return ((self.product.price - self.salePrice) / self.product.price) * 100
