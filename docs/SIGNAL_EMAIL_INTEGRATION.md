# Signal-Email Integration Guide

## Overview
This document covers all Django signals that trigger email notifications in the Idrissimart platform.

## Email Service Configuration

### EmailService Class
Location: `main/services/email_service.py`

The EmailService class provides centralized email functionality using SendGrid or SMTP backend.

**Key Methods:**
- `send_email()` - Generic email sending
- `send_template_email()` - Render Django template and send
- `send_welcome_email()` - Welcome new users
- `send_otp_email()` - OTP verification
- `send_password_reset_email()` - Password reset
- `send_ad_approved_email()` - Ad approval notification
- `send_saved_search_notification()` - Saved search results

### Email Configuration
**Production (SendGrid):**
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = config.SENDGRID_API_KEY
```

**Local Development (smtp4dev):**
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp4dev"  # Docker container name
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = "noreply@idrissimart.local"
```

**Web UI:** http://localhost:3100
**SMTP Port:** localhost:2525 (host) or smtp4dev:25 (container)

---

## Signal-Email Integrations

### 1. User Registration

**Signal:** `post_save` on `User` model
**Handler:** `assign_default_package_to_new_user()`
**Location:** `main/signals.py` (lines 230-285)

**Trigger:** When a new DEFAULT user is created

**Actions:**
- Creates in-app notification
- Assigns default ad package (if verification not required)
- No direct email (uses welcome flow)

**Related Emails:**
- Welcome email sent separately during registration flow
- Template: `emails/welcome.html`

---

### 2. User Verification Complete

**Signal:** `pre_save` on `User` model
**Handler:** `assign_package_after_verification()`
**Location:** `main/signals.py` (lines 288-367)

**Trigger:** When user completes email AND mobile verification

**Actions:**
- Assigns free package to verified user
- Creates in-app notification
- No direct email

**Context:**
```python
{
    "user_name": user.get_full_name() or user.username,
    "package_name": package.name,
    "ad_count": package.ad_count
}
```

---

### 3. Ad Approval/Rejection

**Signal:** `pre_save` on `ClassifiedAd` model
**Handler:** `send_ad_approval_notification()`
**Location:** `main/signals.py` (lines 88-170)

**Trigger:** When ad status changes from PENDING to ACTIVE (approved) or REJECTED

**Email Template:** `emails/ad_approved.html`

**EmailService Method:** `send_ad_approved_email()`

**Context:**
```python
{
    "site_name": config.SITE_NAME,
    "user_name": user.get_full_name() or user.username,
    "ad_title": ad.title,
    "ad_url": ad.get_absolute_url()
}
```

**Also Sends:**
- In-app notification ✓
- SMS notification ✓ (if enabled)

**Visual Features:**
- Gradient header with success icon (🎉)
- Ad title prominently displayed
- CTA button to view ad
- Next steps guidance

---

### 4. New Order Created

**Signal:** `post_save` on `Order` model (created=True)
**Handler:** `send_order_notifications()`
**Location:** `main/signals.py` (lines 410-502)

**Trigger:** When a new order is created

**Email Template:** `emails/order_created.html`

**EmailService Method:** `send_template_email()`

**Context:**
```python
{
    "order": order_instance,
    "user": user_instance,
    "items": order.items.all(),
    "site_url": settings.SITE_URL
}
```

**Recipients:**
- **Customer:** Order confirmation email
- **Admin:** New order notification (in-app only)
- **Publishers:** Revenue notification (in-app only)

**Also Sends:**
- SMS to customer ✓
- In-app notifications ✓

**Visual Features:**
- Order number and total amount
- Itemized list of products
- Shipping and payment info
- Order tracking link

---

### 5. Order Status Update

**Signal:** `post_save` on `Order` model
**Handler:** `send_order_status_notifications()`
**Location:** `main/signals.py` (lines 507-628)

**Trigger:** When order status changes (processing, shipped, delivered, cancelled, refunded)

**Email Template:** `emails/order_status_update.html`

**EmailService Method:** `send_template_email()`

**Context:**
```python
{
    "order": order_instance,
    "currency": currency_symbol,
    "site_name": config.SITE_NAME,
    "site_url": config.SITE_URL
}
```

