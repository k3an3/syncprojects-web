# Generated by Django 3.1.6 on 2021-03-13 18:54

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sync', '0008_auto_20210310_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated',
                 models.DateTimeField(default=datetime.datetime(2021, 3, 13, 18, 54, 45, 332481, tzinfo=utc))),
                ('sync_root', models.TextField(
                    help_text='Absolute path to the root directory where your song project files will be synced.')),
                ('flat_layout', models.BooleanField(default=False,
                                                    help_text='Whether to keep all song project files in one folder, or separate them by project.')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
