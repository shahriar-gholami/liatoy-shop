# Generated by Django 4.2.8 on 2025-01-22 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_alter_product_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.CharField(blank=True, default='محصول-جدید', max_length=200),
        ),
    ]