**Status-Specific Styles:**
- **Processing:** Yellow/amber theme (⏳)
- **Shipped:** Blue theme (🚚)
- **Delivered:** Green success theme (✅)
- **Cancelled:** Red theme (❌)
- **Refunded:** Purple theme (💰)

**Also Sends:**
- SMS for shipped/delivered statuses ✓
- In-app notification ✓

**Visual Features:**
- Dynamic status card with color coding
- Tracking info (for shipped status)
- Delivery confirmation notes
- Refund timeline info

---

### 6. Package Activation

**Signal:** `post_save` on `Payment` model
**Handler:** `activate_package_on_payment_completion()`
**Location:** `main/signals.py` (lines 630-720)

**Trigger:** When payment status becomes COMPLETED (both electronic and manual payments)

**Email Template:** `emails/package_activated.html`

**EmailService Method:** `send_template_email()`

**Context:**
```python
{
    "user": user_instance,
    "package": package_instance,
    "user_package": user_package_instance,
    "payment_amount": payment.amount,
    "site_name": config.SITE_NAME,
    "site_url": config.SITE_URL
}
```

**Actions:**
- Creates `UserPackage` record
- Sends email notification
- Sends SMS notification ✓
- Creates in-app notification ✓

**Visual Features:**
- Celebration icon (🎉)
- Package details card with gradient
- Large ad count display (orange highlight)
- Payment confirmation
- Expiry date display
- Feature list with checkmarks
- CTA button to start posting

---

### 7. Saved Search Notifications

**Signal:** Scheduled task (not signal-based)
**Handler:** Custom management command or scheduled job

**Email Template:** `emails/saved_search_notification.html`

**EmailService Method:** `send_saved_search_notification()`

**Context:**
```python
{
    "site_name": config.SITE_NAME,
    "user_name": user.get_full_name() or user.username,
    "search_name": search.name,
    "ads": matching_ads_list,
    "search_url": search.get_absolute_url()
}
```

**Visual Features:**
- Search criteria summary
- List of new matching ads
- Ad thumbnail images
- Price and location info
- CTA buttons to view ads

---

## Email Template Standards

### Brand Colors
```css
/* Primary */
--primary-purple: #4b315e;
--primary-purple-light: #6b4c7a;

/* Secondary */
--secondary-orange: #ff6001;
--secondary-orange-light: #ff8534;

/* Backgrounds */
--bg-light-purple: #f8f6f9;
--bg-light-orange: #fff8f0;
```

### Typography
- **Font Family:** 'Cairo', 'Segoe UI', sans-serif
- **Direction:** RTL (right-to-left)
- **Language:** Arabic primary, English secondary

### Layout Structure
```html
<div class="container">
    <div class="header">
        <!-- Icon + Title -->
    </div>
    <div class="content">
        <!-- Main message -->
        <!-- Info cards -->
        <!-- CTA buttons -->
    </div>
    <div class="footer">
        <!-- Links + Copyright -->
    </div>
</div>
```

### Responsive Design
- Max width: 600px
- Mobile breakpoint: 600px
- Fluid typography scaling
- Stack layouts on mobile

---

## Testing Email Templates

### Local Testing with smtp4dev

**Start smtp4dev:**
```bash
docker compose up smtp4dev
```

**Web UI:** http://localhost:3100
**SMTP:** localhost:2525

**Run Test Suite:**
```bash
# Test all templates
python test_signal_emails.py

# Quick SMTP test
python test_smtp_quick.py
```

### Test Individual Templates

```python
from main.services.email_service import EmailService

email_service = EmailService()

# Test ad approval
email_service.send_ad_approved_email(
    user=user_instance,
    ad_title="شقة للإيجار",
    ad_url="http://localhost:8000/ads/123/"
)

# Test package activation
email_service.send_template_email(
    to_emails=[user.email],
    subject="تم تفعيل باقتك",
    template_name="emails/package_activated.html",
    context={...}
)
```

### Testing in Docker Container

```bash
# Enter web container
docker exec -it idrissimart_web bash

# Run test suite
python test_signal_emails.py

# Test Django shell
python manage.py shell
>>> from main.services.email_service import EmailService
>>> EmailService.is_enabled()
```

---

## Troubleshooting

### Emails Not Sending

**1. Check EmailService Status:**
```python
from main.services.email_service import EmailService
print(EmailService.is_enabled())  # Should return True
```

