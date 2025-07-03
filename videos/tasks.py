"""
Background task for transcoding newly uploaded videos into multiple
resolutions using FFmpeg. Executed by django-rq.
"""

import os
import subprocess
from django.conf import settings
from django_rq import job

from .models import Video


@job  # makes the function runnable in an RQ worker
def generate_resolutions(video_id: int):
    """Render 120p, 360p, 720p and 1080p versions of the original file."""
    video = Video.objects.get(pk=video_id)
    input_path = video.file.path
    base, _ = os.path.splitext(input_path)

    targets = [
        ("120p",  "160x120"),
        ("360p",  "480x360"),
        ("720p",  "1280x720"),
        ("1080p", "1920x1080"),
    ]

    for label, size in targets:
        output_path = f"{base}_{label}.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",                 # overwrite existing file
                "-i", input_path,
                "-vf", f"scale={size}",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                output_path,
            ],
            check=True,
        )
