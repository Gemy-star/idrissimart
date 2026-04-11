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
    # Django Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
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
    # Django REST Framework
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_yasg",
    # Local apps
    "main.apps.MainConfig",
    "content.apps.ContentConfig",
    "api.apps.ApiConfig",
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
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Django Allauth - must be after AuthenticationMiddleware
    "allauth.account.middleware.AccountMiddleware",
    # Block malicious requests (should be early in middleware stack)
    "main.middleware.BlockMaliciousRequestsMiddleware",
    # force App to open in AR language
    "content.middleware.ForceArabicDefaultMiddleware",
    # Force English for /super-admin/ — must be after LocaleMiddleware and ForceArabicDefaultMiddleware
    "content.middleware.ForceAdminEnglishMiddleware",
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
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "constance.context_processors.config",
                # Custom context processors
                "content.context_processors.countries",
                "content.context_processors.home_sliders",
                "content.context_processors.user_preferences",
                "content.context_processors.header_categories",
                "content.context_processors.notifications",
                "content.context_processors.verification_settings",
                "content.context_processors.site_configuration",
                "content.context_processors.paid_advertisements",
                "main.context_processors.cart_wishlist_counts",
                "main.context_processors.recaptcha_keys",
            ],
            "builtins": [
                "django.templatetags.i18n",
                "django.templatetags.l10n",
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
        "OPTIONS": {
            "timeout": 20,  # seconds to wait before raising "database is locked"
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
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
# Rosetta (Translation UI)
# =======================
# Access: /ar/super-admin/translations/
# Requires: staff + superuser
ROSETTA_MESSAGES_PER_PAGE = 25
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = False  # set True & add API key to enable AI suggestions
ROSETTA_AUTO_COMPILE = True          # auto-compile .mo after saving in UI
ROSETTA_REQUIRES_AUTH = True         # must be logged in
ROSETTA_SHOW_AT_ADMIN_PANEL = True   # show link in Django admin sidebar
ROSETTA_SHOW_OCCURRENCES = True      # show where each string appears in code
ROSETTA_EXCLUDED_APPLICATIONS = (    # skip third-party app translations
    "django",
    "rosetta",
    "allauth",
    "rest_framework",
    "django_q",
    "mptt",
    "filer",
    "easy_thumbnails",
    "import_export",
    "ckeditor5",
    "constance",
    "recaptcha",
    "taggit",
    "corsheaders",
)
ROSETTA_POFILE_WRAP_WIDTH = 0        # don't wrap long strings (easier to read)
ROSETTA_MAIN_LANGUAGE = "ar"         # Arabic is the primary language
ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = "ar"
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = "Arabic"

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
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@idrissimart.com")

# =======================
# Google reCAPTCHA v2
# =======================
# Get your own keys from: https://www.google.com/recaptcha/admin/create
# Site Key: Use this in HTML forms (6LcUMSYsAAAAAGKWlIEtHtmD7ecT5U1Vi3B098dD)
# Secret Key: Use this for server-side validation (6LcUMSYsAAAAAARBEdYizpNQTn9SbrZWutEkfuPq)
RECAPTCHA_PUBLIC_KEY = os.getenv(
    "RECAPTCHA_SITE_KEY", "6LcUMSYsAAAAAGKWlIEtHtmD7ecT5U1Vi3B098dD"
)
RECAPTCHA_PRIVATE_KEY = os.getenv(
    "RECAPTCHA_SECRET_KEY", "6LcUMSYsAAAAAARBEdYizpNQTn9SbrZWutEkfuPq"
)

# For backward compatibility with different naming conventions
RECAPTCHA_SITE_KEY = RECAPTCHA_PUBLIC_KEY
RECAPTCHA_SECRET_KEY = RECAPTCHA_PRIVATE_KEY

# Required settings for django-recaptcha v4+
DJANGORECAPTCHA_DEFAULT_CSS_CLASS = "django-recaptcha"
DJANGORECAPTCHA_USE_SSL = True

# Disable reCAPTCHA validation in development if keys are not set
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

# =======================
# Cache Configuration
# =======================
# Use database cache by default (works without Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
        "TIMEOUT": 300,  # 5 minutes default
        "OPTIONS": {"MAX_ENTRIES": 1000},
    },
}

