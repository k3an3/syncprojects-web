# Generated by Django 3.1.6 on 2021-03-01 19:26

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0007_auto_20210301_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('reason', models.CharField(blank=True, max_length=100, null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
