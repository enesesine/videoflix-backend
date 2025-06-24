# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import (
    RegisterView,
    LoginView,
    ForgotPasswordView,
    ResetPasswordView,    # ← hier passen
)

urlpatterns = [
    # Admin-Interface
    path("admin/", admin.site.urls),

    # Auth-Endpoints (öffentlich)
    path("api/auth/register/",       RegisterView.as_view(),          name="auth-register"),
    path("api/auth/login/",          LoginView.as_view(),             name="auth-login"),
    path("api/auth/forgot-password/",ForgotPasswordView.as_view(),    name="auth-forgot-password"),
    path("api/auth/reset-password/", ResetPasswordView.as_view(),     name="auth-reset-password"),

    # Rest-API für Videos (geschützt durch Token)
    path("api/", include("videos.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
