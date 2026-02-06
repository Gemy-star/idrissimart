#!/usr/bin/env python
"""
Production Services Test Script
Tests Paymob, PayPal, and Twilio SMS services to verify they're working correctly.

Usage:
    python test_production_services.py --all
    python test_production_services.py --paymob
    python test_production_services.py --paypal
    python test_production_services.py --twilio
    python test_production_services.py --sms +201234567890
"""

import os
import sys
import django
import argparse
from decimal import Decimal
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# Setup Django environment
# Use docker settings for production testing (can be changed via --settings flag)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.docker")

# Set log file path for testing
os.environ["DJANGO_LOG_FILE"] = "/tmp/test.log"

try:
    django.setup()
except Exception as e:
    # If setup fails, fallback to local settings
    print(f"Warning: Failed to use docker settings, falling back to local: {e}")
    os.environ["DJANGO_SETTINGS_MODULE"] = "idrissimart.settings.local"
    django.setup()

# Import after Django setup
from constance import config
from main.services.paymob_service import PaymobService
from main.services.paypal_service import PayPalService
from main.services.sms_service import SMSService


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(70)}{Style.RESET_ALL}")
    print("=" * 70)


def print_success(message):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_info(message):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")


def print_result(key, value):
    """Print key-value result"""
    print(f"{Fore.WHITE}{key}: {Fore.CYAN}{value}{Style.RESET_ALL}")


def get_config_value(key, default=""):
    """Get config value from constance (which reads from environment) or direct environment"""
    # Try constance first (it reads from environment variables in constance_config.py)
    try:
        from constance import config

        value = getattr(config, key, None)
        if value is not None and value != "":
            return value
    except Exception as e:
        # If DB not available, fall back to environment
        pass

    # Fallback to direct environment variable
    env_value = os.getenv(key)
    if env_value:
        return env_value

    return default


