# Generated by Django 5.1.4 on 2024-12-21 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendors',
            name='profit',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
