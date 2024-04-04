# Generated by Django 5.0.1 on 2024-03-03 18:21

import catalogs.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("title", models.CharField(max_length=250)),
                ("level", models.IntegerField(default=0)),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=catalogs.models.get_category_file_name,
                    ),
                ),
                (
                    "subcategories",
                    models.ManyToManyField(
                        blank=True,
                        null=True,
                        related_name="parent_category",
                        to="catalogs.category",
                    ),
                ),
            ],
        ),
    ]