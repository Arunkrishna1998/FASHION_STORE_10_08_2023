# Generated by Django 4.2.3 on 2023-08-03 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0053_return_request_moreinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='return_request',
            name='item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='store.orderproduct'),
            preserve_default=False,
        ),
    ]
