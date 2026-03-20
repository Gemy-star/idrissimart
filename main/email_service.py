import logging

from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _get_sendgrid_config():
    """Read SendGrid config from constance, falling back to Django settings."""
    from django.conf import settings

    api_key = ""
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@idrissimart.com")
    from_name = "إدريسي مارت"
    enabled = True

    try:
        from constance import config

        api_key = getattr(config, "SENDGRID_API_KEY", "") or getattr(settings, "SENDGRID_API_KEY", "") or ""
        from_email = getattr(config, "SENDGRID_FROM_EMAIL", "") or from_email
        from_name = getattr(config, "SENDGRID_FROM_NAME", "") or from_name
        enabled = getattr(config, "SENDGRID_ENABLED", True)
    except Exception:
        api_key = getattr(settings, "SENDGRID_API_KEY", "") or ""

    return api_key, from_email, from_name, enabled


def send_email(to_email, subject, html_content, text_content=None):
    """
    Send an email via SendGrid using API key and sender info from django-constance.
    Falls back to Django's email backend if SendGrid is not configured.

    Returns True on success, False on failure.
    """
    api_key, from_email, from_name, enabled = _get_sendgrid_config()

    if not enabled:
        logger.info("SendGrid is disabled. Skipping email to %s", to_email)
        return False

    plain_text = text_content or strip_tags(html_content)

    if api_key:
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, From, To, Content

            message = Mail()
            message.from_email = From(from_email, from_name)
            message.to = To(to_email)
            message.subject = subject
            message.content = [
                Content("text/plain", plain_text),
                Content("text/html", html_content),
            ]

            sg = SendGridAPIClient(api_key)
            response = sg.send(message)

            if response.status_code in (200, 201, 202):
                logger.info("SendGrid email sent to %s (status %s)", to_email, response.status_code)
                return True
            else:
                logger.error("SendGrid returned status %s for email to %s", response.status_code, to_email)
        except Exception as exc:
            logger.error("SendGrid email failed for %s: %s", to_email, exc)
            # Fall through to Django email backend

    # Fallback: Django email backend
    try:
        from django.core.mail import send_mail as django_send_mail

        django_send_mail(
            subject,
            plain_text,
            from_email,
            [to_email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info("Fallback email sent to %s via Django backend", to_email)
        return True
    except Exception as exc:
        logger.error("Fallback email send failed for %s: %s", to_email, exc)
        return False


def send_password_reset_email(request, user, uid, token):
    """Send password reset email to user via SendGrid."""
    from django.contrib.sites.shortcuts import get_current_site
    from django.conf import settings

    current_site = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"

    context = {
        "user": user,
        "uid": uid,
        "token": token,
        "domain": current_site.domain,
        "site_name": current_site.name,
        "protocol": protocol,
    }

    html_content = render_to_string("emails/password_reset_email.html", context)
    text_content = render_to_string("password/password_reset_email.txt", context)

    subject = "طلب إعادة تعيين كلمة المرور - Password Reset"

    success = send_email(user.email, subject, html_content, text_content)

    if settings.DEBUG:
        reset_link = f"{protocol}://{current_site.domain}/reset/{uid}/{token}/"
        if not success:
            logger.warning("Email send failed (DEBUG). Reset link for %s: %s", user.email, reset_link)
        print(f"\n{'='*60}")
        print(f"PASSWORD RESET LINK FOR: {user.email}")
        print(f"Link: {reset_link}")
        print(f"{'='*60}\n")

    return success


def send_verification_email(request, user, verification_link):
    """Send email verification link to user via SendGrid."""
    context = {
        "user": user,
        "verification_link": verification_link,
        "site_name": "إدريسي مارت",
    }

    html_content = render_to_string("emails/email_verification.html", context)
    subject = "تأكيد البريد الإلكتروني - Verify Your Email"

    return send_email(user.email, subject, html_content)
