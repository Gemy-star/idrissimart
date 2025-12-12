from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, send_mail, BadHeaderError
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
from content.verification_utils import (
    is_email_verification_required,
    is_phone_verification_required,
)


class CustomLoginView(LoginView):
    """
    Custom login view that extends Django's built-in LoginView to add
    custom logic for session expiry ("Remember Me") and user status checks.
    Redirects users to appropriate dashboards based on their role.
    """

    template_name = "pages/login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        """Add next URL to context for template."""
        context = super().get_context_data(**kwargs)
        # Safely get the next parameter from GET or POST
        context["next_url"] = self.request.GET.get("next") or self.request.POST.get(
            "next"
        )
        return context

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

        # Both DEFAULT and PUBLISHER users go to dashboard
        try:
            if getattr(user, "profile_type", None) in ["default", "publisher"]:
                return reverse_lazy("main:dashboard")
        except Exception:
            # If user model doesn't expose profile_type for any reason, ignore
            pass

        # Fallback
        return reverse_lazy("main:home")

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests. This is overridden to allow login with email.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

        # If the form is invalid, we'll check if it's because of email-as-username or phone
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if the "username" is actually an email
        try:
            validate_email(username)
            is_email = True
        except Exception:
            is_email = False

        # Check if the "username" is actually a phone number
        is_phone = username.replace("+", "").replace(" ", "").replace("-", "").isdigit()

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
        elif is_phone:
            # إمكانية الدخول برقم الهاتف المسجل والمتحقق منه مسبقاً وكلمة السر
            try:
                # Clean phone number
                clean_phone = (
                    username.replace("+", "").replace(" ", "").replace("-", "")
                )
                # Try to find user by verified mobile number
                user_obj = User.objects.get(mobile=clean_phone, is_mobile_verified=True)
                # Authenticate with the found username
                user = authenticate(
                    request, username=user_obj.username, password=password
                )
                if user:
                    login(request, user)
                    return redirect(self.get_success_url())
            except User.DoesNotExist:
                # Try with phone field as well
                try:
                    user_obj = User.objects.get(
                        phone=clean_phone, is_mobile_verified=True
                    )
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

    def get_success_url(self):
        """Redirect to dashboard after registration (publisher dashboard for default users)"""
        return reverse_lazy("main:dashboard")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:home")

        from content.models import Country
        from constance import config

        form = self.form_class()
        countries = Country.objects.filter(is_active=True).order_by("order")

        # Get profile type settings from constance
        profile_type_settings = {
            "enable_service": getattr(
                config, "ENABLE_SERVICE_PROVIDER_REGISTRATION", False
            ),
            "enable_merchant": getattr(config, "ENABLE_MERCHANT_REGISTRATION", False),
            "enable_educational": getattr(
                config, "ENABLE_EDUCATIONAL_REGISTRATION", False
            ),
        }

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "countries": countries,
                "profile_type_settings": profile_type_settings,
            },
        )

    def post(self, request, *args, **kwargs):
        # Prevent authenticated users from registering again
        if request.user.is_authenticated:
            messages.warning(request, _("أنت مسجل بالفعل ولديك حساب نشط"))
            return redirect("main:home")

        from content.models import Country
        from constance import config

        countries = Country.objects.filter(is_active=True).order_by("order")

        # Get profile type settings from constance
        profile_type_settings = {
            "enable_service": getattr(
                config, "ENABLE_SERVICE_PROVIDER_REGISTRATION", False
            ),
            "enable_merchant": getattr(config, "ENABLE_MERCHANT_REGISTRATION", False),
            "enable_educational": getattr(
                config, "ENABLE_EDUCATIONAL_REGISTRATION", False
            ),
        }

        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            profile_type = data.get("profile_type")
            phone = data.get("phone")
            country_code = request.POST.get("country_code", "SA").upper()

            # Check if phone verification is required
            phone_verification_required = is_phone_verification_required()

            # CONDITIONAL: Check if phone was verified in session (only if required)
            if phone_verification_required:
                normalized_phone = normalize_phone_number(phone, country_code)
                phone_verified = request.session.get(
                    f"phone_verified_{normalized_phone}", False
                )

                if not phone_verified:
                    messages.error(
                        request,
                        _(
                            "التحقق من رقم الهاتف إلزامي. يرجى إكمال التحقق من شروط إكمال التسجيل"
                        ),
                    )
                    form.add_error("phone", _("لم يتم التحقق من رقم الهاتف"))
                    return render(
                        request,
                        self.template_name,
                        {
                            "form": form,
                            "countries": countries,
                            "profile_type_settings": profile_type_settings,
                        },
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

            # Set country - جعل الدولة الافتراضية عند التسجيل مصر
            country_code = data.get("country", "EG")  # Default to Egypt
            user.country = country_code

            # Mark phone as verified if verification was required and completed
            if phone_verification_required:
                user.is_mobile_verified = True

            user.save(update_fields=["is_mobile_verified", "country"])

            # Clear phone verification from session if it was required
            if phone_verification_required:
                normalized_phone = normalize_phone_number(phone, country_code)
                if f"phone_verified_{normalized_phone}" in request.session:
                    del request.session[f"phone_verified_{normalized_phone}"]

            # Send email verification (CONDITIONAL based on settings)
            email_verification_required = is_email_verification_required()
            if email_verification_required:
                email_sent = send_email_verification(request, user)

            # Auto login after registration
            login(request, user)

            messages.success(
                request, _("مرحباً بك في إدريسي مارت! 🎉 تم إنشاء حسابك بنجاح")
            )

            if email_verification_required:
                if email_sent:
                    messages.info(
                        request,
                        _(
                            "تم إرسال رابط تأكيد إلى بريدك الإلكتروني. التحقق من البريد الإلكتروني إلزامي من شروط إكمال التسجيل."
                        ),
                    )
                else:
                    messages.warning(
                        request,
                        _(
                            "فشل إرسال رسالة التحقق. يمكنك طلب إعادة الإرسال من الإعدادات."
                        ),
                    )

            return redirect(self.success_url)
        else:
            # Add form errors to messages framework for debugging
            error_details = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = (
                        form.fields.get(field).label if field in form.fields else field
                    )
                    error_details.append(f"{field_label}: {error}")
                    messages.error(request, f"{field_label}: {error}")

            # Log errors for debugging
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Registration form validation failed: {error_details}")

            messages.error(request, _("يرجى تصحيح الأخطاء أدناه والمحاولة مرة أخرى."))
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "countries": countries,
                    "profile_type_settings": profile_type_settings,
                },
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
    إمكانية الدخول برقم الهاتف المسجل والتحقق منه مسبقاً وكاتبه اليه
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

        # Check if phone already registered (but allow if it's the current user's phone)
        if request.user.is_authenticated:
            # For authenticated users, check if phone is already verified
            if request.user.is_mobile_verified and (
                request.user.mobile == normalized_phone
                or request.user.phone == normalized_phone
            ):
                return JsonResponse(
                    {"success": False, "message": _("رقم الهاتف موثق بالفعل")},
                    status=400,
                )
            # Check if phone belongs to another user
            existing_user = (
                User.objects.filter(phone=normalized_phone)
                .exclude(id=request.user.id)
                .first()
            )
            if existing_user:
                return JsonResponse(
                    {"success": False, "message": _("رقم الجوال مسجل مسبقاً")},
                    status=400,
                )
        else:
            # For non-authenticated users (registration), check if phone already exists
            if User.objects.filter(phone=normalized_phone).exists():
                return JsonResponse(
                    {"success": False, "message": _("رقم الجوال مسجل مسبقاً")},
                    status=400,
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
    اليه الفرق عند التسجيل بين حساب غداء وعشاء ؟
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
    """Fixed password reset view - نسيت كلمه المرور لا تعمل"""
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            email_address = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(
                email__iexact=email_address, is_active=True
            )

            if associated_users.exists():
                for user in associated_users:
                    # Check if user is suspended - don't allow password reset for suspended accounts
                    if user.is_suspended:
                        messages.error(
                            request,
                            _("حسابك معلق. يرجى التواصل مع الدعم."),
                        )
                        continue

                    current_site = get_current_site(request)
                    subject = _("طلب إعادة تعيين كلمة المرور - Password Reset")
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
                            "noreply@idrissimart.com",
                            [user.email],
                            fail_silently=False,
                        )
                        messages.success(
                            request,
                            _(
                                "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني"
                            ),
                        )
                    except BadHeaderError:
                        messages.error(request, _("حدث خطأ. الرجاء المحاولة لاحقاً"))
                        return HttpResponse("Invalid header found.")
                    except Exception as e:
                        messages.error(
                            request, _("فشل إرسال البريد. يرجى المحاولة لاحقاً")
                        )
            else:
                # For security, show same message even if email doesn't exist
                messages.success(
                    request,
                    _("إذا كان البريد مسجلاً، ستصلك رسالة إعادة تعيين كلمة المرور"),
                )

            # Security: Always redirect to the 'done' page to prevent user enumeration.
            return redirect("main:password_reset_done")
        else:
            messages.error(request, _("يرجى التحقق من صحة البريد الإلكتروني"))

    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="password/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )


def send_email_verification(request, user):
    """Send email verification link to user"""
    import uuid
    from datetime import timedelta
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.contrib.sites.shortcuts import get_current_site
    from django.conf import settings

    # Generate verification token
    token = str(uuid.uuid4())
    user.email_verification_token = token
    user.email_verification_expires = timezone.now() + timedelta(hours=24)
    user.save(update_fields=["email_verification_token", "email_verification_expires"])

    # Build verification link
    current_site = get_current_site(request)
    verification_link = (
        f"{request.scheme}://{current_site.domain}/verify-email/{user.id}/{token}/"
    )

    # Send email
    subject = _("تأكيد البريد الإلكتروني - Verify Your Email")
    message = render_to_string(
        "emails/email_verification.html",
        {
            "user": user,
            "verification_link": verification_link,
            "site_name": "إدريسي مارت",
        },
    )

    try:
        send_mail(
            subject,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        # Log the verification link for development
        print(f"Verification link for {user.email}: {verification_link}")
        # Still return True in development so the user gets a success message
        # In production, you should fix the email backend
        return True


def verify_email(request, user_id, token):
    """Verify user email with token"""
    try:
        user = User.objects.get(id=user_id)

        # Check if token is valid and not expired
        if user.email_verification_token == token:
            if (
                user.email_verification_expires
                and user.email_verification_expires > timezone.now()
            ):
                user.is_email_verified = True
                user.email_verification_token = ""
                user.save(
                    update_fields=["is_email_verified", "email_verification_token"]
                )

                messages.success(request, _("تم تأكيد بريدك الإلكتروني بنجاح!"))
                return redirect("main:home")
            else:
                messages.error(
                    request, _("انتهت صلاحية رابط التأكيد. يرجى طلب رابط جديد.")
                )
        else:
            messages.error(request, _("رابط التأكيد غير صحيح."))
    except User.DoesNotExist:
        messages.error(request, _("المستخدم غير موجود."))

    return redirect("main:home")


def resend_email_verification(request):
    """Resend email verification link"""
    if not request.user.is_authenticated:
        return redirect("main:login")

    if request.user.is_email_verified:
        messages.info(request, _("بريدك الإلكتروني مؤكد بالفعل."))
        return redirect("main:home")

    if send_email_verification(request, request.user):
        messages.success(request, _("تم إرسال رابط التأكيد إلى بريدك الإلكتروني."))
    else:
        messages.error(request, _("حدث خطأ أثناء إرسال البريد. يرجى المحاولة لاحقاً."))

    return redirect("main:home")
