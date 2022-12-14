# Generated by Django 4.1.1 on 2022-12-18 14:33

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('username', models.CharField(max_length=16, unique=True)),
                ('email', models.EmailField(max_length=255, verbose_name='Email Address')),
                ('avatar', models.CharField(blank=True, max_length=128, null=True)),
                ('description', models.CharField(blank=True, max_length=256, null=True)),
                ('points', models.IntegerField(default=0)),
                ('followers', models.IntegerField(default=0)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('title', models.CharField(max_length=128)),
                ('content', models.TextField(max_length=32767)),
                ('attached', models.CharField(blank=True, max_length=128, null=True)),
                ('nsfw', models.BooleanField(default=False)),
                ('spoiler', models.BooleanField(default=False)),
                ('views', models.IntegerField(default=0)),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=16, unique=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Sub name must be alphanumeric.', regex='^[0-9a-zA-Z]*$')])),
                ('followers', models.IntegerField(default=0)),
                ('mods', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('pinned_post', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pinned', to='red.post')),
            ],
        ),
        migrations.CreateModel(
            name='UserFlair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=64)),
                ('color', models.CharField(blank=True, max_length=6, null=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Invalid hex color', regex='^[a-fA-F0-9]{6}')])),
                ('sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userflairs', to='red.sub')),
            ],
        ),
        migrations.CreateModel(
            name='PostFlair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=64)),
                ('color', models.CharField(blank=True, max_length=6, null=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Invalid hex color', regex='^[a-fA-F0-9]{6}')])),
                ('sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postflairs', to='red.sub')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='flair',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='red.postflair'),
        ),
        migrations.AddField(
            model_name='post',
            name='sub',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='red.sub'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('content', models.CharField(max_length=1024)),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='red.comment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='red.post')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='flairs',
            field=models.ManyToManyField(to='red.userflair'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
