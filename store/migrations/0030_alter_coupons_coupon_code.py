# Generated by Django 4.2.3 on 2023-07-26 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_payment_order_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupons',
            name='coupon_code',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
