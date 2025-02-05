# Generated by Django 5.0.1 on 2024-02-26 17:52

import django.db.models.deletion
import profile_user.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
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
                ("fullName", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "email",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                ("phone", models.CharField(blank=True, max_length=15, null=True)),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        default="profiles/no_avatar.jpg",
                        null=True,
                        upload_to=profile_user.models.get_avatar_file_name,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
