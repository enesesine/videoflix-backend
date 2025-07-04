# tests/test_views.py
import pytest


@pytest.mark.django_db
def test_video_list_endpoint(api_client, VideoFactory):
    VideoFactory.create_batch(2)
    response = api_client.get("/api/videos/")
    assert response.status_code == 200
    assert len(response.data) == 2
