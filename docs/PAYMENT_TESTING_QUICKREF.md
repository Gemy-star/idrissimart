# 💳 Payment Gateway Testing - Quick Reference

## 🚀 Quick Start

### 1. Configure Credentials

Edit `.env` file:

```bash
# PayPal (Sandbox for testing)
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret
PAYPAL_MODE=sandbox

# Paymob (Egypt)
PAYMOB_API_KEY=your-api-key
PAYMOB_INTEGRATION_ID=your-integration-id
PAYMOB_IFRAME_ID=your-iframe-id
PAYMOB_HMAC_SECRET=your-hmac-secret
PAYMOB_ENABLED=true
```

### 2. Run Tests

```bash
# Test PayPal
poetry run python test_paypal_integration.py

# Test Paymob
poetry run python test_paymob_integration.py

# Test both
poetry run python test_paypal_integration.py && poetry run python test_paymob_integration.py
```

### 3. Check Results

✅ **Success**: All tests pass  
⚠️ **Warning**: Some tests failed  
❌ **Error**: Critical issue

## 📋 What Each Test Does

### PayPal Tests
| # | Test | Purpose |
|---|------|---------|
| 1 | Configuration | Verify credentials in .env |
| 2 | Is Enabled | Check if PayPal is active |
| 3 | API Endpoint | Confirm correct sandbox/live URL |
| 4 | Access Token | Test OAuth authentication |
| 5 | Create Order | Create test payment order |
| 6 | Get Details | Retrieve order information |
| 7 | Network | Check internet connectivity |

### Paymob Tests
| # | Test | Purpose |
|---|------|---------|
| 1 | Configuration | Verify all API keys configured |
| 2 | Is Enabled | Check if Paymob is active |
| 3 | API Endpoint | Confirm API server URL |
| 4 | Authentication | Test API key authentication |
| 5 | Create Order | Create test order |
| 6 | Payment Key | Generate payment token |
| 7 | iFrame URL | Get checkout page URL |
| 8 | Network | Check internet connectivity |

## 🔧 Troubleshooting

### PayPal Issues

```bash
# Check credentials
poetry run python -c "from constance import config; print('Client ID:', config.PAYPAL_CLIENT_ID)"

# Test auth only
poetry run python test_paypal_simple.py

# Check mode
poetry run python -c "from constance import config; print('Mode:', config.PAYPAL_MODE)"
```

### Paymob Issues

```bash
# Check API key
poetry run python -c "from constance import config; print('API Key:', config.PAYMOB_API_KEY)"

# Check enabled status
poetry run python -c "from constance import config; print('Enabled:', config.PAYMOB_ENABLED)"

# Test auth
poetry run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings.local')
django.setup()
from main.services.paymob_service import PaymobService
print('Auth:', PaymobService.authenticate())
"
```

## 🌐 Get Credentials

### PayPal Sandbox
1. https://developer.paypal.com/dashboard/
2. Apps & Credentials → Sandbox
3. Create app or use existing
4. Copy **Client ID** and **Secret**

### Paymob
1. https://www.paymob.com/
2. Integrations → Payment Keys
3. Copy API Key, Integration ID, iFrame ID

## ✅ Success Indicators

```
✓ All tests pass
✓ No error messages
✓ Credentials verified
✓ Network connection OK
✓ Orders can be created
```

## ❌ Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid credentials | Verify API keys |
| `Connection Error` | No internet | Check WiFi/Network |
| `Not Configured` | Missing .env values | Add credentials to .env |
| `PayPal is not enabled` | Credentials not loaded | Restart Django |

## 📚 Full Documentation

See: `PAYMENT_GATEWAY_TESTING.md` for detailed guide

## 🎯 Next Steps

1. ✅ Add credentials to `.env`
2. ✅ Run test scripts
3. ✅ Verify all tests pass
4. ✅ Test in web UI
5. ✅ Monitor payment callbacks
6. ✅ Deploy to production

---

**Ready? Run tests now!** 🚀

