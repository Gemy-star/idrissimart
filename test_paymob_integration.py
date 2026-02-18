#!/usr/bin/env python
"""
Paymob Integration Test Suite
Tests Paymob payment gateway functionality
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test_paymob.log")

django.setup()

import requests
from constance import config
from main.services.paymob_service import PaymobService

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

print(f"\n{BLUE}{'=' * 70}")
print("PAYMOB PAYMENT GATEWAY TEST SUITE")
print(f"{'=' * 70}{END}\n")

def test_configuration():
    """Test 1: Check Paymob configuration"""
    print(f"{BLUE}[TEST 1] Checking Paymob Configuration{END}")
    print("-" * 70)

    api_key = config.PAYMOB_API_KEY
    integration_id = config.PAYMOB_INTEGRATION_ID
    iframe_id = config.PAYMOB_IFRAME_ID
    hmac_secret = config.PAYMOB_HMAC_SECRET

    all_configured = True

    if not api_key or api_key == "your-paymob-api-key-here":
        print(f"{RED}✗ PAYMOB_API_KEY not configured{END}")
        all_configured = False
    else:
        print(f"{GREEN}✓ API Key: {api_key[:20]}...{END}")

    if not integration_id or integration_id == "your-integration-id-here":
        print(f"{RED}✗ PAYMOB_INTEGRATION_ID not configured{END}")
        all_configured = False
    else:
        print(f"{GREEN}✓ Integration ID: {integration_id}{END}")

    if not iframe_id or iframe_id == "your-iframe-id-here":
        print(f"{RED}✗ PAYMOB_IFRAME_ID not configured{END}")
        all_configured = False
    else:
        print(f"{GREEN}✓ iFrame ID: {iframe_id}{END}")

    if not hmac_secret or hmac_secret == "your-hmac-secret-here":
        print(f"{YELLOW}⚠ PAYMOB_HMAC_SECRET not configured (needed for verification){END}")
    else:
        print(f"{GREEN}✓ HMAC Secret: {hmac_secret[:20]}...{END}")

    if all_configured:
        print(f"{GREEN}✓ PASSED: All required configuration found{END}\n")
        return True
    else:
        print(f"{RED}✗ FAILED: Some configuration missing{END}\n")
        return False

def test_is_enabled():
    """Test 2: Check if Paymob is enabled"""
    print(f"{BLUE}[TEST 2] Checking if Paymob is Enabled{END}")
    print("-" * 70)

    is_enabled = PaymobService.is_enabled()

    if is_enabled:
        print(f"{GREEN}✓ PASSED: Paymob is enabled{END}\n")
        return True
    else:
        print(f"{YELLOW}⚠ WARNING: Paymob is not enabled{END}")
        print("  Check PAYMOB_ENABLED setting in constance config\n")
        return True  # Don't fail on this

def test_base_url():
    """Test 3: Check API endpoint"""
    print(f"{BLUE}[TEST 3] Checking API Endpoint{END}")
    print("-" * 70)

    base_url = PaymobService.BASE_URL
    expected_url = "https://accept.paymob.com/api"

    if base_url == expected_url:
        print(f"{GREEN}✓ PASSED: Correct endpoint{END}")
        print(f"  URL: {base_url}\n")
        return True
    else:
        print(f"{RED}✗ FAILED: Wrong endpoint{END}")
        print(f"  Expected: {expected_url}")
        print(f"  Got: {base_url}\n")
        return False

def test_authentication():
    """Test 4: Test Paymob authentication"""
    print(f"{BLUE}[TEST 4] Testing Paymob Authentication{END}")
    print("-" * 70)

    try:
        auth_token = PaymobService.authenticate()

        if auth_token:
            print(f"{GREEN}✓ PASSED: Authentication successful{END}")
            print(f"  Token: {auth_token[:50]}...")
            print(f"  Length: {len(auth_token)} characters\n")
            return True, auth_token
        else:
            print(f"{RED}✗ FAILED: Could not authenticate{END}")
            print("  Check your Paymob API Key\n")
            return False, None
    except Exception as e:
        print(f"{RED}✗ FAILED: {str(e)}{END}\n")
        return False, None

def test_create_order(auth_token):
    """Test 5: Create a test order"""
    print(f"{BLUE}[TEST 5] Creating Test Order{END}")
    print("-" * 70)

    try:
        order_data = PaymobService.create_order(
            auth_token=auth_token,
            amount_cents=50000,  # 500 EGP
            currency="EGP",
            merchant_order_id="TEST-ORDER-001",
            items=[
                {
                    "name": "Test Item",
                    "description": "Test item for integration testing",
                    "amount": "50000",
                    "quantity": "1"
                }
            ]
        )

        if order_data:
            order_id = order_data.get("id")
            merchant_order_id = order_data.get("merchant_order_id")

            print(f"{GREEN}✓ PASSED: Order created successfully{END}")
            print(f"  Order ID: {order_id}")
            print(f"  Merchant Order ID: {merchant_order_id}")
            print(f"  Amount: 500 EGP\n")
            return True, order_id, auth_token
        else:
            print(f"{RED}✗ FAILED: Could not create order{END}\n")
            return False, None, None
    except Exception as e:
        print(f"{RED}✗ FAILED: {str(e)}{END}\n")
        return False, None, None

def test_create_payment_key(auth_token, order_id):
    """Test 6: Create payment key"""
    print(f"{BLUE}[TEST 6] Creating Payment Key{END}")
    print("-" * 70)

    try:
        billing_data = {
            "apartment": "Apt 1",
            "email": "test@example.com",
            "floor": "1",
            "first_name": "Test",
            "street": "Test Street",
            "phone_number": "+201001234567",
            "postal_code": "12345",
            "city": "Cairo",
            "country": "EG",
            "last_name": "User",
            "state": "Cairo"
        }

        payment_key = PaymobService.create_payment_key(
            auth_token=auth_token,
            order_id=order_id,
            amount_cents=50000,
            billing_data=billing_data,
            currency="EGP"
        )

        if payment_key:
            print(f"{GREEN}✓ PASSED: Payment key created{END}")
            print(f"  Payment Key: {payment_key[:50]}...")
            print(f"  Length: {len(payment_key)} characters\n")
            return True, payment_key
        else:
            print(f"{RED}✗ FAILED: Could not create payment key{END}\n")
            return False, None
    except Exception as e:
        print(f"{RED}✗ FAILED: {str(e)}{END}\n")
        return False, None

def test_get_iframe_url(payment_key):
    """Test 7: Get iFrame URL"""
    print(f"{BLUE}[TEST 7] Getting iFrame URL{END}")
    print("-" * 70)

    try:
        iframe_url = PaymobService.get_iframe_url(payment_key)

        if iframe_url:
            print(f"{GREEN}✓ PASSED: iFrame URL generated{END}")
            print(f"  URL: {iframe_url}\n")
            return True
        else:
            print(f"{RED}✗ FAILED: Could not generate iFrame URL{END}\n")
            return False
    except Exception as e:
        print(f"{RED}✗ FAILED: {str(e)}{END}\n")
        return False

def test_network_connectivity():
    """Test 8: Network connectivity to Paymob"""
    print(f"{BLUE}[TEST 8] Network Connectivity{END}")
    print("-" * 70)

    try:
        test_url = "https://accept.paymob.com/api/auth/tokens"
        response = requests.head(test_url, timeout=5)

        print(f"{GREEN}✓ PASSED: Network connectivity OK{END}")
        print(f"  Server: {test_url}")
        print(f"  Status: {response.status_code}\n")
        return True
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ FAILED: Cannot reach Paymob API{END}")
        print(f"  Error: {str(e)}")
        print("  Possible issues:")
        print("  1. Internet connection not available")
        print("  2. Paymob API is temporarily unavailable")
        print("  3. Firewall/proxy blocking requests\n")
        return False

# Run all tests
def run_all_tests():
    """Run all Paymob tests"""
    print()
    tests_passed = 0
    tests_total = 8

    # Test 1: Configuration
    if test_configuration():
        tests_passed += 1

    # Test 2: Is enabled
    if test_is_enabled():
        tests_passed += 1

    # Test 3: Base URL
    if test_base_url():
        tests_passed += 1

    # Test 4: Authentication
    auth_success, auth_token = test_authentication()
    if auth_success:
        tests_passed += 1

        # Test 5: Create order
        order_success, order_id, token = test_create_order(auth_token)
        if order_success:
            tests_passed += 1

            # Test 6: Create payment key
            key_success, payment_key = test_create_payment_key(auth_token, order_id)
            if key_success:
                tests_passed += 1

                # Test 7: Get iFrame URL
                if test_get_iframe_url(payment_key):
                    tests_passed += 1

    # Test 8: Network connectivity
    if test_network_connectivity():
        tests_passed += 1

    # Summary
    print(f"{BLUE}{'=' * 70}")
    print("TEST SUMMARY")
    print(f"{'=' * 70}{END}")
    print(f"Tests Passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print(f"{GREEN}✓ ALL TESTS PASSED - Paymob Integration is Working!{END}\n")
        return True
    elif tests_passed >= 5:
        print(f"{YELLOW}⚠ PARTIAL SUCCESS - Some tests failed{END}\n")
        return False
    else:
        print(f"{RED}✗ TESTS FAILED - Paymob Integration has issues{END}\n")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

