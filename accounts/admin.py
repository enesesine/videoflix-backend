"""
Admin registration for the custom User model.
Uses django-rest-authemail’s EmailUserAdmin for convenience.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from authemail.admin import EmailUserAdmin

User = get_user_model()

# Replace default User admin with EmailUserAdmin
admin.site.unregister(User)
admin.site.register(User, EmailUserAdmin)
