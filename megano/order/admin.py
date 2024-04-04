from django.contrib import admin
from order.models import Order, Delivery, Payment, Status


class ProductInline(admin.StackedInline):
    """
    inline-класс для отражения продуктов внутри заказа
    """

    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Класс для отражения в админ-панели информации о заказах
    """

    inlines = (ProductInline,)
    list_display = "pk", "profile", "status", "city", "deliveryType"
    list_display_links = (
        "pk",
        "profile",
        "status",
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """
    Класс для отражения в админ-панели информации о типах доставки
    """

    list_display = "pk", "type", "price"
    list_display_links = "pk", "type", "price"


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """
    Класс для отражения в админ-панели информации о статусах заказов
    """

    list_display = "pk", "title", "description"
    list_display_links = (
        "pk",
        "title",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Класс для отражения в админ-панели информации о типах оплаты
    """

    list_display = (
        "pk",
        "type",
        "description",
    )
    list_display_links = "pk", "type", "description"
