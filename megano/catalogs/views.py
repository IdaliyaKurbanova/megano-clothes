from datetime import datetime

from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q, Count, F, Sum, DecimalField, Subquery, OuterRef, Min
from rest_framework.views import APIView

from order.models import OrderProduct
from profile_user.models import Profile
from .models import Category, Product, Tag, Review, Sale
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    TagSerializer,
    AloneProductSerializer,
    ReviewSerializer,
    SaleSerializer,
)
from rest_framework.response import Response
from rest_framework.request import Request


# словарь для добавления перед признаком сортировки знака "-",
# в зависимости от того, сортируется список по возрастанию или убыванию
sorting_dict: dict = {"inc": "-", "dec": ""}


def get_page_borders(
    limit: int, current_page: int, items: list
) -> tuple[int, int, int]:
    """
    Функция для определения границ среза в списке продуктов для пагинации
    и определения номера последней возможной страницы при пагинации.

    limit: int - количество единиц выводимого товара на одной странице
    current_page: int - номер текущей просматриваемой страницы
    items: список с товарами

    """
    right_border: int = limit * current_page
    left_border: int = right_border - limit

    if len(items) % limit == 0:
        max_page = len(items) // limit
    else:
        max_page = len(items) // limit + 1

    return right_border, left_border, max_page


def get_categories(category_pk: int) -> list:
    """
    Функция, определяющая все категории, по которым необходимо фильтровать получаемые продукты.
    То есть, если с фронтэнда получен номер родительской категории,
    то для дальнейшей фильтрации нужно найти все дочерние категории,
    т.к. товары связаны с дочерними категориями, а не родительскими.

    :param category_pk: номер категории с фронтэнда, по которой необходимо отфильтровать товары.
    :return: список подкатегорий, которые непосредственно связаны с продуктами
    """
    category = (
        Category.objects.filter(pk=category_pk)
        .prefetch_related("subcategories")
        .first()
    )
    if category.subcategories.all():
        categories: list[int] = [sub.pk for sub in category.subcategories.all()]
    else:
        categories: list[int] = [category.pk]
    return categories


class CategoryListView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд списка категорий со всеми дочерними подкатегориями.
    """

    def get(self, request: Request) -> Response:
        categories: list = Category.objects.filter(level=0).prefetch_related(
            "subcategories"
        )
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CatalogView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд списка товаров в категории
    """

    def get(self, request: Request) -> Response:
        """
        Метод получает с фрондэнда параметры в виде querystring, по которым в дальнейшем товары сортируются.
        :param request: Request
        :return: Response со списком товаров для отображения в каталоге на текущей странице
        """

        # список тэгов, которые должны содержаться в искомых товарах
        tags: list = request.query_params.getlist("tags[]", 0)

        # строка, которая должна содержаться в названии товара
        name: str = request.query_params.get("filter[name]")

        # минимальная цена искомого товара
        min_price: int = int(request.query_params.get("filter[minPrice]"))

        # максимальная цена искомого товара
        max_price: int = int(request.query_params.get("filter[maxPrice]"))

        # значение True или False в зависимости, должен ли товар быть с бесплатной доставкой
        free_delivery: str = request.query_params.get(
            "filter[freeDelivery]"
        ).capitalize()

        # значение True или False в зависимости, должен ли товар быть в наличии
        available: str = request.query_params.get("filter[available]").capitalize()

        # количество товаров, которые необходимо разместить на одной странице
        limit: int = int(request.query_params.get("limit"))

        # номер текущей просматриваемой страницы
        current_page: int = int(request.query_params.get("currentPage"))

        # признак для сортировки товаров: может быть price, rating, review или date
        sort_by: str = request.query_params.get("sort")

        # номер категории, товары которой необходимо вывести
        category_pk: int = request.query_params.get("category")

        # получаем из БД список товаров и сразу фильтруем их по содержащемся в названии тексте,
        # минимальной и максимальной цене и убираем товары, представляющее собой доставку.
        products: list[Product] = (
            Product.objects.filter(
                Q(title__iregex=name) & Q(price__range=(min_price, max_price))
            )
            .exclude(description__iregex="доставка")
            .prefetch_related("tags")
            .prefetch_related("images")
            .prefetch_related("reviews")
            .prefetch_related("category")
        ).distinct()

        # если необходимо отсортировать по количеству отзывов, то к товарам добавляется
        # аннотация с количеством отзывов и затем производится сортировка.
        # в другом случае сразу производится сортировка по необходимому признаку
        if sort_by == "reviews":
            products: list[Product] = products.annotate(
                review_count=Count("reviews")
            ).order_by(
                sorting_dict[request.query_params.get("sortType")] + "review_count"
            )
        else:
            order_by: str = sorting_dict[request.query_params.get("sortType")] + sort_by
            products = products.order_by(order_by)

        # фильтрация товаров в зависимости от того, выбраны ли бесплатная доставка и наличие товаров
        if free_delivery == "True" and available == "True":
            products = products.filter(Q(freeDelivery=True) & Q(count__gt=0))
        elif free_delivery == "True" and available == "False":
            products = products.filter(freeDelivery=True)
        elif available == "True" and free_delivery == "False":
            products = products.filter(count__gt=0)

        # фильтрация товаров, если пользователем выбраны тэги
        if tags:
            products: list[Product] = products.filter(tags__pk__in=tags).distinct()

        # фильтрация товаров, если необходима определенная категория
        if category_pk:
            categories: list[int] = get_categories(category_pk)
            products: list[Product] = products.filter(
                category__pk__in=categories
            ).distinct()

        # определение, с какого по какой элемент списка необходимо взять для размещения на текущей странице,
        # а также самой последней возможной страницы пагинации
        right_border, left_border, max_page = get_page_borders(
            limit, current_page, products
        )

        serialized = ProductSerializer(products[left_border:right_border], many=True)
        return Response(
            {
                "items": serialized.data,
                "currentPage": current_page,
                "lastPage": max_page,
            }
        )


