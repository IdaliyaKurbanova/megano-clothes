# Generated by Django 5.0.1 on 2024-03-03 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="subcategories",
            field=models.ManyToManyField(to="catalogs.category"),
        ),
    ]
