from django import forms
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import *

USER_FIELDS = ["username", "email", "avatar", "description", "is_admin"]

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = USER_FIELDS

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if (password1 and password2) and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = USER_FIELDS

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['username', 'email', 'created', 'is_admin']
    list_filter = ['is_admin']
    readonly_fields = ['created']
    fieldsets = [
        (None, {'fields': [
            'edited',
            'deleted',
        ]}),
        ('Credentials', {'fields':[
            'email',
            'password'
        ]}),
        ('Settings', {'fields': [
            'avatar',
            'description'
        ]}),
        ('Permissions', {'fields': [
            'is_admin'
        ]}),
        ('Properties', {'fields': [
            'points',
            'coins',
            'followers',
        ]}),
        ('Content Interaction', {'fields': [
            'liked_posts',
            'disliked_posts',
            'liked_comments',
            'disliked_comments',
            'saved_posts',
            'saved_comments'
        ]})
    ]

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (None, {
            # 'classes': ['wide'],
            'fields': ['username', 'email', 'password1', 'password2'],
        }),
    ]

    search_fields = ['username', 'email']
    ordering = ['username']
    filter_horizontal = []

admin.site.register(User, UserAdmin)

models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass