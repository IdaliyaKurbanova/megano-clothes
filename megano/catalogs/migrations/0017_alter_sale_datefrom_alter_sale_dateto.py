# Generated by Django 5.0.1 on 2024-03-13 12:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0016_product_limited_edition_alter_sale_datefrom_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="dateFrom",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 13, 15, 26, 28, 673369)
            ),
        ),
        migrations.AlterField(
            model_name="sale",
            name="dateTo",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 13, 15, 26, 28, 673369)
            ),
        ),
    ]
