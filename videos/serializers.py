from rest_framework import serializers
from django.core.files.storage import default_storage as storage
from .models import Category, Video


dTZB_VIDEO_EXT = ".mp4"
LEVELS = [
    ("1080p", "1080"),
    ("720p", "720"),
    ("360p", "360"),
    ("120p", "120"),
]


class CategorySerializer(serializers.ModelSerializer):
    """Expose id, name and slug."""
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class VideoSerializer(serializers.ModelSerializer):
    """
    Serialize Video objects with absolute URLs for file, thumbnail, and available resolutions.
    """
    category    = CategorySerializer(read_only=True)
    file        = serializers.SerializerMethodField()
    thumbnail   = serializers.SerializerMethodField()
    resolutions = serializers.SerializerMethodField()

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
            "resolutions",
        ]

    def get_file(self, obj):
        """
        Return absolute URL to the original video file if request is present.
        """
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

    def get_thumbnail(self, obj):
        """
        Return absolute URL to the thumbnail image, or None.
        """
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url if obj.thumbnail else None

    def get_resolutions(self, obj):
        """
        Detect and return available resolution variants of the video.

        It checks for files like '<basename>_<suffix>.mp4' in storage,
        and returns a list of dicts with 'label', 'src', and 'type'.
        """
        request = self.context.get("request")
        basename = obj.file.name.rsplit(dTZB_VIDEO_EXT, 1)[0]
        sources = []
        for label, suffix in LEVELS:
            candidate = f"{basename}_{suffix}{dTZB_VIDEO_EXT}"
            # only include if file exists in storage
            if storage.exists(candidate):
                url = storage.url(candidate)
                if request:
                    url = request.build_absolute_uri(url)
                sources.append({
                    "label": label,
                    "src": url,
                    "type": "video/mp4",
                })
        return sources
