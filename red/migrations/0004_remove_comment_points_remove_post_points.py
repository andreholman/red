# Generated by Django 4.1.1 on 2022-12-27 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('red', '0003_user_disliked_comments_user_disliked_posts_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='points',
        ),
        migrations.RemoveField(
            model_name='post',
            name='points',
        ),
    ]
