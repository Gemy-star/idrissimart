# 💳 Payment Gateway Testing Guide

## Overview

This guide shows you how to test both **PayPal** and **Paymob** payment gateway integrations in your idrissimart application.

## Prerequisites

1. ✅ Django running on your local environment
2. ✅ Python Poetry environment activated
3. ✅ Internet connection for API calls

## Setting Up Credentials

### PayPal Setup

#### Get PayPal Sandbox Credentials:

1. Go to: https://developer.paypal.com/dashboard/
2. Log in with your PayPal account (create one if needed)
3. Go to: **Sandbox** → **Accounts**
4. Copy your **Business Account** credentials:
   - **Client ID**: AWxxxxxxxxxxxxxxxx
   - **Secret**: ECxxxxxxxxxxxxxxxx

#### Configure PayPal in .env:

```bash
# Edit .env file
PAYPAL_CLIENT_ID=your-sandbox-client-id
PAYPAL_CLIENT_SECRET=your-sandbox-client-secret
PAYPAL_MODE=sandbox  # Use 'sandbox' for testing, 'live' for production
```

### Paymob Setup

#### Get Paymob Credentials:

1. Create account at: https://www.paymob.com/
2. Go to: **Integrations** → **Payment Keys**
3. Get your:
   - **API Key**: (also called API Token)
   - **Integration ID**: ID for Accept payments
   - **iFrame ID**: ID for iFrame integration
   - **HMAC Secret**: For verifying callbacks

#### Configure Paymob in .env:

```bash
# Edit .env file
PAYMOB_API_KEY=your-api-key
PAYMOB_INTEGRATION_ID=your-integration-id
PAYMOB_IFRAME_ID=your-iframe-id
PAYMOB_HMAC_SECRET=your-hmac-secret
PAYMOB_ENABLED=true  # Enable Paymob
```

## Testing PayPal Integration

### Quick Test

Run the simple test script:

```bash
poetry run python test_paypal_simple.py
```

This tests:
- Configuration check
- API connectivity
- Authentication with sandbox

### Comprehensive Test

Run the full test suite:

```bash
poetry run python test_paypal_integration.py
```

This tests:
1. ✅ Configuration
2. ✅ Is enabled
3. ✅ Correct API endpoint
4. ✅ OAuth access token
5. ✅ Create order
6. ✅ Get order details
7. ✅ Network connectivity

### Expected Output

```
======================================================================
PAYPAL PAYMENT GATEWAY TEST SUITE
======================================================================

[TEST 1] Checking PayPal Configuration
----------------------------------------------------------------------
✓ PASSED: Configuration found
  Mode: sandbox
  Client ID: AZU7IvJA...
  Secret: EHBVwhFYX...

[TEST 2] Checking if PayPal is Enabled
----------------------------------------------------------------------
✓ PASSED: PayPal is enabled

[TEST 3] Checking API Endpoint
----------------------------------------------------------------------
✓ PASSED: Correct endpoint
  Mode: sandbox
  URL: https://api-m.sandbox.paypal.com

[TEST 4] Testing OAuth Access Token
----------------------------------------------------------------------
✓ PASSED: Access token obtained
  Token: A21AAHsaFx...
  Length: 457 characters

[TEST 5] Creating Test Order
----------------------------------------------------------------------
✓ PASSED: Order created successfully
  Order ID: 5ME45851FR453892L
  Status: CREATED
  Amount: $9.99 USD
  Approval Link: https://sandbox.paypal.com/checkoutnow?token=EC-5ME...

[TEST 6] Getting Order Details
----------------------------------------------------------------------
✓ PASSED: Order details retrieved
  Order ID: 5ME45851FR453892L
  Status: CREATED
  Amount: USD 9.99

[TEST 7] Network Connectivity
----------------------------------------------------------------------
✓ PASSED: Network connectivity OK
  Server: https://api-m.sandbox.paypal.com/v1/oauth2/token
  Status: 200

======================================================================
TEST SUMMARY
======================================================================
Tests Passed: 7/7
✓ ALL TESTS PASSED - PayPal Integration is Working!
```

