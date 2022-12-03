from dateutil.relativedelta import relativedelta
from unittest.util import _MAX_LENGTH

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

# Create your models here.

class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    
    name = models.CharField(max_length=16, validators=[RegexValidator(regex=r"^[0-9a-zA-Z]*$", message="Sub name must be alphanumeric.", code="nomatch")], unique=True)
    followers = models.IntegerField(default=0)
    mods = models.ManyToManyField("User")
    pinned_post = models.ForeignKey("Post", on_delete=models.CASCADE, default=None, null=True, blank=True, related_name="pinned")

    def __str__(self):
        return self.name

class PostFlair(models.Model): # Can be applied to posts and users.
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    text = models.CharField(max_length=64)
    color = models.CharField(max_length=6, validators=[RegexValidator(regex=r"^[a-fA-F0-9]{6}", message='Invalid hex color', code="nomatch")], null=True, blank=True)
    sub = models.ForeignKey(Sub, on_delete=models.CASCADE, related_name="postflairs")

    def __str__(self):
        return f"{self.text} in {self.sub}"

class UserFlair(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    text = models.CharField(max_length=64)
    color = models.CharField(max_length=6, validators=[RegexValidator(regex=r"^[a-fA-F0-9]{6}", message='Invalid hex color', code="nomatch")], null=True, blank=True)
    sub = models.ForeignKey(Sub, on_delete=models.CASCADE, related_name="userflairs")

    def __str__(self):
        return f"{self.text} in {self.sub}"

class User(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    edited = models.DateTimeField(null=True, blank=True, default=None)
    deleted = models.DateTimeField(null=True, blank=True, default=None)

    username = models.CharField(max_length=16, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=64, validators=[RegexValidator(regex='^.{64}$', message="256-bit expected", code="nomatch")])
    avatar = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    points = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    
    flairs = models.ManyToManyField(UserFlair)

    def __str__(self):
        return self.username

    def soft_delete(self):
        self.deleted = timezone.now()

    def edit(self):
        self.edited = timezone.now()

class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    edited = models.DateTimeField(null=True, blank=True, default=None)
    deleted = models.DateTimeField(null=True, blank=True, default=None)

    sub = models.ForeignKey(Sub, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    content = models.TextField(max_length=32767)
    attached = models.CharField(max_length=128, null=True, blank=True)
    flair = models.ForeignKey(PostFlair, on_delete=models.SET_NULL, related_name="posts", null=True, blank=True)
    nsfw = models.BooleanField(null=False, blank=False, default=False)
    spoiler = models.BooleanField(null=False, blank=False, default=False)

    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.title + " by " + self.author.username

    def soft_delete(self):
        self.deleted = timezone.now()

    def edit(self):
        self.edited = timezone.now()
    
    def archived(self):
        return (self.created + relativedelta(months=6)) <= timezone.now()

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    edited = models.DateTimeField(null=True, blank=True, default=None)
    deleted = models.DateTimeField(null=True, blank=True, default=None)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    content = models.CharField(max_length=1024)

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        if self.parent:
            return str(self.author) + " replies to " + str(self.parent.author) + ": " + self.content
        else:
            return str(self.author) + ": " + self.content

    def soft_delete(self):
        self.deleted = timezone.now()

    def edit(self):
        self.edited = timezone.now()