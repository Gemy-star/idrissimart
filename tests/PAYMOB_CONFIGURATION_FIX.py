#!/usr/bin/env python
"""
Configuration Fix Helper
Shows what needs to be fixed in your .env file
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
django.setup()

from constance import config

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     PAYMENT GATEWAY CONFIGURATION CHECK                    ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

# Check PayPal
print("📘 PAYPAL CONFIGURATION")
print("─" * 80)

paypal_client = config.PAYPAL_CLIENT_ID
paypal_secret = config.PAYPAL_CLIENT_SECRET
paypal_mode = config.PAYPAL_MODE

if paypal_client and paypal_client != "your-paypal-client-id-here":
    print(f"✓ Client ID: Configured (length: {len(paypal_client)})")
else:
    print("✗ Client ID: Missing or placeholder")

if paypal_secret and paypal_secret != "your-paypal-client-secret-here":
    print(f"✓ Client Secret: Configured (length: {len(paypal_secret)})")
else:
    print("✗ Client Secret: Missing or placeholder")

print(f"✓ Mode: {paypal_mode}")

if paypal_client and paypal_secret:
    print(f"{chr(10)}✓ PAYPAL READY FOR TESTING")
else:
    print(f"{chr(10)}✗ PAYPAL NEEDS CONFIGURATION")

# Check Paymob
print(f"{chr(10)}{chr(10)}📗 PAYMOB CONFIGURATION")
print("─" * 80)

paymob_api = config.PAYMOB_API_KEY
paymob_secret = config.PAYMOB_SECRET_KEY
paymob_public = config.PAYMOB_PUBLIC_KEY
paymob_integration = config.PAYMOB_INTEGRATION_ID
paymob_iframe = config.PAYMOB_IFRAME_ID
paymob_hmac = config.PAYMOB_HMAC_SECRET
paymob_enabled = config.PAYMOB_ENABLED

missing = []

if paymob_api:
    print(f"✓ API Key: Configured (length: {len(paymob_api)})")
else:
    print("✗ API Key: Missing")
    missing.append("PAYMOB_API_KEY")

if paymob_secret:
    print(f"✓ Secret Key: Configured (length: {len(paymob_secret)})")
else:
    print("✗ Secret Key: Missing")
    missing.append("PAYMOB_SECRET_KEY")

if paymob_public:
    print(f"✓ Public Key: Configured (length: {len(paymob_public)})")
else:
    print("✗ Public Key: Missing")
    missing.append("PAYMOB_PUBLIC_KEY")

if paymob_integration and paymob_integration != "123456":
    print(f"✓ Integration ID: {paymob_integration}")
else:
    print("✗ Integration ID: Missing or placeholder (123456)")
    missing.append("PAYMOB_INTEGRATION_ID")

if paymob_iframe:
    print(f"✓ iFrame ID: {paymob_iframe}")
else:
    print("✗ iFrame ID: Missing")
    missing.append("PAYMOB_IFRAME_ID")

if paymob_hmac:
    print(f"✓ HMAC Secret: Configured (length: {len(paymob_hmac)})")
else:
    print("✗ HMAC Secret: Missing")
    missing.append("PAYMOB_HMAC_SECRET")

print(f"✓ Enabled: {paymob_enabled}")

if missing:
    print(f"{chr(10)}✗ PAYMOB NEEDS CONFIGURATION")
    print(f"Missing: {', '.join(missing)}")
else:
    print(f"{chr(10)}✓ PAYMOB READY FOR TESTING")

# Summary
print(f"{chr(10)}{chr(10)}╔════════════════════════════════════════════════════════════════════════════╗")
print("║                              SUMMARY & NEXT STEPS                             ║")
print("╚════════════════════════════════════════════════════════════════════════════════╝")

all_ready = not missing and paypal_client and paypal_secret

if all_ready:
    print("""
✓ ALL SYSTEMS GO!

Your payment gateways are fully configured.

Next steps:
  1. Restart Django: Ctrl + C, then poetry run python manage.py runserver
  2. Run tests: poetry run python test_ad_checkout_payments.py
  3. Test in browser: http://localhost:8000/ads/checkout/
""")
else:
    print("""
✗ CONFIGURATION INCOMPLETE

You need to:

1. Get your actual Paymob credentials from: https://www.paymob.com/
   - Dashboard → Integrations → Payment Acceptance
   - Find: Integration ID, iFrame ID
   - Dashboard → Settings → Webhooks → HMAC Secret

2. Edit your .env file:
   nano .env

3. Update these fields with your actual values:
   """)

    for field in missing:
        print(f"   - {field}=YOUR-VALUE-HERE")

    print(f"""
4. Restart Django:
   Ctrl + C
   poetry run python manage.py runserver

5. Run this script again to verify:
   python PAYMOB_CONFIGURATION_FIX.py

6. Run tests:
   poetry run python test_ad_checkout_payments.py
""")

print("═" * 80)

