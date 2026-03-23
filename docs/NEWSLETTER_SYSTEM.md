# Newsletter System Documentation

This document explains how to use and configure the Newsletter system in your Idrissi Smart application.

## Overview

The Newsletter system allows users to subscribe to newsletters that can be sent via:
- **Email**: HTML-formatted emails with confirmation templates
- **SMS**: Text message notifications (requires SMS provider configuration)
- **Background Jobs**: Uses Django-Q2 for asynchronous processing

## Architecture

### Components

1. **Model** (`Newsletter` in `models.py`)
   - Stores subscriber information
   - Tracks subscription preferences (email/SMS)
   - Records IP address and user agent for security

2. **Views** (`newsletter_subscribe` in `views.py`)
   - Handles form submissions via AJAX
   - Validates email format
   - Queues background tasks for confirmation emails

3. **Tasks** (`tasks.py`)
   - `send_newsletter_confirmation_email()`: Sends confirmation email to new subscribers
   - `send_newsletter_to_all()`: Sends newsletter to all active subscribers
   - `send_sms_newsletter_to_all()`: Sends SMS to subscribers (requires SMS provider)

4. **Admin Interface** (`NewsletterAdmin` in `admin.py`)
   - Manage subscriber database
   - Send test emails
   - Activate/deactivate subscriptions
   - View subscription statistics

5. **Frontend** (`static/js/newsletter.js`)
   - AJAX form handler
   - Email validation
   - User feedback messages

## Setup Instructions

### 1. Run Migrations

```bash
python manage.py migrate
```

This will create the `Newsletter` table with the following fields:
- `email`: Unique email address
- `phone`: Optional phone number for SMS
- `receive_email`: Boolean flag for email preference
- `receive_sms`: Boolean flag for SMS preference
- `country`: Foreign key to Country model
- `is_active`: Boolean flag for active subscriptions
- `ip_address`: Client IP for security tracking
- `user_agent`: Browser information
- `created_at`: Subscription date
- `updated_at`: Last update date
- `last_notification_sent`: Last newsletter dispatch

### 2. Include Newsletter Form in Templates

Add the newsletter subscription form to your template (usually in footer or sidebar):

```html
<div class="newsletter-box">
    <h4 class="newsletter-title">
        <i class="fas fa-bell me-2"></i>اشترك في نشرتنا البريدية
    </h4>
    <p class="newsletter-desc">احصل على أحدث العروض والأخبار مباشرة في بريدك الإلكتروني</p>
    <form class="newsletter-form" id="newsletterForm">
        {% csrf_token %}
        <div class="input-group">
            <input type="email" class="form-control newsletter-input" 
                   id="newsletterEmail" name="email" 
                   placeholder="أدخل بريدك الإلكتروني" required="">
            <button class="btn btn-custom btn-secondary-custom newsletter-btn" 
                    type="submit" id="newsletterSubmitBtn">
                <i class="fas fa-paper-plane me-2"></i>اشترك
            </button>
        </div>
        <div id="newsletterMessage" class="mt-2" style="display: none;"></div>
    </form>
</div>
```

### 3. Include JavaScript Handler

Add this to your base template or layout file:

```html
<script src="{% static 'js/newsletter.js' %}"></script>
```

### 4. Configure Email Settings

In your Django settings (`idrissimart/settings/local.py` or `docker_local.py`):

```python
# Email Backend Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # For testing
# OR use SendGrid:
EMAIL_BACKEND = "sendgrid_backend.SendGridBackend"

EMAIL_HOST = "smtp.gmail.com"  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-password"
DEFAULT_FROM_EMAIL = "noreply@idrissimart.com"
```

### 5. (Optional) Configure SMS Provider

To enable SMS sending, configure one of the supported SMS providers:

#### Using Twilio

1. Install Twilio: `pip install twilio`

2. Add to settings:

```python
SMS_PROVIDER = "twilio"
TWILIO_ACCOUNT_SID = "your-account-sid"
TWILIO_AUTH_TOKEN = "your-auth-token"
TWILIO_FROM_NUMBER = "+1234567890"
```

