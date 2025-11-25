import tempfile
import logging

from .common import *


# A small logging filter to ignore noisy Invalid HTTP_HOST messages coming from
# probes against random subdomains (e.g. ftp.idrissimart.com, mail.idrissimart.com)
class IgnoreInvalidHostFilter(logging.Filter):
    def filter(self, record):
        try:
            msg = record.getMessage()
        except Exception:
            return True

        # Keep the normal flow; drop messages that indicate invalid host header
        if isinstance(msg, str) and (
            "Invalid HTTP_HOST header" in msg or "DisallowedHost" in msg
        ):
            return False

        # Also check for DisallowedHost exception in the record
        if hasattr(record, "exc_info") and record.exc_info:
            exc_type = record.exc_info[0]
            if exc_type and exc_type.__name__ == "DisallowedHost":
                return False

        return True


DEBUG = False
ALLOWED_HOSTS = [
    "idrissimart.com",
    "www.idrissimart.com",
    # allow all subdomains like mail.idrissimart.com, ftp.idrissimart.com, etc.
    ".idrissimart.com",
    "72.61.88.27",
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
        "PASSWORD": os.getenv("DB_PASSWORD", "Gemy@2803150"),
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
    # Small filter to suppress noisy 'Invalid HTTP_HOST header' logs
    # We attach this filter to django.request so 3rd-party probes to random
    # subdomains (ftp., mail., etc.) don't spam production error logs.
    "filters": {
        "skip_disallowed_host": {
            "()": "idrissimart.settings.docker.IgnoreInvalidHostFilter"
        }
    },
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
            "filters": ["skip_disallowed_host"],
        },
        "main": {
            "handlers": ["file", "console"],
            "level": "ERROR",
            "propagate": False,
        },
        "content": {
            "handlers": ["file", "console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# Security Headers
SESSION_COOKIE_SECURE = True  # Set to True in production with HTTPS
CSRF_TRUSTED_ORIGINS = [
    "https://idrissimart.com",
    "https://www.idrissimart.com",
]

# Admin URL path - change this to something unique for security
# ADMIN_URL = os.getenv("ADMIN_URL", "admin/")
