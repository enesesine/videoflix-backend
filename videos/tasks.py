# videos/tasks.py
import os
import subprocess
from django.conf import settings
from django_rq import job
from .models import Video

@job  # dekoriert den Task für django-rq
def generate_resolutions(video_id: int):
    """
    Rendert die Auflösungen 120p, 360p, 720p, 1080p
    aus der Original-Datei mit ffmpeg.
    """
    video = Video.objects.get(pk=video_id)
    input_path = video.file.path
    base, ext = os.path.splitext(input_path)

    # Liste der Zielauflösungen und Größen
    targets = [
        ("120p",  "160x120"),
        ("360p",  "480x360"),
        ("720p",  "1280x720"),
        ("1080p", "1920x1080"),
    ]

    for label, size in targets:
        output_path = f"{base}_{label}.mp4"
        # ffmpeg-Command: skalieren und neu codieren
        subprocess.run([
            "ffmpeg",
            "-y",  # überschreiben
            "-i", input_path,
            "-vf", f"scale={size}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ], check=True)
