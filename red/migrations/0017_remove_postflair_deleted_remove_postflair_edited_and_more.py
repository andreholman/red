# Generated by Django 4.1.1 on 2022-11-20 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('red', '0016_comment_deleted_post_deleted_postflair_deleted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postflair',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='postflair',
            name='edited',
        ),
        migrations.RemoveField(
            model_name='userflair',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='userflair',
            name='edited',
        ),
    ]