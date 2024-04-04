# Generated by Django 5.0.1 on 2024-03-28 10:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("order", "0010_alter_order_email_alter_order_phone"),
        ("profile_user", "0003_alter_profile_email"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number", models.IntegerField(max_length=16)),
                ("year", models.IntegerField(max_length=4)),
                ("month", models.IntegerField(max_length=2)),
                ("code", models.IntegerField(max_length=3)),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment",
                        to="order.order",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="profile_user.profile",
                    ),
                ),
            ],
        ),
    ]
