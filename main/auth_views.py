from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from django.views.generic.edit import CreateView

from .forms import RegistrationForm
from .models import User


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
        Determine the redirect URL based on user role:
        - Superusers/Staff -> Admin Dashboard
        - Publisher profile -> Publisher Dashboard (My Ads)
        - Users with ads -> Publisher Dashboard (My Ads)
        - Others -> Home page
        """
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

        # Handle "Remember Me" functionality
        remember_me = self.request.POST.get("remember_me")
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
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:home")

        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            profile_type = data.get("profile_type")

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
            return render(request, self.template_name, {"form": form})


@login_required
def logout_view(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, _("تم تسجيل الخروج بنجاح. نراك قريباً! 👋"))
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
