#!/usr/bin/env python
"""
Complete Payment Testing Guide for Ad Checkout
Tests both PayPal and Paymob payment gateways
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test_payments.log")

django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from constance import config
from main.services.paypal_service import PayPalService
from main.services.paymob_service import PaymobService
from main.models import Payment

User = get_user_model()

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
END = '\033[0m'

print(f"\n{BLUE}{'=' * 80}")
print("PAYMENT GATEWAY TESTING - AD CHECKOUT WORKFLOW")
print(f"{'=' * 80}{END}\n")

def print_section(title):
    """Print a section header"""
    print(f"\n{CYAN}{title}{END}")
    print("-" * 80)

def test_paypal_workflow():
    """Test complete PayPal payment workflow"""
    print_section("PAYPAL PAYMENT WORKFLOW TEST")

    print(f"\n{BLUE}[STEP 1] Check Configuration{END}")
    if not PayPalService.is_enabled():
        print(f"{RED}✗ PayPal not configured{END}")
        return False
    print(f"{GREEN}✓ PayPal configured{END}")

    print(f"\n{BLUE}[STEP 2] Get Access Token{END}")
    access_token = PayPalService.get_access_token()
    if not access_token:
        print(f"{RED}✗ Failed to get access token{END}")
        return False
    print(f"{GREEN}✓ Got access token{END}")
    print(f"  Token: {access_token[:50]}...")

    print(f"\n{BLUE}[STEP 3] Create PayPal Order{END}")
    success, order_data, error = PayPalService.create_order(
        amount=Decimal("29.99"),
        currency="USD",
        order_id="AD-PACKAGE-TEST-001",
        description="Test Ad Package - Premium Plan",
        return_url="http://localhost:8000/ads/payment/success/",
        cancel_url="http://localhost:8000/ads/payment/cancel/"
    )

    if not success:
        print(f"{RED}✗ Failed to create PayPal order{END}")
        print(f"  Error: {error}")
        return False

    order_id = order_data.get("id")
    print(f"{GREEN}✓ PayPal order created{END}")
    print(f"  Order ID: {order_id}")
    print(f"  Amount: $29.99 USD")
    print(f"  Status: {order_data.get('status')}")

    # Get approval link
    links = order_data.get("links", [])
    for link in links:
        if link.get("rel") == "approve":
            print(f"  Approval Link: {link.get('href')}")

    print(f"\n{BLUE}[STEP 4] Get Order Details{END}")
    success, details, error = PayPalService.get_order_details(order_id)
    if success:
        print(f"{GREEN}✓ Order details retrieved{END}")
        print(f"  Status: {details.get('status')}")
    else:
        print(f"{YELLOW}⚠ Could not get details{END}")

    return True

def test_paymob_workflow():
    """Test complete Paymob payment workflow"""
    print_section("PAYMOB PAYMENT WORKFLOW TEST")

    print(f"\n{BLUE}[STEP 1] Check Configuration{END}")

    # Check individual credentials
    api_key = config.PAYMOB_API_KEY
    integration_id = config.PAYMOB_INTEGRATION_ID
    iframe_id = config.PAYMOB_IFRAME_ID
    hmac_secret = config.PAYMOB_HMAC_SECRET
    enabled = config.PAYMOB_ENABLED

    all_configured = True

    if api_key and api_key != "your-paymob-api-key-here":
        print(f"{GREEN}✓ API Key configured{END}")
    else:
        print(f"{RED}✗ API Key missing{END}")
        all_configured = False

    if integration_id and integration_id != "123456":
        print(f"{GREEN}✓ Integration ID: {integration_id}{END}")
    else:
        print(f"{YELLOW}⚠ Integration ID: placeholder or missing{END}")
        all_configured = False

    if iframe_id:
        print(f"{GREEN}✓ iFrame ID configured{END}")
    else:
        print(f"{YELLOW}⚠ iFrame ID missing{END}")
        all_configured = False

    if hmac_secret:
        print(f"{GREEN}✓ HMAC Secret configured{END}")
    else:
        print(f"{YELLOW}⚠ HMAC Secret missing{END}")

    if not all_configured or not PaymobService.is_enabled():
        print(f"\n{RED}✗ Paymob not fully configured{END}")
        print("  Missing or placeholder values detected")
        print("  Add credentials to .env file and restart Django")
        return False

    print(f"{GREEN}✓ Paymob fully configured{END}")

    print(f"\n{BLUE}[STEP 2] Authenticate with Paymob{END}")
    auth_token = PaymobService.authenticate()
    if not auth_token:
        print(f"{RED}✗ Authentication failed{END}")
        return False
    print(f"{GREEN}✓ Authentication successful{END}")
    print(f"  Token: {auth_token[:50]}...")

    print(f"\n{BLUE}[STEP 3] Create Paymob Order{END}")
    # Amount in cents: 29.99 EGP = 2999 cents
    order_data = PaymobService.create_order(
        auth_token=auth_token,
        amount_cents=2999,
        currency="EGP",
        merchant_order_id="AD-PACKAGE-TEST-001",
        items=[
            {
                "name": "Premium Ad Package",
                "description": "Premium ad package for testing",
                "amount": 2999,
                "quantity": 1
            }
        ]
    )

    if not order_data:
        print(f"{RED}✗ Failed to create Paymob order{END}")
        return False

    order_id = order_data.get("id")
    print(f"{GREEN}✓ Paymob order created{END}")
    print(f"  Order ID: {order_id}")
    print(f"  Amount: 29.99 EGP")
    print(f"  Status: {order_data.get('status')}")

    print(f"\n{BLUE}[STEP 4] Create Payment Key{END}")
    billing_data = {
        "apartment": "123",
        "email": "test@example.com",
        "floor": "4",
        "first_name": "Test",
        "street": "Test Street",
        "postal_code": "12345",
        "city": "Cairo",
        "phone_number": "201001234567",
        "last_name": "User",
        "state": "Cairo",
        "country": "EG"
    }

    payment_key = PaymobService.create_payment_key(
        auth_token=auth_token,
        order_id=order_id,
        amount_cents=2999,
        billing_data=billing_data,
        currency="EGP"
    )

    if not payment_key:
        print(f"{RED}✗ Failed to create payment key{END}")
        return False

    print(f"{GREEN}✓ Payment key created{END}")
    print(f"  Key: {payment_key[:50]}...")

    print(f"\n{BLUE}[STEP 5] Get iFrame URL{END}")
    iframe_url = PaymobService.get_iframe_url(payment_key)
    print(f"{GREEN}✓ iFrame URL generated{END}")
    print(f"  URL: {iframe_url[:80]}...")

    return True

def test_payment_model():
    """Test Payment model functionality"""
    print_section("PAYMENT MODEL TEST")

    print(f"\n{BLUE}[STEP 1] Get or Create Test User{END}")
    user, created = User.objects.get_or_create(
        username="test_payment_user",
        defaults={
            "email": "test@example.com",
            "password": "test_payment_password_12345",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    # If user was just created, set the password properly
    if created:
        user.set_password("test_payment_password_12345")
        user.save()

    if created:
        print(f"{GREEN}✓ Test user created{END}")
    else:
        print(f"{GREEN}✓ Test user found{END}")
    print(f"  Username: {user.username}")

    print(f"\n{BLUE}[STEP 2] Create PayPal Payment Record{END}")
    paypal_payment, created = Payment.objects.get_or_create(
        provider_transaction_id="PAYPAL-TEST-001",
        defaults={
            "user": user,
            "provider": Payment.PaymentProvider.PAYPAL,
            "amount": Decimal("29.99"),
            "currency": "USD",
            "status": Payment.PaymentStatus.PENDING,
            "description": "Premium Ad Package - Testing",
        }
    )

    if created:
        print(f"{GREEN}✓ PayPal payment record created{END}")
    else:
        print(f"{GREEN}✓ PayPal payment record found{END}")
    print(f"  ID: {paypal_payment.id}")
    print(f"  Amount: {paypal_payment.amount} {paypal_payment.currency}")
    print(f"  Status: {paypal_payment.get_status_display()}")

    print(f"\n{BLUE}[STEP 3] Create Paymob Payment Record{END}")
    paymob_payment, created = Payment.objects.get_or_create(
        provider_transaction_id="PAYMOB-TEST-001",
        defaults={
            "user": user,
            "provider": Payment.PaymentProvider.PAYMOB,
            "amount": Decimal("29.99"),
            "currency": "EGP",
            "status": Payment.PaymentStatus.PENDING,
            "description": "Premium Ad Package - Testing",
        }
    )

    if created:
        print(f"{GREEN}✓ Paymob payment record created{END}")
    else:
        print(f"{GREEN}✓ Paymob payment record found{END}")
    print(f"  ID: {paymob_payment.id}")
    print(f"  Amount: {paymob_payment.amount} {paymob_payment.currency}")
    print(f"  Status: {paymob_payment.get_status_display()}")

    print(f"\n{BLUE}[STEP 4] Test Mark Completed{END}")
    paypal_payment.mark_completed(transaction_id="PAYPAL-TXN-123456")
    print(f"{GREEN}✓ Payment marked as completed{END}")
    print(f"  Status: {paypal_payment.get_status_display()}")
    print(f"  Transaction ID: {paypal_payment.provider_transaction_id}")

    print(f"\n{BLUE}[STEP 5] List All Payments{END}")
    payments = Payment.objects.all()
    print(f"  Total payments: {payments.count()}")
    for payment in payments[:5]:
        print(f"  - {payment.user.username}: {payment.amount} {payment.currency} ({payment.get_status_display()})")

    return True

def print_quick_reference():
    """Print quick reference for manual testing"""
    print_section("QUICK REFERENCE - MANUAL TESTING")

    print(f"\n{CYAN}PayPal Testing:${END}")
    print("  1. Go to: http://localhost:8000/ads/checkout/")
    print("  2. Select 'PayPal' as payment method")
    print("  3. Click 'Checkout with PayPal'")
    print("  4. You'll be redirected to PayPal sandbox")
    print("  5. Use test account credentials from PayPal Developer Dashboard")
    print("  6. After approval, payment status should be marked as COMPLETED")

    print(f"\n{CYAN}Paymob Testing:${END}")
    print("  1. Go to: http://localhost:8000/ads/checkout/")
    print("  2. Select 'Paymob' as payment method")
    print("  3. Fill in billing information")
    print("  4. Click 'Pay with Paymob'")
    print("  5. Complete payment in Paymob iFrame")
    print("  6. Use test card numbers:")
    print("     - Mastercard: 5123456789012346")
    print("     - Visa: 4111111111111111")
    print("     - Any expiry date in future")
    print("     - Any CVV (3 digits)")
    print("  7. After approval, payment status should be marked as COMPLETED")

    print(f"\n{CYAN}Database Queries:${END}")
    print("  # View all payments:")
    print("  poetry run python manage.py shell")
    print("  >>> from main.models import Payment")
    print("  >>> Payment.objects.all().values('id', 'provider', 'amount', 'status')")
    print()
    print("  # View PayPal payments:")
    print("  >>> Payment.objects.filter(provider='paypal')")
    print()
    print("  # View completed payments:")
    print("  >>> Payment.objects.filter(status='completed')")

def main():
    """Run all tests"""
    print()

    tests_passed = 0
    tests_total = 3

    # Test 1: PayPal Workflow
    try:
        if test_paypal_workflow():
            tests_passed += 1
    except Exception as e:
        print(f"{RED}✗ PayPal test error: {str(e)}{END}")

    # Test 2: Paymob Workflow
    try:
        if test_paymob_workflow():
            tests_passed += 1
    except Exception as e:
        print(f"{RED}✗ Paymob test error: {str(e)}{END}")

    # Test 3: Payment Model
    try:
        if test_payment_model():
            tests_passed += 1
    except Exception as e:
        print(f"{RED}✗ Payment model test error: {str(e)}{END}")

    # Print Summary
    print_section("TEST SUMMARY")
    print(f"Tests Passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print(f"{GREEN}✓ ALL TESTS PASSED{END}")
    elif tests_passed >= 2:
        print(f"{YELLOW}⚠ PARTIAL SUCCESS{END}")
    else:
        print(f"{RED}✗ TESTS FAILED{END}")

    # Print Quick Reference
    print_quick_reference()

    print(f"\n{BLUE}{'=' * 80}{END}\n")

if __name__ == "__main__":
    main()

