# Generated by Django 3.1.6 on 2021-06-10 03:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sync', '0015_auto_20210607_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportedclienttarget',
            name='icon',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]