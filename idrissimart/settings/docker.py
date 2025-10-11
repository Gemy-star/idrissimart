import os
import tempfile

# Import specific settings instead of star import

DEBUG = False

ALLOWED_HOSTS = [
    "idrissimart.com",
    "www.idrissimart.com",
    "localhost",
    "127.0.0.1",
    "45.9.191.23",
]

# Ensure Django respects proxy headers (for HTTPS behind Nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# =======================
# Database: MariaDB
# =======================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "idrissimartdb"),
        "USER": os.getenv("DB_USER", "idrissimart"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),  # Set via environment
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "CONN_MAX_AGE": 60,
    }
}

# =======================
# Static & Media
# =======================
# Use system temp directory instead of hardcoded path
FILE_UPLOAD_TEMP_DIR = os.getenv(
    "FILE_UPLOAD_TEMP_DIR",
    tempfile.gettempdir(),
)

# =======================
# Logging
# =======================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.getenv(
                "DJANGO_LOG_FILE",
                "/var/log/django/idrissimart.log",
            ),
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
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["file", "console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
