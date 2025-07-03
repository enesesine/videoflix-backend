"""
Django settings for the Videoflix back-end.
Environment variables are loaded from .env via python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths / debug -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    default="django-insecure-@#x5h3zj!g+8g1v@2^b6^9$8&f1r7g$@t3v!p4#=g0r5qzj4m3",
)
DEBUG = True
ALLOWED_HOSTS = ["*"]  # tighten for production

# Applications -------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

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

    # Local apps  (custom user model before authemail!)
    "accounts",
    "videos.apps.VideosConfig",
]

# Middleware ---------------------------------------------------------
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

# Templates ----------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # authemail templates live here
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

# Database (PostgreSQL) ---------------------------------------------
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

# Password validation ------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalisation ----------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static & media -----------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django-RQ ----------------------------------------------------------
RQ_QUEUES = {
    "default": {
        "HOST": os.getenv("REDIS_HOST", "redis"),
        "PORT": int(os.getenv("REDIS_PORT", 6379)),
        "DB": int(os.getenv("REDIS_DB", 0)),
        "DEFAULT_TIMEOUT": 900,
    }
}

# CORS ---------------------------------------------------------------
CORS_ALLOWED_ORIGINS = ["http://localhost:4200"]

# DRF ----------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# Front-end base URL (used in e-mails) -------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

# E-mail config ------------------------------------------------------
EMAIL_BACKEND       = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST          = os.getenv("EMAIL_HOST", "host.docker.internal")
EMAIL_PORT          = int(os.getenv("EMAIL_PORT", 25))
EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS       = bool(int(os.getenv("EMAIL_USE_TLS", 0)))
EMAIL_USE_SSL       = bool(int(os.getenv("EMAIL_USE_SSL", 0)))
DEFAULT_FROM_EMAIL  = os.getenv("DEFAULT_FROM_EMAIL", "Videoflix ✦ Support <no-reply@videoflix.com>")

EMAIL_FROM = DEFAULT_FROM_EMAIL  # required by django-rest-authemail
EMAIL_BCC  = ""

# django-rest-authemail ---------------------------------------------
AUTHEMAIL_CONFIRM_EMAIL_ON_GET                 = True
AUTHEMAIL_CONFIRM_REDIRECT_URL                 = f"{FRONTEND_URL}/email-verify/"
AUTHEMAIL_PASSWORD_RESET_EXPIRE                = 48  # hours
AUTHEMAIL_TOKEN_EXPIRY                         = 30  # days
AUTHEMAIL_SEND_FROM                            = EMAIL_FROM
AUTHEMAIL_PASSWORD_RESET_EMAIL_PLAINTEXT       = "authemail/password_reset_email.txt"
AUTHEMAIL_PASSWORD_RESET_EMAIL_HTML            = "authemail/password_reset_email.html"
AUTHEMAIL_PASSWORD_RESET_CONFIRM_ON_GET        = True
AUTHEMAIL_PASSWORD_RESET_CONFIRM_REDIRECT_URL  = f"{FRONTEND_URL}/new-password/"
