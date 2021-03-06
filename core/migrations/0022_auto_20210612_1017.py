# Generated by Django 3.1.6 on 2021-06-12 15:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0021_auto_20210610_2104'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureChangelog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('changes', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='album',
            name='release_date',
            field=models.DateField(blank=True,
                                   help_text='If the album is not released yet, this can be used to specify the estimated release date.',
                                   null=True),
        ),
    ]
