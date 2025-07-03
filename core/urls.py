# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth endpoints provided by django-rest-authemail
    path("api/accounts/", include("authemail.urls")),

    # Video catalogue / streaming API
    path("api/", include("videos.urls")),
]

# Serve uploaded media during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
