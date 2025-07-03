"""
Signal handlers for the videos app.
Enqueues background transcoding after a new Video instance is saved.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video
from .tasks import generate_resolutions


@receiver(post_save, sender=Video)
def enqueue_transcoding(sender, instance: Video, created, **kwargs):
    """Push the freshly uploaded video to the transcoding queue."""
    if created and instance.file:  # only on first save and if a file exists
        generate_resolutions.delay(instance.id)
