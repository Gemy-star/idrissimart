# 🚀 Payment Gateway Testing - START HERE

## ⏱️ 5-Minute Quick Start

### Step 1: Get Credentials (2 min)

**PayPal:**
1. Go to: https://developer.paypal.com/dashboard/
2. Navigate to: Sandbox → Apps → Create App
3. Copy **Client ID** and **Secret**

**Paymob:**
1. Go to: https://www.paymob.com/
2. Navigate to: Integrations → Payment Keys
3. Copy **API Key**, **Integration ID**, **iFrame ID**

### Step 2: Add to .env (1 min)

Edit your `.env` file and add:

```bash
# PayPal Settings
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-secret
PAYPAL_MODE=sandbox

# Paymob Settings
PAYMOB_API_KEY=your-paymob-api-key
PAYMOB_INTEGRATION_ID=your-integration-id
PAYMOB_IFRAME_ID=your-iframe-id
PAYMOB_ENABLED=true
```

### Step 3: Run Tests (2 min)

```bash
# Test PayPal
poetry run python test_paypal_integration.py

# Test Paymob
poetry run python test_paymob_integration.py
```

---

## 🎯 Expected Results

### ✅ All Green = Success!
```
Tests Passed: 7/7 (PayPal) or 8/8 (Paymob)
✓ ALL TESTS PASSED!
```

### ❌ Red = Fix It
- ✗ FAILED: Configuration not found → Add credentials to `.env`
- ✗ FAILED: Authentication error → Verify your API keys
- ✗ FAILED: Cannot reach API → Check internet connection

---

## 📖 Documentation

| If you... | Read this |
|-----------|-----------|
| Just want to test | `PAYMENT_TESTING_QUICKREF.md` |
| Want step-by-step help | `PAYMENT_TESTING_SETUP.md` |
| Want all the details | `PAYMENT_GATEWAY_TESTING.md` |
| Need to navigate | `PAYMENT_TESTING_INDEX.md` |

---

## 💡 Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| `401 Unauthorized` | Check PayPal/Paymob credentials are correct |
| `Connection Error` | Check internet connection: `ping google.com` |
| `Not Configured` | Make sure you added credentials to `.env` |
| `Tests still failing?` | Restart Django: `poetry run python manage.py runserver` |

---

## 🎉 You're All Set!

Your payment gateways are ready to test. Go ahead and run those commands above! 🚀

For detailed info, see the documentation files listed above.

---

**Questions?** Check `PAYMENT_TESTING_QUICKREF.md` for troubleshooting!

