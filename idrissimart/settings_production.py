"""
Production settings for Idrissimart
"""
import os
from decouple import config
from .settings import *

# =============================================================================
# Security Settings
# =============================================================================

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='change-this-in-production')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Site URL
SITE_URL = config('SITE_URL', default='https://yourdomain.com')

# =============================================================================
# Database Configuration
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='idrissimart_db'),
        'USER': config('DB_USER', default='idrissimart_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# =============================================================================
# PayPal Configuration
# =============================================================================

PAYPAL_MODE = config('PAYPAL_MODE', default='sandbox')  # 'sandbox' or 'live'
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')

# =============================================================================
# Twilio Configuration
# =============================================================================

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# =============================================================================
# Paymob Configuration
# =============================================================================

PAYMOB_API_KEY = config('PAYMOB_API_KEY', default='')
PAYMOB_INTEGRATION_ID = config('PAYMOB_INTEGRATION_ID', default='')
PAYMOB_IFRAME_ID = config('PAYMOB_IFRAME_ID', default='')

# =============================================================================
# Email Configuration
# =============================================================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# =============================================================================
# Cache Configuration (Redis)
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'idrissimart',
        'TIMEOUT': 300,
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# =============================================================================
# Static and Media Files
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT', default='/var/www/idrissimart/static')

MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default='/var/www/idrissimart/media')

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# Security Settings
# =============================================================================

# HTTPS Settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie Security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [SITE_URL]

# =============================================================================
# Logging Configuration
# =============================================================================

LOG_LEVEL = config('LOG_LEVEL', default='INFO')
LOG_FILE = config('LOG_FILE', default='/var/log/idrissimart/django.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'main': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'twilio': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# Performance Settings
# =============================================================================

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# =============================================================================
# Celery Configuration (for background tasks)
# =============================================================================

CELERY_BROKER_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# =============================================================================
# Admin Settings
# =============================================================================

ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='admin@yourdomain.com')),
]

MANAGERS = ADMINS

# =============================================================================
# File Upload Settings
# =============================================================================

# Maximum file size (10MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv']

# =============================================================================
# Internationalization
# =============================================================================

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# =============================================================================
# Third-party App Settings
# =============================================================================

# Django CORS (if needed for API)
CORS_ALLOWED_ORIGINS = [
    SITE_URL,
]

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# Custom Settings
# =============================================================================

# Payment settings
PAYMENT_SUCCESS_URL = SITE_URL + '/payment/success/'
PAYMENT_CANCEL_URL = SITE_URL + '/payment/cancel/'

# SMS settings
SMS_RATE_LIMIT = 5  # Maximum SMS per hour per user
OTP_EXPIRY_MINUTES = 10

# File storage settings
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# =============================================================================
# Error Reporting
# =============================================================================

# Sentry (optional - for error tracking)
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=0.1,
        send_default_pii=True
    )
