# Production Error Fix Guide

## Current Issues
Your production server is showing 500 errors due to several reasons:

### 1. Malicious Bot Traffic
The logs show requests to:
- `/telescope/requests` (Laravel endpoint)
- `/info.php` (PHP info file)
- `/?rest_route=/wp/v2/users/` (WordPress endpoint)

These are **bot attacks** scanning for vulnerabilities.

### 2. Actual Application Errors
The `GET / HTTP/1.0" 500` errors indicate your home page is failing.

## Solutions

### Step 1: Check Production Logs
```bash
# SSH to your server
ssh your-server

# Check the full error log
sudo tail -f /var/log/django/idrissimart.log

# Or check Gunicorn logs
sudo journalctl -u gunicorn -f
```

### Step 2: Common Fixes

#### A. Missing Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Set proper permissions
sudo chown -R www-data:www-data /path/to/staticfiles
sudo chown -R www-data:www-data /path/to/media
```

#### B. Database Connection Issues
Check your `.env` file has correct database credentials:
```env
DB_NAME=idrissimartdb
DB_USER=idrissimart
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Test database connection:
```bash
python manage.py dbshell
```

#### C. Missing Migrations
```bash
python manage.py migrate
```

#### D. Check Environment Variables
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)  # Should be False
>>> print(settings.ALLOWED_HOSTS)
>>> print(settings.DATABASES)
```

### Step 3: Security - Block Malicious Requests

Add this to your Nginx configuration (`/etc/nginx/sites-available/idrissimart`):

```nginx
# Block common attack patterns
location ~* \.(php|asp|aspx|jsp)$ {
    return 404;
}

location ~* /(wp-|wordpress|telescope|.env|config|phpinfo) {
    return 404;
}

# Block suspicious query strings
if ($args ~* "(rest_route|wp-json|telescope)") {
    return 404;
}
```

Then reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 4: Enable Better Error Logging

Update your production settings to capture more details.

### Step 5: Check Gunicorn Service

```bash
# Check status
sudo systemctl status gunicorn

# Restart if needed
sudo systemctl restart gunicorn

# Check for errors
sudo journalctl -u gunicorn -n 100
```

### Step 6: Check File Permissions

```bash
# Django project directory
sudo chown -R your_user:www-data /path/to/idrissimart
sudo chmod -R 755 /path/to/idrissimart

# Static and media directories
sudo chown -R www-data:www-data /path/to/staticfiles
sudo chown -R www-data:www-data /path/to/media
```

## Most Likely Cause

Based on the error pattern, the issue is probably:

1. **Context processor error** - The `header_categories` context processor might be failing
2. **Missing constance config** - Database not initialized properly
3. **Template error** - Missing template variables or filters

## Quick Diagnostic Commands

```bash
# 1. Check if manage.py works
python manage.py check --deploy

# 2. Test URL patterns
python manage.py show_urls

# 3. Check constance
python manage.py shell
>>> from constance import config
>>> print(config.SITE_NAME)

# 4. Test database
python manage.py dbshell
```

## Emergency Fix - Temporarily Enable Debug

**WARNING: Only for diagnosis, disable immediately after!**

In `/path/to/idrissimart/.env`:
```env
DJANGO_DEBUG=True
```

Restart Gunicorn:
```bash
sudo systemctl restart gunicorn
```

Visit the site - you'll see the full error traceback.
Copy the error, then immediately set `DJANGO_DEBUG=False` and restart.

## Contact Me After Running

Run these commands and share the output:

```bash
# 1. Check logs
sudo tail -100 /var/log/django/idrissimart.log

# 2. Check Gunicorn
sudo journalctl -u gunicorn -n 50

# 3. Test settings
python manage.py check --deploy

# 4. Database test
python manage.py showmigrations
```
