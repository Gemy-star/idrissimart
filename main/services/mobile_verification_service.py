"""
Mobile Verification Service
Handles mobile number verification for ad creation
"""

import random
import string
import logging
from datetime import timedelta

from constance import config
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .sms_service import SMSService

logger = logging.getLogger(__name__)


class MobileVerificationService:
    """Service for handling mobile number verification in ad creation"""

    def __init__(self):
        self.sms_service = SMSService()

    def check_mobile_verification_required(self, user, mobile_number):
        """Check if mobile verification is required for ad creation"""
        # Check if mobile verification is enabled in constance
        verification_enabled = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)

        if not verification_enabled:
            return False, _("التحقق من الجوال غير مطلوب")

        if not mobile_number:
            return False, _("رقم الجوال مطلوب")

        # If user's mobile is already verified and matches
        if user.mobile == mobile_number and user.is_mobile_verified:
            return False, _("الجوال موثق مسبقاً")

        # If user is using a different mobile number, verification is required
        return True, _("يجب التحقق من رقم الجوال")

    def initiate_verification(self, user, mobile_number):
        """Start the mobile verification process"""
        # Update user's mobile number
        user.mobile = mobile_number
        user.is_mobile_verified = False
        user.save(update_fields=["mobile", "is_mobile_verified"])

        # Generate OTP code
        otp_code = self.generate_otp()

        # Set expiration time (configurable minutes from now)
        otp_expiry_minutes = getattr(config, "OTP_EXPIRY_MINUTES", 10)
        expiration_time = timezone.now() + timedelta(minutes=otp_expiry_minutes)

        # Save OTP to user
        user.mobile_verification_code = otp_code
        user.mobile_verification_expires = expiration_time
        user.save(
            update_fields=["mobile_verification_code", "mobile_verification_expires"]
        )

        # Send verification code via SMS
        success = self.sms_service.send_otp(user.mobile, otp_code)

        if success:
            logger.info(
                f"Verification code sent to user {user.username} at {user.mobile}"
            )
            return True, _("تم إرسال رمز التحقق بنجاح")
        else:
            logger.error(
                f"Failed to send verification code to user {user.username} at {user.mobile}"
            )
            return False, _("فشل في إرسال رمز التحقق")

    def verify_mobile_for_ad(self, user, verification_code):
        """Verify mobile number for ad creation"""
        if not user.mobile_verification_code:
            return False, _("لم يتم إرسال رمز التحقق")

        if not user.mobile_verification_expires:
            return False, _("انتهت صلاحية رمز التحقق")

        if timezone.now() > user.mobile_verification_expires:
            return False, _("انتهت صلاحية رمز التحقق")

        if user.mobile_verification_code != verification_code:
            return False, _("رمز التحقق غير صحيح")

        # Mark mobile as verified
        user.is_mobile_verified = True
        user.mobile_verification_code = ""
        user.mobile_verification_expires = None
        user.save(
            update_fields=[
                "is_mobile_verified",
                "mobile_verification_code",
                "mobile_verification_expires",
            ]
        )

        return True, _("تم التحقق من الجوال بنجاح")

    def generate_otp(self, length=6):
        """Generate a random OTP code"""
        return "".join(random.choices(string.digits, k=length))
