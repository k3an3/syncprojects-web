# Generated by Django 3.1.6 on 2021-03-15 00:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_auto_20210310_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='coreuser',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coreuser',
            name='genres_musical_taste',
            field=models.TextField(blank=True, null=True, verbose_name='Genres and Musical Taste'),
        ),
        migrations.AddField(
            model_name='coreuser',
            name='instruments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coreuser',
            name='open_to_collaboration',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coreuser',
            name='private',
            field=models.BooleanField(default=True,
                                      help_text='Profiles of private accounts will have their details hidden.'),
        ),
        migrations.AddField(
            model_name='coreuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='project',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
    ]
