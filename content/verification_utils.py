"""
Utilities for handling verification requirements
"""

from django.utils.translation import get_language


def is_email_verification_required():
    """Check if email verification is required during registration"""
    from content.site_config import SiteConfiguration

    site_config = SiteConfiguration.get_solo()
    return site_config.require_email_verification


def is_phone_verification_required():
    """Check if phone verification is required during registration"""
    from constance import config
    from content.site_config import SiteConfiguration

    # Check both django-constance and site_config
    constance_enabled = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)
    site_config = SiteConfiguration.get_solo()
    site_config_enabled = site_config.require_phone_verification

    # Return True if either is enabled
    return constance_enabled or site_config_enabled


def is_verification_required_for_services():
    """Check if verification is required to use site services"""
    from content.site_config import SiteConfiguration

    site_config = SiteConfiguration.get_solo()
    return site_config.require_verification_for_services


def is_free_package_verification_required():
    """Check if email/phone verification is required before assigning the free package"""
    from content.site_config import SiteConfiguration

    site_config = SiteConfiguration.get_solo()
    return getattr(site_config, "require_verification_for_free_package", False)


def get_verification_message():
    """Get the verification message for services"""
    from content.site_config import SiteConfiguration

    site_config = SiteConfiguration.get_solo()
    current_lang = get_language()
    if current_lang == "ar":
        return (
            site_config.verification_services_message_ar
            or "يجب التحقق من حسابك لاستخدام هذه الخدمة"
        )
    return (
        site_config.verification_services_message
        or "You must verify your account to use this service"
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

    from content.social_auth_config import (
        is_google_auth_configured,
        is_facebook_auth_configured,
    )

    return {
        "email_required": is_email_verification_required(),
        "phone_required": is_phone_verification_required(),
        "services_require_verification": is_verification_required_for_services(),
        "verification_message": get_verification_message(),
        "social_auth_enabled": getattr(constance_config, "SOCIAL_AUTH_ENABLED", False),
        "google_auth_enabled": is_google_auth_configured(),
        "facebook_auth_enabled": is_facebook_auth_configured(),
    }


def phone_needs_verification(user, phone_number, country_code="EG"):
    """
    Check if a phone number needs verification for the given user.
    Returns True if:
    - Phone verification is required AND
    - User's phone is not verified OR
    - The provided phone number is different from user's verified phone

    Args:
        user: User instance
        phone_number: Phone number to check (can be with or without country code)
        country_code: Country code (default: SA)

    Returns:
        tuple: (needs_verification: bool, message: str)
    """
    from main.utils import normalize_phone_number

    # If phone verification is not required globally, no need to verify
    if not is_phone_verification_required():
        return False, ""

    # If user is not authenticated, require verification
    if not user or not user.is_authenticated:
        return True, "يجب تسجيل الدخول أولاً"

    # Staff and superusers bypass verification
    if user.is_staff or user.is_superuser:
        return False, ""

    # If user has no verified phone, require verification
    if not hasattr(user, 'is_mobile_verified') or not user.is_mobile_verified:
        return True, "يجب التحقق من رقم الجوال قبل المتابعة"

    # If user has no phone stored, require verification
    if not hasattr(user, 'phone') or not user.phone:
        return True, "يجب إدخال والتحقق من رقم الجوال"

    # Normalize both phone numbers for comparison
    try:
        user_phone = normalize_phone_number(user.phone, country_code)
        new_phone = normalize_phone_number(phone_number, country_code)

        # If phones are different, require verification
        if user_phone != new_phone:
            return True, "رقم الجوال المدخل مختلف عن الرقم الموثق. يجب التحقق من الرقم الجديد"
    except Exception:
        # If normalization fails, require verification to be safe
        return True, "يجب التحقق من رقم الجوال"

    # Phone is verified and matches user's verified phone
    return False, ""


def check_session_phone_verification(request, phone_number, country_code="EG"):
    """
    Check if a phone number has been verified in the current session.
    This is used during checkout/payment when user might verify a new number.

    Args:
        request: Django request object
        phone_number: Phone number to check
        country_code: Country code (default: SA)

    Returns:
        bool: True if phone is verified in session
    """
    from main.utils import normalize_phone_number

    try:
        normalized_phone = normalize_phone_number(phone_number, country_code)
        session_key = f"phone_verified_{normalized_phone}"
        return request.session.get(session_key, False)
    except Exception:
        return False
