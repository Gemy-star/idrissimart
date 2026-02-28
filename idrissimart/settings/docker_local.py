"""
Django Settings for Docker Development Environment
===================================================
This settings file is specifically for development in Docker containers.
It extends local.py but overrides database and cache settings to use
Docker services (MariaDB, Redis) instead of local SQLite and localhost.

Use this for:
- docker-compose development
- VS Code dev containers
- Any containerized development environment
"""

import os
from .local import *  # noqa: F401, F403

# Override: Keep DEBUG mode for development
DEBUG = True

# Override: Allow Docker service names and common development hosts
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
    "web",  # Docker service name
    "*.localhost",  # Allow subdomains in dev
    "*",  # Allow all in development (not recommended for production)
]

# =======================
# Database: MySQL/MariaDB (Docker Service)
# =======================
# Using MariaDB container instead of SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "idrissimart"),
        "USER": os.getenv("DB_USER", "idrissimart_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "idrissimart_password"),
        "HOST": os.getenv("DB_HOST", "db"),  # Docker service name
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
            "use_unicode": True,
        },
        "CONN_MAX_AGE": 60,
        "ATOMIC_REQUESTS": True,
        "AUTOCOMMIT": True,
    }
}

# =======================
# Database Connection for MySQL (required for mysqlclient)
# =======================
import pymysql

pymysql.version_info = (1, 4, 6, "final", 0)
pymysql.install_as_MySQLdb()

# =======================
# Redis Configuration for Docker Development
# =======================
# Using Redis container instead of localhost Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redispassword")

# Django-Q2 Settings with Docker Redis
Q_CLUSTER = {
    "name": "idrissimart_docker_dev",
    "workers": 2,  # Fewer workers for dev
    "timeout": 90,
    "retry": 120,
    "redis": {
        "host": REDIS_HOST,
        "port": REDIS_PORT,
        "db": 0,
        "password": REDIS_PASSWORD,
        "socket_timeout": 5,
        "charset": "utf-8",
        "errors": "strict",
    },
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "label": "Django Q Docker Dev",
    "sync": False,  # Async execution
    "catch_up": True,
    "orm": "default",
}

# Channels Redis Configuration for Docker Development
if REDIS_PASSWORD:
    redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1"
else:
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [redis_url],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# =======================
# Email Configuration - SMTP4Dev (Docker Service)
# =======================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp4dev")  # Docker service name
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 25))  # Container internal port
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = "noreply@idrissimart.local"
SERVER_EMAIL = "server@idrissimart.local"

# View sent emails at: http://localhost:3100

# =======================
# Session & CSRF Settings for Docker Development
# =======================
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:80",
    "http://localhost:80",
    "http://web:8000",
]

# =======================
# Static and Media Files
# =======================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # type: ignore # noqa: F405

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # type: ignore # noqa: F405

# =======================
# Logging Configuration for Docker Development
# =======================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
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
            "level": os.getenv("SQL_DEBUG", "WARNING"),  # Set SQL_DEBUG=DEBUG to see queries
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

# =======================
# Development Tools
# =======================
# Enable Django Debug Toolbar in Docker (optional)
# if "debug_toolbar" in INSTALLED_APPS:  # noqa: F405
#     import socket
#     hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
#     INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

print("=" * 80)
print("🐳 Docker Local Development Environment")
print("=" * 80)
print(f"DEBUG: {DEBUG}")
print(f"DATABASE: {DATABASES['default']['ENGINE']} @ {DATABASES['default']['HOST']}")
print(f"REDIS: {REDIS_HOST}:{REDIS_PORT}")
print(f"EMAIL: {EMAIL_HOST}:{EMAIL_PORT}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print("=" * 80)
