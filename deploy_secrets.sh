#!/bin/bash

# =============================================================================
# Idrissimart Deployment Script for Ubuntu
# This script sets up environment variables for production deployment
# =============================================================================

echo "🚀 Setting up Idrissimart environment variables..."

# Create .env file if it doesn't exist
ENV_FILE="/var/www/idrissimart/.env"
BACKUP_FILE="/var/www/idrissimart/.env.backup.$(date +%Y%m%d_%H%M%S)"

# Backup existing .env file if it exists
if [ -f "$ENV_FILE" ]; then
    echo "📋 Backing up existing .env file to $BACKUP_FILE"
    cp "$ENV_FILE" "$BACKUP_FILE"
fi

# Create new .env file
echo "📝 Creating new environment configuration..."

cat > "$ENV_FILE" << 'EOF'
# =============================================================================
# Idrissimart Production Environment Variables
# =============================================================================

# Django Settings
DEBUG=False
SECRET_KEY=your_django_secret_key_here_change_this_in_production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1
SITE_URL=https://yourdomain.com

# Database Configuration (PostgreSQL recommended for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=idrissimart_db
DB_USER=idrissimart_user
DB_PASSWORD=your_secure_database_password
DB_HOST=localhost
DB_PORT=5432

# PayPal Configuration
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AQnjmPBtvIVbTH0Ims4qnmEMVXZ-NcI3aNugVKmEkHIKi7tbJQYIfl4OSPrhd6_w9tfNIn_LDjWD1foq
PAYPAL_CLIENT_SECRET=EJmH3ZcwaNpD-Mesof6fcMQws8JRDRJwdiVrb85NY_uxqyjUNaJYaPuZrIi46wnybdb38tWH_1UWwYYr

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACbda2c87d81ac899a614f26b69c25c8af
TWILIO_AUTH_TOKEN=f8cad167753ac2bacca2c70db8a4f541
TWILIO_PHONE_NUMBER=+1234567890

# Paymob Configuration
PAYMOB_API_KEY=your_paymob_api_key_here
PAYMOB_INTEGRATION_ID=your_paymob_integration_id
PAYMOB_IFRAME_ID=your_paymob_iframe_id

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Redis Configuration (for caching and sessions)
REDIS_URL=redis://localhost:6379/0

# Media and Static Files
MEDIA_ROOT=/var/www/idrissimart/media
STATIC_ROOT=/var/www/idrissimart/static

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/idrissimart/django.log
EOF

# Set proper permissions
chmod 600 "$ENV_FILE"
chown www-data:www-data "$ENV_FILE"

echo "✅ Environment file created successfully!"

# =============================================================================
# Install Required System Packages
# =============================================================================

echo "📦 Installing system dependencies..."

# Update package list
apt update

# Install Python and pip
apt install -y python3 python3-pip python3-venv python3-dev

# Install PostgreSQL
apt install -y postgresql postgresql-contrib libpq-dev

# Install Redis
apt install -y redis-server

# Install Nginx
apt install -y nginx

# Install system dependencies for Python packages
apt install -y build-essential libssl-dev libffi-dev libjpeg-dev zlib1g-dev

echo "✅ System packages installed!"

# =============================================================================
# Setup Python Virtual Environment
# =============================================================================

echo "🐍 Setting up Python virtual environment..."

# Create project directory
mkdir -p /var/www/idrissimart
cd /var/www/idrissimart

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
cat > requirements.txt << 'EOF'
Django>=4.2,<5.0
psycopg2-binary>=2.9.0
redis>=4.0.0
celery>=5.3.0
gunicorn>=21.0.0
whitenoise>=6.5.0
Pillow>=10.0.0
django-mptt>=0.14.0
django-filter>=23.0.0
twilio>=8.10.0
requests>=2.31.0
python-decouple>=3.8.0
django-cors-headers>=4.3.0
django-extensions>=3.2.0
EOF

pip install -r requirements.txt

echo "✅ Python environment setup complete!"

# =============================================================================
# Database Setup
# =============================================================================

echo "🗄️ Setting up PostgreSQL database..."

# Create database user and database
sudo -u postgres psql << EOF
CREATE USER idrissimart_user WITH PASSWORD 'your_secure_database_password';
CREATE DATABASE idrissimart_db OWNER idrissimart_user;
GRANT ALL PRIVILEGES ON DATABASE idrissimart_db TO idrissimart_user;
ALTER USER idrissimart_user CREATEDB;
\q
EOF

echo "✅ Database setup complete!"

# =============================================================================
# Django Setup
# =============================================================================

echo "🌐 Setting up Django application..."

# Run Django migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (interactive)
echo "Creating Django superuser..."
python manage.py createsuperuser

