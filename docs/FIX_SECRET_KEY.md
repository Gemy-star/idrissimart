# 🔐 Fix SECRET_KEY for Production

## Problem
Your production server is using the default insecure SECRET_KEY from `common.py`.

## Solution

### Step 1: Generate a Secure Secret Key

On your **local machine** (or production server):

```bash
# Method 1: Use the provided script
python generate_secret_key.py

# Method 2: Use Django directly
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

This will generate something like:
```
django-insecure-a8f^2k$3m!x@9vz#1p*q&7w_s4u+6y=n5h-e0r2t@9i^k8l
```

**⚠️ IMPORTANT: Keep this key secret! Never commit it to git.**

---

### Step 2: Set Environment Variable on Production Server

SSH to your production server:

```bash
ssh your-server
```

Create or edit the `.env` file in your project directory:

```bash
cd /path/to/idrissimart
sudo nano .env
```

Add or update these lines:

```env
# REQUIRED: Set your generated secret key
DJANGO_SECRET_KEY=your-generated-secret-key-here

# Other important settings
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=idrissimart.settings.docker

# Database
DB_NAME=idrissimartdb
DB_USER=idrissimart
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

---

### Step 3: Set Correct Permissions

```bash
# Make .env readable only by owner and group
sudo chmod 600 .env

# Set ownership (replace 'your_user' with your actual username)
sudo chown your_user:www-data .env
```

---

### Step 4: Verify the .env File is Loaded

```bash
# Test that Django can read the SECRET_KEY
python manage.py shell
>>> from django.conf import settings
>>> print(settings.SECRET_KEY)
>>> # Should print your new key, NOT the insecure default
>>> exit()
```

---

### Step 5: Run Production Health Check

```bash
python manage.py check_production
```

You should see:
```
✓ SECRET_KEY is set
```

---

### Step 6: Restart Gunicorn

```bash
sudo systemctl restart gunicorn
```

Check status:
```bash
sudo systemctl status gunicorn
```

---

### Step 7: Verify Production Site Works

Visit your site: https://idrissimart.com

Check logs for any errors:
```bash
sudo tail -f /var/log/django/idrissimart.log
```

---

## Security Best Practices

### ✅ Do:
- Use different SECRET_KEY for development and production
- Store SECRET_KEY in environment variables (`.env` file)
- Add `.env` to `.gitignore` (already done)
- Set restrictive permissions on `.env` file (600 or 640)
- Generate long, random keys (50+ characters)
- Rotate keys periodically

### ❌ Don't:
- Commit SECRET_KEY to git
- Share SECRET_KEY publicly
- Use the same key across environments
- Use short or simple keys
- Leave the default "insecure" key in production

---

## Troubleshooting

### Error: "DJANGO_SECRET_KEY environment variable must be set"

**Cause**: The `.env` file is not being loaded or doesn't have DJANGO_SECRET_KEY

**Fix**:
```bash
# Check if .env exists
ls -la /path/to/idrissimart/.env

# Check if python-dotenv is installed
pip list | grep python-dotenv

# Verify .env is being loaded in settings
cat idrissimart/settings/common.py | grep load_dotenv
```

### Error: "Invalid SECRET_KEY"

**Cause**: Special characters in key causing issues

**Fix**: Generate a new key and ensure it's properly quoted in `.env`:
```env
DJANGO_SECRET_KEY='your-key-with-special-chars'
```

### Site Still Shows Error After Fix

**Fix**:
```bash
# 1. Clear any cached sessions
python manage.py clearsessions

# 2. Restart Gunicorn
sudo systemctl restart gunicorn

# 3. Clear Nginx cache (if applicable)
sudo systemctl restart nginx
```

---

## Quick Reference

```bash
# Generate key
python generate_secret_key.py

# Edit .env
sudo nano /path/to/idrissimart/.env

# Test configuration
python manage.py check_production

# Restart service
sudo systemctl restart gunicorn

# Check logs
sudo tail -f /var/log/django/idrissimart.log
```

---

## Next Steps

After fixing SECRET_KEY, run the full health check:

```bash
python manage.py check_production
```

This will verify:
- ✓ DEBUG = False
- ✓ SECRET_KEY is secure
- ✓ Database connection
- ✓ Static/Media files
- ✓ Security settings
- ✓ Constance config
