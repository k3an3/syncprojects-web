# Generated by Django 3.1.6 on 2021-06-13 16:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0007_user_latest_feature_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='links',
            field=models.TextField(blank=True,
                                   help_text="Insert URLs (separated by space, comma, or newline) for your music, website, or social media, and we'll automatically display them.",
                                   null=True),
        ),
    ]