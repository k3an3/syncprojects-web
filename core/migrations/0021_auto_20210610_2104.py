# Generated by Django 3.1.6 on 2021-06-11 02:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0020_auto_20210610_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='release_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
