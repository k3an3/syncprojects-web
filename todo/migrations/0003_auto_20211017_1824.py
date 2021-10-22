# Generated by Django 3.1.6 on 2021-10-17 23:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0037_auto_20211017_1824'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('todo', '0002_auto_20211017_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='assignee',
            field=models.ForeignKey(blank=True, help_text='Optional', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='todo',
            name='due',
            field=models.DateTimeField(blank=True, help_text='Optional; YYYY-MM-DD', null=True),
        ),
        migrations.AlterField(
            model_name='todo',
            name='song',
            field=models.ForeignKey(blank=True, help_text='Optional', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, to='core.song'),
        ),
    ]
