"""
Background tasks for Newsletter using Django-Q2
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_newsletter_confirmation_email(newsletter_id):
    """
    Send confirmation email to newly subscribed newsletter user
    
    Args:
        newsletter_id: ID of the Newsletter model instance
    """
    try:
        from .models import Newsletter

        newsletter = Newsletter.objects.get(id=newsletter_id)

        subject = _("تأكيد الاشتراك في النشرة البريدية - idrissimart")
        # Create email context
        context = {
            "email": newsletter.email,
            "created_at": newsletter.created_at,
            "site_name": getattr(
                settings, "SITE_NAME", "Idrissi Smart"
            ),
        }

        # HTML email body
        html_message = render_to_string(
            "email/newsletter_confirmation.html", context
        )
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[newsletter.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Newsletter confirmation email sent to {newsletter.email}")

    except Exception as e:
        logger.error(
            f"Error sending newsletter confirmation email: {e}",
            exc_info=True,
        )
        raise


def send_newsletter_to_all(content_subject, content_html, content_plain=None):
    """
    Send newsletter to all active subscribers via email
    
    Args:
        content_subject: Email subject
        content_html: HTML email body
        content_plain: Plain text email body (optional, will be stripped from HTML)
    
    Returns:
        dict with success status and number of sent emails
    """
    try:
        from .models import Newsletter

        # Get all active subscribers who want email
        subscribers = Newsletter.objects.filter(
            is_active=True,
            receive_email=True,
        )

        if not content_plain:
            content_plain = strip_tags(content_html)

        email_list = list(subscribers.values_list("email", flat=True))
        
        if not email_list:
            logger.warning("No active newsletter subscribers found")
            return {
                "success": True,
                "sent_count": 0,
                "message": "No active subscribers found",
            }

        # Send emails - using BCC to protect subscriber privacy
        send_mail(
            subject=content_subject,
            message=content_plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Main recipient
            bcc=email_list,  # Hidden recipients for privacy
            html_message=content_html,
            fail_silently=False,
        )

        # Update last_notification_sent for all subscribers
        from django.utils import timezone

        subscribers.update(last_notification_sent=timezone.now())

        logger.info(f"Newsletter sent to {len(email_list)} subscribers")

        return {
            "success": True,
            "sent_count": len(email_list),
            "message": f"Newsletter sent to {len(email_list)} subscribers",
        }

    except Exception as e:
        logger.error(
            f"Error sending newsletter to all subscribers: {e}",
            exc_info=True,
        )
        return {
            "success": False,
            "sent_count": 0,
            "message": str(e),
        }


def send_sms_newsletter_to_all(content_message):
    """
    Send SMS newsletter to all active subscribers via SMS
    
    Note: This requires configuring an SMS provider (Twilio, AWS SNS, etc.)
    
    Args:
        content_message: SMS message body (keep under 160 characters for single SMS)
    
    Returns:
        dict with success status and number of sent messages
    """
    try:
        from .models import Newsletter

        # Get all active subscribers who want SMS
        subscribers = Newsletter.objects.filter(
            is_active=True,
            receive_sms=True,
            phone__isnull=False,
        ).exclude(phone="")

        if not subscribers.exists():
            logger.warning("No active SMS newsletter subscribers found")
            return {
                "success": True,
                "sent_count": 0,
                "message": "No active SMS subscribers found",
            }

        # Check if SMS service is configured
        sms_provider = getattr(settings, "SMS_PROVIDER", None)
        
        if not sms_provider:
            logger.warning(
                "SMS provider not configured. "
                "Set SMS_PROVIDER in settings to enable SMS sending."
            )
            return {
                "success": False,
                "sent_count": 0,
                "message": "SMS provider not configured",
            }

        sent_count = 0

        # Example: Using Twilio (you would need to install and configure it)
        if sms_provider.lower() == "twilio":
            try:
                from twilio.rest import Client

                account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
                auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
                from_number = getattr(settings, "TWILIO_FROM_NUMBER", "")

                if not all([account_sid, auth_token, from_number]):
                    logger.error("Twilio credentials not fully configured")
                    return {
                        "success": False,
                        "sent_count": 0,
                        "message": "Twilio credentials not configured",
                    }

                client = Client(account_sid, auth_token)

                for subscriber in subscribers:
                    try:
                        client.messages.create(
                            body=content_message,
                            from_=from_number,
                            to=subscriber.phone,
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error(
                            f"Error sending SMS to {subscriber.phone}: {e}"
                        )

                # Update last_notification_sent
                from django.utils import timezone

                subscribers.update(last_notification_sent=timezone.now())

                logger.info(f"SMS newsletter sent to {sent_count} subscribers")

                return {
                    "success": True,
                    "sent_count": sent_count,
                    "message": f"SMS newsletter sent to {sent_count} subscribers",
                }

            except ImportError:
                logger.error("Twilio library not installed")
                return {
                    "success": False,
                    "sent_count": 0,
                    "message": "Twilio library not installed",
                }

        else:
            logger.warning(f"Unknown SMS provider: {sms_provider}")
            return {
                "success": False,
                "sent_count": 0,
                "message": f"Unknown SMS provider: {sms_provider}",
            }

    except Exception as e:
        logger.error(
            f"Error sending SMS newsletter: {e}",
            exc_info=True,
        )
        return {
            "success": False,
            "sent_count": 0,
            "message": str(e),
        }


def send_newsletter_scheduled_task():
    """
    Scheduled task to send periodic newsletters
    This should be called via Django-Q2 scheduler
    (Configure in settings.py Q_CLUSTER with scheduled_tasks)
    """
    logger.info("Starting scheduled newsletter task")

    subject = getattr(
        settings,
        "NEWSLETTER_SCHEDULED_SUBJECT",
        _("نشرة إدريسي مارت الأسبوعية"),
    )
    html_message = getattr(
        settings,
        "NEWSLETTER_SCHEDULED_HTML",
        "<h2>أهلا بك في النشرة الأسبوعية</h2><p>تابع أحدث العروض والإعلانات الجديدة.</p>",
    )
    plain_message = getattr(settings, "NEWSLETTER_SCHEDULED_PLAIN", None)

    result = send_newsletter_to_all(
        content_subject=subject,
        content_html=html_message,
        content_plain=plain_message,
    )

    if not result.get("success"):
        logger.error("Scheduled email newsletter failed: %s", result.get("message"))
    else:
        logger.info(
            "Scheduled email newsletter sent to %s subscribers",
            result.get("sent_count", 0),
        )

    return result


def send_newsletter_sms_scheduled_task():
    """Scheduled SMS newsletter task using default message from settings."""
    logger.info("Starting scheduled SMS newsletter task")

    sms_message = getattr(
        settings,
        "NEWSLETTER_SCHEDULED_SMS",
        "أحدث عروض إدريسي مارت متاحة الآن. زر الموقع لمزيد من التفاصيل.",
    )

    result = send_sms_newsletter_to_all(content_message=sms_message)

    if not result.get("success"):
        logger.error("Scheduled SMS newsletter failed: %s", result.get("message"))
    else:
        logger.info(
            "Scheduled SMS newsletter sent to %s subscribers",
            result.get("sent_count", 0),
        )

    return result
