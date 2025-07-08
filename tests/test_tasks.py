# tests/test_tasks.py
from unittest import mock
import pytest
from videos.tasks import generate_resolutions


@pytest.mark.django_db
@mock.patch("videos.tasks.subprocess.run")
def test_transcoding_task_queues_four_ffmpeg_calls(mock_run, VideoFactory, tmp_path):
    file_path = tmp_path / "orig.mp4"
    file_path.write_bytes(b"dummy")
    video = VideoFactory(file=file_path.open("rb"))
    generate_resolutions(video.id)
    assert mock_run.call_count == 4  
