# videos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
from .tasks import generate_resolutions

@receiver(post_save, sender=Video)
def enqueue_transcoding(sender, instance: Video, created, **kwargs):
    # Nur direkt nach dem ersten Speichern
    if created and instance.file:
        generate_resolutions.queue(instance.id)
