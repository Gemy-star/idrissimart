import tempfile

from .common import *

DEBUG = False

ALLOWED_HOSTS = [
    "idrissimart.com",
    "www.idrissimart.com",
    "localhost",
    "127.0.0.1",
    "45.9.191.23",
]

# Respect proxy headers (for HTTPS behind Nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# =======================
# Database: MariaDB
# =======================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "idrissimartdb"),
        "USER": os.getenv("DB_USER", "idrissimart"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "CONN_MAX_AGE": 60,
    }
}

# =======================
# Compressor for production
# =======================
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True  # Precompress for production

# =======================
# Upload Temp & Logging
# =======================
FILE_UPLOAD_TEMP_DIR = os.getenv(
    "FILE_UPLOAD_TEMP_DIR",
    tempfile.gettempdir(),
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.getenv("DJANGO_LOG_FILE", "/var/log/django/idrissimart.log"),
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["file", "console"], "level": "INFO", "propagate": True},
        "django.request": {
            "handlers": ["file", "console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
SESSION_COOKIE_SECURE = True  # Set to True in production with HTTPS
