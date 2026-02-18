# SMTP4Dev - Local Email Testing Guide

## 📧 Overview

smtp4dev is a fake SMTP server for local development that captures all emails sent by your application and displays them in a web interface. No real emails are sent!

## 🚀 Quick Start

### Start smtp4dev

```bash
# Start the smtp4dev service
docker compose up -d smtp4dev

# Check if it's running
docker compose ps smtp4dev
```

### Access Web Interface

Open your browser and go to:
```
http://localhost:3100
```

## 🔧 Configuration

### Django Email Settings (Already Configured in .env)

```bash
EMAIL_HOST=smtp4dev
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@idrissimart.local
```

### Ports

- **Port 3100**: Web UI (HTTP)
- **Port 2525**: SMTP server (host) → Port 25 (container internal)

## 📨 Testing Email Functionality

### 1. Send a Test Email from Django Shell

```bash
# Access Django shell
docker compose exec web python manage.py shell

# Send test email
from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'This is a test email from Idrissimart.',
    'noreply@idrissimart.local',
    ['test@example.com'],
    fail_silently=False,
)
```

### 2. Test User Registration

```bash
# Register a new user via your application
# Check http://localhost:3100 to see the confirmation email
```

### 3. Test Password Reset

```bash
# Request password reset via your application
# Check http://localhost:3100 to see the reset email with link
```

## 🎯 Features

### Web Interface Features

1. **Message List**: See all emails sent by your application
2. **View Email Content**:
   - HTML version
   - Plain text version
   - Raw message source
3. **Attachments**: Download any attachments sent with emails
4. **Headers**: View complete email headers
5. **Search**: Filter emails by subject, recipient, etc.
6. **Delete**: Clear individual or all messages

### Development Benefits

✅ **Safe Testing**: No real emails sent to actual users
✅ **No Configuration**: Works without SMTP credentials
✅ **Instant Delivery**: Emails appear immediately
✅ **Easy Debugging**: Inspect email content and headers
✅ **No Spam Filters**: All emails delivered successfully

## 📋 Common Use Cases

### User Registration Workflow

1. User registers on your site
2. Django sends confirmation email
3. Email appears in smtp4dev UI (http://localhost:3100)
4. Copy confirmation link from email
5. Test the confirmation process

### Password Reset Workflow

1. User requests password reset
2. Django sends reset email with token
3. Email appears in smtp4dev UI (http://localhost:3100)
4. Copy reset link from email
5. Test the reset process

### Order Confirmation

1. User places an order
2. Django sends confirmation email
3. Email appears in smtp4dev UI (http://localhost:3100)
4. Verify email content and formatting

## 🔄 Service Management

### Start smtp4dev

```bash
# Start only smtp4dev
docker compose up -d smtp4dev

# Start all services including smtp4dev
docker compose up -d
```

### Stop smtp4dev

```bash
# Stop smtp4dev
docker compose stop smtp4dev

# Remove smtp4dev container
docker compose rm smtp4dev
```

### View Logs

```bash
# View smtp4dev logs
docker compose logs -f smtp4dev

# View last 100 lines
docker compose logs --tail=100 smtp4dev
```

### Restart smtp4dev

```bash
docker compose restart smtp4dev
```

## 🐛 Troubleshooting

### Web UI Not Loading

```bash
# Check if container is running
docker compose ps smtp4dev

# Check logs for errors
docker compose logs smtp4dev

# Restart the service
docker compose restart smtp4dev

# Check if port 3000 is available
sudo netstat -tulpn | grep 3000
```

### Emails Not Appearing

1. **Check Django email settings in .env**:
   ```bash
   EMAIL_HOST=smtp4dev
   EMAIL_PORT=25
   ```

2. **Restart web service after .env changes**:
   ```bash
   docker compose restart web
   ```

3. **Check Django logs**:
   ```bash
   docker compose logs -f web
   ```

4. **Test connection from web container**:
   ```bash
   docker compose exec web telnet smtp4dev 25
   # Should connect successfully
   # Type: quit
   ```

### Port Already in Use

If port 3000 or 25 is already in use:

```bash
# Check what's using the ports
sudo netstat -tulpn | grep :3100
sudo netstat -tulpn | grep :2525

# Option 1: Stop the conflicting service
# Option 2: Change port in docker-compose.yml
# Change "3100:80" to "3200:80" for example
```

## 🔀 Switching Between Development and Production

### Development (smtp4dev)

In `.env`:
```bash
EMAIL_HOST=smtp4dev
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
```

### Production (Gmail)

In `.env`:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
```

**Important**: Always restart services after changing `.env`:
```bash
docker compose restart web qcluster
```

## 📊 Monitoring

### Check Email Statistics

```bash
# View all emails sent
Open http://localhost:3100

# Check SMTP logs
docker compose logs smtp4dev | grep "Message received"
```

### Clear All Messages

In the web UI (http://localhost:3100):
- Click "Delete All" button to clear all captured emails

## 🔐 Security Notes

- **Development Only**: smtp4dev is for local development only
- **No Authentication**: Anyone can send emails to it
- **Not for Production**: Never use in production environments
- **Local Network**: Accessible only from your machine (localhost)

## 📚 Additional Resources

- **smtp4dev GitHub**: https://github.com/rnwood/smtp4dev
- **Docker Hub**: https://hub.docker.com/r/rnwood/smtp4dev
- **Documentation**: https://github.com/rnwood/smtp4dev/wiki

## 💡 Tips

1. **Keep smtp4dev Running**: Start it with other services for continuous email testing
2. **Check Regularly**: Keep the web UI open in a browser tab during development
3. **Test Early**: Test email functionality early in development
4. **Verify Templates**: Check HTML rendering and links in emails
5. **Test All Workflows**: Test registration, password reset, notifications, etc.

## 🎬 Quick Commands Reference

```bash
# Start
docker compose up -d smtp4dev

# Access Web UI
# http://localhost:3100

# Stop
docker compose stop smtp4dev

# View logs
docker compose logs -f smtp4dev

# Restart
docker compose restart smtp4dev

# Remove
docker compose rm smtp4dev

# Test from Django shell
docker compose exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Hello', 'from@test.com', ['to@test.com'])
```

## ✅ Verification Checklist

- [ ] smtp4dev container is running: `docker compose ps smtp4dev`
- [ ] Web UI accessible: http://localhost:3100
- [ ] Django email settings configured in .env
- [ ] Test email sent successfully from Django shell
- [ ] Email appears in smtp4dev UI
- [ ] Can view email HTML content
- [ ] Can view plain text content
- [ ] Can see email headers

---

**Happy Email Testing! 📧**
