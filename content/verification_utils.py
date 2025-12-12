"""
Utilities for handling verification requirements
"""

from django.utils.translation import get_language
from content.site_config import SiteConfiguration


def get_site_config():
    """Get site configuration singleton"""
    return SiteConfiguration.get_solo()


def is_email_verification_required():
    """Check if email verification is required during registration"""
    config = get_site_config()
    return config.require_email_verification


def is_phone_verification_required():
    """Check if phone verification is required during registration"""
    config = get_site_config()
    return config.require_phone_verification


def is_verification_required_for_services():
    """Check if verification is required to use site services"""
    config = get_site_config()
    return config.require_verification_for_services


def get_verification_message():
    """Get the verification message for services"""
    config = get_site_config()
    current_language = get_language()

    if current_language == "ar":
        return (
            config.verification_services_message_ar
            or config.verification_services_message
        )
    return config.verification_services_message


def user_can_use_services(user):
    """
    Check if user can use site services based on verification requirements
    Returns: (bool, str) - (can_use, message)
    """
    if not is_verification_required_for_services():
        return True, ""

    if not user.is_authenticated:
        return False, "يجب تسجيل الدخول أولاً"

    # Check if user is verified (email or phone)
    is_verified = False

    if hasattr(user, "email_verified") and user.email_verified:
        is_verified = True

    if hasattr(user, "phone_verified") and user.phone_verified:
        is_verified = True

    # Staff and superusers can always use services
    if user.is_staff or user.is_superuser:
        is_verified = True

    if not is_verified:
        return False, get_verification_message()

    return True, ""


def get_verification_requirements():
    """
    Get all verification requirements as a dictionary
    Useful for passing to templates
    """
    return {
        "email_required": is_email_verification_required(),
        "phone_required": is_phone_verification_required(),
        "services_require_verification": is_verification_required_for_services(),
        "verification_message": get_verification_message(),
    }
