# Generated by Django 3.1.6 on 2021-10-23 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20211017_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='show_in_player',
            field=models.BooleanField(default=True),
        ),
    ]