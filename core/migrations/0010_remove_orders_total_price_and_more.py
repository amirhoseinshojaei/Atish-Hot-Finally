# Generated by Django 5.1.4 on 2024-12-19 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_orders_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='total_price',
        ),
        migrations.AlterField(
            model_name='orders',
            name='identification_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
