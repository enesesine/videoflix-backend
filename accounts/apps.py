# accounts/apps.py
"""
App configuration for the custom accounts module.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Register the accounts app and its signals."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Import signal handlers once the app is fully loaded
        import accounts.signals  # noqa: F401
