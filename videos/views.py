# videos/views.py
from rest_framework import viewsets
from .models import Category, Video
from .serializers import CategorySerializer, VideoSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.select_related("category").order_by("-created_at")
    serializer_class = VideoSerializer
