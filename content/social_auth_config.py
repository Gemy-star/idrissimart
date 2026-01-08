"""
Dynamic configuration for Social Authentication providers
Loads settings from Constance (django-constance) at runtime
"""

from constance import config


def get_socialaccount_providers():
    """
    Dynamically build SOCIALACCOUNT_PROVIDERS based on Constance settings
    This allows admins to configure OAuth settings without code changes
    """
    providers = {}

    # Check if social auth is enabled
    if not getattr(config, "SOCIAL_AUTH_ENABLED", False):
        return providers

    # Google OAuth
    google_client_id = getattr(config, "GOOGLE_OAUTH_CLIENT_ID", "")
    google_secret = getattr(config, "GOOGLE_OAUTH_SECRET", "")

    if google_client_id and google_secret:
        providers["google"] = {
            "APP": {
                "client_id": google_client_id,
                "secret": google_secret,
                "key": "",
            },
            "SCOPE": [
                "profile",
                "email",
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
            },
        }

    # Facebook OAuth
    facebook_app_id = getattr(config, "FACEBOOK_APP_ID", "")
    facebook_secret = getattr(config, "FACEBOOK_APP_SECRET", "")

    if facebook_app_id and facebook_secret:
        providers["facebook"] = {
            "APP": {
                "client_id": facebook_app_id,
                "secret": facebook_secret,
            },
            "METHOD": "oauth2",
            "SCOPE": ["email", "public_profile"],
            "AUTH_PARAMS": {"auth_type": "reauthenticate"},
            "FIELDS": [
                "id",
                "email",
                "name",
                "first_name",
                "last_name",
                "verified",
                "locale",
                "timezone",
                "link",
                "gender",
                "updated_time",
            ],
            "EXCHANGE_TOKEN": True,
            "VERIFIED_EMAIL": False,
            "VERSION": "v12.0",
        }

    return providers


def is_social_auth_enabled():
    """Check if social authentication is enabled"""
    return getattr(config, "SOCIAL_AUTH_ENABLED", False)


def is_google_auth_configured():
    """Check if Google OAuth is properly configured"""
    if not is_social_auth_enabled():
        return False

    google_client_id = getattr(config, "GOOGLE_OAUTH_CLIENT_ID", "")
    google_secret = getattr(config, "GOOGLE_OAUTH_SECRET", "")

    return bool(google_client_id and google_secret)


def is_facebook_auth_configured():
    """Check if Facebook OAuth is properly configured"""
    if not is_social_auth_enabled():
        return False

    facebook_app_id = getattr(config, "FACEBOOK_APP_ID", "")
    facebook_secret = getattr(config, "FACEBOOK_APP_SECRET", "")

    return bool(facebook_app_id and facebook_secret)
