# Generated by Django 5.1.4 on 2024-12-20 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_vendors_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendors',
            name='profit',
        ),
    ]