class TagListView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд списка возможных тэгов для фильтрации
    """

    def get(self, request: Request) -> Response:
        """
        Метод получает из БД все существующие тэги,
        а затем фильтрует по полученной из querystring категории, если она, конечно, была выбрана.
        :param request: Request
        :return: Response со списком тэгов, пройденных через соответствующий сериализатор
        """
        category_pk: int = request.query_params.get("category")
        tags: list[Tag] = Tag.objects.all()

        if category_pk:
            categories: list[int] = get_categories(category_pk)
            products_in_categories: list[Product] = Product.objects.filter(
                category__pk__in=categories
            )
            tags: list[Tag] = tags.filter(
                products__in=products_in_categories
            ).distinct()

        serialized = TagSerializer(tags, many=True)
        return Response(serialized.data)


class ProductRetrieveView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд информации об отдельном товаре.
    """

    def get(self, request: Request, id: int) -> Response:
        """
        Метод получает на вход id отдельного товара, получает его из БД и возвращает, используя сериализатор.
        :param request:
        :param id: pk-номер искомого товара в БД
        :return: Response с информацией об отдельном товаре
        """
        product: Product = (
            Product.objects.filter(pk=id).prefetch_related("sales").first()
        )
        serialized = AloneProductSerializer(product)
        return Response(serialized.data)


class ReviewPostView(APIView):
    """
    API-класс с методом post для создания нового отзыва о товаре.
    К методам класса применяется ограничение - новый отзыв может разместить
    только аутентифицированный пользователь.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, id: int) -> Response:
        """
        Метод проверяет, писал ли текущий пользователь отзыв на данный товар,
        и если не писал, то создает в БД новый отзыв, который привязывается к продукту и пользователю.

        :param id: pk-номер товара, отзыв на который необходимо создать
        :return: Response со списком отзывов для данного товара
        """
        product: Product = Product.objects.get(pk=id)

        # получаем профиль текущего пользователя, а если еще не существует, то создаем его.
        try:
            profile: Profile = Profile.objects.get(user=request.user)
        except Exception:
            user = User.objects.get(pk=request.user.pk)
            profile: Profile = Profile.objects.create(user=user)

        # проверяем, есть ли в БД отзыв для данного товара от текущего пользователя
        review = Review.objects.filter(Q(product=product) & Q(profile=profile))

        # если отзыв уже есть, то возвращается ответ по статусом 400, в противном случае - создается новый отзыв
        if review:
            return Response(
                {"error": "Данный пользователь уже писал отзыв на этот товар"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            Review.objects.create(
                profile=profile,
                author=request.data.get("author", ""),
                email=request.data.get("email", ""),
                text=request.data.get("text", ""),
                rate=request.data.get("rate", ""),
                product=product,
            )
            product.avg_rating = product.avg_rating

        # получаем все отзывы для данного товара и передаем через сериализатор на фронтэнд.
        reviews = Review.objects.filter(product=product).all()
        serialized = ReviewSerializer(reviews, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class SaleView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд списка акционных товаров.
    """

    def get(self, request: Request) -> Response:
        """
        Метод получает их БД список акционных товаров и передает их на фронтэнд, используя сериализатор.
        :return: Response со списком текущих акционных товаров.
        """
        # получаем номер текущей страницы для пагинации
        current_page: int = int(request.query_params.get("currentPage"))

        # установили количество элементов на странице по умолчанию как 20,
        # поскольку данный параметр не передается на бэкэнд.
        limit: int = 20

        sales: list[Sale] = Sale.objects.filter(
            dateTo__gte=datetime.now(), dateFrom__lte=datetime.now()
        ).all()

        right_border, left_border, max_page = get_page_borders(
            limit, current_page, sales
        )

        serialized = SaleSerializer(sales[left_border:right_border], many=True)
        return Response(
            {
                "items": serialized.data,
                "currentPage": current_page,
                "lastPage": max_page,
            }
        )


