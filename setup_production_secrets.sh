#!/bin/bash

# =============================================================================
# Idrissimart Production Secrets Setup Script
# Run this script on your Ubuntu production server to configure secrets
# =============================================================================

set -e

echo "======================================"
echo "Idrissimart Production Secrets Setup"
echo "======================================"

# Define the .env file location
ENV_FILE="${ENV_FILE:-/var/www/idrissimart/.env}"
PROJECT_DIR="${PROJECT_DIR:-/var/www/idrissimart}"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Create project directory if it doesn't exist
mkdir -p "$PROJECT_DIR"

# Backup existing .env file
if [ -f "$ENV_FILE" ]; then
    BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backing up existing .env to $BACKUP_FILE"
    cp "$ENV_FILE" "$BACKUP_FILE"
fi

# Generate a secure Django secret key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(50))"
}

DJANGO_SECRET_KEY=$(generate_secret_key)

echo "Creating production environment file..."

cat > "$ENV_FILE" << 'ENVEOF'
# =============================================================================
# Idrissimart Production Environment Variables
# Generated: TIMESTAMP_PLACEHOLDER
# =============================================================================

# -----------------------------------------------------------------------------
# Django Core Settings
# -----------------------------------------------------------------------------
DEBUG=False
SECRET_KEY=SECRET_KEY_PLACEHOLDER
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1
SITE_URL=https://yourdomain.com
DJANGO_SETTINGS_MODULE=idrissimart.settings.production

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
DB_ENGINE=django.db.backends.postgresql
DB_NAME=idrissimart_db
DB_USER=idrissimart_user
DB_PASSWORD=CHANGE_THIS_TO_SECURE_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# -----------------------------------------------------------------------------
# PayPal Payment Gateway
# Mode: sandbox (testing) or live (production)
# Get credentials from: https://developer.paypal.com/dashboard/applications
# -----------------------------------------------------------------------------
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AQnjmPBtvIVbTH0Ims4qnmEMVXZ-NcI3aNugVKmEkHIKi7tbJQYIfl4OSPrhd6_w9tfNIn_LDjWD1foq
PAYPAL_CLIENT_SECRET=EJmH3ZcwaNpD-Mesof6fcMQws8JRDRJwdiVrb85NY_uxqyjUNaJYaPuZrIi46wnybdb38tWH_1UWwYYr

# -----------------------------------------------------------------------------
# Paymob Payment Gateway (Egypt)
# Get credentials from: https://accept.paymob.com/portal2/en/settings
# -----------------------------------------------------------------------------
PAYMOB_API_KEY=your_paymob_api_key
PAYMOB_SECRET_KEY=your_paymob_secret_key
PAYMOB_PUBLIC_KEY=your_paymob_public_key
PAYMOB_INTEGRATION_ID=your_integration_id
PAYMOB_IFRAME_ID=your_iframe_id
PAYMOB_HMAC_SECRET=your_hmac_secret
PAYMOB_VISA_INTEGRATION_ID=
PAYMOB_MASTERCARD_INTEGRATION_ID=

# -----------------------------------------------------------------------------
# Twilio SMS Gateway
# Get credentials from: https://console.twilio.com/
# -----------------------------------------------------------------------------
TWILIO_ACCOUNT_SID=ACbda2c87d81ac899a614f26b69c25c8af
TWILIO_AUTH_TOKEN=f8cad167753ac2bacca2c70db8a4f541
TWILIO_PHONE_NUMBER=+12605822569

# -----------------------------------------------------------------------------
# SendGrid Email Service
# Get API key from: https://app.sendgrid.com/settings/api_keys
# -----------------------------------------------------------------------------
SENDGRID_API_KEY=your_sendgrid_api_key

# -----------------------------------------------------------------------------
# Google reCAPTCHA v2
# Get keys from: https://www.google.com/recaptcha/admin
# -----------------------------------------------------------------------------
RECAPTCHA_SITE_KEY=6LcUMSYsAAAAAGKWlIEtHtmD7ecT5U1Vi3B098dD
RECAPTCHA_SECRET_KEY=6LcUMSYsAAAAAARBEdYizpNQTn9SbrZWutEkfuPq

# -----------------------------------------------------------------------------
# Redis Configuration (for caching and Celery)
# -----------------------------------------------------------------------------
REDIS_URL=redis://localhost:6379/0

# -----------------------------------------------------------------------------
# Media and Static Files
# -----------------------------------------------------------------------------
MEDIA_ROOT=/var/www/idrissimart/media
STATIC_ROOT=/var/www/idrissimart/static

# -----------------------------------------------------------------------------
# Security Settings
# -----------------------------------------------------------------------------
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL=INFO
LOG_FILE=/var/log/idrissimart/django.log
ENVEOF

# Replace placeholders
sed -i "s/TIMESTAMP_PLACEHOLDER/$(date)/g" "$ENV_FILE"
sed -i "s/SECRET_KEY_PLACEHOLDER/$DJANGO_SECRET_KEY/g" "$ENV_FILE"

# Set proper permissions (only owner can read/write)
chmod 600 "$ENV_FILE"
chown www-data:www-data "$ENV_FILE"

echo ""
echo "======================================"
echo "Environment file created successfully!"
echo "======================================"
echo ""
echo "File location: $ENV_FILE"
echo ""
echo "IMPORTANT: Please update the following values:"
echo "  1. ALLOWED_HOSTS - Set to your actual domain"
echo "  2. SITE_URL - Set to your actual site URL"
echo "  3. DB_PASSWORD - Set a secure database password"
echo "  4. PAYPAL_MODE - Change to 'live' for production payments"
echo "  5. PAYMOB_* - Add your Paymob credentials if using"
echo "  6. SENDGRID_API_KEY - Add your SendGrid API key"
echo ""
echo "To edit the file:"
echo "  sudo nano $ENV_FILE"
echo ""
echo "After editing, restart the application:"
echo "  sudo systemctl restart idrissimart"
echo ""
