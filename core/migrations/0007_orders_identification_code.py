# Generated by Django 5.1.4 on 2024-12-18 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_orderitem_orders_productsimage_delete_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='identification_code',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
