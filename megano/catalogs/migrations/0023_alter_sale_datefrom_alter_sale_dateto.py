# Generated by Django 5.0.1 on 2024-03-20 07:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0022_alter_sale_datefrom_alter_sale_dateto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="dateFrom",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 20, 10, 34, 30, 265570)
            ),
        ),
        migrations.AlterField(
            model_name="sale",
            name="dateTo",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 20, 10, 34, 30, 265570)
            ),
        ),
    ]
