from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView
from django.utils import timezone
from datetime import timedelta
import json

from .forms import RegistrationForm
from .models import User
from .utils import (
    generate_verification_code,
    send_sms_verification_code,
    validate_phone_number,
    normalize_phone_number,
)


class CustomLoginView(LoginView):
    """
    Custom login view that extends Django's built-in LoginView to add
    custom logic for session expiry ("Remember Me") and user status checks.
    Redirects users to appropriate dashboards based on their role.
    """

    template_name = "pages/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Determine the redirect URL based on:
        1. 'next' parameter (highest priority) - with proper validation
        2. User role:
           - Superusers/Staff -> Admin Dashboard
           - Publisher profile -> Publisher Dashboard (My Ads)
           - Users with ads -> Publisher Dashboard (My Ads)
           - Others -> Home page
        """
        # First check if there's a 'next' parameter
        next_url = self.request.POST.get("next") or self.request.GET.get("next")

        if next_url:
            # Validate the next URL to prevent open redirect vulnerabilities
            from django.utils.http import url_has_allowed_host_and_scheme
            from django.core.exceptions import ValidationError

            try:
                # Additional validation: ensure URL doesn't contain dangerous patterns
                if url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={self.request.get_host()},
                    require_https=self.request.is_secure(),
                ):
                    # Ensure it's not a logout URL to prevent redirect loops
                    if not next_url.startswith("/logout"):
                        return next_url
            except (ValidationError, ValueError):
                # If validation fails, fall through to role-based redirect
                pass

        user = self.request.user

        # Admins
        if user.is_superuser or user.is_staff:
            return reverse_lazy("main:admin_dashboard")

        # Publisher profile type
        try:
            if getattr(user, "profile_type", None) == "publisher":
                return reverse_lazy("main:my_ads")
        except Exception:
            # If user model doesn't expose profile_type for any reason, ignore
            pass

        # Users who have created ads
        from .models import ClassifiedAd

        if ClassifiedAd.objects.filter(user=user).exists():
            return reverse_lazy("main:my_ads")

        # Fallback
        return reverse_lazy("main:home")

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests. This is overridden to allow login with email.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

        # If the form is invalid, we'll check if it's because of email-as-username
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if the "username" is actually an email
        try:
            validate_email(username)
            is_email = True
        except Exception:
            is_email = False

        if is_email:
            try:
                user_obj = User.objects.get(email__iexact=username)
                # Authenticate with the found username
                user = authenticate(
                    request, username=user_obj.username, password=password
                )
                if user:
                    login(request, user)
                    return redirect(self.get_success_url())
            except User.DoesNotExist:
                pass  # Fall through to the default form_invalid

        return self.form_invalid(form)

    def form_valid(self, form):
        """
        Called when the form is valid. Logs the user in and adds custom logic.
        """
        user = form.get_user()

        # Custom check for suspended users
        if user.is_suspended:
            messages.error(self.request, _("حسابك معلق. يرجى التواصل مع الدعم."))
            return self.form_invalid(form)

        # Log the user in
        login(self.request, user)

        # Merge session cart into user cart
        self.merge_session_cart(user)

        # Handle "Remember Me" functionality
        remember_me = self.request.POST.get("remember_me")

        # In local development, always keep session active
        from django.conf import settings

        if settings.DEBUG:
            # For local development, set longer session timeout
            self.request.session.set_expiry(86400)  # 1 day
        else:
            # Production behavior
            if not remember_me:
                self.request.session.set_expiry(0)  # Session expires on browser close
            else:
                self.request.session.set_expiry(1209600)  # 2 weeks

        # Log IP address
        user.last_login_ip = get_client_ip(self.request)
        user.save(update_fields=["last_login_ip"])

        # Custom welcome message based on role
        if user.is_superuser:
            messages.success(
                self.request,
                _(f"مرحباً بك في لوحة الإدارة، {user.get_display_name()}! 👨‍💼"),
            )
        else:
            messages.success(self.request, _(f"مرحباً بك {user.get_display_name()}! 🎉"))

        return super().form_valid(form)

    def merge_session_cart(self, user):
        """
        Merge guest session cart into authenticated user's cart after login
        """
        try:
            from main.models import Cart, CartItem, ClassifiedAd

            session_cart = self.request.session.get("cart", {})
            if not session_cart:
                return

            # Get or create user cart
            cart, _ = Cart.objects.get_or_create(user=user)

            # Merge each session cart item
            for ad_id_str, item_data in session_cart.items():
                try:
                    ad_id = int(ad_id_str)
                    ad = ClassifiedAd.objects.get(
                        id=ad_id,
                        status=ClassifiedAd.AdStatus.ACTIVE,
                        cart_enabled_by_admin=True,
                    )

                    # Get or create cart item
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        ad=ad,
                        defaults={"quantity": item_data.get("quantity", 1)},
                    )

                    if not created:
                        # Item already exists, add quantities
                        cart_item.quantity += item_data.get("quantity", 1)
                        cart_item.save()

                except (ValueError, ClassifiedAd.DoesNotExist):
                    continue

            # Clear session cart
            self.request.session["cart"] = {}
            self.request.session.modified = True

        except Exception as e:
            # Don't fail login if cart merge fails
            pass

    def form_invalid(self, form):
        """
        Adds a generic error message for invalid login attempts.
        """
        messages.error(self.request, _("اسم المستخدم أو كلمة المرور غير صحيحة"))
        return super().form_invalid(form)


class RegisterView(CreateView):
    """
    Class-based view for user registration.
    """

    model = User
    form_class = RegistrationForm
    template_name = "pages/register.html"
    success_url = reverse_lazy("main:home")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:home")

        from content.models import Country

        form = self.form_class()
        countries = Country.objects.filter(is_active=True).order_by("order")

        return render(
            request, self.template_name, {"form": form, "countries": countries}
        )

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:home")

        from content.models import Country

        countries = Country.objects.filter(is_active=True).order_by("order")

        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            profile_type = data.get("profile_type")
            phone = data.get("phone")
            country_code = request.POST.get("country_code", "SA").upper()

            # Check if phone was verified in session
            normalized_phone = normalize_phone_number(phone, country_code)
            if not request.session.get(f"phone_verified_{normalized_phone}"):
                messages.error(request, _("يجب التحقق من رقم الجوال قبل إنشاء الحساب"))
                return render(
                    request, self.template_name, {"form": form, "countries": countries}
                )

            if profile_type == "service":
                user = User.objects.create_service_provider(
                    username=data.get("username"),
                    email=data.get("email"),
                    password=data.get("password"),
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    phone=data.get("phone"),
                    specialization=data.get("specialization"),
                    years_of_experience=(data.get("years_of_experience")),
                )
            elif profile_type == "merchant":
                user = User.objects.create_merchant(
                    username=data.get("username"),
                    email=data.get("email"),
                    password=data.get("password"),
                    company_name=data.get("company_name"),
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    phone=data.get("phone"),
                    tax_number=data.get("tax_number"),
                    commercial_register=data.get("commercial_register"),
                )
                if data.get("company_name_ar"):
                    user.company_name_ar = data.get("company_name_ar")
                    user.save(update_fields=["company_name_ar"])
            elif profile_type == "educational":
                user = User.objects.create_educational(
                    username=data.get("username"),
                    email=data.get("email"),
                    password=data.get("password"),
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    phone=data.get("phone"),
                    company_name=data.get("company_name"),
                )
                if data.get("company_name_ar"):
                    user.company_name_ar = data.get("company_name_ar")
                    user.save(update_fields=["company_name_ar"])
            else:
                user = User.objects.create_user(
                    username=data.get("username"),
                    email=data.get("email"),
                    password=data.get("password"),
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    phone=data.get("phone"),
                    profile_type=data.get("profile_type"),
                )

            # Mark phone as verified
            user.is_mobile_verified = True
            user.save(update_fields=["is_mobile_verified"])

            # Clear phone verification from session
            if f"phone_verified_{normalized_phone}" in request.session:
                del request.session[f"phone_verified_{normalized_phone}"]

            # Auto login after registration
            login(request, user)

            messages.success(
                request, _("مرحباً بك في إدريسي مارت! 🎉 تم إنشاء حسابك بنجاح")
            )
            return redirect(self.success_url)
        else:
            # Add form errors to messages framework
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
            messages.error(request, _("يرجى تصحيح الأخطاء أدناه والمحاولة مرة أخرى."))
            return render(
                request, self.template_name, {"form": form, "countries": countries}
            )


@login_required
def logout_view(request):
    """
    User logout view with support for 'next' parameter
    """
    # Check for next URL parameter
    next_url = request.POST.get("next") or request.GET.get("next")

    logout(request)
    messages.success(request, _("تم تسجيل الخروج بنجاح. نراك قريباً! 👋"))

    # Validate and redirect to next URL if provided
    if next_url:
        from django.utils.http import url_has_allowed_host_and_scheme

        if url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)

    return redirect("main:home")


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


@require_POST
def send_phone_verification_code(request):
    """
    Send verification code to phone number via SMS
    """
    try:
        data = json.loads(request.body)
        phone = data.get("phone", "").strip()
        country_code = data.get("country_code", "SA").upper()

        if not phone:
            return JsonResponse(
                {"success": False, "message": _("رقم الجوال مطلوب")}, status=400
            )

        # Validate phone format for the selected country
        if not validate_phone_number(phone, country_code):
            return JsonResponse(
                {"success": False, "message": _("رقم الجوال غير صحيح لهذه الدولة")},
                status=400,
            )

        # Normalize phone number based on country
        normalized_phone = normalize_phone_number(phone, country_code)

        # Check if phone already registered
        if User.objects.filter(phone=normalized_phone).exists():
            return JsonResponse(
                {"success": False, "message": _("رقم الجوال مسجل مسبقاً")}, status=400
            )

        # Generate verification code
        code = generate_verification_code()

        # Store code in session temporarily (valid for 10 minutes)
        request.session[f"phone_verification_{normalized_phone}"] = {
            "code": code,
            "expires": (timezone.now() + timedelta(minutes=10)).isoformat(),
            "attempts": 0,
        }

        # Send SMS
        if send_sms_verification_code(normalized_phone, code):
            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم إرسال رمز التحقق إلى رقم الجوال"),
                    "phone": normalized_phone,
                }
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("فشل إرسال رمز التحقق. الرجاء المحاولة لاحقاً"),
                },
                status=500,
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": _("بيانات غير صالحة")}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ. الرجاء المحاولة لاحقاً")},
            status=500,
        )


@require_POST
def verify_phone_code(request):
    """
    Verify the phone verification code entered by user
    """
    try:
        data = json.loads(request.body)
        phone = data.get("phone", "").strip()
        code = data.get("code", "").strip()
        country_code = data.get("country_code", "SA").upper()

        if not phone or not code:
            return JsonResponse(
                {"success": False, "message": _("الرجاء إدخال رقم الجوال ورمز التحقق")},
                status=400,
            )

        # Normalize phone based on country
        normalized_phone = normalize_phone_number(phone, country_code)

        # Get stored verification data
        session_key = f"phone_verification_{normalized_phone}"
        verification_data = request.session.get(session_key)

        if not verification_data:
            return JsonResponse(
                {"success": False, "message": _("لم يتم إرسال رمز تحقق لهذا الرقم")},
                status=400,
            )

        # Check expiry
        expires = timezone.datetime.fromisoformat(verification_data["expires"])
        if timezone.now() > expires:
            del request.session[session_key]
            return JsonResponse(
                {
                    "success": False,
                    "message": _("انتهت صلاحية رمز التحقق. الرجاء طلب رمز جديد"),
                },
                status=400,
            )

        # Check attempts (max 5)
        if verification_data.get("attempts", 0) >= 5:
            del request.session[session_key]
            return JsonResponse(
                {"success": False, "message": _("تم تجاوز عدد المحاولات المسموحة")},
                status=400,
            )

        # Verify code
        if code == verification_data["code"]:
            # Mark as verified in session
            request.session[f"phone_verified_{normalized_phone}"] = True
            del request.session[session_key]

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم التحقق من رقم الجوال بنجاح"),
                    "verified": True,
                }
            )
        else:
            # Increment attempts
            verification_data["attempts"] = verification_data.get("attempts", 0) + 1
            request.session[session_key] = verification_data

            remaining = 5 - verification_data["attempts"]
            return JsonResponse(
                {
                    "success": False,
                    "message": _("رمز التحقق غير صحيح. المحاولات المتبقية: {}").format(
                        remaining
                    ),
                },
                status=400,
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": _("بيانات غير صالحة")}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ. الرجاء المحاولة لاحقاً")},
            status=500,
        )


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            email_address = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(email__iexact=email_address)
            if associated_users.exists():
                for user in associated_users:
                    current_site = get_current_site(request)
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    context = {
                        "email": user.email,
                        "domain": current_site.domain,
                        "site_name": current_site.name,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "https" if request.is_secure() else "http",
                    }
                    email_body = render_to_string(email_template_name, context)
                    try:
                        send_mail(
                            subject,
                            email_body,
                            "noreply@idrissimart.com",  # Use a no-reply address from your domain
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
            # Security: Always redirect to the 'done' page to prevent user enumeration.
            return redirect("main:password_reset_done")

    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="password/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )
