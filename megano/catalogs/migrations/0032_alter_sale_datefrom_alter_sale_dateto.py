# Generated by Django 5.0.1 on 2024-03-25 11:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0031_alter_product_category_alter_sale_datefrom_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="dateFrom",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 25, 14, 50, 49, 244238)
            ),
        ),
        migrations.AlterField(
            model_name="sale",
            name="dateTo",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 25, 14, 50, 49, 244238)
            ),
        ),
    ]
