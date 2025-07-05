"""
Django settings for the Videoflix back-end.
Environment variables are loaded from .env via python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


# helper – safe bool from .env ------------------------------------------------
def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


# basics ----------------------------------------------------------------------
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    default="django-insecure-@#x5h3zj!g+8g1v@2^b6^9$8&f1r7g$@t3v!p4#=g0r5qzj4m3",
)
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = ["*"]  # tighten for production
AUTH_USER_MODEL = "accounts.User"

# apps ------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd-party
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "authemail",
    "django_rq",
    # local
    "accounts",
    "videos.apps.VideosConfig",
]

# middleware ------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# templates -------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.frontend_url",
            ],
            "debug": DEBUG,
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# database --------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", 5432),
    }
}

# cache (redis) ---------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', 6379)}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESS_MIN_LEN": 1024,
        },
        "TIMEOUT": 60 * 30,  # 30 min
    }
}

# password validation ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# i18n / tz -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# static / media --------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-rq -------------------------------------------------------------------
RQ_QUEUES = {
    "default": {
        "HOST": os.getenv("REDIS_HOST", "redis"),
        "PORT": int(os.getenv("REDIS_PORT", 6379)),
        "DB": int(os.getenv("REDIS_DB", 0)),
        "DEFAULT_TIMEOUT": 900,
    }
}

# cors ------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = ["http://localhost:4200"]

# drf -------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# front-end url ---------------------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

# email -----------------------------------------------------------------------
EMAIL_BACKEND       = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST          = os.getenv("EMAIL_HOST", "host.docker.internal")
EMAIL_PORT          = int(os.getenv("EMAIL_PORT", 25))
EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS       = env_bool("EMAIL_USE_TLS")
EMAIL_USE_SSL       = env_bool("EMAIL_USE_SSL")
DEFAULT_FROM_EMAIL  = os.getenv("DEFAULT_FROM_EMAIL", "Videoflix ✦ Support <no-reply@videoflix.com>")

EMAIL_FROM = DEFAULT_FROM_EMAIL
EMAIL_BCC  = ""

# authemail -------------------------------------------------------------------
AUTHEMAIL_CONFIRM_EMAIL_ON_GET                 = True
AUTHEMAIL_CONFIRM_REDIRECT_URL                 = f"{FRONTEND_URL}/email-verify/"
AUTHEMAIL_PASSWORD_RESET_EXPIRE                = 48  # h
AUTHEMAIL_TOKEN_EXPIRY                         = 30  # d
AUTHEMAIL_SEND_FROM                            = EMAIL_FROM
AUTHEMAIL_PASSWORD_RESET_EMAIL_PLAINTEXT       = "authemail/password_reset_email.txt"
AUTHEMAIL_PASSWORD_RESET_EMAIL_HTML            = "authemail/password_reset_email.html"
AUTHEMAIL_PASSWORD_RESET_CONFIRM_ON_GET        = True
AUTHEMAIL_PASSWORD_RESET_CONFIRM_REDIRECT_URL  = f"{FRONTEND_URL}/new-password/"
