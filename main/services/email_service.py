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
    def _render_db_template(template_key: str, context: dict, lang: str = "ar") -> Optional[tuple]:
        """
        Try to load a template from DB (EmailTemplate model).
        Returns (subject, html_body) tuple if found and active, else None.
        Language is determined by ``lang`` ("ar" or "en").
        """
        try:
            from main.models import EmailTemplate
            tmpl = EmailTemplate.get_template(template_key)
            if tmpl is None:
                return None
            subject = (tmpl.subject_ar if lang == "ar" else tmpl.subject) or tmpl.subject_ar or tmpl.subject
            body = (tmpl.body_ar if lang == "ar" else tmpl.body) or tmpl.body_ar or tmpl.body
            if not body:
                return None
            # Simple variable substitution: replace {{var}} with context values
            for key, value in context.items():
                body = body.replace(f"{{{{{key}}}}}", str(value))
                subject = subject.replace(f"{{{{{key}}}}}", str(value))
            return subject, body
        except Exception as e:
            logger.warning("DB email template lookup failed for key '%s': %s", template_key, e)
            return None

    @staticmethod
    def send_otp_email(email: str, otp_code: str, user_name: str = "") -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "otp_code": otp_code,
            "expiry_minutes": config.OTP_EXPIRY_MINUTES,
        }
        db = EmailService._render_db_template("otp_verification", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        subject = f"{config.SITE_NAME} - رمز التحقق"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/otp_verification.html", context=context,
        )

    @staticmethod
    def send_welcome_email(email: str, user_name: str) -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "site_url": config.SITE_URL,
        }
        db = EmailService._render_db_template("welcome", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        subject = f"مرحباً بك في {config.SITE_NAME}"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/welcome.html", context=context,
        )

    @staticmethod
    def send_password_reset_email(
        email: str, reset_link: str, user_name: str = ""
    ) -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "reset_link": reset_link,
        }
        db = EmailService._render_db_template("password_reset", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        subject = f"{config.SITE_NAME} - إعادة تعيين كلمة المرور"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/password_reset.html", context=context,
        )

    @staticmethod
    def send_ad_approved_email(
        email: str, ad_title: str, ad_url: str, user_name: str = ""
    ) -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "ad_title": ad_title,
            "ad_url": ad_url,
        }
        db = EmailService._render_db_template("ad_approved", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(
                to_emails=[email], subject=subject, html_content=html_content,
                from_email=config.AD_APPROVAL_FROM_EMAIL,
            )

        subject = config.AD_APPROVAL_EMAIL_SUBJECT.format(ad_title=ad_title)
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/ad_approved.html", context=context,
            from_email=config.AD_APPROVAL_FROM_EMAIL,
        )

    @staticmethod
    def send_email_verification_email(email: str, verification_link: str, user_name: str = "") -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "verification_link": verification_link,
        }
        db = EmailService._render_db_template("email_verification", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        subject = f"{config.SITE_NAME} - تأكيد البريد الإلكتروني"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/email_verification.html", context=context,
        )

    @staticmethod
    def send_ad_rejected_email(email: str, ad_title: str, reject_reason: str = "", user_name: str = "") -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "ad_title": ad_title,
            "reject_reason": reject_reason,
            "site_url": config.SITE_URL,
        }
        db = EmailService._render_db_template("ad_rejected", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        # Fallback: simple plain HTML (no dedicated file template)
        subject = f"{config.SITE_NAME} - إعلانك بحاجة إلى مراجعة"
        html_content = (
            f"<p>مرحباً {user_name}،</p>"
            f"<p>نأسف لإعلامك بأن إعلانك <strong>{ad_title}</strong> لم يتم قبوله.</p>"
            + (f"<p>السبب: {reject_reason}</p>" if reject_reason else "")
            + f"<p>يمكنك تعديل الإعلان وإعادة تقديمه. فريق {config.SITE_NAME}</p>"
        )
        return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

    @staticmethod
    def send_order_created_email(email: str, order, user_name: str = "") -> bool:
        from constance import config
        from django.conf import settings

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "order_number": str(order.order_number),
            "order_total": str(order.total_amount if hasattr(order, "total_amount") else ""),
            "site_url": getattr(settings, "SITE_URL", config.SITE_URL),
        }
        db = EmailService._render_db_template("order_created", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        subject = f"{config.SITE_NAME} - تأكيد الطلب #{order.order_number}"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/order_created.html",
            context={"order": order, "user": order.user, "items": order.items.all(),
                     "site_url": context["site_url"], "site_name": config.SITE_NAME},
        )

    @staticmethod
    def send_order_status_update_email(email: str, order, user_name: str = "") -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "order_number": str(order.order_number),
            "order_status": str(order.get_status_display()),
            "site_url": config.SITE_URL,
        }
        db = EmailService._render_db_template("order_status_update", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        currency = "ج.م"
        try:
            first_item = order.items.first()
            if first_item and first_item.ad and first_item.ad.country:
                currency = first_item.ad.country.currency_symbol
        except Exception:
            pass

        subject = f"{config.SITE_NAME} - تحديث حالة الطلب #{order.order_number}"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/order_status_update.html",
            context={"order": order, "currency": currency,
                     "site_name": config.SITE_NAME, "site_url": config.SITE_URL},
        )

    @staticmethod
    def send_package_activated_email(email: str, user, package, user_package, payment_amount, user_name: str = "") -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name or (user.get_full_name() if hasattr(user, "get_full_name") else ""),
            "package_name": str(package.name if hasattr(package, "name") else package),
            "ad_count": str(package.ad_count if hasattr(package, "ad_count") else ""),
            "payment_amount": str(payment_amount),
            "site_url": config.SITE_URL,
        }
        db = EmailService._render_db_template("package_activated", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        subject = f"{config.SITE_NAME} - تم تفعيل باقتك"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/package_activated.html",
            context={"user": user, "package": package, "user_package": user_package,
                     "payment_amount": payment_amount,
                     "site_name": config.SITE_NAME, "site_url": config.SITE_URL},
        )

    @staticmethod
    def send_newsletter_confirmation_email(email: str, unsubscribe_url: str = "") -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "site_url": config.SITE_URL,
            "unsubscribe_url": unsubscribe_url,
        }
        db = EmailService._render_db_template("newsletter_confirmation", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[email], subject=subject, html_content=html_content)

        subject = f"{config.SITE_NAME} - تأكيد الاشتراك في النشرة البريدية"
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/newsletter_confirmation.html", context=context,
        )

    @staticmethod
    def send_contact_form_email(to_email: str, sender_name: str, sender_email: str, message: str, subject_text: str = "") -> bool:
        from constance import config

        context = {
            "site_name": config.SITE_NAME,
            "sender_name": sender_name,
            "sender_email": sender_email,
            "message": message,
            "subject_text": subject_text,
        }
        db = EmailService._render_db_template("contact_form", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(to_emails=[to_email], subject=subject, html_content=html_content)

        subject = f"{config.SITE_NAME} - رسالة جديدة من {sender_name}"
        html_content = (
            f"<p><strong>المرسل:</strong> {sender_name} ({sender_email})</p>"
            f"<p><strong>الموضوع:</strong> {subject_text}</p>"
            f"<p><strong>الرسالة:</strong></p><p>{message}</p>"
        )
        return EmailService.send_email(to_emails=[to_email], subject=subject, html_content=html_content)

    @staticmethod
    def send_saved_search_notification(
        email: str, search_name: str, ads: list, search_url: str, user_name: str = ""
    ) -> bool:
        from constance import config

        if not getattr(config, "ENABLE_EMAIL_NOTIFICATIONS", True):
            return False
        if not getattr(config, "ENABLE_SAVED_SEARCH_NOTIFICATIONS", True):
            return False

        context = {
            "site_name": config.SITE_NAME,
            "user_name": user_name,
            "search_name": search_name,
            "search_url": search_url,
        }
        db = EmailService._render_db_template("saved_search_notification", context)
        if db:
            subject, html_content = db
            return EmailService.send_email(
                to_emails=[email], subject=subject, html_content=html_content,
                from_email=config.SAVED_SEARCH_FROM_EMAIL,
            )

        subject = config.SAVED_SEARCH_EMAIL_SUBJECT.format(search_name=search_name)
        context["ads"] = ads
        return EmailService.send_template_email(
            to_emails=[email], subject=subject,
            template_name="emails/saved_search_notification.html", context=context,
            from_email=config.SAVED_SEARCH_FROM_EMAIL,
        )
