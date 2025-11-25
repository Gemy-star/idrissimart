"""
Django settings for idrissimart project (common).
"""

import os
from pathlib import Path

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from .constance_config import CONSTANCE_CONFIG, CONSTANCE_CONFIG_FIELDSETS

load_dotenv()

# =======================
# Base Paths
# =======================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =======================
# Security
# =======================
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-u65j76hw%g$3p*l4_4msuzuvz-das==de_9%k2f)0%hjy33i0k",
)
DEBUG = True
ALLOWED_HOSTS = []

# =======================
# Apps
# =======================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "channels",
    "compressor",
    "crispy_forms",
    "crispy_bootstrap5",
    "constance",
    "constance.backends.database",
    "imagekit",
    "rosetta",
    "django_filters",
    "sendgrid",
    "taggit",
    "django_q",
    "mptt",
    # Local apps
    "main.apps.MainConfig",
    "content.apps.ContentConfig",
]
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}

SITE_ID = 1
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# =======================
# Middleware
# =======================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Block malicious requests (should be early in middleware stack)
    "main.middleware.BlockMaliciousRequestsMiddleware",
    # force App to open in AR language
    "content.middleware.ForceArabicDefaultMiddleware",
    # Country filtering middleware
    "main.middleware.CountryFilterMiddleware",
    # User permissions middleware
    "main.middleware.UserPermissionMiddleware",
]

ROOT_URLCONF = "idrissimart.urls"

# =======================
# Templates
# =======================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "constance.context_processors.config",
                # Custom context processors
                "content.context_processors.countries",
                "content.context_processors.user_preferences",
                "content.context_processors.header_categories",
                "content.context_processors.notifications",
                "main.context_processors.cart_wishlist_counts",
            ],
        },
    },
]

WSGI_APPLICATION = "idrissimart.wsgi.application"

# =======================
# Database (SQLite fallback)
# =======================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =======================
# Password Validation
# =======================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =======================
# i18n / l10n
# =======================
LANGUAGE_CODE = "ar"
TIME_ZONE = "Africa/Cairo"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

# =======================
# Static & Media
# =======================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =======================
# Compressor
# =======================
EMAIL_BACKEND = "sendgrid_backend.SendGridBackend"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False  # overridden in production
COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]
COMPRESS_JS_FILTERS = [
    "compressor.filters.jsmin.JSMinFilter",
]

# =======================
# Auth / Upload
# =======================
AUTH_USER_MODEL = "main.User"

LOGIN_URL = "main:login"
LOGIN_REDIRECT_URL = "main:home"
LOGOUT_REDIRECT_URL = "main:home"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024  # 200 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024  # 200 MB
# =======================
# Session Settings
# =======================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_SAMESITE = "Lax"
# ===========================
# Custom Settings
# ===========================
# Cart & Wishlist settings
CART_SESSION_KEY = "cart"
WISHLIST_SESSION_KEY = "wishlist"
MAX_CART_ITEMS = 100
MAX_WISHLIST_ITEMS = 50

# Country settings
DEFAULT_COUNTRY = "SA"
SUPPORTED_COUNTRIES = ["SA", "AE", "EG", "KW", "QA", "BH", "OM", "JO"]

CONSTANCE_CONFIG = CONSTANCE_CONFIG
CONSTANCE_CONFIG_FIELDSETS = CONSTANCE_CONFIG_FIELDSETS

# ===========================
# System Check Settings
# ===========================
# Suppress warnings that are not applicable to our setup
SILENCED_SYSTEM_CHECKS = [
    # MariaDB doesn't support conditional indexes - this is expected
    "models.W037",
    # Suppress other MariaDB-related warnings if they appear
    "mysql.W003",  # MySQL may not support timezone-aware datetimes
]

# ===========================
# Django-Q2 Task Queue Settings
# ===========================
Q_CLUSTER = {
    "name": "idrissimart_q",
    "workers": 4,
    "recycle": 500,
    "timeout": 60,
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "cpu_affinity": 1,
    "label": "Django Q",
    "orm": "default",  # Use Django's ORM as the broker
}

# ===========================
# Django Channels Settings
# ===========================
ASGI_APPLICATION = "idrissimart.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}
