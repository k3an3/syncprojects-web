# Generated by Django 3.1.6 on 2021-02-27 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_delete_lock'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='directory_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='sync_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
