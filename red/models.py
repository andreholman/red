from dateutil.relativedelta import relativedelta
from unittest.util import _MAX_LENGTH
from math import log10
from hashlib import sha512
from base64 import urlsafe_b64encode

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import JSONField
from django.conf import settings as config
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

# User/Auth schema

class RedUserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email or not username:
            raise ValueError('Users must have an email and username.')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.is_admin = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    edited = models.DateTimeField(null=True, blank=True, default=None)
    deleted = models.DateTimeField(null=True, blank=True, default=None)

    username = models.CharField(max_length=16, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, verbose_name="Email Address")
    avatar = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    points = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    coins = models.PositiveIntegerField(default=0)
    followers = models.PositiveIntegerField(default=0)
    is_admin = models.BooleanField(default=False)

    flairs = models.ManyToManyField("UserFlair")

    liked_posts = models.ManyToManyField("Post", related_name="liked_posts")
    disliked_posts = models.ManyToManyField("Post", related_name="disliked_posts")
    saved_posts = models.ManyToManyField("Post", related_name="saved_posts")
    
    liked_comments = models.ManyToManyField("Comment", related_name="liked_comments")
    disliked_comments = models.ManyToManyField("Comment", related_name="disliked_comments")
    saved_comments = models.ManyToManyField("Comment", related_name="saved_comments")

    def __str__(self):
        return self.username

    def soft_delete(self):
        self.deleted = timezone.now()

    def edit(self):
        self.edited = timezone.now()
    
    @property
    def is_staff(self):
        return self.is_admin

    objects = RedUserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

# class LinkOpenedRequestManager(models.Manager):
#     # def get_queryset(self):
#     #     minimum_created = timezone.now() - relativedelta(minutes=15)
#     #     return super(LinkOpenedRequestManager, self).get_queryset().filter(created__gte=minimum_created)
    
#     # def save(self, *args, **kwargs):
#     #     self.save(*args, **kwargs)
#     #     print(urlsafe_b64encode(sha512(str(self.id).encode()).digest()).decode()[:-2])
#     #     self.url = urlsafe_b64encode(sha512(str(self.id).encode()).digest()).decode()[:-2]

class LinkOpenedRequest(models.Model): # resetting password, email verification...
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=1, null=False, blank=False) # P for password, E for email

    # objects = LinkOpenedRequestManager()

    url = models.SlugField(unique=True, null=False, blank=False, max_length=86)

    def __str__(self):
        return self.url[:16] + "..."

# Content Data

class AbstractBaseContent(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False) # ADD EDITABLE=FALSE TO DISABLE DEBUG
    edited = models.DateTimeField(null=True, blank=True, default=None)
    deleted = models.DateTimeField(null=True, blank=True, default=None)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=32767)

    awards = JSONField(blank=True, default=dict)

    @property
    def award_count(self):
        award_counts = {}
    
        for award_type in self.awards:
            award_counts[award_type] = len(self.awards[award_type])
        
        # sort from lowest to highest value awards
        award_order = list(config.AWARDS_LIST.keys())
        return {key: award_counts[key] for key in reversed(award_order) if key in award_counts}

    @property
    def delta_timestamp(self):
        seconds = int((timezone.now() - self.created).total_seconds())
        periods = [
            ('y', 31536000), # year
            ('mo', 2628000),  # month
            ('d', 86400),    # day
            ('h', 3600),     # hour
            ('m', 60),       # minute
            ('s', 1)         # second
        ]
        parts = []
        parts_appended = 0
        previous_index = 67

        for period_name, period_seconds in periods:
            if seconds >= period_seconds:
                if periods.index((period_name, period_seconds)) - previous_index >= 2:
                    break
                previous_index = periods.index((period_name, period_seconds))
                
                period_value, seconds = divmod(seconds, period_seconds)
                parts.append('{}{}'.format(period_value, period_name))
                
                parts_appended += 1
                if parts_appended >= 2:
                    break # stops after listing two date types
        return ' '.join(parts) if len(parts) > 0 else '0s'
    
    def soft_delete(self):
        self.deleted = timezone.now()

    def edit(self):
        self.edited = timezone.now()

    def score(self):
        difference = self.likes - self.dislikes

        if difference > 0: majority_vote = 1
        elif difference == 0: majority_vote = 0
        else: majority_vote = -1

        if abs(difference) >= 1: z = abs(difference)
        else: z = 1
        
        age = (self.created - timezone.now()).total_seconds()

        return log10(z) + (majority_vote * age) / 45000
    
    class Meta:
        abstract = True

class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    
    name = models.CharField(max_length=16, validators=[RegexValidator(regex=r"^[0-9a-zA-Z]*$", message="Sub name must be alphanumeric.", code="nomatch")], unique=True)
    followers = models.PositiveIntegerField(default=0)
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

class Post(AbstractBaseContent):
    sub = models.ForeignKey(Sub, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=128)
    attached = models.CharField(max_length=128, null=True, blank=True)
    flair = models.ForeignKey(PostFlair, on_delete=models.SET_NULL, related_name="posts", null=True, blank=True)
    nsfw = models.BooleanField(null=False, blank=False, default=False)
    spoiler = models.BooleanField(null=False, blank=False, default=False)

    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()
    
    @property
    def vote_difference(self):
        return self.likes - self.dislikes

    def __str__(self):
        return self.title + " by " + self.author.username
    
    def archived(self):
        return (self.created + relativedelta(months=6)) <= timezone.now()

class Comment(AbstractBaseContent):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    content = models.CharField(max_length=1024)

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    @property
    def vote_difference(self):
        return self.likes - self.dislikes

    def __str__(self):
        if len(self.content) > 64:
            comment_content = self.content[:64] + "..."
        else:
            comment_content = self.content
        
        if self.parent:
            return str(self.author) + " replies to " + str(self.parent.author) + ": " + comment_content
        else:
            return str(self.author) + ": " + comment_content