# Generated by Django 3.1.6 on 2021-07-27 01:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0026_auto_20210629_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='bpm',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
