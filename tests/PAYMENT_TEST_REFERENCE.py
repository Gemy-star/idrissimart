#!/usr/bin/env python
"""
Quick Reference: Testing PayPal & Paymob in Ad Checkout
Run this to see all available test commands
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                 PAYMENT GATEWAY TESTING - QUICK REFERENCE                  ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 PREREQUISITE: Configure .env file with credentials
────────────────────────────────────────────────────────────────────────────

1. Get PayPal Sandbox Credentials:
   └─ https://developer.paypal.com/dashboard/
   └─ Sandbox → Accounts → Business Account

2. Get Paymob Credentials:
   └─ https://www.paymob.com/
   └─ Integrations → Payment Acceptance

3. Update .env:
   ──────────────
   PAYPAL_CLIENT_ID=your-client-id
   PAYPAL_CLIENT_SECRET=your-secret
   PAYPAL_MODE=sandbox
   
   PAYMOB_API_KEY=your-api-key
   PAYMOB_INTEGRATION_ID=123456
   PAYMOB_IFRAME_ID=789012
   PAYMOB_HMAC_SECRET=your-hmac-secret
   PAYMOB_ENABLED=true

4. Restart Django:
   ──────────────
   Ctrl + C
   poetry run python manage.py runserver


🧪 AUTOMATED TESTS
────────────────────────────────────────────────────────────────────────────

# Complete payment workflow test (RECOMMENDED)
poetry run python test_ad_checkout_payments.py

# PayPal-only tests
poetry run python test_paypal_integration.py

# Paymob-only tests
poetry run python test_paymob_integration.py

# Simple PayPal authentication test
poetry run python test_paypal_simple.py


🌐 MANUAL TESTING IN WEB UI
────────────────────────────────────────────────────────────────────────────

PayPal Checkout:
  1. Go to: http://localhost:8000/ads/checkout/
  2. Select 'PayPal' as payment method
  3. Click 'Pay with PayPal'
  4. Log in with PayPal test account credentials
  5. Review and approve payment
  6. Verify payment status in database

Paymob Checkout:
  1. Go to: http://localhost:8000/ads/checkout/
  2. Select 'Paymob' as payment method
  3. Fill in billing information
  4. Click 'Pay with Paymob'
  5. Use test card numbers (see below)
  6. Complete payment in iFrame
  7. Verify payment status in database

Test Card Numbers (Paymob):
  ├─ Visa: 4111111111111111, Exp: 12/25, CVV: 123
  └─ Mastercard: 5123456789012346, Exp: 12/25, CVV: 456


📊 VIEW PAYMENTS IN DATABASE
────────────────────────────────────────────────────────────────────────────

# Open Django shell
poetry run python manage.py shell

# View all payments
from main.models import Payment
Payment.objects.all()

# View PayPal payments
Payment.objects.filter(provider='paypal')

# View Paymob payments
Payment.objects.filter(provider='paymob')

# View completed payments
Payment.objects.filter(status='completed')

# View specific user's payments
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
Payment.objects.filter(user=user)


🔍 DEBUG & VERIFY
────────────────────────────────────────────────────────────────────────────

# Check configuration
poetry run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings.local')
django.setup()
from constance import config
print('PayPal:', 'Configured' if config.PAYPAL_CLIENT_ID else 'Not configured')
print('Paymob:', 'Configured' if config.PAYMOB_API_KEY else 'Not configured')
"

# Test API connectivity
poetry run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings.local')
django.setup()
from main.services.paypal_service import PayPalService
from main.services.paymob_service import PaymobService

print('Testing PayPal...')
token = PayPalService.get_access_token()
print('✓ PayPal OK' if token else '✗ PayPal Failed')

print('Testing Paymob...')
token = PaymobService.authenticate()
print('✓ Paymob OK' if token else '✗ Paymob Failed')
"

# View email logs
tail -f test.log

# View Django logs
poetry run python manage.py runserver --verbosity 2


💾 ADMIN INTERFACE
────────────────────────────────────────────────────────────────────────────

# View all payments via web interface
http://localhost:8000/admin/
→ Payments section


🆘 TROUBLESHOOTING
────────────────────────────────────────────────────────────────────────────

Issue: "PayPal not configured"
└─ Fix: Add PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET to .env, restart Django

Issue: "Paymob authentication failed"
└─ Fix: Verify PAYMOB_API_KEY in .env, check Paymob dashboard

Issue: "Connection error"
└─ Fix: Check internet connection, verify API endpoints are reachable

Issue: "Payment not in database"
└─ Fix: Run migrations: poetry run python manage.py migrate

Issue: "Email not sent"
└─ Fix: Check EMAIL settings in idrissimart/settings/local.py


📚 FULL DOCUMENTATION
────────────────────────────────────────────────────────────────────────────

├─ AD_CHECKOUT_TESTING.md ..................... Quick guide
├─ PAYMENT_GATEWAY_TESTING.md ................. Full guide
├─ PAYMENT_TESTING_QUICKREF.md ................ Reference
└─ test_ad_checkout_payments.py ............... Main test script


🎯 SUCCESS CHECKLIST
────────────────────────────────────────────────────────────────────────────

□ Credentials added to .env
□ Django restarted with new credentials
□ Automated tests pass: test_ad_checkout_payments.py
□ PayPal payment workflow works end-to-end
□ Paymob payment workflow works end-to-end
□ Payments appear in database with correct status
□ Email notifications sent correctly
□ Ad package activated after payment
□ Admin interface shows all payments


═════════════════════════════════════════════════════════════════════════════

Ready to test? Run:

    poetry run python test_ad_checkout_payments.py

═════════════════════════════════════════════════════════════════════════════
""")

