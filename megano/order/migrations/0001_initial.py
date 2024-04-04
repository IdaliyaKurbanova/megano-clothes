# Generated by Django 5.0.1 on 2024-03-19 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Delivery",
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
                ("type", models.CharField(max_length=250)),
                ("description", models.TextField(blank=True)),
                (
                    "price",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=6),
                ),
                (
                    "min_amount_for_free",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=10),
                ),
            ],
        ),
    ]
