# Generated by Django 4.2.3 on 2023-08-03 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0052_return_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='return_request',
            name='moreinfo',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]