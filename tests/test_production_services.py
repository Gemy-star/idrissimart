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
    python test_production_services.py --settings=idrissimart.settings.local --all
    python test_production_services.py --settings=idrissimart.settings.docker --paypal
"""

import os
import sys
import django
import argparse
from decimal import Decimal
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# Parse --settings argument early (before Django setup)
settings_module = "idrissimart.settings.docker"
for i, arg in enumerate(sys.argv[1:]):  # Skip script name
    if arg.startswith("--settings="):
        settings_module = arg.split("=", 1)[1]
        sys.argv.pop(i + 1)  # Remove from argv (i+1 because we skipped index 0)
        break
    elif arg == "--settings" and i + 2 < len(sys.argv):
        # Handle --settings without equals: --settings idrissimart.settings.local
        settings_module = sys.argv[i + 2]
        sys.argv.pop(i + 2)
        sys.argv.pop(i + 1)
        break

# Setup Django environment with specified settings
os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
os.environ["DJANGO_LOG_FILE"] = "/tmp/test.log"

print(f"Using Django settings: {settings_module}")

try:
    django.setup()
except Exception as e:
    # If setup fails, fallback to local settings
    print(f"Warning: Failed to use {settings_module}, falling back to local: {e}")
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
    """Get config value from django-constance (with database fallback to environment)"""
    try:
        # Try constance config (reads from database first, then falls back to defaults)
        value = getattr(config, key, None)
        if value is not None and value != "":
            return value
    except Exception as e:
        # If constance is not available, fall back to environment
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
        # Check configuration from constance
        print_info("Checking Paymob configuration from django-constance...")

        api_key = config.PAYMOB_API_KEY
        secret_key = config.PAYMOB_SECRET_KEY
        public_key = config.PAYMOB_PUBLIC_KEY

        if not api_key or not secret_key or not public_key:
            print_error("Paymob credentials not configured in constance")
            print_info("Configure via .env and update database, or via admin panel")
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
                print_success(f"Authentication successful!")
                print_result("Token", f"{auth_token[:30]}...")
            else:
                print_error("Authentication failed - no token returned")
                return False

        except Exception as e:
            print_error(f"Authentication failed: {str(e)}")
            return False

        # Test payment creation
        print_info("\nTesting payment order creation...")
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
            print_error(f"Order creation error: {str(e)}")
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
        # Check configuration from constance
        print_info("Checking PayPal configuration from django-constance...")

        client_id = config.PAYPAL_CLIENT_ID
        client_secret = config.PAYPAL_CLIENT_SECRET
        mode = config.PAYPAL_MODE

        if not client_id or not client_secret:
            print_error("PayPal credentials not configured in constance")
            print_info("Configure via admin panel or .env + update_paypal_config.py")
            return False

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

        # Test API connection using requests library (more reliable)
        print_info("\nTesting PayPal API connection...")
        try:
            import requests

            # Determine API endpoint based on mode
            if mode.lower() == "sandbox":
                base_url = "https://api-m.sandbox.paypal.com"
            else:
                base_url = "https://api-m.paypal.com"

            url = f"{base_url}/v1/oauth2/token"
            headers = {"Accept": "application/json", "Accept-Language": "en_US"}
            data = {"grant_type": "client_credentials"}

            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(client_id, client_secret),
                timeout=10,
            )

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")

                print_success(f"API connection successful!")
                print_result("Token", f"{access_token[:30]}...")
                print_result("Expires In", f"{token_data.get('expires_in')} seconds")

                # Test order creation
                print_info("\nTesting PayPal order creation...")
                try:
                    order_url = f"{base_url}/v2/checkout/orders"
                    order_headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    }
                    order_data = {
                        "intent": "CAPTURE",
                        "purchase_units": [
                            {
                                "amount": {"currency_code": "USD", "value": "10.00"},
                                "description": "Test Payment",
                            }
                        ],
                        "payer": {"name": {"given_name": "Test", "surname": "User"}},
                    }

                    order_response = requests.post(
                        order_url, json=order_data, headers=order_headers, timeout=10
                    )

                    if order_response.status_code == 201:
                        order_result = order_response.json()
                        print_success("Test order created successfully!")
                        print_result("Order ID", order_result.get("id", "N/A"))
                        print_result("Status", order_result.get("status", "N/A"))
                        return True
                    else:
                        print_error(
                            f"Order creation failed: {order_response.status_code}"
                        )
                        print_error(f"Response: {order_response.text}")
                        return False

                except Exception as e:
                    print_error(f"Order creation error: {str(e)}")
                    return False

            else:
                print_error(f"API authentication failed: {response.status_code}")
                print_error(f"Response: {response.text}")

                if response.status_code == 401:
                    print_info("\n💡 Hint: Authentication failed. This usually means:")
                    print_info("   1. PAYPAL_CLIENT_ID is incorrect")
                    print_info("   2. PAYPAL_CLIENT_SECRET is incorrect")
                    print_info(
                        "   3. Credentials don't match the mode (sandbox vs live)"
                    )
                    print_info(
                        "   4. Check PayPal Developer: https://developer.paypal.com/"
                    )

                return False

        except requests.exceptions.RequestException as e:
            print_error(f"Network error: {str(e)}")
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
        # Check configuration from constance
        print_info("Checking Twilio configuration from django-constance...")

        account_sid = config.TWILIO_ACCOUNT_SID
        auth_token = config.TWILIO_AUTH_TOKEN
        from_number = config.TWILIO_PHONE_NUMBER

        if not account_sid or not auth_token or not from_number:
            print_error("Twilio credentials not configured in constance")
            print_info("Configure via .env or admin panel")
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
                message = client.messages.create(
                    body="Test SMS from IdrissiMart - Production test",
                    from_=from_number,
                    to=phone_number,
                )

                if message.sid:
                    print_success("Test SMS sent successfully!")
                    print_result("Message SID", message.sid)
                    return True
                else:
                    print_error("SMS sending failed - no message SID")
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
  python test_production_services.py --settings=idrissimart.settings.local --all
  python test_production_services.py --settings=idrissimart.settings.docker --paypal

Available settings modules:
  - idrissimart.settings.local     (development with SQLite)
  - idrissimart.settings.docker    (production with MySQL in Docker)
  - idrissimart.settings.common    (shared settings)

Note:
  This script uses django-constance which loads credentials from environment variables.
  Credentials are configured in:
  - .env file (development)
  - environment.production file (production)
  - System environment variables (docker/production)        """,
    )

    parser.add_argument(
        "--settings",
        metavar="MODULE",
        help="Django settings module to use (default: idrissimart.settings.docker)",
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
        return 0

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
