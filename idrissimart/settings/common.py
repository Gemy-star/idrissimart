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
    "django.contrib.humanize",
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
    "django_ckeditor_5",
    "solo",
    "django_recaptcha",
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
    # Visitor tracking middleware
    "main.middleware.VisitorTrackingMiddleware",
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
                "main.context_processors.recaptcha_keys",
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
# Email Configuration
# =======================
EMAIL_BACKEND = "sendgrid_backend.SendGridBackend"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@idrissimart.com")
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL

# =======================
# Google reCAPTCHA
# =======================
RECAPTCHA_PUBLIC_KEY = os.getenv(
    "RECAPTCHA_SITE_KEY", "6LcFPR4sAAAAAF2OLomwf-srKNlJtt33V05-FziB"
)
RECAPTCHA_PRIVATE_KEY = os.getenv(
    "RECAPTCHA_SECRET_KEY", "6LcFPR4sAAAAAAPO3McKxxpBR1-hehL9A-gy5uAI"
)

RECAPTCHA_REQUIRED_SCORE = 0.85  # for reCAPTCHA v3
# For backward compatibility
RECAPTCHA_SITE_KEY = RECAPTCHA_PUBLIC_KEY
RECAPTCHA_SECRET_KEY = RECAPTCHA_PRIVATE_KEY

# =======================
# Compressor
# =======================

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

# ===========================
# Paymob Payment Gateway Settings
# ===========================
# Note: Paymob credentials are managed via django-constance
# They can be configured in the admin panel under "Config"
# Sensitive keys are loaded from environment variables
PAYMOB_BASE_URL = "https://accept.paymob.com/api"

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

# ===========================
# CKEditor 5 Settings
# ===========================
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "removePlugins": [
            "DocumentOutline",
            "RealTimeCollaborativeEditing",
            "RealTimeCollaborativeComments",
            "RealTimeCollaborativeTrackChanges",
            "RealTimeCollaborativeRevisionHistory",
            "PresenceList",
            "Comments",
            "TrackChanges",
            "TrackChangesData",
            "RevisionHistory",
            "AIAssistant",
            "TableOfContents",
            "FormatPainter",
            "Template",
            "PasteFromOfficeEnhanced",
            "CKBox",
            "CKFinder",
            "EasyImage",
            "MultiLevelList",
            "CaseChange",
        ],
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
            "|",
            "insertTable",
            "tableColumn",
            "tableRow",
            "mergeTableCells",
            "|",
            "undo",
            "redo",
        ],
        "language": "ar",
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignCenter",
                "imageStyle:alignRight",
                "imageStyle:side",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignCenter",
                "alignRight",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "admin": {
        "removePlugins": [
            "DocumentOutline",
            "RealTimeCollaborativeEditing",
            "RealTimeCollaborativeComments",
            "RealTimeCollaborativeTrackChanges",
            "RealTimeCollaborativeRevisionHistory",
            "PresenceList",
            "Comments",
            "TrackChanges",
            "TrackChangesData",
            "RevisionHistory",
            "Pagination",
            "WProofreader",
            "MathType",
            "SlashCommand",
            "AIAssistant",
            "TableOfContents",
            "FormatPainter",
            "Template",
            "PasteFromOfficeEnhanced",
            "CKBox",
            "CKFinder",
            "EasyImage",
            "MultiLevelList",
            "CaseChange",
        ],
        "toolbar": {
            "items": [
                "heading",
                "|",
                "bold",
                "italic",
                "underline",
                "strikethrough",
                "code",
                "subscript",
                "superscript",
                "|",
                "link",
                "bulletedList",
                "numberedList",
                "todoList",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "|",
                "alignment",
                "indent",
                "outdent",
                "|",
                "blockQuote",
                "codeBlock",
                "htmlEmbed",
                "|",
                "imageUpload",
                "insertTable",
                "mediaEmbed",
                "horizontalLine",
                "pageBreak",
                "|",
                "highlight",
                "removeFormat",
                "findAndReplace",
                "|",
                "undo",
                "redo",
                "sourceEditing",
            ],
            "shouldNotGroupWhenFull": True,
        },
        "language": "ar",
        "fontSize": {"options": [9, 11, 13, "default", 17, 19, 21, 24, 28, 32, 36]},
        "fontFamily": {
            "options": [
                "default",
                "Arial, Helvetica, sans-serif",
                "Courier New, Courier, monospace",
                "Georgia, serif",
                "Lucida Sans Unicode, Lucida Grande, sans-serif",
                "Tahoma, Geneva, sans-serif",
                "Times New Roman, Times, serif",
                "Trebuchet MS, Helvetica, sans-serif",
                "Verdana, Geneva, sans-serif",
            ]
        },
        "htmlEmbed": {"showPreviews": True},
        "codeBlock": {
            "languages": [
                {"language": "plaintext", "label": "Plain text"},
                {"language": "c", "label": "C"},
                {"language": "cs", "label": "C#"},
                {"language": "cpp", "label": "C++"},
                {"language": "css", "label": "CSS"},
                {"language": "diff", "label": "Diff"},
                {"language": "html", "label": "HTML"},
                {"language": "java", "label": "Java"},
                {"language": "javascript", "label": "JavaScript"},
                {"language": "php", "label": "PHP"},
                {"language": "python", "label": "Python"},
                {"language": "ruby", "label": "Ruby"},
                {"language": "typescript", "label": "TypeScript"},
                {"language": "xml", "label": "XML"},
            ]
        },
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:inline",
                "imageStyle:wrapText",
                "imageStyle:breakText",
                "imageStyle:alignLeft",
                "imageStyle:alignCenter",
                "imageStyle:alignRight",
                "|",
                "toggleImageCaption",
                "linkImage",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignCenter",
                "alignRight",
                "inline",
                "wrapText",
                "breakText",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
                "toggleTableCaption",
            ],
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
                {
                    "model": "heading4",
                    "view": "h4",
                    "title": "Heading 4",
                    "class": "ck-heading_heading4",
                },
            ]
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True,
            }
        },
        "fontColor": {"colors": customColorPalette},
        "fontBackgroundColor": {"colors": customColorPalette},
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "insertImage",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageUpload",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "toggleImageCaption",
                "imageStyle:inline",
                "imageStyle:block",
                "imageStyle:side",
                "linkImage",
            ]
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PATH = "uploads/"
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"
