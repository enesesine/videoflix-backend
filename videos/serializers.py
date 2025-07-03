"""
Serializers for Category and Video REST endpoints.
"""

from rest_framework import serializers
from .models import Category, Video


class CategorySerializer(serializers.ModelSerializer):
    """Expose id, name and slug."""
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class VideoSerializer(serializers.ModelSerializer):
    """Serialize Video objects with absolute URLs for file and thumbnail."""
    category  = CategorySerializer(read_only=True)
    file      = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "description",
            "file",
            "category",
            "created_at",
            "thumbnail",
        ]

    def get_file(self, obj):
        """Return an absolute URL to the video file if request context exists."""
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

    def get_thumbnail(self, obj):
        """Return an absolute URL to the thumbnail (or None)."""
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url if obj.thumbnail else None
