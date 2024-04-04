from django.urls import path, include
from .views import OrdersView, SingleOrderView

app_name = "order"

urlpatterns = [
    path("api/orders/", OrdersView.as_view()),
    path("api/order/<int:id>/", SingleOrderView.as_view()),
]
