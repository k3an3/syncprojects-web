# Generated by Django 3.1.6 on 2021-11-11 19:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0038_song_show_in_player'),
        ('comments', '0003_comment_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='internal',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='tags',
            field=models.ManyToManyField(to='comments.Tag'),
        ),
    ]
