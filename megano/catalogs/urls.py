from django.urls import path
from .views import (
    CategoryListView,
    CatalogView,
    TagListView,
    ProductRetrieveView,
    ReviewPostView,
    SaleView,
    LimitedProductsView,
    BannersView,
    PopularProductsView,
)

app_name = "site_auth"

urlpatterns = [
    path("api/categories/", CategoryListView.as_view()),
    path("api/catalog/", CatalogView.as_view()),
    path("api/product/<int:id>/", ProductRetrieveView.as_view()),
    path("api/product/<int:id>/reviews/", ReviewPostView.as_view()),
    path("api/products/limited/", LimitedProductsView.as_view()),
    path("api/products/popular/", PopularProductsView.as_view()),
    path("api/tags/", TagListView.as_view()),
    path("api/sales/", SaleView.as_view()),
    path("api/banners/", BannersView.as_view()),
]
