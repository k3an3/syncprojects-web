# Generated by Django 3.1.6 on 2021-03-11 00:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('sync', '0007_auto_20210310_1922'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clientupdate',
            old_name='_updater',
            new_name='updater',
        ),
    ]
