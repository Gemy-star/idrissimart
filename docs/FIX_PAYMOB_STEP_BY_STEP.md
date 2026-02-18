# 🔧 Complete Guide: Fix Paymob Configuration

## Current Status

```
✓ PayPal:     READY (all credentials configured)
✗ Paymob:     INCOMPLETE (4 fields missing)
```

### Missing Fields:
1. ❌ `PAYMOB_API_KEY` (empty)
2. ❌ `PAYMOB_INTEGRATION_ID` (placeholder: 123456)
3. ❌ `PAYMOB_IFRAME_ID` (empty)
4. ❌ `PAYMOB_HMAC_SECRET` (empty)

---

## Step-by-Step: Get Missing Paymob Credentials

### Step 1: Log in to Paymob Dashboard

🔗 Go to: **https://www.paymob.com/dashboard**

Log in with your Paymob account credentials.

### Step 2: Get API Key

1. In Dashboard, click **Settings** (gear icon)
2. Go to **Developer Settings** → **API Keys**
3. You should see your **API Key** (looks like: `ZXlKaGJHY2lPaUpJVXpVeE...`)
4. **Copy** this entire key

**Important:** The API Key in your .env appears truncated. The full key is very long. Make sure you copy the COMPLETE key.

### Step 3: Get Integration ID

1. Go to **Integrations** in the menu
2. Click **Payment Acceptance**
3. Look for **"Accept"** integration (the main one for payments)
4. The **Integration ID** will be displayed as a number (example: `1234567`)
5. **Copy** this number

**Note:** Your .env has placeholder `123456` - replace with actual value

### Step 4: Get iFrame ID

1. In **Integrations** → **Payment Acceptance**
2. Look for the **"Payment Form iFrame"** option
3. The **iFrame ID** will be shown (example: `789012`)
4. **Copy** this number

**Note:** Currently empty in your .env - needs to be added

### Step 5: Get HMAC Secret

1. Go to **Settings** (gear icon)
2. Click **Webhooks** or **Security** section
3. Look for **HMAC Secret** or **Signature Key**
4. It's a long alphanumeric string (example: `abc123def456...`)
5. **Copy** the entire secret

**Note:** Currently empty in .env - needs to be added

---

## Update Your .env File

### Step 1: Open .env

```bash
nano .env
```

### Step 2: Find the Paymob Section

Look for lines starting with `PAYMOB_`:

```
PAYMOB_API_KEY=ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5...
PAYMOB_SECRET_KEY=egy_sk_test_f0fc353ab953fb7cb4034a5640e22d6849e1cd0b...
PAYMOB_PUBLIC_KEY=egy_pk_test_n3iBXXil41RSEAFxl4bvi7d4Hmqj0srZ
PAYMOB_IFRAME_ID=
PAYMOB_INTEGRATION_ID=123456
PAYMOB_HMAC_SECRET=
```

### Step 3: Update Each Field

Replace with your actual values:

```bash
# Line 1: Make sure API_KEY is complete (not truncated)
PAYMOB_API_KEY=YOUR-COMPLETE-API-KEY-FROM-DASHBOARD

# Line 4: Add the iFrame ID number
PAYMOB_IFRAME_ID=YOUR-IFRAME-ID-NUMBER

# Line 5: Replace placeholder with actual Integration ID
PAYMOB_INTEGRATION_ID=YOUR-INTEGRATION-ID-NUMBER

# Line 6: Add the HMAC Secret
PAYMOB_HMAC_SECRET=YOUR-HMAC-SECRET-FROM-DASHBOARD
```

### Step 4: Save File

1. Press `Ctrl + X`
2. Press `Y` (for Yes)
3. Press `Enter` to confirm filename

### Step 5: Restart Django

```bash
# Kill current process
Ctrl + C

# Restart
poetry run python manage.py runserver
```

---

## Verify Configuration

After updating .env and restarting Django, run:

```bash
poetry run python PAYMOB_CONFIGURATION_FIX.py
```

You should see:

```
✓ API Key: Configured
✓ Integration ID: YOUR-ID
✓ iFrame ID: YOUR-ID
✓ HMAC Secret: Configured

✓ PAYMOB READY FOR TESTING
```

---

## Test Both Payment Gateways

Once configuration is complete:

```bash
# Test everything
poetry run python test_ad_checkout_payments.py
```

Expected output:
```
✓ PAYPAL PAYMENT WORKFLOW TEST
  ✓ PASSED: Configuration found
  ✓ PASSED: Got access token
  ✓ PASSED: PayPal order created

✓ PAYMOB PAYMENT WORKFLOW TEST
  ✓ PASSED: Configuration found
  ✓ PASSED: Authentication successful
  ✓ PASSED: Paymob order created
  ✓ PASSED: Payment key created
  ✓ PASSED: iFrame URL generated

✓ ALL TESTS PASSED
```

---

## Quick Reference

| Field | Where to Find | Example |
|-------|---------------|---------|
| API Key | Settings → Developer → API Keys | `ZXlKaGJHY2lPa...` |
| Integration ID | Integrations → Payment Acceptance | `1234567` |
| iFrame ID | Integrations → Payment Acceptance | `789012` |
| HMAC Secret | Settings → Webhooks → HMAC Secret | `abc123def456...` |

---

## Troubleshooting

### "API Key is truncated in .env"

If your API key appears cut off with a `>` at the end:

1. Copy the FULL API key from Paymob
2. Paste it completely in .env
3. Make sure there's no `>` at the end

### "Still showing 'not configured' after restart"

1. Check that you edited the correct .env file:
   ```bash
   cat .env | grep PAYMOB_API_KEY
   ```

2. Make sure it's in the right format (no extra spaces):
   ```bash
   PAYMOB_API_KEY=your-value-here
   ```

3. Restart Django again

### "Getting 'connection error' in tests"

- Verify API Key is correct
- Check internet connection
- Try the verification script again

---

## Next Steps

1. ✅ Go to Paymob dashboard and copy all 4 values
2. ✅ Update .env file with the values
3. ✅ Restart Django
4. ✅ Run: `python PAYMOB_CONFIGURATION_FIX.py`
5. ✅ Run: `python test_ad_checkout_payments.py`
6. ✅ Test in browser: http://localhost:8000/ads/checkout/

---

**Need Help?**

If you're stuck, share the output of:
```bash
poetry run python PAYMOB_CONFIGURATION_FIX.py
```

This will show exactly what's still missing!