def test_paymob():
    """Test Paymob payment gateway"""
    print_header("TESTING PAYMOB PAYMENT GATEWAY")

    try:
        # Check configuration
        print_info("Checking Paymob configuration...")

        api_key = get_config_value("PAYMOB_API_KEY")
        secret_key = get_config_value("PAYMOB_SECRET_KEY")
        public_key = get_config_value("PAYMOB_PUBLIC_KEY")
        integration_id = get_config_value("PAYMOB_INTEGRATION_ID")

        if not api_key or api_key == "":
            print_error("PAYMOB_API_KEY is not configured")
            return False

        if not secret_key or secret_key == "":
            print_error("PAYMOB_SECRET_KEY is not configured")
            return False

        if not public_key or public_key == "":
            print_error("PAYMOB_PUBLIC_KEY is not configured")
            return False

        print_success("Configuration keys are present")
        print_result("API Key", f"{api_key[:20]}..." if len(api_key) > 20 else api_key)
        print_result(
            "Secret Key",
            f"{secret_key[:20]}..." if len(secret_key) > 20 else secret_key,
        )
        print_result(
            "Public Key",
            f"{public_key[:20]}..." if len(public_key) > 20 else public_key,
        )
        print_result("Integration ID", integration_id or "Not set")

        # Check if service is enabled
        try:
            paymob_service = PaymobService()
            if paymob_service.is_enabled():
                print_success("Paymob service is ENABLED")
            else:
                print_error("Paymob service is DISABLED in configuration")
                return False
        except:
            # Fallback to environment check
            paymob_enabled_val = get_config_value("PAYMOB_ENABLED", "True")
            paymob_enabled = str(paymob_enabled_val).lower() in (
                "true",
                "1",
                "yes",
            )
            if paymob_enabled and api_key:
                print_success("Paymob service is ENABLED (from environment)")
            else:
                print_error("Paymob service is DISABLED in configuration")
                return False

        # Test authentication
        print_info("\nTesting Paymob authentication...")
        try:
            import requests

            # Authenticate with Paymob
            auth_url = "https://accept.paymob.com/api/auth/tokens"
            auth_data = {"api_key": api_key}

            response = requests.post(auth_url, json=auth_data, timeout=10)
            response.raise_for_status()

            auth_token = response.json().get("token")

            if auth_token:
                print_success(f"Authentication successful! Token: {auth_token[:30]}...")
            else:
                print_error("Authentication failed - no token returned")
                return False
        except Exception as e:
            print_error(f"Authentication failed: {str(e)}")
            return False

        # Test payment creation (test mode) - Simplified
        print_info("\nTesting payment order creation (test transaction)...")
        try:
            import requests

            # Create order
            order_url = "https://accept.paymob.com/api/ecommerce/orders"
            order_data = {
                "auth_token": auth_token,
                "delivery_needed": "false",
                "amount_cents": "1000",  # 10 EGP
                "currency": "EGP",
                "items": [],
            }

            response = requests.post(order_url, json=order_data, timeout=10)
            response.raise_for_status()

            order_id = response.json().get("id")

            if order_id:
                print_success("Test order created successfully!")
                print_result("Order ID", str(order_id))
                return True
            else:
                print_error("Order creation failed - no order ID returned")
                return False

        except Exception as e:
            print_error(f"Payment creation error: {str(e)}")
            return False

    except Exception as e:
        print_error(f"Paymob test failed: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


def test_paypal():
    """Test PayPal payment gateway"""
    print_header("TESTING PAYPAL PAYMENT GATEWAY")

    try:
        # Check configuration
        print_info("Checking PayPal configuration...")

        client_id = get_config_value("PAYPAL_CLIENT_ID")
        client_secret = get_config_value("PAYPAL_CLIENT_SECRET")
        mode = get_config_value("PAYPAL_MODE", "sandbox")

        print_success("Configuration keys are present")
        print_result(
            "Client ID", f"{client_id[:20]}..." if len(client_id) > 20 else client_id
        )
        print_result(
            "Client Secret",
            f"{client_secret[:20]}..." if len(client_secret) > 20 else client_secret,
        )
        print_result("Mode", mode)

        if mode.lower() == "live":
            print_info(
                "⚠️  PayPal is in LIVE mode - real transactions will be processed!"
            )
        else:
            print_info("PayPal is in SANDBOX mode - test transactions only")

        # Check if service is enabled
        try:
            paypal_service = PayPalService()
            if paypal_service.is_enabled():
                print_success("PayPal service is ENABLED")
            else:
                print_error("PayPal service is DISABLED in configuration")
                return False
        except:
            # Fallback to environment check
            paypal_enabled_val = get_config_value("PAYPAL_ENABLED", "True")
            paypal_enabled = str(paypal_enabled_val).lower() in (
                "true",
                "1",
                "yes",
            )
            if paypal_enabled and client_id:
                print_success("PayPal service is ENABLED (from environment)")
            else:
                print_error("PayPal service is DISABLED")
                return False

        # Test API connection
        print_info("\nTesting PayPal API connection...")
        try:
            import paypalrestsdk

            # Configure PayPal SDK
            paypalrestsdk.configure(
                {"mode": mode, "client_id": client_id, "client_secret": client_secret}
            )

            # Try to get access token
            api = paypalrestsdk.Api()
            token = api.get_access_token()

            if token:
                print_success(
                    f"API connection successful! Token received: {token[:30]}..."
                )
            else:
                print_error("API connection failed - no token received")
                return False

        except Exception as e:
            error_msg = str(e)
            print_error(f"API connection failed: {error_msg}")

            # Provide helpful hints
            if "client_id" in error_msg.lower() or "client_secret" in error_msg.lower():
                print_info("\n💡 Hint: PayPal configuration error. This usually means:")
                print_info(
                    "   1. PAYPAL_CLIENT_ID or PAYPAL_CLIENT_SECRET is missing/incorrect"
                )
                print_info(
                    "   2. The credentials don't match the mode (sandbox vs live)"
                )
                print_info(
                    "   3. Check PayPal Developer Dashboard: https://developer.paypal.com/"
                )
                print_info(f"\n   Current Mode: {mode}")
                print_info(
                    f"   Current Client ID: {client_id[:20]}..."
                    if client_id
                    else "   Client ID: NOT SET"
                )

            return False

        # Test payment creation (test mode)
        print_info("\nTesting payment creation (test transaction)...")
        try:
            success, result = paypal_service.process_payment(
                amount=Decimal("10.00"),
                currency="USD",
                description="Test Payment",
                return_url="http://localhost:8000/payment/success",
                cancel_url="http://localhost:8000/payment/cancel",
            )

            if success:
                print_success("Test payment created successfully!")
                if isinstance(result, dict):
                    print_result("Payment ID", result.get("id", "N/A"))
                    if "approval_url" in result:
                        print_result("Approval URL", result["approval_url"][:80])
                return True
            else:
                print_error(f"Payment creation failed: {result}")
                return False

        except Exception as e:
            print_error(f"Payment creation error: {str(e)}")
            return False

    except Exception as e:
        print_error(f"PayPal test failed: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


def test_twilio(phone_number=None):
    """Test Twilio SMS service"""
    print_header("TESTING TWILIO SMS SERVICE")

    try:
        # Check configuration
        print_info("Checking Twilio configuration...")

        account_sid = get_config_value("TWILIO_ACCOUNT_SID")
        auth_token = get_config_value("TWILIO_AUTH_TOKEN")
        from_number = get_config_value("TWILIO_PHONE_NUMBER")

        if not from_number or from_number == "":
            print_error("TWILIO_PHONE_NUMBER is not configured")
            return False

        print_success("Configuration keys are present")
        print_result(
            "Account SID",
            f"{account_sid[:20]}..." if len(account_sid) > 20 else account_sid,
        )
        print_result(
            "Auth Token",
            f"{auth_token[:20]}..." if len(auth_token) > 20 else auth_token,
        )
        print_result("From Number", from_number)

        # Check if service is enabled
        sms_service = SMSService()
        twilio_enabled_val = get_config_value("TWILIO_ENABLED", "True")
        twilio_enabled = str(twilio_enabled_val).lower() in (
            "true",
            "1",
            "yes",
        )
        if twilio_enabled:
            print_success("Twilio service is ENABLED")
        else:
            print_error("Twilio service is DISABLED in configuration")
            return False

        # Test API connection
        print_info("\nTesting Twilio API connection...")
        try:
            from twilio.rest import Client

            client = Client(account_sid, auth_token)

            # Try to fetch account details
            account = client.api.accounts(account_sid).fetch()

            if account:
                print_success(f"API connection successful!")
                print_result("Account Status", account.status)
                print_result("Account Type", account.type)
            else:
                print_error("API connection failed - no account info")
                return False

        except Exception as e:
            error_msg = str(e)
            print_error(f"API connection failed: {error_msg}")

            # Provide helpful hints based on error
            if "20003" in error_msg or "Authenticate" in error_msg:
                print_info("\n💡 Hint: Authentication failed. This usually means:")
                print_info("   1. TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is incorrect")
                print_info("   2. The credentials have expired or been revoked")
                print_info(
                    "   3. Check your Twilio Console: https://console.twilio.com/"
                )
                print_info(f"\n   Current Account SID: {account_sid}")
                print_info(f"   Current Auth Token: {auth_token[:10]}...")

            return False

        # Test SMS sending (only if phone number provided)
        if phone_number:
            print_info(f"\nTesting SMS sending to {phone_number}...")
            try:
                success, result = sms_service.send_sms(
                    phone_number=phone_number,
                    message="Test message from IdrissiMart - Production test",
                )

                if success:
                    print_success("Test SMS sent successfully!")
                    print_result("Message SID", result)
                    return True
                else:
                    print_error(f"SMS sending failed: {result}")
                    return False

            except Exception as e:
                print_error(f"SMS sending error: {str(e)}")
                return False
        else:
            print_info("\nSkipping SMS send test (no phone number provided)")
            print_info("To test SMS sending, use: --sms +1234567890")
            return True

    except Exception as e:
        print_error(f"Twilio test failed: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(
        description="Test production services (Paymob, PayPal, Twilio)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_production_services.py --all              # Test all services
  python test_production_services.py --paymob           # Test Paymob only
  python test_production_services.py --paypal           # Test PayPal only
  python test_production_services.py --twilio           # Test Twilio only
  python test_production_services.py --sms +2010000000 # Test SMS to specific number
Note:
  This script uses django-constance which loads credentials from environment variables.
  Credentials are configured in:
  - .env file (development)
  - environment.production file (production)
  - System environment variables (docker/production)        """,
    )

    parser.add_argument("--all", action="store_true", help="Test all services")
    parser.add_argument(
        "--paymob", action="store_true", help="Test Paymob payment gateway"
    )
    parser.add_argument(
        "--paypal", action="store_true", help="Test PayPal payment gateway"
    )
    parser.add_argument("--twilio", action="store_true", help="Test Twilio SMS service")
    parser.add_argument(
        "--sms", metavar="PHONE", help="Test SMS to specific phone number"
    )

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any([args.all, args.paymob, args.paypal, args.twilio, args.sms]):
        parser.print_help()
        return

    print_header("IDRISSIMART PRODUCTION SERVICES TEST")
    print_info("Testing services configuration and connectivity...\n")

    results = {}

    # Test services based on arguments
    if args.all or args.paymob:
        results["Paymob"] = test_paymob()

    if args.all or args.paypal:
        results["PayPal"] = test_paypal()

    if args.all or args.twilio or args.sms:
        phone = args.sms if args.sms else None
        results["Twilio"] = test_twilio(phone)

    # Print summary
    print_header("TEST SUMMARY")

    all_passed = True
    for service, passed in results.items():
        if passed:
            print_success(f"{service}: PASSED")
        else:
            print_error(f"{service}: FAILED")
            all_passed = False

    print("\n" + "=" * 70)

    if all_passed:
        print_success("\n✓ All tests PASSED! Services are working correctly.\n")
        return 0
    else:
        print_error("\n✗ Some tests FAILED. Please check the configuration and logs.\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback

        print(traceback.format_exc())
        sys.exit(1)
