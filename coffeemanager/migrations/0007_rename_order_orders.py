# Generated by Django 3.2.13 on 2022-04-29 20:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coffeemanager', '0006_cart_cart_item_order_order_item'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order',
            new_name='Orders',
        ),
    ]
