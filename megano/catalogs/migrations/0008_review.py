# Generated by Django 5.0.1 on 2024-03-04 17:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0007_specification"),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
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
                ("author", models.CharField(max_length=150)),
                ("email", models.CharField(blank=True, max_length=150, null=True)),
                ("text", models.TextField(blank=True, null=True)),
                ("rate", models.IntegerField()),
                ("date", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="catalogs.product",
                    ),
                ),
            ],
        ),
    ]