from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy


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
            warning_msg = "يجب توثيق حسابك أولاً - You must verify your account first"
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
                        "Your profile type does not have access to this resource"
                    ),
                    "required_types": list(allowed_types),
                    "your_type": request.user.profile_type,
                }
                return JsonResponse(error_response, status=403)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# ============================================
# CLASS-BASED VIEW MIXINS
# ============================================


class ProfileTypeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to restrict access to class-based views based on user profile type

    Usage:
    class MyView(ProfileTypeRequiredMixin, ListView):
        allowed_profile_types = ['publisher', 'merchant']
        profile_redirect_url = 'main:home'
    """

    allowed_profile_types = []  # Override in subclass
    profile_redirect_url = "main:home"  # Override if needed
    profile_error_message = "ليس لديك صلاحية للوصول إلى هذه الصفحة"

    def test_func(self):
        """Check if user's profile type is in allowed types"""
        return self.request.user.profile_type in self.allowed_profile_types

    def handle_no_permission(self):
        """Handle failed permission check"""
        messages.error(self.request, self.profile_error_message)
        return redirect(self.profile_redirect_url)


class PublisherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin specifically for publisher dashboard and features
    Checks if user is a publisher or has publisher-like permissions

    Usage:
    class PublisherDashboardView(PublisherRequiredMixin, ListView):
        pass
    """

    login_url = reverse_lazy("main:login")

    def test_func(self):
        """Check if user is publisher or has ads (auto-promote to publisher)"""
        user = self.request.user

        # Superadmins can access publisher dashboard
        if user.is_superuser:
            return True

        # Users with PUBLISHER profile type
        if user.profile_type == "publisher":
            return True

        # Auto-promote users who have created ads
        from .models import ClassifiedAd

        if ClassifiedAd.objects.filter(user=user).exists():
            # Auto-upgrade to publisher if they have ads
            if user.profile_type == "default":
                user.profile_type = "publisher"
                user.save(update_fields=["profile_type"])
            return True

        return False

    def handle_no_permission(self):
        """Redirect with appropriate message"""
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)

        messages.warning(
            self.request,
            "لوحة الناشر متاحة فقط للمستخدمين الذين لديهم إعلانات. قم بإنشاء إعلانك الأول!",
        )
        return redirect("main:ad_create")


class SuperadminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for superadmin dashboard access

    Usage:
    class SuperadminDashboardView(SuperadminRequiredMixin, ListView):
        pass
    """

    login_url = reverse_lazy("main:login")

    def test_func(self):
        """Only superusers can access"""
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """Redirect with error message"""
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)

        messages.error(self.request, "هذه الصفحة متاحة فقط لمسؤولي النظام")
        return redirect("main:home")


class VerifiedPublisherMixin(PublisherRequiredMixin):
    """
    Mixin for features that require verified publisher status

    Usage:
    class PremiumFeatureView(VerifiedPublisherMixin, View):
        pass
    """

    def test_func(self):
        """Check if user is verified publisher"""
        # First check if they're a publisher
        if not super().test_func():
            return False

        # Then check verification status
        return self.request.user.verification_status == "verified"

    def handle_no_permission(self):
        """Handle verification requirement"""
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)

        user = self.request.user

        # If not a publisher at all
        if user.profile_type not in ["publisher", "merchant", "service", "educational"]:
            return super().handle_no_permission()

        # If publisher but not verified
        messages.warning(
            self.request, "هذه الميزة متاحة فقط للناشرين الموثقين. يرجى توثيق حسابك."
        )
        return redirect("main:profile_verification")


# ============================================
# FUNCTION-BASED VIEW DECORATORS
# ============================================


def publisher_required(view_func):
    """
    Decorator for function-based views requiring publisher access

    Usage:
    @publisher_required
    def my_publisher_view(request):
        pass
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Superadmins can access
        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Publisher profile type
        if user.profile_type == "publisher":
            return view_func(request, *args, **kwargs)

        # Auto-promote if they have ads
        from .models import ClassifiedAd

        if ClassifiedAd.objects.filter(user=user).exists():
            if user.profile_type == "default":
                user.profile_type = "publisher"
                user.save(update_fields=["profile_type"])
            return view_func(request, *args, **kwargs)

        # No permission
        messages.warning(
            request, "لوحة الناشر متاحة فقط للمستخدمين الذين لديهم إعلانات"
        )
        return redirect("main:ad_create")

    return wrapper


def superadmin_required(view_func):
    """
    Decorator for superadmin-only views

    Usage:
    @superadmin_required
    def admin_only_view(request):
        pass
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "هذه الصفحة متاحة فقط لمسؤولي النظام")
            return redirect("main:home")
        return view_func(request, *args, **kwargs)

    return wrapper
