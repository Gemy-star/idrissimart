#!/bin/bash

# =============================================================================
# Idrissimart Production Secrets Setup Script
# Run this script on your Ubuntu production server to configure secrets
# Sets environment variables in systemd service file (no .env file)
# =============================================================================

set -e

echo "======================================"
echo "Idrissimart Production Secrets Setup"
echo "======================================"

# Define the systemd service file location
SERVICE_FILE="/etc/systemd/system/idrissimart.service"
SERVICE_ENV_DIR="/etc/idrissimart"
SERVICE_ENV_FILE="$SERVICE_ENV_DIR/environment"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Create environment directory
mkdir -p "$SERVICE_ENV_DIR"

# Backup existing environment file
if [ -f "$SERVICE_ENV_FILE" ]; then
    BACKUP_FILE="${SERVICE_ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backing up existing environment file to $BACKUP_FILE"
    cp "$SERVICE_ENV_FILE" "$BACKUP_FILE"
fi

# Generate a secure Django secret key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(50))"
}

DJANGO_SECRET_KEY=$(generate_secret_key)
DB_PASSWORD=$(generate_secret_key | head -c 32)

echo "Creating production environment variables file..."

cat > "$SERVICE_ENV_FILE" << 'ENVEOF'
# =============================================================================
# Idrissimart Production Environment Variables
# Generated: TIMESTAMP_PLACEHOLDER
# Used by systemd service
# =============================================================================

# Django Core Settings
DEBUG=False
SECRET_KEY=SECRET_KEY_PLACEHOLDER
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1
SITE_URL=https://yourdomain.com
DJANGO_SETTINGS_MODULE=idrissimart.settings.production

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=idrissimart_db
DB_USER=idrissimart_user
DB_PASSWORD=DB_PASSWORD_PLACEHOLDER
DB_HOST=localhost
DB_PORT=5432

# PayPal Payment Gateway
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AQnjmPBtvIVbTH0Ims4qnmEMVXZ-NcI3aNugVKmEkHIKi7tbJQYIfl4OSPrhd6_w9tfNIn_LDjWD1foq
PAYPAL_CLIENT_SECRET=EJmH3ZcwaNpD-Mesof6fcMQws8JRDRJwdiVrb85NY_uxqyjUNaJYaPuZrIi46wnybdb38tWH_1UWwYYr

# Paymob Payment Gateway (Egypt)
PAYMOB_API_KEY=your_paymob_api_key
PAYMOB_SECRET_KEY=your_paymob_secret_key
PAYMOB_PUBLIC_KEY=your_paymob_public_key
PAYMOB_INTEGRATION_ID=your_integration_id
PAYMOB_IFRAME_ID=your_iframe_id
PAYMOB_HMAC_SECRET=your_hmac_secret
PAYMOB_VISA_INTEGRATION_ID=
PAYMOB_MASTERCARD_INTEGRATION_ID=

# Twilio SMS Gateway
TWILIO_ACCOUNT_SID=ACbda2c87d81ac899a614f26b69c25c8af
TWILIO_AUTH_TOKEN=f8cad167753ac2bacca2c70db8a4f541
TWILIO_PHONE_NUMBER=+12605822569

# SendGrid Email Service
SENDGRID_API_KEY=your_sendgrid_api_key

# Google reCAPTCHA v2
RECAPTCHA_SITE_KEY=6LcUMSYsAAAAAGKWlIEtHtmD7ecT5U1Vi3B098dD
RECAPTCHA_SECRET_KEY=6LcUMSYsAAAAAARBEdYizpNQTn9SbrZWutEkfuPq

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Media and Static Files
MEDIA_ROOT=/var/www/idrissimart/media
STATIC_ROOT=/var/www/idrissimart/static

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/idrissimart/django.log
ENVEOF

# Replace placeholders
sed -i "s/TIMESTAMP_PLACEHOLDER/$(date)/g" "$SERVICE_ENV_FILE"
sed -i "s/SECRET_KEY_PLACEHOLDER/$DJANGO_SECRET_KEY/g" "$SERVICE_ENV_FILE"
sed -i "s/DB_PASSWORD_PLACEHOLDER/$DB_PASSWORD/g" "$SERVICE_ENV_FILE"

# Set proper permissions (only root and service can read)
chmod 600 "$SERVICE_ENV_FILE"

# Create or update systemd service file
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Creating systemd service file..."
    cat > "$SERVICE_FILE" << 'SERVICEEOF'
[Unit]
Description=Idrissimart Django Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/idrissimart
EnvironmentFile=/etc/idrissimart/environment

ExecStart=/var/www/idrissimart/.venv/bin/gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/idrissimart/access.log \
    --error-logfile /var/log/idrissimart/error.log \
    idrissimart.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF
    
    echo "Systemd service file created at $SERVICE_FILE"
else
    # Update existing service file to use EnvironmentFile
    if ! grep -q "EnvironmentFile" "$SERVICE_FILE"; then
        echo "Updating existing service file to use environment file..."
        sed -i "/\[Service\]/a EnvironmentFile=/etc/idrissimart/environment" "$SERVICE_FILE"
    fi
fi

# Create log directory
mkdir -p /var/log/idrissimart
chown www-data:www-data /var/log/idrissimart

# Reload systemd
systemctl daemon-reload

echo ""
echo "======================================"
echo "Environment setup completed!"
echo "======================================"
echo ""
echo "Environment file: $SERVICE_ENV_FILE"
echo "Service file: $SERVICE_FILE"
echo ""
echo "Generated credentials:"
echo "  Database Password: $DB_PASSWORD"
echo ""
echo "IMPORTANT: Please update the following values in $SERVICE_ENV_FILE:"
echo "  1. ALLOWED_HOSTS - Set to your actual domain"
echo "  2. SITE_URL - Set to your actual site URL"
echo "  3. PAYPAL_MODE - Change to 'live' for production payments"
echo "  4. PAYMOB_* - Add your Paymob credentials if using"
echo "  5. SENDGRID_API_KEY - Add your SendGrid API key"
echo ""
echo "To edit environment variables:"
echo "  sudo nano $SERVICE_ENV_FILE"
echo ""
echo "After editing, restart all services:"
echo "  sudo systemctl restart gunicorn"
echo "  sudo systemctl restart daphne-idrissimart"
echo "  sudo systemctl restart idrissimart-q"
echo ""
echo "To enable services on boot:"
echo "  sudo systemctl enable gunicorn"
echo "  sudo systemctl enable daphne-idrissimart"
echo "  sudo systemctl enable idrissimart-q"
echo ""
