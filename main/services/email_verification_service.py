"""
Email Verification Service
Handles email verification using OTP codes for user registration
"""

import random
import string
import logging
from datetime import timedelta

from constance import config
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .email_service import EmailService

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for handling email OTP verification during registration"""

    def __init__(self):
        self.email_service = EmailService()

    def check_email_verification_required(self):
        """Check if email verification is enabled"""
        # Check constance kill-switch
        verification_enabled = getattr(config, "ENABLE_EMAIL_VERIFICATION", True)
        if not verification_enabled:
            return False

        # Check SiteConfiguration setting
        from content.site_config import SiteConfiguration
        from content.verification_utils import is_email_verification_required

        return is_email_verification_required()

    def generate_otp(self, length=6):
        """Generate a random OTP code (numeric only for email)"""
        return "".join(random.choices(string.digits, k=length))

    def initiate_verification(self, user):
        """
        Start the email verification process
        Generates OTP and sends it to user's email
        """
        # Generate OTP code
        otp_code = self.generate_otp()

        # Set expiration time (configurable minutes from now)
        otp_expiry_minutes = getattr(config, "OTP_EXPIRY_MINUTES", 10)
        expiration_time = timezone.now() + timedelta(minutes=otp_expiry_minutes)

        # Save OTP to user (using email_verification_token field for OTP)
        user.email_verification_token = otp_code
        user.email_verification_expires = expiration_time
        user.is_email_verified = False
        user.save(
            update_fields=[
                "email_verification_token",
                "email_verification_expires",
                "is_email_verified",
            ]
        )

        # Send OTP via email
        success = self.email_service.send_otp_email(
            email=user.email, otp_code=otp_code, user_name=user.get_full_name()
        )

        if success:
            return True, _("تم إرسال رمز التحقق إلى بريدك الإلكتروني بنجاح")
        else:
            logger.error(
                f"Failed to send email verification code to user {user.username} at {user.email}"
            )
            return False, _("فشل في إرسال رمز التحقق")

    def verify_email_otp(self, user, otp_code):
        """Verify email using OTP code"""
        if not user.email_verification_token:
            return False, _("لم يتم إرسال رمز التحقق")

        if not user.email_verification_expires:
            return False, _("انتهت صلاحية رمز التحقق")

        if timezone.now() > user.email_verification_expires:
            return False, _("انتهت صلاحية رمز التحقق. يرجى طلب رمز جديد")

        # Check max attempts
        max_attempts = getattr(config, "MAX_OTP_ATTEMPTS", 3)
        attempts_key = f"email_otp_attempts_{user.id}"

        # Get current attempt count from session or user meta
        # For now, we'll implement by checking the code directly

        if user.email_verification_token != otp_code:
            return False, _("رمز التحقق غير صحيح")

        # Mark email as verified
        user.is_email_verified = True
        user.email_verification_token = ""
        user.email_verification_expires = None
        user.save(
            update_fields=[
                "is_email_verified",
                "email_verification_token",
                "email_verification_expires",
            ]
        )

        logger.info(f"Email verified successfully for user {user.username}")
        return True, _("تم التحقق من البريد الإلكتروني بنجاح")

    def resend_otp(self, user):
        """Resend OTP code to user's email"""
        # Check if user email is already verified
        if user.is_email_verified:
            return False, _("البريد الإلكتروني موثق مسبقاً")

        # Initiate new verification (generates new OTP)
        return self.initiate_verification(user)
