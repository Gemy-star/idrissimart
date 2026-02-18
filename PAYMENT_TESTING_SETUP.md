# 💳 Payment Gateway Testing - Complete Setup

## Summary

I've created comprehensive testing tools for both PayPal and Paymob payment gateway integrations. Follow this guide to verify your payment integrations are working correctly.

## 📁 Files Created

1. **`test_paypal_integration.py`** - Full PayPal integration test suite (7 tests)
2. **`test_paymob_integration.py`** - Full Paymob integration test suite (8 tests)
3. **`PAYMENT_GATEWAY_TESTING.md`** - Detailed testing guide with troubleshooting
4. **`PAYMENT_TESTING_QUICKREF.md`** - Quick reference for commands and common issues

## 🚀 Quick Start (5 minutes)

### Step 1: Get Your Credentials

#### PayPal Sandbox:
- Visit: https://developer.paypal.com/dashboard/
- Copy: Client ID and Secret from your sandbox app

#### Paymob:
- Visit: https://www.paymob.com/
- Go to: Integrations → Payment Keys
- Copy: API Key, Integration ID, iFrame ID

### Step 2: Update .env File

```bash
# Edit .env file
nano .env

# Add these lines:
PAYPAL_CLIENT_ID=your-sandbox-client-id
PAYPAL_CLIENT_SECRET=your-sandbox-client-secret
PAYPAL_MODE=sandbox

PAYMOB_API_KEY=your-api-key
PAYMOB_INTEGRATION_ID=your-integration-id
PAYMOB_IFRAME_ID=your-iframe-id
PAYMOB_HMAC_SECRET=your-hmac-secret
PAYMOB_ENABLED=true
```

### Step 3: Run Tests

```bash
# Test PayPal
poetry run python test_paypal_integration.py

# Test Paymob
poetry run python test_paymob_integration.py
```

## ✅ What Gets Tested

### PayPal Tests (7 total)
1. **Configuration** - Verify credentials are loaded
2. **Is Enabled** - Check if PayPal service is enabled
3. **API Endpoint** - Verify correct sandbox/live URL
4. **OAuth Token** - Test authentication with PayPal
5. **Create Order** - Create a test payment order
6. **Get Order Details** - Retrieve order information
7. **Network** - Test internet connectivity to PayPal

### Paymob Tests (8 total)
1. **Configuration** - Verify all credentials are present
2. **Is Enabled** - Check if Paymob service is enabled
3. **API Endpoint** - Verify correct API URL
4. **Authentication** - Test API key authentication
5. **Create Order** - Create a test order
6. **Payment Key** - Generate payment token
7. **iFrame URL** - Get checkout page URL
8. **Network** - Test internet connectivity to Paymob

## 📊 Expected Results

### PayPal Success ✅
```
======================================================================
TEST SUMMARY
======================================================================
Tests Passed: 7/7
✓ ALL TESTS PASSED - PayPal Integration is Working!
```

### Paymob Success ✅
```
======================================================================
TEST SUMMARY
======================================================================
Tests Passed: 8/8
✓ ALL TESTS PASSED - Paymob Integration is Working!
```

## 🔍 Reading Test Output

### ✓ Green (Success)
- ✓ PASSED: Configuration found
- ✓ PASSED: Access token obtained
- ✓ PASSED: Order created successfully

### ✗ Red (Failed)
- ✗ FAILED: PayPal Client ID not configured
- ✗ FAILED: Could not authenticate
- ✗ FAILED: Cannot reach PayPal API

### ⚠ Yellow (Warning)
- ⚠ PAYMOB_HMAC_SECRET not configured (optional for testing)
- ⚠ WARNING: Paymob is not enabled

## 🛠️ Troubleshooting

### PayPal Issues

#### "401 Unauthorized" Error
```bash
✗ FAILED: Could not obtain access token
  Check your PayPal credentials

# Fix:
1. Open: https://developer.paypal.com/dashboard/
2. Verify Client ID and Secret
3. Make sure you're using Sandbox credentials (not Live)
4. Update .env with correct values
```

#### "Connection Error"
```bash
✗ FAILED: Cannot reach PayPal API

# Fix:
1. Check internet connection: ping google.com
2. Check firewall/proxy settings
3. Try accessing: https://api-m.sandbox.paypal.com
```

