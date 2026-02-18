#!/usr/bin/env python
"""
Quick Production Services Check
Fast check to verify all services are configured and accessible
"""

import os
import sys
import django

# Use docker settings for production (loads from environment.production)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.docker")

# Load .env file before Django setup
from dotenv import load_dotenv

load_dotenv()

# Set log file path for testing to avoid errors
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test.log")

try:
    django.setup()
except Exception as e:
    # If setup fails due to logging or other issues, try with local settings
    print(f"Warning: {e}")
    print("Falling back to local settings...")
    os.environ["DJANGO_SETTINGS_MODULE"] = "idrissimart.settings.local"
    django.setup()

from constance import config
from colorama import init, Fore, Style

init(autoreset=True)


def get_config_value(key):
    """Get config value from constance or environment"""
    try:
        # Try constance first
        value = getattr(config, key, None)
        if value and value != "":
            return value
    except:
        pass

    # Fallback to environment variable
    return os.getenv(key, "")


def check_service(name, checks):
    """Check if a service is configured"""
    print(f"\n{Fore.CYAN}━━━ {name} ━━━{Style.RESET_ALL}")

    all_ok = True
    for check_name, key_info in checks.items():
        # Handle optional fields
        if isinstance(key_info, tuple):
            key, optional = key_info
        else:
            key, optional = key_info, False

        value = get_config_value(key)
        if value and value != "":
            print(
                f"{Fore.GREEN}✓{Style.RESET_ALL} {check_name}: {'*' * 10}{str(value)[-5:]}"
            )
        elif optional:
            print(f"{Fore.YELLOW}○{Style.RESET_ALL} {check_name}: Optional (not set)")
        else:
            print(f"{Fore.RED}✗{Style.RESET_ALL} {check_name}: NOT SET")
            all_ok = False

    return all_ok


def main():
    print(f"{Fore.YELLOW}{'=' * 50}")
    print(f"  PRODUCTION SERVICES - QUICK CHECK")
    print(f"{'=' * 50}{Style.RESET_ALL}\n")

    results = {}

    # Check Paymob
    results["Paymob"] = check_service(
        "PAYMOB",
        {
            "API Key": "PAYMOB_API_KEY",
            "Secret Key": "PAYMOB_SECRET_KEY",
            "Public Key": "PAYMOB_PUBLIC_KEY",
            "Integration ID": ("PAYMOB_INTEGRATION_ID", True),  # Optional
        },
    )

    # Check PayPal
    results["PayPal"] = check_service(
        "PAYPAL",
        {
            "Client ID": "PAYPAL_CLIENT_ID",
            "Client Secret": "PAYPAL_CLIENT_SECRET",
            "Mode": "PAYPAL_MODE",
        },
    )

    # Check Twilio
    results["Twilio"] = check_service(
        "TWILIO SMS",
        {
            "Account SID": "TWILIO_ACCOUNT_SID",
            "Auth Token": "TWILIO_AUTH_TOKEN",
            "Phone Number": "TWILIO_PHONE_NUMBER",
        },
    )

    # Summary
    print(f"\n{Fore.YELLOW}{'=' * 50}")
    print("  SUMMARY")
    print(f"{'=' * 50}{Style.RESET_ALL}\n")

    for service, ok in results.items():
        status = (
            f"{Fore.GREEN}CONFIGURED{Style.RESET_ALL}"
            if ok
            else f"{Fore.RED}MISSING CONFIG{Style.RESET_ALL}"
        )
        print(f"  {service}: {status}")

    all_configured = all(results.values())

    print(f"\n{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}\n")

    if all_configured:
        print(f"{Fore.GREEN}✓ All services are configured!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}To test connectivity, run:{Style.RESET_ALL}")
        print(f"  poetry run python test_production_services.py --all\n")
        return 0
    else:
        print(f"{Fore.RED}✗ Some services need configuration{Style.RESET_ALL}")
        print(
            f"\n{Fore.CYAN}Update your .env file with the missing values{Style.RESET_ALL}\n"
        )
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Interrupted{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
