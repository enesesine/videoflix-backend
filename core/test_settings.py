# core/test_settings.py
from core.settings import *          


EXTRA_APPS = [
    "videos.apps.VideosConfig",     
    "accounts",                    
    "media",
]


for app in EXTRA_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
