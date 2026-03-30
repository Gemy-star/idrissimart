import logging

from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_email(to_email, subject, html_content, text_content=None):
    """
    Send an email via Django's email backend.
    Returns True on success, False on failure.
    """
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@idrissimart.com")
    plain_text = text_content or strip_tags(html_content)

    try:
        django_send_mail(
            subject,
            plain_text,
            from_email,
            [to_email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info("Email sent to %s", to_email)
        return True
    except Exception as exc:
        logger.error("Email send failed for %s: %s", to_email, exc)
        return False


def send_password_reset_email(request, user, uid, token):
    """Send password reset email to user."""
    from django.contrib.sites.shortcuts import get_current_site

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
    """Send email verification link to user."""
    context = {
        "user": user,
        "verification_link": verification_link,
        "site_name": "إدريسي مارت",
    }

    html_content = render_to_string("emails/email_verification.html", context)
    subject = "تأكيد البريد الإلكتروني - Verify Your Email"

    return send_email(user.email, subject, html_content)
