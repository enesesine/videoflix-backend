# videos/apps.py
from django.apps import AppConfig


class VideosConfig(AppConfig):
    """App registration for the videos module."""
    name = "videos"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Import signal handlers once the app is fully loaded
        import videos.signals  # noqa: F401
