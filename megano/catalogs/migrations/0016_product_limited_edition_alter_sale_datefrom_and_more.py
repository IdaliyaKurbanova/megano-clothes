# Generated by Django 5.0.1 on 2024-03-13 09:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0015_sale"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="limited_edition",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="sale",
            name="dateFrom",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 13, 12, 10, 0, 413067)
            ),
        ),
        migrations.AlterField(
            model_name="sale",
            name="dateTo",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 13, 12, 10, 0, 413067)
            ),
        ),
    ]