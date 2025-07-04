# tests/test_serializers.py
from rest_framework.test import APIRequestFactory
from videos.serializers import VideoSerializer
import pytest


@pytest.mark.django_db
def test_video_serializer_returns_absolute_url(VideoFactory):
    video = VideoFactory()
    request = APIRequestFactory().get("/")
    data = VideoSerializer(video, context={"request": request}).data
    assert data["file"].startswith("http://testserver/")
