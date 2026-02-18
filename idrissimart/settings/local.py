from .common import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Dynamic compression for dev
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False

# =======================
# Redis Configuration for Local Development
# =======================
# Make sure Redis is running locally on port 6379
# Install Redis: sudo apt install redis-server
# Start Redis: sudo service redis-server start
# Check status: sudo service redis-server status

# Django-Q2 Settings with Local Redis
Q_CLUSTER = {
    "name": "idrissimart_local",
    "workers": 2,  # Fewer workers for local dev
    "timeout": 90,
    "retry": 120,
    "redis": {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 0,
        "password": None,  # No password for local Redis
        "socket_timeout": 5,
        "charset": "utf-8",
        "errors": "strict",
    },
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "label": "Django Q Local",
    "sync": False,  # Async execution
    "catch_up": True,
    "orm": "default",
}

# Channels Redis Configuration for Local Development
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

# Add Silk for profiling

# =======================
# Session Settings for Local Development
# =======================
# Note: Remember Me functionality is handled in auth_views.py via set_expiry()
# Don't override SESSION_EXPIRE_AT_BROWSER_CLOSE here to allow remember_me to work
SESSION_COOKIE_SECURE = False  # HTTP is fine for local
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Disable CSRF for easier local development (optional)
# CSRF_COOKIE_SECURE = False

# =======================
# CSRF Settings for Local Development
# =======================
# Ensure proper CSRF handling in local development
CSRF_COOKIE_SECURE = False  # HTTP is fine for local
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access in dev
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:6522",
    "http://localhost:6522",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Database for local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =======================
# Email Configuration - SMTP4Dev (Local Development)
# =======================
# Using smtp4dev for local email testing
# All emails are captured and displayed in web UI at http://localhost:3100
# No real emails are sent - perfect for development and testing

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp4dev"  # Docker container name
EMAIL_PORT = 25  # Internal container port
EMAIL_HOST_USER = ""  # No authentication needed
EMAIL_HOST_PASSWORD = ""  # No authentication needed
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = "noreply@idrissimart.local"
SERVER_EMAIL = "server@idrissimart.local"

# For local development without Docker, use:
# EMAIL_HOST = "localhost"
# EMAIL_PORT = 2525  # Host port mapping

# To view sent emails, open: http://localhost:3100

# =======================
# Logging Configuration for Local Development
# =======================
# Console-only logging (no file logging for local dev)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",  # Set to DEBUG to see SQL queries
            "propagate": False,
        },
        "main": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "content": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "daphne": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "channels": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

