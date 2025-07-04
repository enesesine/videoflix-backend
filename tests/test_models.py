import pytest   # <-- hinzugefügt

@pytest.mark.django_db
def test_video_str_representation(VideoFactory):
    video = VideoFactory()
    assert str(video) == video.title
