# Generated by Django 5.0.1 on 2024-03-29 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0010_alter_order_email_alter_order_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderproduct",
            name="final_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
