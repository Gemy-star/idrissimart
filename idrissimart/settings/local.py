import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env.development secrets (overrides any values already set by common.py)
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env.development", override=True)

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
# Tries MariaDB/MySQL first; falls back to SQLite if connection fails.

def _get_database_config():
    import warnings
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
        import MySQLdb
        conn = MySQLdb.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "idrissimart"),
            passwd=os.getenv("DB_PASSWORD", "Gemy@2803150"),
            db=os.getenv("DB_NAME", "idrissimartdb"),
            connect_timeout=3,
        )
        conn.close()
        return _mysql_config
    except Exception as e:
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
