"""
Management command to test django-constance configuration for payment and SMS services
"""

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from constance import config
from main.payment_services import PaymentService
from main.services.sms_service import SMSService
from main.services.email_service import EmailService


class Command(BaseCommand):
    help = "Test django-constance configuration for payment and SMS services"

    def add_arguments(self, parser):
        parser.add_argument(
            "--service",
            type=str,
            choices=["paypal", "paymob", "twilio", "all"],
            default="all",
            help="Specify which service to test",
        )

    def handle(self, *args, **options):
        service = options["service"]

        self.stdout.write(
            self.style.SUCCESS("🔧 Testing django-constance configuration...\n")
        )

        if service in ["paypal", "all"]:
            self.test_paypal_config()

        if service in ["paymob", "all"]:
            self.test_paymob_config()

        if service in ["twilio", "all"]:
            self.test_twilio_config()

        if service == "all":
            self.test_payment_service()

        self.stdout.write(self.style.SUCCESS("\n✅ Configuration test completed!"))

    def test_paypal_config(self):
        """Test PayPal configuration"""
        self.stdout.write(self.style.WARNING("💳 Testing PayPal Configuration:"))

        try:
            client_id = getattr(config, "PAYPAL_CLIENT_ID", "")
            client_secret = getattr(config, "PAYPAL_CLIENT_SECRET", "")
            mode = getattr(config, "PAYPAL_MODE", "sandbox")

            if client_id and client_secret:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ PayPal Client ID: {client_id[:20]}...")
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ PayPal Client Secret: {client_secret[:20]}..."
                    )
                )
                self.stdout.write(self.style.SUCCESS(f"  ✅ PayPal Mode: {mode}"))

                # Test PayPal service initialization
                from main.payment_services import PayPalService

                paypal_service = PayPalService()
                if paypal_service.client_id and paypal_service.client_secret:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "  ✅ PayPal service initialized successfully"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR("  ❌ PayPal service initialization failed")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("  ❌ PayPal credentials not configured")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ PayPal configuration error: {str(e)}")
            )

    def test_paymob_config(self):
        """Test Paymob configuration"""
        self.stdout.write(self.style.WARNING("\n💰 Testing Paymob Configuration:"))

        try:
            api_key = getattr(config, "PAYMOB_API_KEY", "")
            integration_id = getattr(config, "PAYMOB_INTEGRATION_ID", "")
            iframe_id = getattr(config, "PAYMOB_IFRAME_ID", "")

            if api_key:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Paymob API Key: {api_key[:20]}...")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠️  Paymob API Key not configured")
                )

            if integration_id:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Paymob Integration ID: {integration_id}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠️  Paymob Integration ID not configured")
                )

            if iframe_id:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Paymob iFrame ID: {iframe_id}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠️  Paymob iFrame ID not configured")
                )

            # Test Paymob service initialization
            from main.services.paymob_service import PaymobService

            if PaymobService.is_enabled():
                self.stdout.write(
                    self.style.SUCCESS("  ✅ Paymob service enabled and configured")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠️  Paymob service needs configuration")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Paymob configuration error: {str(e)}")
            )

    def test_twilio_config(self):
        """Test Twilio configuration"""
        self.stdout.write(self.style.WARNING("\n📱 Testing Twilio Configuration:"))

        try:
            account_sid = getattr(config, "TWILIO_ACCOUNT_SID", "")
            auth_token = getattr(config, "TWILIO_AUTH_TOKEN", "")
            phone_number = getattr(config, "TWILIO_PHONE_NUMBER", "")

            if account_sid and auth_token:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ Twilio Account SID: {account_sid[:20]}..."
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Twilio Auth Token: {auth_token[:20]}...")
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Twilio Phone Number: {phone_number}")
                )

                # Test Twilio service initialization
                if SMSService.is_enabled():
                    self.stdout.write(
                        self.style.SUCCESS(
                            "  ✅ Twilio/SMS service enabled and configured"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "  ❌ Twilio/SMS service not properly configured"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("  ❌ Twilio credentials not configured")
                )

            # Test security settings
            enable_verification = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)
            otp_expiry = getattr(config, "OTP_EXPIRY_MINUTES", 10)
            max_attempts = getattr(config, "MAX_OTP_ATTEMPTS", 3)

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ Mobile Verification Enabled: {enable_verification}"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ OTP Expiry Minutes: {otp_expiry}")
            )
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Max OTP Attempts: {max_attempts}")
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Twilio configuration error: {str(e)}")
            )

    def test_payment_service(self):
        """Test PaymentService integration"""
        self.stdout.write(
            self.style.WARNING("\n🔄 Testing Payment Service Integration:")
        )

        try:
            payment_service = PaymentService()
            supported_providers = payment_service.get_supported_providers()

            if supported_providers:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ Found {len(supported_providers)} supported payment providers:"
                    )
                )
                for provider in supported_providers:
                    mode_info = (
                        f" ({provider.get('mode', 'N/A')})"
                        if "mode" in provider
                        else ""
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    - {provider["name"]}{mode_info}: {", ".join(provider["currencies"])}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠️  No payment providers configured")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Payment service error: {str(e)}"))
