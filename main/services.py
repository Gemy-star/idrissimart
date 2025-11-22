"""
Services for handling external integrations and business logic
"""

import random
import string
from datetime import datetime, timedelta
from constance import config
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """Service for handling Twilio SMS and OTP verification"""

    def __init__(self):
        # Get Twilio configuration from django-constance
        self.account_sid = getattr(config, "TWILIO_ACCOUNT_SID", "")
        self.auth_token = getattr(config, "TWILIO_AUTH_TOKEN", "")
        self.phone_number = getattr(config, "TWILIO_PHONE_NUMBER", "")
        self.development_mode = getattr(config, "TWILIO_DEVELOPMENT_MODE", False)

        # If development mode is enabled, skip Twilio initialization
        if self.development_mode:
            self.client = None
            logger.info(
                "Twilio running in DEVELOPMENT MODE - SMS will be logged to console only"
            )
            return

        if self.account_sid and self.auth_token:
            try:
                # Log credentials (partially masked for security)
                logger.info(
                    f"Initializing Twilio with Account SID: {self.account_sid[:10]}..."
                )
                logger.info(f"Auth Token length: {len(self.auth_token)} chars")
                logger.info(f"Phone Number: {self.phone_number}")

                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                self.client = None
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                logger.error(f"Account SID used: {self.account_sid[:10]}...")
        else:
            self.client = None
            logger.warning("Twilio credentials not configured in django-constance")
            logger.warning(f"Account SID empty: {not self.account_sid}")
            logger.warning(f"Auth Token empty: {not self.auth_token}")

    def generate_otp(self, length=6):
        """Generate a random OTP code"""
        return "".join(random.choices(string.digits, k=length))

    def send_otp(self, mobile_number, otp_code):
        """Send OTP via SMS using Twilio"""

        # Development mode: Just log the OTP
        if self.development_mode:
            logger.warning(f"🔐 DEVELOPMENT MODE - OTP for {mobile_number}: {otp_code}")
            print(f"\n{'='*60}")
            print(f"🔐 OTP VERIFICATION CODE (Development Mode)")
            print(f"{'='*60}")
            print(f"Mobile Number: {mobile_number}")
            print(f"OTP Code: {otp_code}")
            print(f"{'='*60}\n")
            return True, _("تم إرسال رمز التحقق بنجاح (وضع التطوير)")

        if not self.client:
            logger.error("Twilio client not initialized")
            return False, _("خدمة الرسائل غير متاحة")

        try:
            # Format mobile number (add country code if not present)
            if not mobile_number.startswith("+"):
                # Assuming Saudi Arabia (+966) as default
                mobile_number = f"+966{mobile_number.lstrip('0')}"

            message = self.client.messages.create(
                body=f"رمز التحقق الخاص بك في إدريسي مارت: {otp_code}\nلا تشارك هذا الرمز مع أحد.",
                from_=self.phone_number,
                to=mobile_number,
            )

            logger.info(f"OTP sent successfully to {mobile_number}, SID: {message.sid}")
            return True, _("تم إرسال رمز التحقق بنجاح")

        except TwilioException as e:
            logger.error(f"Twilio error sending OTP to {mobile_number}: {str(e)}")
            return False, _("فشل في إرسال رمز التحقق")
        except Exception as e:
            logger.error(f"Unexpected error sending OTP to {mobile_number}: {str(e)}")
            return False, _("حدث خطأ غير متوقع")

    def verify_otp(self, user, submitted_code):
        """Verify the submitted OTP code"""
        if not user.mobile_verification_code:
            return False, _("لم يتم إرسال رمز التحقق")

        if not user.mobile_verification_expires:
            return False, _("انتهت صلاحية رمز التحقق")

        if timezone.now() > user.mobile_verification_expires:
            return False, _("انتهت صلاحية رمز التحقق")

        if user.mobile_verification_code != submitted_code:
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

    def send_verification_code(self, user):
        """Generate and send OTP to user's mobile"""
        if not user.mobile:
            return False, _("رقم الجوال غير محدد")

        # Generate OTP
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

        # Send SMS
        success, message = self.send_otp(user.mobile, otp_code)

        if success:
            logger.info(
                f"Verification code sent to user {user.username} at {user.mobile}"
            )
        else:
            logger.error(
                f"Failed to send verification code to user {user.username} at {user.mobile}"
            )

        return success, message


class MobileVerificationService:
    """Service for handling mobile number verification in ad creation"""

    def __init__(self):
        self.twilio_service = TwilioService()

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

        # Send verification code
        return self.twilio_service.send_verification_code(user)

    def verify_mobile_for_ad(self, user, verification_code):
        """Verify mobile number for ad creation"""
        return self.twilio_service.verify_otp(user, verification_code)
