# Generated by Django 3.1.6 on 2021-03-01 19:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('sync', '0003_auto_20210301_1417'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Lock',
        ),
    ]
