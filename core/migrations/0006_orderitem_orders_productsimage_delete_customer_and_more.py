# Generated by Django 5.1.4 on 2024-12-18 13:17

import core.models
import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_customer_options_customer_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='شماره شما باید با فرمت 09 وارد شود', regex='^09\\d{9}$')])),
                ('city', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=1500)),
                ('postal_code', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Canceled', 'Canceled')], default='Pending', max_length=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_shipped', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'db_table': 'orders',
                'ordering': ['-created_at'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='ProductsImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to=core.models.ProductsImage.get_upload_path)),
            ],
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
        migrations.AddField(
            model_name='products',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.Products.get_upload_path),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='core.products'),
        ),
        migrations.AddField(
            model_name='orders',
            name='products',
            field=models.ManyToManyField(through='core.OrderItem', to='core.products'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='core.orders'),
        ),
        migrations.AddField(
            model_name='productsimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='core.products'),
        ),
    ]