# Cache time to live is 5 minutes by default
CACHE_TTL = 60 * 5

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
LOGOUT_REDIRECT_URL = "main:home"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =======================
# Django Allauth Settings
# =======================
AUTHENTICATION_BACKENDS = [
    # Django default
    "django.contrib.auth.backends.ModelBackend",
    # Allauth specific
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Allauth configuration
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"  # 'mandatory', 'optional', or 'none'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "optional"

# Redirect URLs after social auth
SOCIALACCOUNT_LOGIN_ON_GET = True
LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Social Account Providers (loaded dynamically from Constance)
# To configure: Go to Admin Panel -> Constance -> Config -> Social Authentication
SOCIALACCOUNT_PROVIDERS = {}

# We'll load Google and Facebook settings dynamically from Constance
# This is done in the AppConfig.ready() method
# Admins can configure OAuth credentials in the admin panel without code changes

DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024  # 200 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024  # 200 MB
# =======================
# Session Settings
# =======================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True  # Keep sessions alive during active use
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
DEFAULT_COUNTRY = "EG"
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
    "catch_up": False,  # Don't pile up missed schedules; run once then reschedule
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
            "bold",
            "italic",
            "link",
            "|",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "|",
            "specialCharacters",
            "emoji",
            "|",
            "imageUpload",
            "insertTable",
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
        "specialCharacters": {
            "includeEmoji": True,
        },
        "emoji": {
            "feedbackUrl": None,  # Disable feedback
        },
        "placeholder": "اكتب وصف الإعلان هنا... يمكنك استخدام الإيموجي 😊",
    },
    "public_ad": {
        # Enhanced but secure configuration for public ad forms
        "toolbar": {
            "items": [
                "heading",
                "|",
                "bold",
                "italic",
                "underline",
                "strikethrough",
                "|",
                "fontSize",
                "fontColor",
                "fontBackgroundColor",
                "|",
                "alignment",
                "|",
                "bulletedList",
                "numberedList",
                "todoList",
                "|",
                "outdent",
                "indent",
                "|",
                "link",
                "insertTable",
                "blockQuote",
                "horizontalLine",
                "|",
                "undo",
                "redo",
            ],
            "shouldNotGroupWhenFull": True
        },
        "heading": {
            "options": [
                {"model": "paragraph", "title": "فقرة", "class": "ck-heading_paragraph"},
                {"model": "heading2", "view": "h2", "title": "عنوان 1", "class": "ck-heading_heading2"},
                {"model": "heading3", "view": "h3", "title": "عنوان 2", "class": "ck-heading_heading3"},
                {"model": "heading4", "view": "h4", "title": "عنوان 3", "class": "ck-heading_heading4"},
            ]
        },
        "fontSize": {
            "options": [
                "tiny",
                "small",
                "default",
                "big",
                "huge"
            ]
        },
        "fontColor": {
            "colors": [
                {"color": "#000000", "label": "أسود"},
                {"color": "#4d4d4d", "label": "رمادي غامق"},
                {"color": "#999999", "label": "رمادي"},
                {"color": "#e6e6e6", "label": "رمادي فاتح"},
                {"color": "#ffffff", "label": "أبيض"},
                {"color": "#e74c3c", "label": "أحمر"},
                {"color": "#e67e22", "label": "برتقالي"},
                {"color": "#f39c12", "label": "أصفر"},
                {"color": "#27ae60", "label": "أخضر"},
                {"color": "#3498db", "label": "أزرق"},
                {"color": "#9b59b6", "label": "بنفسجي"},
                {"color": "#6b4c7a", "label": "بنفسجي داكن"},
            ]
        },
        "fontBackgroundColor": {
            "colors": [
                {"color": "#ffffff", "label": "أبيض"},
                {"color": "#ffebee", "label": "أحمر فاتح"},
                {"color": "#fff3e0", "label": "برتقالي فاتح"},
                {"color": "#fff9c4", "label": "أصفر فاتح"},
                {"color": "#e8f5e9", "label": "أخضر فاتح"},
                {"color": "#e3f2fd", "label": "أزرق فاتح"},
                {"color": "#f3e5f5", "label": "بنفسجي فاتح"},
            ]
        },
        "alignment": {
            "options": ["left", "right", "center", "justify"]
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
        "link": {
            "decorators": {
                "openInNewTab": {
                    "mode": "manual",
                    "label": "فتح في نافذة جديدة",
                    "attributes": {
                        "target": "_blank",
                        "rel": "noopener noreferrer"
                    }
                }
            },
            "addTargetToExternalLinks": True,
        },
        "language": "ar",
        "placeholder": "اكتب وصف الإعلان هنا... استخدم الأدوات لتنسيق النص",
        "htmlSupport": {
            "allow": [
                {
                    "name": "/.*/",
                    "attributes": True,
                    "classes": True,
                    "styles": True,
                }
            ],
            "disallow": [
                {"name": "script"},
                {"name": "style"},
                {"name": "iframe"},
                {"name": "object"},
                {"name": "embed"},
                {"name": "form"},
                {"name": "input"},
                {"name": "button"},
            ],
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
                "specialCharacters",
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
        "specialCharacters": {
            "includeEmoji": True,
        },
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
            "|",
            "specialCharacters",
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
        "specialCharacters": {
            "includeEmoji": True,
        },
        "language": "ar",
    },
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PATH = "uploads/"
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"

# ===========================
# Django REST Framework Settings
# ===========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ===========================
# CORS Settings
# ===========================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8081",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8081",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ===========================
# Swagger/OpenAPI Settings (drf-yasg)
# ===========================
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'DEFAULT_MODEL_RENDERING': 'example',
    'DEFAULT_MODEL_DEPTH': 2,
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_INFO': 'api.urls.api_info',
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': True,
}


