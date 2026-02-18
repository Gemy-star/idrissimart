# 🚀 QUICK FIX: Configure Paymob & PayPal Credentials

## Current Status

✅ PayPal: Credentials found
❌ Paymob: Incomplete configuration (missing IFRAME_ID and HMAC_SECRET)

## What You Need to Do

### 1. Get Your Complete Paymob Credentials

Go to: **https://www.paymob.com/** → Dashboard

Navigate to:
- **Settings** → **Developers** → **API Keys**
  - Copy: **API Key** (you have this)
  - Copy: **Secret Key** (you have this)
  - Copy: **Public Key** (you have this)

- **Integrations** → **Payment Methods** → **Accept Online Payments**
  - Find "Accept" integration
  - Copy: **Integration ID** (use this)
  - Copy: **iFrame ID** (currently empty - NEED THIS!)

- **Settings** → **Webhook/Callbacks** → **HMAC**
  - Copy: **HMAC Secret** (currently empty - NEED THIS!)

### 2. Update Your .env File

Edit your `.env` file and update the Paymob section:

**Current (Incorrect):**
```bash
PAYMOB_API_KEY=ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5...
PAYMOB_SECRET_KEY=egy_sk_test_f0fc353ab953fb7cb4034a5640e22d6849e1cd0b...
PAYMOB_PUBLIC_KEY=egy_pk_test_n3iBXXil41RSEAFxl4bvi7d4Hmqj0srZ
PAYMOB_IFRAME_ID=
PAYMOB_INTEGRATION_ID=123456
PAYMOB_HMAC_SECRET=
```

**Should Be (Add Your Actual Values):**
```bash
PAYMOB_API_KEY=ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1Rjek1qTTFMQ0p1WVcxbElqb2lNVGMyTVRVMk5UZzBOUzR6TkRjNE56TWlmUS43b0o1U2ZIWWJ
PAYMOB_SECRET_KEY=egy_sk_test_f0fc353ab953fb7cb4034a5640e22d6849e1cd0b4b3e701d66a2e669140f7ea4
PAYMOB_PUBLIC_KEY=egy_pk_test_n3iBXXil41RSEAFxl4bvi7d4Hmqj0srZ
PAYMOB_IFRAME_ID=ADD-YOUR-IFRAME-ID-HERE
PAYMOB_INTEGRATION_ID=ADD-YOUR-INTEGRATION-ID-HERE
PAYMOB_HMAC_SECRET=ADD-YOUR-HMAC-SECRET-HERE
PAYMOB_ENABLED=true
```

### 3. Verify PayPal Credentials

Your PayPal credentials look good:
```bash
PAYPAL_CLIENT_ID=Aac8509Yx5K7gHSh1UTkRUvQsfWoo9SrCXo7r1VQKFVxx3KzBinBy01h2RjYwoqQSfw3v7DXFJYy3AiF
PAYPAL_CLIENT_SECRET=ENsaf-yuIK2Eo9wrskjKH4Zr2wocTZWVezaue7dBUjfw1zOHtyp0r2dLwHmihqKnS0T0hxTG1YaH9o6D
PAYPAL_MODE=sandbox
```

✅ These are configured correctly!

## 🔍 How to Find Missing Paymob Credentials

### Finding iFrame ID:

1. Log in to Paymob Dashboard
2. Go to **Integrations** → **Payment Acceptance**
3. Look for **"Accept Online Payments"** section
4. Find the iFrame integration (usually labeled "Payment Form iFrame")
5. The ID will be a number like: `123456` or `789012`

### Finding HMAC Secret:

1. Go to **Settings** → **Developer Settings** → **Webhooks/Callbacks**
2. Look for **"HMAC Secret"** or **"Signature Key"**
3. It's a long alphanumeric string
4. Copy the exact value (case-sensitive!)

## ✅ Complete Configuration Template

Here's what your Paymob section should look like when complete:

```bash
# =============================================================================
# Payment Gateway Configuration - Paymob (Egypt)
# =============================================================================
PAYMOB_API_KEY=ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1Rjek1qTTFMQ0p1WVcxbElqb2lNVGMyTVRVMk5UZzBOUzR6TkRjNE56TWlmUS43b0o1U2ZIWWJ
PAYMOB_SECRET_KEY=egy_sk_test_f0fc353ab953fb7cb4034a5640e22d6849e1cd0b4b3e701d66a2e669140f7ea4
PAYMOB_PUBLIC_KEY=egy_pk_test_n3iBXXil41RSEAFxl4bvi7d4Hmqj0srZ
PAYMOB_INTEGRATION_ID=YOUR-INTEGRATION-ID-HERE
PAYMOB_IFRAME_ID=YOUR-IFRAME-ID-HERE
PAYMOB_HMAC_SECRET=YOUR-HMAC-SECRET-HERE
PAYMOB_ENABLED=true
PAYMOB_CURRENCY=EGP

# =============================================================================
# Payment Gateway Configuration - PayPal (International)
# =============================================================================
PAYPAL_CLIENT_ID=Aac8509Yx5K7gHSh1UTkRUvQsfWoo9SrCXo7r1VQKFVxx3KzBinBy01h2RjYwoqQSfw3v7DXFJYy3AiF
PAYPAL_CLIENT_SECRET=ENsaf-yuIK2Eo9wrskjKH4Zr2wocTZWVezaue7dBUjfw1zOHtyp0r2dLwHmihqKnS0T0hxTG1YaH9o6D
PAYPAL_MODE=sandbox
```

## 🧪 Test Your Configuration

### Step 1: Update .env with actual values

```bash
nano .env
```

### Step 2: Restart Django

```bash
Ctrl + C
poetry run python manage.py runserver
```

### Step 3: Run Tests

```bash
# Test both gateways
poetry run python test_ad_checkout_payments.py

# Or test individually
poetry run python test_paypal_integration.py
poetry run python test_paymob_integration.py
```

## 📋 Checklist Before Testing

- [ ] Got Paymob credentials from dashboard
- [ ] Added PAYMOB_INTEGRATION_ID to .env
- [ ] Added PAYMOB_IFRAME_ID to .env
- [ ] Added PAYMOB_HMAC_SECRET to .env
- [ ] Set PAYMOB_ENABLED=true
- [ ] Restarted Django
- [ ] Ran test scripts to verify

## 🆘 Still Having Issues?

Run this diagnostic:

```bash
poetry run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings.local')
django.setup()
from constance import config

print('=== CONFIGURATION CHECK ===')
print()
print('PayPal:')
print(f'  Client ID: {\"✓\" if config.PAYPAL_CLIENT_ID else \"✗\"}')
print(f'  Secret: {\"✓\" if config.PAYPAL_CLIENT_SECRET else \"✗\"}')
print(f'  Mode: {config.PAYPAL_MODE}')
print()
print('Paymob:')
print(f'  API Key: {\"✓\" if config.PAYMOB_API_KEY else \"✗\"}')
print(f'  Integration ID: {\"✓\" if config.PAYMOB_INTEGRATION_ID else \"✗\"}')
print(f'  iFrame ID: {\"✓\" if config.PAYMOB_IFRAME_ID else \"✗\"}')
print(f'  HMAC Secret: {\"✓\" if config.PAYMOB_HMAC_SECRET else \"✗\"}')
print(f'  Enabled: {config.PAYMOB_ENABLED}')
"
```

---

**Next Steps:**

1. Get your missing Paymob credentials from dashboard
2. Update .env file with the actual values
3. Restart Django
4. Run tests again
5. Report back if still having issues!

