from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    # bereits bestehende Felder …
    file = models.FileField(upload_to="videos/")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # ▶️  NEU  ◀️
    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,          # darf leer sein → wir generieren sonst einen Default
    )

    def __str__(self):
        return self.title