# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # alle Auth-Routen liefert jetzt django-rest-authemail
    path("api/accounts/", include("authemail.urls")),

    # Video-API
    path("api/", include("videos.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
