# Generated by Django 4.1.1 on 2022-11-20 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('red', '0018_remove_comment_edited_remove_post_edited_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='edited',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='edited',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='edited',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
