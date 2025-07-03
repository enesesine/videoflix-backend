# videos/views.py
"""Read-only API endpoints for categories and videos."""

from rest_framework import viewsets
from .models import Category, Video
from .serializers import CategorySerializer, VideoSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/categories/ and /<id>/."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_serializer_context(self):
        # Pass the request so serializers can build absolute URLs if needed
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/videos/ and /<id>/, ordered newest first."""
    queryset = Video.objects.select_related("category").order_by("-created_at")
    serializer_class = VideoSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request  # enables absolute file/thumbnail URLs
        return ctx
