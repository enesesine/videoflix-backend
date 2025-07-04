# core/test_settings.py
from core.settings import *          # alles übernehmen …

# … und dann die für Tests notwendige, schlanke Konfiguration setzen
EXTRA_APPS = [
    "videos.apps.VideosConfig",     # oder nur "videos" – aber eben nur einmal!
    "accounts",                     # falls nicht schon drin
    "media",
]


for app in EXTRA_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)
# superschneller (unsicherer) Password-Hasher
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# In-Memory-Datenbank für Tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
