"""
Video catalogue models: Category and Video.
"""

from django.db import models


class Category(models.Model):
    """Genre / category for grouping videos."""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    """Single video entry with optional thumbnail and basic metadata."""
    file = models.FileField(upload_to="videos/")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Thumbnail can be null – a placeholder is used client-side otherwise
    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
    )

    def __str__(self):
        return self.title