class LimitedProductsView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд списка лимитированных товаров.
    """

    def get(self, request: Request) -> Response:
        """
        Метод получает из БД 16 товаров, у которых признак limited_edition = True и возвращает на фронтэнд,
        используя сериализатор.

        :return: Response со списком лимитированных товаров.
        """

        limited_products: list[Product] = (
            Product.objects.filter(limited_edition=True, count__gt=0)
            .prefetch_related("tags")
            .prefetch_related("images")
            .prefetch_related("reviews")
            .prefetch_related("category")[:16]
        )
        serialized = ProductSerializer(limited_products, many=True)
        return Response(serialized.data)


class BannersView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд товаров из 3-х избранных категорий.
    """

    def get(self, request: Request) -> Response:
        """
        Метод фильтрует по одному самому дешёвому товару из 3-х избранных категорий - 'Платья', 'Бижутерия', 'Туфли'
        и передает на фронтэнд.

        :return: Response с самым дешёвым товаром в каждой из избранных категорий.
        """
        # добавляем к каждой категории минимальную цену товара в данной категории
        categories_with_min_price = Category.objects.annotate(
            min_price=Min("product__price", output_field=DecimalField())
        ).all()
        # выбираем 3 категории - 'Платья', 'Бижутерия', 'Туфли'
        filtered_categories = categories_with_min_price.filter(
            min_price__isnull=False, title__in=["Платья", "Бижутерия", "Туфли"]
        )

        # добавляем условия для фильтрации товаров при помощи Q-объектов, объеденных через знак | (или)
        cond = Q()
        for item in filtered_categories:
            cond |= Q(category=item.pk, price=item.min_price)

        # фильтруем товары, у которых категория избранная, а цена - минимальная внутри категории
        products = (
            Product.objects.filter(cond)
            .filter(count__gt=0)
            .prefetch_related("tags")
            .prefetch_related("images")
            .prefetch_related("reviews")
            .prefetch_related("category")
        )

        serialized = ProductSerializer(products, many=True)
        return Response(serialized.data)


class PopularProductsView(APIView):
    """
    API-класс с методом get для передачи на фронтэнд 8 самых популярных товаров
    """

    def get(self, request: Request) -> Response:
        """
        Метод получает из БД имеющиеся в наличии товары, фильтрует из по количеству отзывов (не менее 3-х)
        и сортирует по убыванию суммы принесенной выручки, а если выручка совпадает, то по количество проданных единиц товара.

        :return: Response со списком популярных товаров
        """

        products: list[Product] = (
            Product.objects.annotate(reviews_count=Count("reviews"))
            .filter(reviews_count__gte=3, count__gt=0)
            .prefetch_related("tags")
            .prefetch_related("images")
            .prefetch_related("reviews")
            .prefetch_related("category")
            .all()
        )

        # Подзапрос для вычисления выручки, которую принес каждый из проданных товаров
        product_revenue_subquery: list[tuple] = (
            OrderProduct.objects.filter(order__status__title="Оплачен")
            .values("product")
            .annotate(
                revenue=Sum(
                    F("quantity") * F("final_price"), output_field=DecimalField()
                )
            )
            .values("product", "revenue")
        )

        # Подзапрос для вычисления общего количества проданных товаров для каждого продукта
        product_quantity_subquery = (
            OrderProduct.objects.filter(order__status__title="Оплачен")
            .values("product")
            .annotate(total_quantity=Sum("quantity"))
            .values("product", "total_quantity")
        )

        # при помощи подзапросов добавляем к каждому продукту из первого запроса выручку от товара и общее количество
        # проданного товара, а затем сортируем в порядке убывания выручки, а если выручка совпадает, то по количеству
        # проданного товара, а если совпадает количество, то по рейтингу товара

        products_with_revenue: list[Product] = products.annotate(
            revenue=Subquery(
                product_revenue_subquery.filter(product=OuterRef("pk")).values(
                    "revenue"
                )[:1],
                output_field=DecimalField(),
            ),
            total_quantity=Subquery(
                product_quantity_subquery.filter(product=OuterRef("pk")).values(
                    "total_quantity"
                )[:1],
                output_field=DecimalField(),
            ),
        ).order_by("-revenue", "-total_quantity", "-rating")

        serialized = ProductSerializer(products_with_revenue[:8], many=True)
        return Response(serialized.data)
