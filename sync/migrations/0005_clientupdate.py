# Generated by Django 3.1.6 on 2021-03-08 02:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sync', '0004_delete_lock'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=20, unique=True)),
                ('updater', models.FileField(upload_to='updates/updater/')),
                ('package', models.FileField(upload_to='updates/')),
            ],
        ),
    ]
