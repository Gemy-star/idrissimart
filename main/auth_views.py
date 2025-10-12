from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .models import User


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login view
    """
    if request.user.is_authenticated:
        return redirect("main:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me")

        if not username or not password:
            messages.error(request, _("يرجى إدخال اسم المستخدم وكلمة المرور"))
            return render(request, "pages/login.html")

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                if not user.is_suspended:
                    login(request, user)

                    # Set session expiry
                    if not remember_me:
                        request.session.set_expiry(
                            0
                        )  # Session expires on browser close
                    else:
                        request.session.set_expiry(1209600)  # 2 weeks

                    # Log IP address
                    user.last_login_ip = get_client_ip(request)
                    user.save(update_fields=["last_login_ip"])

                    messages.success(
                        request, _(f"مرحباً بك {user.get_display_name()}! 🎉")
                    )

                    # Redirect to next or home
                    next_url = request.GET.get("next", "main:home")
                    return redirect(next_url)
                else:
                    messages.error(request, _("حسابك معلق. يرجى التواصل مع الدعم."))
            else:
                messages.error(request, _("حسابك غير مفعل. يرجى تفعيل حسابك أولاً."))
        else:
            messages.error(request, _("اسم المستخدم أو كلمة المرور غير صحيحة"))

    return render(request, "pages/login.html")


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    User registration view
    """
    if request.user.is_authenticated:
        return redirect("main:home")

    if request.method == "POST":
        # Get form data
        username = request.POST.get("username", "").strip().lower()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        profile_type = request.POST.get("profile_type", "default")
        terms_accepted = request.POST.get("terms_accepted")

        # Validation
        errors = []

        if not username:
            errors.append(_("اسم المستخدم مطلوب"))
        elif len(username) < 3:
            errors.append(_("اسم المستخدم يجب أن يكون 3 أحرف على الأقل"))
        elif User.objects.filter(username=username).exists():
            errors.append(_("اسم المستخدم موجود بالفعل"))

        if not email:
            errors.append(_("البريد الإلكتروني مطلوب"))
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors.append(_("البريد الإلكتروني مسجل بالفعل"))
            except ValidationError:
                errors.append(_("البريد الإلكتروني غير صالح"))

        if not password:
            errors.append(_("كلمة المرور مطلوبة"))
        elif len(password) < 8:
            errors.append(_("كلمة المرور يجب أن تكون 8 أحرف على الأقل"))

        if password != password2:
            errors.append(_("كلمات المرور غير متطابقة"))

        if not terms_accepted:
            errors.append(_("يجب الموافقة على الشروط والأحكام"))

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request, "accounts/register.html", {"form_data": request.POST}
            )

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                profile_type=profile_type,
            )

            # Auto login after registration
            login(request, user)

            messages.success(
                request, _("مرحباً بك في إدريسي مارت! 🎉 تم إنشاء حسابك بنجاح")
            )
            return redirect("main:home")

        except Exception:
            messages.error(
                request, _("حدث خطأ أثناء إنشاء الحساب. يرجى المحاولة مرة أخرى.")
            )
            return render(request, "pages/register.html", {"form_data": request.POST})

    return render(request, "pages/register.html")


@login_required
def logout_view(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, _("تم تسجيل الخروج بنجاح. نراك قريباً! 👋"))
    return redirect("accounts:login")


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