echo "✅ Django setup complete!"

# =============================================================================
# Gunicorn Configuration
# =============================================================================

echo "🦄 Setting up Gunicorn..."

cat > /etc/systemd/system/idrissimart.service << 'EOF'
[Unit]
Description=Idrissimart Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/idrissimart
Environment="PATH=/var/www/idrissimart/venv/bin"
EnvironmentFile=/var/www/idrissimart/.env
ExecStart=/var/www/idrissimart/venv/bin/gunicorn --workers 3 --bind unix:/var/www/idrissimart/idrissimart.sock idrissimart.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable idrissimart
systemctl start idrissimart

echo "✅ Gunicorn service configured!"

# =============================================================================
# Nginx Configuration
# =============================================================================

echo "🌐 Setting up Nginx..."

cat > /etc/nginx/sites-available/idrissimart << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (you'll need to obtain SSL certificates)
    ssl_certificate /etc/ssl/certs/idrissimart.crt;
    ssl_certificate_key /etc/ssl/private/idrissimart.key;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Static files
    location /static/ {
        alias /var/www/idrissimart/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/idrissimart/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Django application
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/idrissimart/idrissimart.sock;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Security: Block access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /(\.env|requirements\.txt|manage\.py) {
        deny all;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/idrissimart /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

echo "✅ Nginx configured!"

# =============================================================================
# SSL Certificate Setup (Let's Encrypt)
# =============================================================================

echo "🔒 Setting up SSL certificates..."

# Install Certbot
apt install -y certbot python3-certbot-nginx

# Note: You'll need to run this manually after updating your domain
echo "📝 To obtain SSL certificates, run:"
echo "certbot --nginx -d yourdomain.com -d www.yourdomain.com"

# =============================================================================
# Firewall Configuration
# =============================================================================

echo "🔥 Configuring firewall..."

# Enable UFW
ufw --force enable

# Allow SSH
ufw allow ssh

# Allow HTTP and HTTPS
ufw allow 'Nginx Full'

# Allow PostgreSQL (only from localhost)
ufw allow from 127.0.0.1 to any port 5432

echo "✅ Firewall configured!"

# =============================================================================
# Log Setup
# =============================================================================

echo "📋 Setting up logging..."

# Create log directory
mkdir -p /var/log/idrissimart
chown www-data:www-data /var/log/idrissimart

# Setup log rotation
cat > /etc/logrotate.d/idrissimart << 'EOF'
/var/log/idrissimart/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload idrissimart
    endscript
}
EOF

echo "✅ Logging configured!"

# =============================================================================
# Backup Script
# =============================================================================

echo "💾 Creating backup script..."

cat > /usr/local/bin/idrissimart-backup.sh << 'EOF'
#!/bin/bash

# Idrissimart Backup Script
BACKUP_DIR="/var/backups/idrissimart"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
pg_dump -h localhost -U idrissimart_user idrissimart_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# Backup media files
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C /var/www/idrissimart media/

# Backup configuration
cp /var/www/idrissimart/.env "$BACKUP_DIR/env_backup_$DATE"

# Remove backups older than 30 days
find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/idrissimart-backup.sh

# Setup daily backup cron job
echo "0 2 * * * root /usr/local/bin/idrissimart-backup.sh" >> /etc/crontab

echo "✅ Backup system configured!"

# =============================================================================
# Final Steps
# =============================================================================

echo "🎉 Deployment script completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your domain name in /etc/nginx/sites-available/idrissimart"
echo "2. Update SITE_URL and ALLOWED_HOSTS in /var/www/idrissimart/.env"
echo "3. Obtain SSL certificates: certbot --nginx -d yourdomain.com"
echo "4. Update Django SECRET_KEY in .env file"
echo "5. Configure Paymob API credentials in .env file"
echo "6. Test the application: systemctl status idrissimart"
echo ""
echo "🔧 Useful Commands:"
echo "- View logs: journalctl -u idrissimart -f"
echo "- Restart app: systemctl restart idrissimart"
echo "- Restart nginx: systemctl restart nginx"
echo "- Run backup: /usr/local/bin/idrissimart-backup.sh"
echo ""
echo "🌐 Your application will be available at: https://yourdomain.com"
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "- Change all default passwords"
echo "- Update Django SECRET_KEY"
echo "- Configure proper SSL certificates"
echo "- Review and update firewall rules"
echo "- Set up monitoring and alerting"
echo ""

# Set proper ownership
chown -R www-data:www-data /var/www/idrissimart
chmod -R 755 /var/www/idrissimart
chmod 600 /var/www/idrissimart/.env

echo "✅ All done! 🚀"
