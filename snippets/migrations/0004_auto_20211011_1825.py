# Generated by Django 3.1.6 on 2021-10-11 23:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0036_auto_20210825_2158'),
        ('snippets', '0003_auto_20211011_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippet',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project'),
        ),
    ]
