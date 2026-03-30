"""
Email Service using Django's built-in email backend.
"""

import logging
from typing import List, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails using Django's email backend."""

    @staticmethod
    def send_email(
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List] = None,
    ) -> bool:
        try:
            sender_email = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@idrissimart.com")
            if from_name:
                sender = f"{from_name} <{sender_email}>"
            else:
                sender = sender_email

            plain_text = text_content or strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=sender,
                to=to_emails,
                reply_to=[reply_to] if reply_to else None,
            )
            email.attach_alternative(html_content, "text/html")

            if attachments:
                for attachment in attachments:
                    email.attach(*attachment)

            email.send()
            logger.info("Email sent successfully to %s", ", ".join(to_emails))
            return True

        except Exception as e:
            logger.error("Failed to send email: %s", str(e))
            return False

    @staticmethod
    def send_template_email(
        to_emails: List[str],
        subject: str,
        template_name: str,
        context: dict,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> bool:
        try:
            html_content = render_to_string(template_name, context)
            return EmailService.send_email(
                to_emails=to_emails,
                subject=subject,
                html_content=html_content,
                from_email=from_email,
                from_name=from_name,
                reply_to=reply_to,
            )
        except Exception as e:
            logger.error("Failed to send template email: %s", str(e))
            return False

    @staticmethod
    def send_otp_email(email: str, otp_code: str, user_name: str = "") -> bool:
        from constance import config

        subject = f"{config.SITE_NAME} - رمز التحقق"
        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "otp_code": otp_code,
            "expiry_minutes": config.OTP_EXPIRY_MINUTES,
        }
        return EmailService.send_template_email(
            to_emails=[email],
            subject=subject,
            template_name="emails/otp_verification.html",
            context=context,
        )

    @staticmethod
    def send_welcome_email(email: str, user_name: str) -> bool:
        from constance import config

        subject = f"مرحباً بك في {config.SITE_NAME}"
        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "site_url": config.SITE_URL,
        }
        return EmailService.send_template_email(
            to_emails=[email],
            subject=subject,
            template_name="emails/welcome.html",
            context=context,
        )

    @staticmethod
    def send_password_reset_email(
        email: str, reset_link: str, user_name: str = ""
    ) -> bool:
        from constance import config

        subject = f"{config.SITE_NAME} - إعادة تعيين كلمة المرور"
        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "reset_link": reset_link,
        }
        return EmailService.send_template_email(
            to_emails=[email],
            subject=subject,
            template_name="emails/password_reset.html",
            context=context,
        )

    @staticmethod
    def send_ad_approved_email(
        email: str, ad_title: str, ad_url: str, user_name: str = ""
    ) -> bool:
        from constance import config

        subject = config.AD_APPROVAL_EMAIL_SUBJECT.format(ad_title=ad_title)
        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "ad_title": ad_title,
            "ad_url": ad_url,
        }
        return EmailService.send_template_email(
            to_emails=[email],
            subject=subject,
            template_name="emails/ad_approved.html",
            context=context,
            from_email=config.AD_APPROVAL_FROM_EMAIL,
        )

    @staticmethod
    def send_saved_search_notification(
        email: str, search_name: str, ads: list, search_url: str, user_name: str = ""
    ) -> bool:
        from constance import config

        subject = config.SAVED_SEARCH_EMAIL_SUBJECT.format(search_name=search_name)
        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "search_name": search_name,
            "ads": ads,
            "search_url": search_url,
        }
        return EmailService.send_template_email(
            to_emails=[email],
            subject=subject,
            template_name="emails/saved_search_notification.html",
            context=context,
            from_email=config.SAVED_SEARCH_FROM_EMAIL,
        )
