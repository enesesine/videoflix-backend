# videos/serializers.py
from rest_framework import serializers
from .models import Category, Video

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class VideoSerializer(serializers.ModelSerializer):
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
        """
        Gibt eine absolute URL zum Video zurück.
        """
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        # Fallback auf relative URL, falls kein request da ist
        return obj.file.url if obj.file else None

    def get_thumbnail(self, obj):
        """
        Gibt eine absolute URL zum Thumbnail zurück.
        """
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        # Fallback auf relative URL, falls kein request da ist
        return obj.thumbnail.url if obj.thumbnail else None
