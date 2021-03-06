# Generated by Django 3.1.6 on 2021-03-01 19:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_auto_20210228_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='seafile_uuid',
            field=models.UUIDField(blank=True, help_text='ID of project from Seafile (optional)', null=True),
        ),
        migrations.AlterField(
            model_name='song',
            name='directory_name',
            field=models.CharField(blank=True,
                                   help_text='Specify a different folder name for Syncprojects-client to use (optional)',
                                   max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='song',
            name='url',
            field=models.CharField(blank=True, help_text='URL to audio file for this song (optional)', max_length=300,
                                   null=True),
        ),
    ]
