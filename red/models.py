from unittest.util import _MAX_LENGTH
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
import datetime

# Create your models here.

class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    name = models.CharField(max_length=16, unique=True)
    followers = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class User(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    username = models.CharField(max_length=16, unique=True)
    email = models.CharField(max_length=256, validators=[RegexValidator(regex='.+@.+\..{2,}', message='Invalid email', code="nomatch")], unique=True)
    password = models.CharField(max_length=64, validators=[RegexValidator(regex='^.{64}$', message='256-bit expected', code='nomatch')])
    avatar = models.CharField(max_length=128, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    points = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    sub = models.ForeignKey(Sub, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    content = models.TextField(max_length=32767)
    attached = models.CharField(max_length=128, null=True, blank=True)
    
    views = models.IntegerField(default=0)
    
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.title + " by " + self.author.username

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    content = models.CharField(max_length=1024)
    edited = models.DateTimeField(auto_now=True, null=True, blank=True)

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        if self.parent:
            return str(self.author) + " replies to " + str(self.parent.author) + ": " + self.content
        else:
            return str(self.author) + ": " + self.content