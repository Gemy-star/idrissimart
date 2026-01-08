from .common import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Dynamic compression for dev
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False

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
