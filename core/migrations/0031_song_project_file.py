# Generated by Django 3.1.6 on 2021-08-12 02:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0030_song_key_tuning'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='project_file',
            field=models.CharField(blank=True,
                                   help_text='By default, the most recently edited .cpr file is opened. Use this to supply a custom file.',
                                   max_length=200, null=True),
        ),
    ]
