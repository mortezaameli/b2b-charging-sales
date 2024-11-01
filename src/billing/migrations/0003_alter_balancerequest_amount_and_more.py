# Generated by Django 4.2.16 on 2024-10-27 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_balancerequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balancerequest',
            name='amount',
            field=models.DecimalField(decimal_places=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='rechargerequest',
            name='amount',
            field=models.DecimalField(decimal_places=0, max_digits=15),
        ),
    ]
