# Generated by Django 4.2.8 on 2025-01-24 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0028_rename_sho_blog_store_show_blog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='store',
            old_name='sho_specials',
            new_name='show_specials',
        ),
    ]
