#!/usr/bin/env python
"""
PayPal Integration Test Suite
Tests PayPal payment gateway functionality
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test_paypal.log")

django.setup()

import requests
from decimal import Decimal
from constance import config
from main.services.paypal_service import PayPalService

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

print(f"\n{BLUE}{'=' * 70}")
print("PAYPAL PAYMENT GATEWAY TEST SUITE")
print(f"{'=' * 70}{END}\n")

def test_configuration():
    """Test 1: Check PayPal configuration"""
    print(f"{BLUE}[TEST 1] Checking PayPal Configuration{END}")
    print("-" * 70)

    client_id = config.PAYPAL_CLIENT_ID
    client_secret = config.PAYPAL_CLIENT_SECRET
    mode = config.PAYPAL_MODE

    if not client_id or client_id == "your-paypal-client-id-here":
        print(f"{RED}✗ FAILED: PayPal Client ID not configured{END}")
        print("  Set PAYPAL_CLIENT_ID in .env file")
        return False

    if not client_secret or client_secret == "your-paypal-client-secret-here":
        print(f"{RED}✗ FAILED: PayPal Client Secret not configured{END}")
        print("  Set PAYPAL_CLIENT_SECRET in .env file")
        return False

    print(f"{GREEN}✓ PASSED: Configuration found{END}")
    print(f"  Mode: {mode}")
    print(f"  Client ID: {client_id[:20]}...")
    print(f"  Secret: {client_secret[:20]}...\n")
    return True

def test_is_enabled():
    """Test 2: Check if PayPal is enabled"""
    print(f"{BLUE}[TEST 2] Checking if PayPal is Enabled{END}")
    print("-" * 70)

    is_enabled = PayPalService.is_enabled()

    if is_enabled:
        print(f"{GREEN}✓ PASSED: PayPal is enabled{END}\n")
        return True
    else:
        print(f"{RED}✗ FAILED: PayPal is not enabled{END}\n")
        return False

def test_base_url():
    """Test 3: Check correct API endpoint"""
    print(f"{BLUE}[TEST 3] Checking API Endpoint{END}")
    print("-" * 70)

    mode = config.PAYPAL_MODE.lower()
    base_url = PayPalService.get_base_url()

    if mode == "sandbox":
        expected_url = "https://api-m.sandbox.paypal.com"
    else:
        expected_url = "https://api-m.paypal.com"

    if base_url == expected_url:
        print(f"{GREEN}✓ PASSED: Correct endpoint{END}")
        print(f"  Mode: {mode}")
        print(f"  URL: {base_url}\n")
        return True
    else:
        print(f"{RED}✗ FAILED: Wrong endpoint{END}")
        print(f"  Expected: {expected_url}")
        print(f"  Got: {base_url}\n")
        return False

def test_access_token():
    """Test 4: Get OAuth access token"""
    print(f"{BLUE}[TEST 4] Testing OAuth Access Token{END}")
    print("-" * 70)

    try:
        access_token = PayPalService.get_access_token()

        if access_token:
            print(f"{GREEN}✓ PASSED: Access token obtained{END}")
            print(f"  Token: {access_token[:50]}...")
            print(f"  Length: {len(access_token)} characters\n")
            return True, access_token
        else:
            print(f"{RED}✗ FAILED: Could not obtain access token{END}")
            print("  Check your PayPal credentials\n")
            return False, None
    except Exception as e:
        print(f"{RED}✗ FAILED: {str(e)}{END}\n")
        return False, None

def test_create_order():
    """Test 5: Create a test order"""
    print(f"{BLUE}[TEST 5] Creating Test Order{END}")
    print("-" * 70)

    try:
        success, order_data, error = PayPalService.create_order(
            amount=Decimal("9.99"),
            currency="USD",
            order_id="TEST-ORDER-001",
            description="Test Order for PayPal Integration",
            return_url="http://localhost:8000/payment/success/",
            cancel_url="http://localhost:8000/payment/cancel/"
        )

        if success and order_data:
            order_id = order_data.get("id")
            status = order_data.get("status")

            print(f"{GREEN}✓ PASSED: Order created successfully{END}")
            print(f"  Order ID: {order_id}")
            print(f"  Status: {status}")
            print(f"  Amount: $9.99 USD")

            # Show approval link if available
            links = order_data.get("links", [])
            for link in links:
                if link.get("rel") == "approve":
                    print(f"  Approval Link: {link.get('href')}")
            print()
            return True, order_id
        else:
            print(f"{RED}✗ FAILED: Could not create order{END}")
            print(f"  Error: {error}\n")
            return False, None
    except Exception as e:
        print(f"{RED}✗ FAILED: {str(e)}{END}\n")
        return False, None

def test_get_order_details(order_id):
    """Test 6: Get order details"""
    print(f"{BLUE}[TEST 6] Getting Order Details{END}")
    print("-" * 70)

    try:
        success, order_data, error = PayPalService.get_order_details(order_id)

        if success and order_data:
            print(f"{GREEN}✓ PASSED: Order details retrieved{END}")
            print(f"  Order ID: {order_data.get('id')}")
            print(f"  Status: {order_data.get('status')}")

            # Show purchase units
            purch_units = order_data.get("purchase_units", [])
            for unit in purch_units:
                amount = unit.get("amount", {})
                print(f"  Amount: {amount.get('currency_code')} {amount.get('value')}")
            print()
            return True
        else:
            print(f"{RED}✗ FAILED: Could not get order details{END}")
            print(f"  Error: {error}\n")
            return False
    except Exception as e:
        print(f"{RED}✗ FAILED: {str(e)}{END}\n")
        return False

def test_network_connectivity():
    """Test 7: Network connectivity to PayPal"""
    print(f"{BLUE}[TEST 7] Network Connectivity{END}")
    print("-" * 70)

    try:
        mode = config.PAYPAL_MODE.lower()
        if mode == "sandbox":
            test_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        else:
            test_url = "https://api-m.paypal.com/v1/oauth2/token"

        response = requests.head(test_url, timeout=5)

        print(f"{GREEN}✓ PASSED: Network connectivity OK{END}")
        print(f"  Server: {test_url}")
        print(f"  Status: {response.status_code}\n")
        return True
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ FAILED: Cannot reach PayPal API{END}")
        print(f"  Error: {str(e)}")
        print("  Possible issues:")
        print("  1. Internet connection not available")
        print("  2. PayPal API is temporarily unavailable")
        print("  3. Firewall/proxy blocking requests\n")
        return False

# Run all tests
def run_all_tests():
    """Run all PayPal tests"""
    print()
    tests_passed = 0
    tests_total = 7

    # Test 1: Configuration
    if test_configuration():
        tests_passed += 1

    # Test 2: Is enabled
    if test_is_enabled():
        tests_passed += 1

    # Test 3: Base URL
    if test_base_url():
        tests_passed += 1

    # Test 4: Access token
    token_success, access_token = test_access_token()
    if token_success:
        tests_passed += 1

    # Test 5: Create order
    if token_success:
        order_success, order_id = test_create_order()
        if order_success:
            tests_passed += 1

            # Test 6: Get order details
            if test_get_order_details(order_id):
                tests_passed += 1

    # Test 7: Network connectivity
    if test_network_connectivity():
        tests_passed += 1

    # Summary
    print(f"{BLUE}{'=' * 70}")
    print("TEST SUMMARY")
    print(f"{'=' * 70}{END}")
    print(f"Tests Passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print(f"{GREEN}✓ ALL TESTS PASSED - PayPal Integration is Working!{END}\n")
        return True
    elif tests_passed >= 4:
        print(f"{YELLOW}⚠ PARTIAL SUCCESS - Some tests failed{END}\n")
        return False
    else:
        print(f"{RED}✗ TESTS FAILED - PayPal Integration has issues{END}\n")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

