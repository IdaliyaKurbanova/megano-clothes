from django.urls import path
from .views import PaymentView

app_name = "payment"

urlpatterns = [
    path("api/payment/<int:id>/", PaymentView.as_view()),
]
