# Generated by Django 3.1.6 on 2021-09-02 00:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sync', '0022_auto_20210827_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientupdate',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
