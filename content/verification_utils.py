"""
Utilities for handling verification requirements
"""

from django.utils.translation import get_language
from constance import config


def is_email_verification_required():
    """Check if email verification is required during registration"""
    return getattr(config, "REQUIRE_EMAIL_VERIFICATION", False)


def is_phone_verification_required():
    """Check if phone verification is required during registration"""
    return getattr(config, "REQUIRE_PHONE_VERIFICATION", False)


def is_verification_required_for_services():
    """Check if verification is required to use site services"""
    return getattr(config, "REQUIRE_VERIFICATION_FOR_SERVICES", False)


def get_verification_message():
    """Get the verification message for services"""
    return getattr(
        config,
        "VERIFICATION_SERVICES_MESSAGE",
        "يجب التحقق من حسابك لاستخدام هذه الخدمة",
    )


def user_can_use_services(user):
    """
    Check if user can use site services based on verification requirements
    Returns: (bool, str) - (can_use, message)
    """
    if not is_verification_required_for_services():
        return True, ""

    if not user or not user.is_authenticated:
        return False, "يجب تسجيل الدخول أولاً"

    # Staff and superusers can always use services
    if user.is_staff or user.is_superuser:
        return True, ""

    # Check if user has at least one verification (email OR phone)
    is_verified = False

    if hasattr(user, "is_email_verified") and user.is_email_verified:
        is_verified = True

    if hasattr(user, "is_mobile_verified") and user.is_mobile_verified:
        is_verified = True

    if not is_verified:
        return False, get_verification_message()

    return True, ""


def get_verification_requirements():
    """
    Get all verification requirements as a dictionary
    Useful for passing to templates
    """
    from constance import config as constance_config

    from content.social_auth_config import is_google_auth_configured, is_facebook_auth_configured

    return {
        "email_required": is_email_verification_required(),
        "phone_required": is_phone_verification_required(),
        "services_require_verification": is_verification_required_for_services(),
        "verification_message": get_verification_message(),
        "social_auth_enabled": getattr(constance_config, "SOCIAL_AUTH_ENABLED", False),
        "google_auth_enabled": is_google_auth_configured(),
        "facebook_auth_enabled": is_facebook_auth_configured(),
    }
