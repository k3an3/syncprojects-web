# Generated by Django 3.1.6 on 2021-10-11 23:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0036_auto_20210825_2158'),
        ('snippets', '0002_auto_20211001_1930'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='snippet',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='snippet',
            name='object_id',
        ),
        migrations.AddField(
            model_name='snippet',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='core.project'),
        ),
    ]