# Generated by Django 3.1.6 on 2021-05-28 20:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0016_song_url_last_fetched'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='url_last_error',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
