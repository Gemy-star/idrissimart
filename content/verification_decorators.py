"""
Decorators for verification requirements
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from content.verification_utils import (
    is_verification_required_for_services,
    user_can_use_services,
)


def verification_required(redirect_url="main:dashboard"):
    """
    Decorator to check if user verification is required for services

    Usage:
        @verification_required()
        def my_view(request):
            ...

    Args:
        redirect_url: URL name to redirect to if verification is required
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if verification is required for services
            if not is_verification_required_for_services():
                # Verification not required, proceed normally
                return view_func(request, *args, **kwargs)

            # Check if user can use services
            can_use, message = user_can_use_services(request.user)

            if not can_use:
                # User cannot use services, redirect with message
                messages.warning(request, message)

                # Determine where to redirect
                if not request.user.is_authenticated:
                    return redirect("main:login")
                elif not getattr(request.user, "is_email_verified", False):
                    return redirect("main:email_verification_required")
                elif not getattr(request.user, "is_mobile_verified", False):
                    return redirect("main:phone_verification_required")
                else:
                    return redirect(redirect_url)

            # User can use services, proceed normally
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def email_verification_required(redirect_url="main:email_verification_required"):
    """
    Decorator to check if user email is verified

    Usage:
        @email_verification_required()
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, _("يجب تسجيل الدخول أولاً"))
                return redirect("main:login")

            is_email_verified = getattr(request.user, "is_email_verified", False)
            if not is_email_verified:
                messages.warning(
                    request, _("يجب التحقق من بريدك الإلكتروني لاستخدام هذه الخدمة")
                )
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def phone_verification_required(redirect_url="main:phone_verification_required"):
    """
    Decorator to check if user phone is verified

    Usage:
        @phone_verification_required()
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, _("يجب تسجيل الدخول أولاً"))
                return redirect("main:login")

            is_mobile_verified = getattr(request.user, "is_mobile_verified", False)
            if not is_mobile_verified:
                messages.warning(
                    request, _("يجب التحقق من رقم هاتفك لاستخدام هذه الخدمة")
                )
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