#### Other SMS Providers

You can extend `send_sms_newsletter_to_all()` in `tasks.py` to support:
- AWS SNS
- Nexmo/Vonage
- Firebase Cloud Messaging
- Any custom SMS API

## Usage

### 1. User Subscribes (Frontend)

1. User fills email in the newsletter form
2. JavaScript validates the email format
3. AJAX request is sent to `/ar/api/newsletter/subscribe/`
4. Django-Q2 background job queues confirmation email
5. User receives confirmation email

### 2. Admin Manages Subscribers

Access the newsletter admin panel:
1. Go to Django Admin
2. Navigate to "Content" → "Newsletter"
3. View all subscribers with:
   - Email address
   - Country
   - Subscription preferences (email/SMS)
   - Subscription date
   - Last notification sent

**Admin Actions:**
- **Activate Selected**: Enable inactive subscriptions
- **Deactivate Selected**: Disable active subscriptions
- **Send Test Email**: Send test email to up to 5 selected subscribers

### 3. Send Newsletters via Management Command

#### Send Email Newsletter

```bash
# Send to all subscribers
python manage.py send_newsletter \
    --subject "Newsletter Subject" \
    --html-file path/to/newsletter.html

# Send test to admin email
python manage.py send_newsletter \
    --subject "Newsletter Subject" \
    --html-file path/to/newsletter.html \
    --test
```

#### Send SMS Newsletter

```bash
python manage.py send_newsletter \
    --method sms \
    --sms-message "Your SMS message here"
```

#### Send Both Email and SMS

```bash
python manage.py send_newsletter \
    --method both \
    --subject "Newsletter" \
    --html-file template.html \
    --sms-message "SMS content"
```

### 4. Send Newsletters Programmatically

In your Django code:

```python
from content.tasks import send_newsletter_to_all, send_sms_newsletter_to_all
from django_q.tasks import async_task

# Send email asynchronously (queued task)
async_task(
    'content.tasks.send_newsletter_to_all',
    'Newsletter Subject',
    '<h1>Newsletter Content</h1>',
    'Plain text content'
)

# Send email synchronously
result = send_newsletter_to_all(
    content_subject='Newsletter Subject',
    content_html='<h1>Newsletter</h1>',
    content_plain='Newsletter text'
)

# Send SMS
result = send_sms_newsletter_to_all(
    content_message='Your SMS message here'
)
```

### 5. Schedule Periodic Newsletters

Add to your Django settings for scheduled newsletter sending:

```python
Q_CLUSTER = {
    # ... existing configuration ...
    'scheduled_tasks': [
        {
            'name': 'content.tasks.send_newsletter_scheduled_task',
            'schedule': 'cron',
            'repeats': -1,  # Infinite
            'cron': '0 9 * * 1',  # Every Monday at 9:00 AM
        },
    ],
}
```

Then implement the task in `tasks.py`:

```python
def send_newsletter_scheduled_task():
    """Scheduled task - send newsletter weekly"""
    from django.template.loader import render_to_string
    
    context = {
        'subject': 'Weekly Newsletter',
        'date': timezone.now(),
    }
    
    html_message = render_to_string('email/weekly_newsletter.html', context)
    result = send_newsletter_to_all(
        content_subject='أسبوعيتك من إدريسي مارت',
        content_html=html_message,
    )
    
    logger.info(f"Scheduled newsletter sent: {result}")
```

## Creating Newsletter Templates

Create HTML templates in `templates/email/`:

```html
{% extends "emails/base_email.html" %}

{% block title %}Newsletter Title{% endblock %}

{% block content %}
<div class="body">
    <h2>Newsletter Title</h2>
    <p>Newsletter content here...</p>
    
    <!-- Links and CTA buttons -->
    <div class="btn-container">
        <a href="https://example.com" class="btn">View More</a>
    </div>
    
    <!-- Unsubscribe link -->
    <p style="font-size: 12px; color: #999;">
        <a href="https://example.com/newsletter/unsubscribe/?email={{ email }}">
            Unsubscribe from our newsletter
        </a>
    </p>
</div>
{% endblock %}
```

