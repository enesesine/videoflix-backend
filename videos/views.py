# videos/views.py
from rest_framework import viewsets
from .models import Category, Video
from .serializers import CategorySerializer, VideoSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_serializer_context(self):
        """
        Damit auch bei Category-Serializern bei Bedarf der Request
        im Kontext zur Verfügung steht (z.B. für Hyperlinked-Felder).
        """
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.select_related("category").order_by("-created_at")
    serializer_class = VideoSerializer

    def get_serializer_context(self):
        """
        Übergebe den Request an den Serializer, damit absolute URLs
        für file und thumbnail generiert werden können.
        """
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