### Troubleshooting PayPal

#### ❌ "401 Unauthorized"
- **Cause**: Invalid Client ID or Secret
- **Fix**: Double-check credentials in PayPal Dashboard
- **Verify**: https://developer.paypal.com/dashboard/

#### ❌ "Connection Error"
- **Cause**: Network/firewall issue
- **Fix**: Check internet connection
- **Verify**: `ping api-m.sandbox.paypal.com`

#### ❌ "PayPal is not enabled"
- **Cause**: Credentials not in .env
- **Fix**: Add `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` to .env
- **Test**: Run `poetry run python manage.py shell -c "from constance import config; print(config.PAYPAL_CLIENT_ID)"`

## Testing Paymob Integration

### Quick Test

Run the simple authentication test:

```bash
poetry run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings.local')
django.setup()
from main.services.paymob_service import PaymobService
token = PaymobService.authenticate()
print('✓ Auth successful' if token else '✗ Auth failed')
"
```

### Comprehensive Test

Run the full test suite:

```bash
poetry run python test_paymob_integration.py
```

This tests:
1. ✅ Configuration
2. ✅ Is enabled
3. ✅ Correct API endpoint
4. ✅ Authentication
5. ✅ Create order
6. ✅ Create payment key
7. ✅ Get iFrame URL
8. ✅ Network connectivity

### Expected Output

```
======================================================================
PAYMOB PAYMENT GATEWAY TEST SUITE
======================================================================

[TEST 1] Checking Paymob Configuration
----------------------------------------------------------------------
✓ API Key: sk_live_2a3b4c5d6...
✓ Integration ID: 123456
✓ iFrame ID: 789012
✓ HMAC Secret: abcdef1234...
✓ PASSED: All required configuration found

[TEST 2] Checking if Paymob is Enabled
----------------------------------------------------------------------
✓ PASSED: Paymob is enabled

[TEST 3] Checking API Endpoint
----------------------------------------------------------------------
✓ PASSED: Correct endpoint
  URL: https://accept.paymob.com/api

[TEST 4] Testing Paymob Authentication
----------------------------------------------------------------------
✓ PASSED: Authentication successful
  Token: aAbBcCdDeEfFg...
  Length: 64 characters

[TEST 5] Creating Test Order
----------------------------------------------------------------------
✓ PASSED: Order created successfully
  Order ID: 123456789
  Merchant Order ID: TEST-ORDER-001
  Amount: 500 EGP

[TEST 6] Creating Payment Key
----------------------------------------------------------------------
✓ PASSED: Payment key created
  Payment Key: ZXhhbXBsZV9...
  Length: 356 characters

[TEST 7] Getting iFrame URL
----------------------------------------------------------------------
✓ PASSED: iFrame URL generated
  URL: https://accept.paymob.com/api/acceptance/iframes/789012?payment_token=ZXhhbXBsZV9...

[TEST 8] Network Connectivity
----------------------------------------------------------------------
✓ PASSED: Network connectivity OK
  Server: https://accept.paymob.com/api/auth/tokens
  Status: 200

======================================================================
TEST SUMMARY
======================================================================
Tests Passed: 8/8
✓ ALL TESTS PASSED - Paymob Integration is Working!
```

### Troubleshooting Paymob

#### ❌ "PAYMOB_API_KEY not configured"
- **Cause**: Missing API key in .env
- **Fix**: Add `PAYMOB_API_KEY` to .env
- **Get it from**: https://www.paymob.com/ → Integrations → API Keys

#### ❌ "Paymob is not enabled"
- **Cause**: `PAYMOB_ENABLED` not set to true
- **Fix**: Add `PAYMOB_ENABLED=true` to .env or configure in Django Constance

#### ❌ "Authentication failed"
- **Cause**: Invalid API Key
- **Fix**: Verify API key in Paymob dashboard
- **Test**: `curl -X POST https://accept.paymob.com/api/auth/tokens -H "Content-Type: application/json" -d '{"api_key":"your-key"}'`

