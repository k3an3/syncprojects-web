# Generated by Django 3.1.6 on 2021-08-15 01:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0031_song_project_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='project_file',
            field=models.CharField(blank=True,
                                   help_text='By default, the most recently edited .cpr file is opened. Usethis to supply a custom filename.',
                                   max_length=200, null=True),
        ),
    ]
