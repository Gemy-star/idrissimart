"""
Email Service using SendGrid
Integrates with django-constance for dynamic configuration
"""

import logging
from typing import List, Optional

from constance import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails using SendGrid"""

    @staticmethod
    def is_enabled() -> bool:
        """Check if SendGrid email service is enabled"""
        return config.SENDGRID_ENABLED and bool(config.SENDGRID_API_KEY)

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
        """
        Send email using SendGrid

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional, auto-generated from HTML if not provided)
            from_email: Sender email (uses config if not provided)
            from_name: Sender name (uses config if not provided)
            reply_to: Reply-to email address
            attachments: List of attachments

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not EmailService.is_enabled():
            logger.warning("SendGrid email service is disabled")
            return False

        try:
            # Use configured values if not provided
            from_email = from_email or config.SENDGRID_FROM_EMAIL
            from_name = from_name or config.SENDGRID_FROM_NAME

            # Auto-generate text content if not provided
            if not text_content:
                text_content = strip_tags(html_content)

            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=f"{from_name} <{from_email}>",
                to=to_emails,
                reply_to=[reply_to] if reply_to else None,
            )
            email.attach_alternative(html_content, "text/html")

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    email.attach(*attachment)

            # Send email
            email.send()

            logger.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
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
        """
        Send email using Django template

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            template_name: Path to email template
            context: Template context dictionary
            from_email: Sender email (uses config if not provided)
            from_name: Sender name (uses config if not provided)
            reply_to: Reply-to email address

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Render template
            html_content = render_to_string(template_name, context)

            # Send email
            return EmailService.send_email(
                to_emails=to_emails,
                subject=subject,
                html_content=html_content,
                from_email=from_email,
                from_name=from_name,
                reply_to=reply_to,
            )

        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            return False

    @staticmethod
    def send_otp_email(email: str, otp_code: str, user_name: str = "") -> bool:
        """
        Send OTP verification email

        Args:
            email: Recipient email address
            otp_code: OTP code
            user_name: User's name (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
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
        """
        Send welcome email to new user

        Args:
            email: Recipient email address
            user_name: User's name

        Returns:
            bool: True if email sent successfully, False otherwise
        """
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
        """
        Send password reset email

        Args:
            email: Recipient email address
            reset_link: Password reset link
            user_name: User's name (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
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
        """
        Send ad approval notification email

        Args:
            email: Recipient email address
            ad_title: Ad title
            ad_url: URL to the ad
            user_name: User's name (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
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
        """
        Send saved search notification email

        Args:
            email: Recipient email address
            search_name: Name of the saved search
            ads: List of new ads matching the search
            search_url: URL to view the search results
            user_name: User's name (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
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
