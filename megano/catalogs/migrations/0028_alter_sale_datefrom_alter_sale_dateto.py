# Generated by Django 5.0.1 on 2024-03-21 10:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0027_alter_sale_datefrom_alter_sale_dateto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="dateFrom",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 21, 13, 22, 7, 15476)
            ),
        ),
        migrations.AlterField(
            model_name="sale",
            name="dateTo",
            field=models.DateField(
                default=datetime.datetime(2024, 3, 21, 13, 22, 7, 15476)
            ),
        ),
    ]