# videos/urls.py
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, VideoViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"videos", VideoViewSet)

urlpatterns = router.urls