#### ❌ "Connection Error"
- **Cause**: Network/firewall issue
- **Fix**: Check internet connection
- **Verify**: `ping accept.paymob.com`

## Integration Testing (End-to-End)

### Test Payment Flow

#### PayPal Flow:

```python
from decimal import Decimal
from main.services.paypal_service import PayPalService

# 1. Create order
success, order_data, error = PayPalService.create_order(
    amount=Decimal("50.00"),
    currency="USD",
    order_id="MYORDER-001",
    description="Test payment"
)

if success:
    paypal_order_id = order_data["id"]
    approval_link = [l for l in order_data["links"] if l["rel"] == "approve"][0]["href"]
    print(f"Send user to: {approval_link}")
    
    # 2. After user approves, capture order
    success, capture_data, error = PayPalService.capture_order(paypal_order_id)
    if success:
        print("✓ Payment captured successfully!")
```

#### Paymob Flow:

```python
from main.services.paymob_service import PaymobService

# 1. Authenticate
auth_token = PaymobService.authenticate()

# 2. Create order
order_data = PaymobService.create_order(
    auth_token=auth_token,
    amount_cents=5000,  # 50 EGP
    merchant_order_id="MYORDER-001"
)

# 3. Create payment key
payment_key = PaymobService.create_payment_key(
    auth_token=auth_token,
    order_id=order_data["id"],
    amount_cents=5000,
    billing_data={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "+201001234567",
        "city": "Cairo",
        "country": "EG"
    }
)

# 4. Get iFrame URL
iframe_url = PaymobService.get_iframe_url(payment_key)
print(f"Display payment in iFrame: {iframe_url}")
```

## Configuration Reference

### PayPal Configuration

| Setting | Value | Note |
|---------|-------|------|
| `PAYPAL_CLIENT_ID` | Your Client ID | From PayPal Dashboard |
| `PAYPAL_CLIENT_SECRET` | Your Secret | From PayPal Dashboard |
| `PAYPAL_MODE` | `sandbox` or `live` | Use `sandbox` for testing |

### Paymob Configuration

| Setting | Value | Note |
|---------|-------|------|
| `PAYMOB_API_KEY` | Your API Key | From Paymob Dashboard |
| `PAYMOB_INTEGRATION_ID` | Integration ID | For Accept payments |
| `PAYMOB_IFRAME_ID` | iFrame ID | For iFrame integration |
| `PAYMOB_HMAC_SECRET` | HMAC Secret | For callback verification |
| `PAYMOB_ENABLED` | `true` or `false` | Enable/disable Paymob |

## Quick Commands Reference

```bash
# Test PayPal simple auth
poetry run python test_paypal_simple.py

# Test PayPal full integration
poetry run python test_paypal_integration.py

# Test Paymob full integration
poetry run python test_paymob_integration.py

# Run all tests
poetry run python test_paypal_integration.py && poetry run python test_paymob_integration.py

# Check configuration
poetry run python manage.py shell -c "
from constance import config
print('PayPal:', config.PAYPAL_CLIENT_ID)
print('Paymob:', config.PAYMOB_API_KEY)
"
```

## Useful Resources

- **PayPal Developer Dashboard**: https://developer.paypal.com/dashboard
- **PayPal API Reference**: https://developer.paypal.com/docs/api/orders/v2/
- **Paymob Dashboard**: https://www.paymob.com/
- **Paymob API Docs**: https://docs.paymob.com/
- **PayPal Sandbox Testing**: https://developer.paypal.com/docs/checkout/reference/server-integration/
- **Paymob Integration Guide**: https://docs.paymob.com/docs/accept-payments

## Next Steps

1. ✅ Configure credentials in .env
2. ✅ Run test scripts to verify
3. ✅ Test in your application UI
4. ✅ Handle payment callbacks
5. ✅ Deploy to production

---

**Happy Testing! 🎉**

