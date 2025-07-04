# tests/conftest.py
import io
import pytest
import factory
from django.core.files.base import ContentFile
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from videos.models import Category, Video

User = get_user_model()

# ------------------------------------------------------------------ #
#  Factories
# ------------------------------------------------------------------ #
class _UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # Dein Custom-User hat nur 'email' (USERNAME_FIELD='email')
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "secret")


class _CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"cat-{n}")


class _VideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Video

    title = factory.Sequence(lambda n: f"Video {n}")
    category = factory.SubFactory(_CategoryFactory)

    # Standard-File für alle Factory-Aufrufe ohne eigenes file=
    @factory.lazy_attribute
    def file(self):
        return ContentFile(b"dummy mp4 bytes", name="dummy.mp4")

# ------------------------------------------------------------------ #
#  Pytest-Fixtures, die die Factory-Klassen exposen
# ------------------------------------------------------------------ #
@pytest.fixture(name="UserFactory")
def _user_factory():
    return _UserFactory


@pytest.fixture(name="CategoryFactory")
def _category_factory():
    return _CategoryFactory


@pytest.fixture(name="VideoFactory")
def _video_factory():
    return _VideoFactory

# ------------------------------------------------------------------ #
#  API-Client – automatisch eingeloggt
# ------------------------------------------------------------------ #
@pytest.fixture
def api_client(UserFactory):
    client = APIClient()
    client.force_authenticate(user=UserFactory())
    return client

# ------------------------------------------------------------------ #
#  Redis / RQ & FileField-Patch stummschalten
# ------------------------------------------------------------------ #
@pytest.fixture(autouse=True)
def _silence_rq_and_fix_filefield(monkeypatch):
    """
    1) RQ-Signale/Jobs ausschalten
    2) FileField.pre_save vollständig stubben, sodass rohe Files aus den
       Tests (BufferedReader) akzeptiert werden.
    """
    from django.db.models.signals import post_save
    from videos import signals as v_signals
    post_save.disconnect(v_signals.enqueue_transcoding, sender=Video)

    # RQ stubben
    monkeypatch.setattr("videos.tasks.generate_resolutions.delay", lambda *a, **k: None)
    monkeypatch.setattr("django_rq.queues.get_queue", lambda *a, **k: None)

    # ----------   FileField-Stub   ---------------------------------
    from django.db.models.fields.files import FileField

    def _safe_pre_save(self, model_instance, add):        # noqa: D401
        """
        Minimal-Version: holt das aktuelle File-Objekt und sorgt dafür,
        dass Django es als 'bereits gespeichert' betrachtet.
        """
        file_obj = getattr(model_instance, self.attname)
        if file_obj and not getattr(file_obj, "_committed", False):
            file_obj._committed = True
        return file_obj

    monkeypatch.setattr(FileField, "pre_save", _safe_pre_save, raising=True)
    yield
