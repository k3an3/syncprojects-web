# Generated by Django 3.1.6 on 2021-09-03 03:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('player', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='songregion',
            name='end',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='songregion',
            name='start',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
