# Generated by Django 3.1.6 on 2021-11-10 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0005_auto_20211017_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippet',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='snippet',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
