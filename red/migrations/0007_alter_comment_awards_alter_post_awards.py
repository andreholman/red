# Generated by Django 4.1.1 on 2023-01-13 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('red', '0006_comment_awards_post_awards_user_coins_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='awards',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='post',
            name='awards',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
