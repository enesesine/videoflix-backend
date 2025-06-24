# videos/apps.py
from django.apps import AppConfig

class VideosConfig(AppConfig):
    name = 'videos'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Damit deine RQ-Tasks registriert werden
        import videos.tasks
        # Wenn du später noch Signals hast, kannst du sie hier importieren:
        # import videos.signals
