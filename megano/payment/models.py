from django.db import models
from order.models import Order
from profile_user.models import Profile


class PaymentItem(models.Model):
    """
    Модель для проводимого платежа, который связан с профилем пользователя и заказом.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    number = models.IntegerField()
    year = models.IntegerField()
    month = models.IntegerField()
    code = models.IntegerField()
