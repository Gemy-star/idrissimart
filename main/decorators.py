from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect


def profile_type_required(*allowed_types):
    """
    Decorator to restrict access based on user profile type

    Usage:
    @profile_type_required('merchant', 'service')
    def my_view(request):
        pass
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.profile_type not in allowed_types:
                error_msg = (
                    "ليس لديك صلاحية للوصول إلى هذه الصفحة - "
                    "You do not have permission to access this page"
                )
                messages.error(request, error_msg)
                return redirect("home")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def verified_user_required(view_func):
    """
    Decorator to ensure user is verified

    Usage:
    @verified_user_required
    def my_view(request):
        pass
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.verification_status != "verified":
            warning_msg = "يجب توثيق حسابك أولاً - " "You must verify your account first"
            messages.warning(request, warning_msg)
            return redirect("profile_verification")
        return view_func(request, *args, **kwargs)

    return wrapper


def premium_required(view_func):
    """
    Decorator to ensure user has active premium subscription

    Usage:
    @premium_required
    def my_view(request):
        pass
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.has_premium_access():
            info_msg = (
                "هذه الميزة متاحة للأعضاء المميزين فقط - "
                "This feature is only available for premium members"
            )
            messages.info(request, info_msg)
            return redirect("subscription_plans")
        return view_func(request, *args, **kwargs)

    return wrapper


def action_permission_required(action):
    """
    Decorator to check if user can perform specific action

    Usage:
    @action_permission_required('post_classified_ad')
    def my_view(request):
        pass
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not request.user.can_perform_action(action):
                error_msg = (
                    "ليس لديك صلاحية لتنفيذ هذا الإجراء - "
                    "You do not have permission to perform this action"
                )
                messages.error(request, error_msg)
                return redirect("home")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def api_profile_type_required(*allowed_types):
    """
    API version of profile_type_required for REST endpoints

    Usage:
    @api_profile_type_required('merchant')
    def my_api_view(request):
        pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"},
                    status=401,
                )

            if request.user.profile_type not in allowed_types:
                error_response = {
                    "error": "Permission denied",
                    "message": (
                        "Your profile type does not have access " "to this resource"
                    ),
                    "required_types": list(allowed_types),
                    "your_type": request.user.profile_type,
                }
                return JsonResponse(error_response, status=403)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