#### "PayPal is not enabled"
```bash
✗ FAILED: PayPal is not enabled

# Fix:
1. Verify .env has PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET
2. Restart Django: poetry run python manage.py runserver
3. Check credentials: poetry run python -c "from constance import config; print(config.PAYPAL_CLIENT_ID)"
```

### Paymob Issues

#### "PAYMOB_API_KEY not configured"
```bash
✗ FAILED: Some configuration missing

# Fix:
1. Get API key from: https://www.paymob.com/
2. Go to Integrations → Payment Keys
3. Add to .env: PAYMOB_API_KEY=your-key
4. Restart Django
```

#### "Authentication failed"
```bash
✗ FAILED: Could not authenticate

# Fix:
1. Verify API key is correct in Paymob dashboard
2. Update .env with correct key
3. Check internet connection
4. Try manual test: 
   curl -X POST https://accept.paymob.com/api/auth/tokens \
   -H "Content-Type: application/json" \
   -d '{"api_key":"your-key"}'
```

#### "Paymob is not enabled"
```bash
⚠ WARNING: Paymob is not enabled

# Fix:
1. Add to .env: PAYMOB_ENABLED=true
2. Or configure in Django Admin:
   - Go to Admin → Constance
   - Find PAYMOB_ENABLED and set to True
3. Restart Django
```

## 📖 Documentation Files

### Quick Reference
- **`PAYMENT_TESTING_QUICKREF.md`** - Commands and common errors (start here!)

### Detailed Guide
- **`PAYMENT_GATEWAY_TESTING.md`** - Complete setup, testing, and troubleshooting

### Test Files
- **`test_paypal_integration.py`** - PayPal test suite
- **`test_paymob_integration.py`** - Paymob test suite

## 🎯 Test Execution Flow

```
Run Test
    ↓
Check Configuration
    ↓
Test Connectivity
    ↓
Authenticate
    ↓
Create Order (PayPal) or Get Token (Paymob)
    ↓
Test Additional Features
    ↓
Generate Report
    ↓
Pass/Fail Result
```

## 💡 Testing Tips

### Before Testing
1. Ensure internet connection is working
2. Make sure .env file has been updated
3. Restart Django after updating .env
4. Have your credentials ready

### During Testing
1. Read error messages carefully
2. Note the exact error details
3. Check the troubleshooting section
4. Verify credentials in dashboard

### After Testing
1. Save test output for debugging
2. Document any failures
3. Check credentials are correct
4. Contact payment provider if needed

## 🔐 Security Notes

- **Never commit credentials to Git**
- Use `.env` file for local testing only
- Use environment variables or secrets manager for production
- Keep API keys and secrets private
- Rotate credentials periodically

## 📞 Getting Help

### If Tests Fail

1. **Check error message** - It usually tells you what's wrong
2. **Verify credentials** - Double-check in payment provider dashboard
3. **Check internet** - Make sure you're connected
4. **Restart Django** - Sometimes caching causes issues
5. **Read documentation** - See PAYMENT_GATEWAY_TESTING.md

### Payment Provider Support

- **PayPal**: https://developer.paypal.com/docs/
- **Paymob**: https://docs.paymob.com/
- **PayPal Support**: https://www.paypal.com/us/business/support
- **Paymob Support**: support@paymob.com

## 🎉 Success Checklist

- [x] Created test scripts
- [ ] Updated .env with credentials
- [ ] Run test_paypal_integration.py
- [ ] Run test_paymob_integration.py
- [ ] All tests passing
- [ ] Ready for integration testing in web UI

## Next Steps

1. ✅ Update .env with payment credentials
2. ✅ Run both test suites
3. ✅ Verify all tests pass
4. ✅ Test payment flow in web UI
5. ✅ Set up payment callbacks
6. ✅ Deploy to production

---

## Quick Command Reference

```bash
# Run PayPal tests
poetry run python test_paypal_integration.py

# Run Paymob tests
poetry run python test_paymob_integration.py

# Run both tests
poetry run python test_paypal_integration.py && poetry run python test_paymob_integration.py

# Check configuration
poetry run python manage.py shell -c "
from constance import config
print('PayPal Client ID:', config.PAYPAL_CLIENT_ID)
print('Paymob API Key:', config.PAYMOB_API_KEY)
"

# View .env payment settings
grep -E "PAYPAL|PAYMOB" .env

# Edit .env
nano .env
```

---

**Created**: February 17, 2026  
**Status**: Ready to Use  
**Tests**: PayPal (7) + Paymob (8) = 15 total integration tests

