# Generated by Django 3.1.6 on 2021-08-05 03:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0029_comment_resolved'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='key_tuning',
            field=models.CharField(blank=True, help_text='E.g. G# Minor, Half-step down tuning', max_length=40,
                                   null=True, verbose_name='Key/tuning'),
        ),
    ]