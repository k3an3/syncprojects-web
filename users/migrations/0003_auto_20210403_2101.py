# Generated by Django 3.1.6 on 2021-04-04 02:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0013_delete_coreuser'),
        ('users', '0002_auto_20210403_2052'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='genres_musical_taste',
            field=models.TextField(blank=True, null=True, verbose_name='Genres and Musical Taste'),
        ),
        migrations.AddField(
            model_name='user',
            name='instruments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='open_to_collaboration',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='private',
            field=models.BooleanField(default=True,
                                      help_text='Profiles of private accounts will have their details hidden.'),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='user',
            name='projects',
            field=models.ManyToManyField(blank=True, to='core.Project'),
        ),
        migrations.AddField(
            model_name='user',
            name='subscribed_projects',
            field=models.ManyToManyField(blank=True, related_name='subscribed_projects', to='core.Project'),
        ),
    ]
