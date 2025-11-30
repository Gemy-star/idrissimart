"""
SMS Service using Twilio
Integrates with django-constance for dynamic configuration
"""

import logging
from typing import Optional

from constance import config
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS using Twilio"""

    @staticmethod
    def is_enabled() -> bool:
        """Check if Twilio SMS service is enabled"""
        return (
            config.TWILIO_ENABLED
            and bool(config.TWILIO_ACCOUNT_SID)
            and bool(config.TWILIO_AUTH_TOKEN)
            and bool(config.TWILIO_PHONE_NUMBER)
        )

    @staticmethod
    def get_client() -> Optional[Client]:
        """
        Get Twilio client instance

        Returns:
            Twilio Client or None if disabled
        """
        if not SMSService.is_enabled():
            return None

        try:
            return Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        except Exception as e:
            logger.error(f"Failed to create Twilio client: {str(e)}")
            return None

    @staticmethod
    def send_sms(to_number: str, message: str) -> bool:
        """
        Send SMS message

        Args:
            to_number: Recipient phone number (international format: +1234567890)
            message: SMS message content

        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        # Check if development mode is enabled
        if config.TWILIO_DEVELOPMENT_MODE:
            logger.info(f"[DEVELOPMENT MODE] SMS to {to_number}: {message}")
            print(f"\n{'='*50}")
            print(f"SMS DEVELOPMENT MODE")
            print(f"To: {to_number}")
            print(f"Message: {message}")
            print(f"{'='*50}\n")
            return True

        if not SMSService.is_enabled():
            logger.warning("Twilio SMS service is disabled")
            return False

        try:
            client = SMSService.get_client()
            if not client:
                logger.error("Failed to get Twilio client")
                return False

            # Format phone number
            if not to_number.startswith("+"):
                # Assume Saudi Arabia if no country code
                to_number = f"+966{to_number.lstrip('0')}"

            # Send SMS
            message = client.messages.create(
                body=message,
                from_=config.TWILIO_PHONE_NUMBER,
                to=to_number,
            )

            logger.info(f"SMS sent successfully to {to_number}. SID: {message.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return False

    @staticmethod
    def send_otp(phone_number: str, otp_code: str) -> bool:
        """
        Send OTP verification code via SMS

        Args:
            phone_number: Recipient phone number
            otp_code: OTP code to send

        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        message = (
            f"{config.SITE_NAME}\n"
            f"رمز التحقق الخاص بك: {otp_code}\n"
            f"صالح لمدة {config.OTP_EXPIRY_MINUTES} دقائق"
        )

        return SMSService.send_sms(phone_number, message)

    @staticmethod
    def send_verification_code(
        phone_number: str, code: str, purpose: str = "التحقق"
    ) -> bool:
        """
        Send generic verification code

        Args:
            phone_number: Recipient phone number
            code: Verification code
            purpose: Purpose of the code (e.g., "التحقق", "إعادة تعيين كلمة المرور")

        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        message = f"{config.SITE_NAME}\nرمز {purpose}: {code}"

        return SMSService.send_sms(phone_number, message)

    @staticmethod
    def send_ad_notification(phone_number: str, ad_title: str, status: str) -> bool:
        """
        Send ad status notification

        Args:
            phone_number: Recipient phone number
            ad_title: Title of the ad
            status: Status message (e.g., "تم الموافقة على إعلانك")

        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        message = f"{config.SITE_NAME}\n{status}: {ad_title}"

        return SMSService.send_sms(phone_number, message)

    @staticmethod
    def send_order_notification(phone_number: str, order_id: str, status: str) -> bool:
        """
        Send order status notification

        Args:
            phone_number: Recipient phone number
            order_id: Order ID
            status: Order status message

        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        message = f"{config.SITE_NAME}\nطلب #{order_id}\n{status}"

        return SMSService.send_sms(phone_number, message)

    @staticmethod
    def send_welcome_sms(phone_number: str, user_name: str = "") -> bool:
        """
        Send welcome SMS to new user

        Args:
            phone_number: Recipient phone number
            user_name: User's name (optional)

        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        greeting = f"مرحباً {user_name}!" if user_name else "مرحباً بك!"
        message = f"{greeting}\nشكراً لانضمامك إلى {config.SITE_NAME}"

        return SMSService.send_sms(phone_number, message)

    @staticmethod
    def format_phone_number(phone: str, country_code: str = "+966") -> str:
        """
        Format phone number to international format

        Args:
            phone: Phone number
            country_code: Country code (default: +966 for Saudi Arabia)

        Returns:
            str: Formatted phone number
        """
        # Remove any spaces, dashes, or parentheses
        phone = "".join(filter(str.isdigit, phone))

        # Remove leading zeros
        phone = phone.lstrip("0")

        # Add country code if not present
        if not phone.startswith("+"):
            phone = f"{country_code}{phone}"

        return phone

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number format

        Args:
            phone: Phone number to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Remove any non-digit characters except +
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")

        # Check if it starts with + and has at least 10 digits
        if cleaned.startswith("+") and len(cleaned.replace("+", "")) >= 10:
            return True

        # Check if it's a Saudi number (starts with 05 or 5)
        if cleaned.startswith("05") or (cleaned.startswith("5") and len(cleaned) == 9):
            return True

        return False
