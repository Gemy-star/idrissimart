import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env.development secrets (overrides any values already set by common.py)
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env.development", override=True)

from .common import *

# Allow Django's MySQL backend to work even when mysqlclient is not installed.
try:
    import pymysql

    pymysql.version_info = (1, 4, 6, "final", 0)
    pymysql.install_as_MySQLdb()
except Exception:
    # If PyMySQL is unavailable, local settings will gracefully fall back to SQLite.
    pass

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
    "http://127.0.0.1:4554",
    "http://localhost:4554",
    "http://127.0.0.1:5455",
    "http://localhost:5455",
    "http://127.0.0.1:6522",
    "http://localhost:6522",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# =======================
# CORS Settings (for frontend development)
# =======================
# Override common.py CORS settings for local development
# Allows various frontend dev servers to access the API
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Vue.js dev server
    "http://127.0.0.1:8080",
    "http://localhost:8082",  # React Native dev server
    "http://127.0.0.1:8082",
    "http://localhost:8081",  # React Native dev server
    "http://127.0.0.1:8081",
]

# =======================
# Database for Local Development
# =======================
# Uses MariaDB/MySQL by default; falls back to SQLite only when MySQL drivers
# are not available in the local Python environment.

def _get_database_config():
    _mysql_config = {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "idrissimartdb"),
        "USER": os.getenv("DB_USER", "idrissimart"),
        "PASSWORD": os.getenv("DB_PASSWORD", "Gemy@2803150"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
            "use_unicode": True,
            "connect_timeout": 3,
        },
        "CONN_MAX_AGE": 60,
        "ATOMIC_REQUESTS": True,
    }

    try:
        # Driver presence check only; do not force a live connection at import-time.
        # This avoids accidental SQLite fallback while MariaDB is still starting.
        import MySQLdb
        _ = MySQLdb
        return _mysql_config
    except Exception as e:
        import warnings

        warnings.warn(f"MariaDB unavailable ({e}), falling back to SQLite.", stacklevel=2)
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {
                "timeout": 20,
            },
        }

DATABASES = {"default": _get_database_config()}

# =======================
# Email Configuration - Local SMTP Server
# =======================
# Using local SMTP server on port 25

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "127.0.0.1"
EMAIL_PORT = 25
# EMAIL_USE_TLS = True  # Does not work with our SMTP server
# Email address used to send regular messages
DEFAULT_FROM_EMAIL = "admin@idrissimart.com"

# =======================
# Payment & Third-party Secrets (from .env.development)
# =======================
PAYMOB_API_KEY = os.getenv("PAYMOB_API_KEY", "")
PAYMOB_SECRET_KEY = os.getenv("PAYMOB_SECRET_KEY", "")
PAYMOB_PUBLIC_KEY = os.getenv("PAYMOB_PUBLIC_KEY", "")
PAYMOB_IFRAME_ID = os.getenv("PAYMOB_IFRAME_ID", "")
PAYMOB_INTEGRATION_ID = os.getenv("PAYMOB_INTEGRATION_ID", "")
PAYMOB_HMAC_SECRET = os.getenv("PAYMOB_HMAC_SECRET", "")

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
RECAPTCHA_SITE_KEY = RECAPTCHA_PUBLIC_KEY
RECAPTCHA_SECRET_KEY = RECAPTCHA_PRIVATE_KEY

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# SMS will be sent to console in local development instead of using Twilio
TWILIO_DEVELOPMENT_MODE = True

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
