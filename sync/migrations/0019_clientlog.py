# Generated by Django 3.1.6 on 2021-06-14 14:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sync', '0018_supportedclienttarget_friendly_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('log_compressed', models.BinaryField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
