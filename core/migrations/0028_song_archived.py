# Generated by Django 3.1.6 on 2021-08-05 00:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0027_song_bpm'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='archived',
            field=models.BooleanField(default=False,
                                      help_text='Prevent further syncs to this song. It can be downloaded, but no new changes made.'),
        ),
    ]
