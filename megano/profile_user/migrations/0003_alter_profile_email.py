# Generated by Django 5.0.1 on 2024-03-04 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profile_user", "0002_alter_profile_phone"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="email",
            field=models.EmailField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
