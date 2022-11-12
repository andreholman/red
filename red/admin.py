from django.apps import apps
from django.contrib import admin
from .models import *

# admin.site.register(Sub, User, Post, Comment)

models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass