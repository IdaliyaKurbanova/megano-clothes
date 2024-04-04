# Generated by Django 5.0.1 on 2024-03-04 11:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0003_alter_category_subcategories"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                (
                    "price",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=10),
                ),
                ("count", models.IntegerField(default=0)),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=300)),
                ("fullDescription", models.TextField(blank=True)),
                ("freeDelivery", models.BooleanField(default=False)),
                ("rating", models.IntegerField(blank=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="catalogs.category",
                    ),
                ),
            ],
        ),
    ]
