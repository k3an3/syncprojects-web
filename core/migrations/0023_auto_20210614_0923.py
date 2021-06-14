# Generated by Django 3.1.6 on 2021-06-14 14:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0022_auto_20210612_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='release_date',
            field=models.DateField(blank=True,
                                   help_text='If the album is not released yet, this can be used to specify the estimated release date. YYYY-MM-DD',
                                   null=True),
        ),
    ]
