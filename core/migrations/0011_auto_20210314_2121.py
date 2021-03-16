# Generated by Django 3.1.6 on 2021-03-15 01:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_auto_20210314_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coreuser',
            name='projects',
            field=models.ManyToManyField(blank=True, to='core.Project'),
        ),
        migrations.AlterField(
            model_name='coreuser',
            name='subscribed_projects',
            field=models.ManyToManyField(blank=True, related_name='subscribed_projects', to='core.Project'),
        ),
    ]