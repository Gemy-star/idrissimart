#!/usr/bin/env python
"""
View Production Service Test Logs
Shows detailed logs and debugging information for service test failures
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)


def print_header(title):
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{title.center(70)}")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")


def check_django_logs():
    """Check Django application logs"""
    print_header("DJANGO APPLICATION LOGS")

    log_locations = [
        "C:\\var\\log\\django\\idrissimart.log",  # Windows production
        "/var/log/django/idrissimart.log",  # Linux production
        os.path.join(os.getcwd(), "test.log"),  # Test log
        os.path.join(os.getcwd(), "django.log"),  # Local log
    ]

    found = False
    for log_path in log_locations:
        if os.path.exists(log_path):
            found = True
            print(f"{Fore.GREEN}✓ Found log file: {log_path}{Style.RESET_ALL}")

            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                if lines:
                    print(f"\n{Fore.YELLOW}Last 50 lines:{Style.RESET_ALL}")
                    for line in lines[-50:]:
                        if "ERROR" in line or "CRITICAL" in line:
                            print(f"{Fore.RED}{line.strip()}{Style.RESET_ALL}")
                        elif "WARNING" in line:
                            print(f"{Fore.YELLOW}{line.strip()}{Style.RESET_ALL}")
                        else:
                            print(line.strip())
                else:
                    print(f"{Fore.YELLOW}Log file is empty{Style.RESET_ALL}")

            except Exception as e:
                print(f"{Fore.RED}Error reading log: {e}{Style.RESET_ALL}")

    if not found:
        print(
            f"{Fore.YELLOW}No Django log files found in common locations{Style.RESET_ALL}"
        )
        print("\nTo enable logging, ensure DJANGO_LOG_FILE is set in your environment")


def check_service_responses():
    """Show how to check service-specific logs"""
    print_header("SERVICE-SPECIFIC DEBUGGING")

    print(f"{Fore.CYAN}📋 Paymob Debugging:{Style.RESET_ALL}")
    print(
        "   1. Check Paymob Dashboard: https://accept.paymob.com/portal2/en/dashboard"
    )
    print("   2. View API requests in: Dashboard > Developers > API Logs")
    print("   3. Verify API credentials: Dashboard > Settings > API Keys")
    print("   4. Test mode orders: Dashboard > Transactions")

    print(f"\n{Fore.CYAN}📋 PayPal Debugging:{Style.RESET_ALL}")
    print("   1. PayPal Developer Dashboard: https://developer.paypal.com/dashboard/")
    print("   2. View sandbox logs: Apps & Credentials > [Your App] > Sandbox Logs")
    print("   3. Check credentials: Apps & Credentials > [Your App] > API Credentials")
    print("   4. Test account details: Sandbox > Accounts")
    print("   5. Common issues:")
    print("      - Credentials expired (regenerate in dashboard)")
    print("      - Wrong mode (sandbox vs live)")
    print("      - App disabled or restricted")

    print(f"\n{Fore.CYAN}📋 Twilio Debugging:{Style.RESET_ALL}")
    print("   1. Twilio Console: https://console.twilio.com/")
    print("   2. View logs: Monitor > Logs > Error Logs")
    print("   3. Check credentials: Settings > General > API Credentials")
    print("   4. Account status: Console > Dashboard")
    print("   5. Common issues:")
    print("      - Auth Token expired (reset in Account Settings)")
    print("      - Account SID incorrect")
    print("      - Account suspended or trial limitations")
    print("      - IP address restrictions")


def check_environment_config():
    """Check environment configuration"""
    print_header("ENVIRONMENT CONFIGURATION")

    env_files = [".env", "environment.production", ".env.local", ".env.production"]

    print(f"{Fore.CYAN}Checking environment files:{Style.RESET_ALL}\n")

    for env_file in env_files:
        path = os.path.join(os.getcwd(), env_file)
        if os.path.exists(path):
            print(f"{Fore.GREEN}✓ Found: {env_file}{Style.RESET_ALL}")

            # Show which keys are set (without values)
            try:
                with open(path, "r") as f:
                    lines = f.readlines()

                service_keys = {
                    "Paymob": [
                        "PAYMOB_API_KEY",
                        "PAYMOB_SECRET_KEY",
                        "PAYMOB_PUBLIC_KEY",
                    ],
                    "PayPal": [
                        "PAYPAL_CLIENT_ID",
                        "PAYPAL_CLIENT_SECRET",
                        "PAYPAL_MODE",
                    ],
                    "Twilio": [
                        "TWILIO_ACCOUNT_SID",
                        "TWILIO_AUTH_TOKEN",
                        "TWILIO_PHONE_NUMBER",
                    ],
                }

                for service, keys in service_keys.items():
                    found_keys = []
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        for key in keys:
                            if line.startswith(key + "="):
                                value = line.split("=", 1)[1].strip()
                                if value and value not in ['""', "''", ""]:
                                    found_keys.append(key)

                    if found_keys:
                        print(f"  {service}: {', '.join(found_keys)}")

            except Exception as e:
                print(f"  {Fore.RED}Error reading file: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}○ Not found: {env_file}{Style.RESET_ALL}")


def show_debugging_tips():
    """Show general debugging tips"""
    print_header("DEBUGGING TIPS")

    print(f"{Fore.CYAN}🔍 Quick Checks:{Style.RESET_ALL}")
    print("   1. Run with verbose output:")
    print(
        "      poetry run python test_production_services.py --paymob 2>&1 | tee test.log"
    )
    print()
    print("   2. Check Django settings:")
    print("      poetry run python manage.py diffsettings")
    print()
    print("   3. Test database connection:")
    print("      poetry run python manage.py check --database default")
    print()
    print("   4. View constance configuration:")
    print("      poetry run python manage.py shell")
    print("      >>> from constance import config")
    print("      >>> print(config.PAYMOB_API_KEY[:20])")
    print()
    print(f"{Fore.CYAN}📊 Enable Debug Mode (Testing Only):{Style.RESET_ALL}")
    print("   1. Set DEBUG=True in .env")
    print("   2. Check Django debug toolbar logs")
    print("   3. View detailed error pages")
    print()
    print(f"{Fore.CYAN}🔐 Security Reminders:{Style.RESET_ALL}")
    print("   ⚠️  Never commit real credentials to git")
    print("   ⚠️  Use environment variables for secrets")
    print("   ⚠️  Keep DEBUG=False in production")
    print("   ⚠️  Rotate credentials if exposed")


def show_common_errors():
    """Show common errors and solutions"""
    print_header("COMMON ERRORS & SOLUTIONS")

    errors = [
        {
            "error": "Cannot read properties of null (reading 'addEventListener')",
            "cause": "JavaScript trying to access element that doesn't exist",
            "solution": "Add null checks before addEventListener calls",
        },
        {
            "error": "Twilio Error 20003: Authenticate",
            "cause": "Invalid Twilio credentials",
            "solution": "1. Verify Account SID and Auth Token in Twilio Console\n"
            + "               2. Ensure credentials match the account\n"
            + "               3. Check if account is active (not suspended)",
        },
        {
            "error": "PayPal 'client_id' error",
            "cause": "PayPal SDK configuration issue",
            "solution": "1. Verify CLIENT_ID and CLIENT_SECRET are correct\n"
            + "               2. Ensure mode matches credentials (sandbox/live)\n"
            + "               3. Regenerate credentials in PayPal Developer Portal",
        },
        {
            "error": "Paymob Authentication Failed",
            "cause": "Invalid or expired Paymob API key",
            "solution": "1. Check API key in Paymob Dashboard\n"
            + "               2. Ensure API key is for correct environment (test/live)\n"
            + "               3. Regenerate API key if expired",
        },
        {
            "error": "Database connection refused",
            "cause": "MySQL/MariaDB not running or wrong credentials",
            "solution": "1. Start database: sudo systemctl start mariadb\n"
            + "               2. Check DB credentials in .env\n"
            + "               3. Verify DB_HOST and DB_PORT",
        },
    ]

    for i, err in enumerate(errors, 1):
        print(f"{Fore.YELLOW}{i}. {err['error']}{Style.RESET_ALL}")
        print(f"   Cause: {err['cause']}")
        print(f"   Solution: {err['solution']}")
        print()


def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 70)
    print("  PRODUCTION SERVICES - LOG VIEWER & DEBUGGING GUIDE")
    print("=" * 70)
    print(Style.RESET_ALL)

    # Check logs
    check_django_logs()

    # Show service debugging
    check_service_responses()

    # Check environment
    check_environment_config()

    # Show debugging tips
    show_debugging_tips()

    # Show common errors
    show_common_errors()

    print(f"\n{Fore.GREEN}{'=' * 70}")
    print("For more help, check TEST_SERVICES_GUIDE.md")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback

        traceback.print_exc()
