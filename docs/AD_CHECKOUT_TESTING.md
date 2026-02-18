# 💳 Testing PayPal & Paymob in Ad Checkout

## Quick Start

### 1. Configure Credentials

Edit `.env` file:

```bash
# PayPal Sandbox
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-secret
PAYPAL_MODE=sandbox

# Paymob
PAYMOB_API_KEY=your-api-key
PAYMOB_INTEGRATION_ID=123456
PAYMOB_IFRAME_ID=789012
PAYMOB_HMAC_SECRET=your-hmac-secret
PAYMOB_ENABLED=true
```

### 2. Get Credentials

**PayPal:** https://developer.paypal.com/dashboard/
- Sandbox → Accounts → Business Account

**Paymob:** https://www.paymob.com/
- Integrations → Payment Acceptance

### 3. Restart Django

```bash
Ctrl + C
poetry run python manage.py runserver
```

## Run Automated Tests

```bash
# Complete test suite
poetry run python test_ad_checkout_payments.py

# PayPal only
poetry run python test_paypal_integration.py

# Paymob only  
poetry run python test_paymob_integration.py
```

## Manual Testing

### PayPal Flow

1. Go to: `http://localhost:8000/ads/checkout/`
2. Select PayPal → Pay
3. Log in to PayPal Sandbox
4. Approve payment
5. Verify in database

### Paymob Flow

1. Go to: `http://localhost:8000/ads/checkout/`
2. Select Paymob → Pay
3. Fill billing info
4. Use test card:
   - **Visa:** 4111111111111111
   - **Mastercard:** 5123456789012346
   - Expiry: 12/25, CVV: 123
5. Verify in database

## View Payments

```bash
poetry run python manage.py shell
```

```python
from main.models import Payment

# All payments
Payment.objects.all()

# PayPal payments
Payment.objects.filter(provider='paypal')

# Completed payments
Payment.objects.filter(status='completed')

# User's payments
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
Payment.objects.filter(user=user)
```

## Check Configuration

```bash
poetry run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings.local')
django.setup()
from constance import config

print('PayPal:', 'Configured' if config.PAYPAL_CLIENT_ID else 'Not configured')
print('Paymob:', 'Configured' if config.PAYMOB_API_KEY else 'Not configured')
"
```

## Test Cards (Paymob)

| Card Type | Number | Expiry | CVV |
|-----------|--------|--------|-----|
| Visa | 4111111111111111 | 12/25 | 123 |
| Mastercard | 5123456789012346 | 12/25 | 456 |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not configured" | Add credentials to .env, restart Django |
| "Connection error" | Check internet, verify API keys |
| "Payment not in database" | Check migrations: `poetry run python manage.py migrate` |
| "Email not sent" | Check SMTP settings in local.py |

---

**See full guide:** `PAYMENT_GATEWAY_TESTING.md`

