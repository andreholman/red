# Generated by Django 4.1.1 on 2023-03-22 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('red', '0010_alter_linkopenedrequest_purpose_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saved_comments',
            field=models.ManyToManyField(related_name='saved_comments', to='red.comment'),
        ),
        migrations.AddField(
            model_name='user',
            name='saved_posts',
            field=models.ManyToManyField(related_name='saved_posts', to='red.post'),
        ),
    ]