## API Endpoints

### Subscribe to Newsletter

**Endpoint:** `POST /ar/api/newsletter/subscribe/`

**Request:**
```json
{
    "email": "user@example.com"
}
```

**Response - Success:**
```json
{
    "success": true,
    "message": "شكراً لاشتراكك في نشرتنا البريدية!"
}
```

**Response - Error:**
```json
{
    "success": false,
    "message": "هذا البريد الإلكتروني مشترك بالفعل"
}
```

## Troubleshooting

### Newsletters Not Sending

1. **Check Django-Q2 status:**
   ```bash
   python manage.py qcluster
   ```

2. **Check email backend:**
   ```bash
   python manage.py shell
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

3. **Check logs:**
   ```bash
   tail -f logs/django.log
   ```

### CSRF Token Issues

Ensure your form includes CSRF token:
```html
{% csrf_token %}
```

### SMS Not Sending

1. Verify SMS provider is configured
2. Check phone numbers are valid with country code
3. Verify account has sufficient balance/credits

### Email Not Being Received

1. Check spam folder
2. Verify sender email is not on blacklist
3. Check SPF/DKIM records for your domain
4. Use `--test` flag to verify email backend

## Performance Considerations

### Database Optimization

The Newsletter model includes indexes on frequently queried fields:
- `email` (unique index)
- `is_active`
- `created_at`

### Bulk Operations

For sending to large subscriber lists:

```python
# Use iterator() for memory efficiency
subscribers = Newsletter.objects.filter(
    is_active=True,
    receive_email=True
).iterator(chunk_size=1000)

for batch in subscribers:
    # Process batch
    pass
```

### Email Sending Options

```python
# Use BCC for privacy (default)
send_mail(
    'Subject',
    'Message',
    'from@example.com',
    ['main@example.com'],
    bcc=['sub1@example.com', 'sub2@example.com'],
)

# Use connection pooling for multiple emails
from django.core.mail import get_connection

with get_connection() as connection:
    for subscriber in subscribers:
        send_mail(
            'Subject',
            'Message',
            'from@example.com',
            [subscriber.email],
            connection=connection,
        )
```

## Security Best Practices

1. **Email Validation:** Client-side validation + server-side validation
2. **CSRF Protection:** All forms use Django's CSRF tokens
3. **Rate Limiting:** Consider adding rate limiting to the subscribe endpoint
4. **IP Tracking:** Track subscriber IP for security audit
5. **User Agent Logging:** Log browser information for suspicious activity

Example rate limiting (requires `django-ratelimit`):

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/h', method='POST')
def newsletter_subscribe(request):
    # ... implementation
```

## Unsubscribe Feature

Add an unsubscribe view:

```python
# In views.py
def newsletter_unsubscribe(request):
    email = request.GET.get('email')
    token = request.GET.get('token')
    
    try:
        newsletter = Newsletter.objects.get(email=email)
        newsletter.is_active = False
        newsletter.save()
        return render(request, 'newsletter/unsubscribed.html', {
            'email': email
        })
    except Newsletter.DoesNotExist:
        return render(request, 'newsletter/not_found.html', status=404)

# In urls.py
path('api/newsletter/unsubscribe/', newsletter_unsubscribe, name='newsletter_unsubscribe'),
```

## Analytics & Reporting

Track newsletter engagement:

```python
# Add to Newsletter model
class Newsletter(models.Model):
    # ... existing fields ...
    emails_sent = models.IntegerField(default=0)
    emails_opened = models.IntegerField(default=0)
    links_clicked = models.IntegerField(default=0)
    
    def engagement_rate(self):
        if self.emails_sent == 0:
            return 0
        return (self.emails_opened / self.emails_sent) * 100
```

## Support & Troubleshooting

For issues:
1. Check Django logs: `logs/django.log`
2. Verify email backend configuration
3. Test with management command: `python manage.py send_newsletter --test`
4. Check Django-Q2 status: `python manage.py qcluster`
