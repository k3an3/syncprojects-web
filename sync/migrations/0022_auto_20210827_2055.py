# Generated by Django 3.1.6 on 2021-08-28 01:55

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sync', '0021_clientfeaturechangelog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientfeaturechangelog',
            name='date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