**2. Check Constance Config:**
```python
from constance import config
print(config.SENDGRID_ENABLED)  # Should be True
print(config.SENDGRID_API_KEY)  # Should have value
```

**3. Check SMTP Connection:**
```python
import smtplib
server = smtplib.SMTP('smtp4dev', 25)  # Docker
# or
server = smtplib.SMTP('localhost', 2525)  # Host
server.noop()  # Should return (250, ...)
```

**4. Check Signal Connections:**
```bash
python manage.py shell
>>> from django.db.models.signals import post_save
>>> from main.models import ClassifiedAd
>>> post_save.receivers_for(ClassifiedAd)
```

### Template Rendering Errors

**Common Issues:**
- Missing context variables
- Invalid template tags
- Incorrect file paths

**Debug Template:**
```python
from django.template.loader import render_to_string

try:
    html = render_to_string('emails/template.html', context)
    print(html)
except Exception as e:
    print(f"Template error: {e}")
```

### smtp4dev Not Receiving

**Check Container:**
```bash
docker ps | grep smtp4dev
docker logs idrissimart_smtp4dev
```

**Check Ports:**
```bash
netstat -tulpn | grep 2525
netstat -tulpn | grep 3100
```

**Restart smtp4dev:**
```bash
docker compose restart smtp4dev
```

---

## Production Checklist

### Before Deployment

- [ ] Update `SENDGRID_API_KEY` in environment
- [ ] Set `SENDGRID_ENABLED=True` in Constance
- [ ] Configure `SENDGRID_FROM_EMAIL` and `SENDGRID_FROM_NAME`
- [ ] Test all email templates in staging
- [ ] Verify domain authentication in SendGrid
- [ ] Set up email monitoring/alerts
- [ ] Configure email rate limits
- [ ] Test unsubscribe functionality

### Email Monitoring

**SendGrid Dashboard:**
- Delivery rates
- Bounce rates
- Spam reports
- Open rates (if tracking enabled)

**Django Logs:**
```bash
tail -f logs/email.log
```

**Error Tracking:**
```python
import logging
logger = logging.getLogger(__name__)
logger.error(f"Email failed: {e}")
```

---

## Email Template Locations

```
templates/emails/
├── welcome.html                      # User registration welcome
├── otp_verification.html             # OTP code email
├── password_reset.html               # Password reset
├── email_verification.html           # Email address verification
├── ad_approved.html                  # Ad approval notification
├── ad_approval_notification.html     # Alternative ad approval
├── order_created.html                # New order confirmation
├── order_status_update.html          # Order status changes ⭐ NEW
├── package_activated.html            # Package activation ⭐ NEW
├── saved_search_notification.html    # Saved search results
├── password_reset_email.html         # Legacy password reset
└── password_reset_email.txt          # Plain text version
```

---

## Signal Handler Summary

| Signal | Model | Handler | Email Template | Status |
|--------|-------|---------|----------------|--------|
| `post_save` (created) | User | assign_default_package | (welcome flow) | ✅ |
| `pre_save` | User | assign_package_after_verification | - | ✅ |
| `pre_save` | ClassifiedAd | send_ad_approval_notification | ad_approved.html | ✅ |
| `post_save` (created) | Order | send_order_notifications | order_created.html | ✅ |
| `post_save` | Order | send_order_status_notifications | order_status_update.html | ✅ |
| `post_save` | Payment | activate_package_on_payment_completion | package_activated.html | ✅ |

---

## Next Steps

1. **Add Email Preferences**
   - User settings for email notifications
   - Opt-out for specific email types
   - Frequency controls for saved searches

2. **Email Analytics**
   - Track open rates
   - Monitor click-through rates
   - A/B test subject lines

3. **Additional Templates**
   - Order cancellation confirmation
   - Refund processed notification
   - Package expiry warning
   - Ad expiry reminder

4. **Internationalization**
   - English translations for all templates
   - French support (if required)
   - RTL/LTR layout switching

---

## Related Documentation

- [Email Templates Guide](EMAIL_TEMPLATES_GUIDE.md)
- [Admin Dashboard](ADMIN_DASHBOARD_UPDATES.md)
- [Ad System](AD_FEATURES_SYSTEM.md)
- [Payment System](AD_FEATURES_PAYMENT_SYSTEM.md)

---

**Last Updated:** 2024-01-09
**Author:** Development Team
**Version:** 1.0
