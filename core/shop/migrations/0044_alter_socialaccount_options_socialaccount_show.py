# Generated by Django 4.2.8 on 2025-05-27 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0043_socialaccount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='socialaccount',
            options={'verbose_name': 'شبکه\u200cهای اجتماعی', 'verbose_name_plural': 'شبکه\u200cهای اجتماعی'},
        ),
        migrations.AddField(
            model_name='socialaccount',
            name='show',
            field=models.BooleanField(default=True),
        ),
    ]
