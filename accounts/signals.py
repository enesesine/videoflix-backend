"""
accounts.signals
~~~~~~~~~~~~~~~~
Creates a DRF auth token automatically whenever a new user instance
is saved to the database.

Hooked up via Django’s `post_save` signal on the custom User model.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generate a Token for every newly registered user."""
    if created:
        Token.objects.get_or_create(user=instance)
