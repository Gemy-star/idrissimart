# Newsletter System - Quick Reference Guide

## Files Created/Modified

### 1. **Models** - `content/models.py`
- Added `Newsletter` model with fields for email, phone, preferences, and tracking

### 2. **Views** - `content/views.py`
- Added `newsletter_subscribe()` view for handling form submissions
- Integrated with Django-Q2 for background job processing

### 3. **Tasks** - `content/tasks.py`
- `send_newsletter_confirmation_email()` - Send confirmation upon subscription
- `send_newsletter_to_all()` - Broadcast email to all subscribers
- `send_sms_newsletter_to_all()` - Send SMS messages (optional)
- `send_newsletter_scheduled_task()` - Framework for scheduled newsletters

### 4. **URLs** - `content/urls.py`
- Added `POST /ar/api/newsletter/subscribe/` endpoint

### 5. **Admin** - `content/admin.py`
- `NewsletterAdmin` class with:
  - List view with email/SMS status indicators
  - Actions: activate, deactivate, send test emails
  - Filtering by status, country, subscription type
  - Admin dashboard statistics

### 6. **Frontend** - `static/js/newsletter.js`
- AJAX form handler with email validation
- Success/error message display
- Loading states and CSRF protection

### 7. **Email Template** - `templates/emails/newsletter_confirmation.html`
- HTML email template for confirmation
- Supports Arabic RTL layout
- Styled with project branding

### 8. **Management Command** - `content/management/commands/send_newsletter.py`
- CLI command for sending newsletters via email or SMS
- Test mode for admin email only
- File-based content support

### 9. **Database Migration** - `content/migrations/0033_add_newsletter_model.py`
- Creates Newsletter table with proper indexes

### 10. **Documentation** - `docs/NEWSLETTER_SYSTEM.md`
- Comprehensive setup and usage guide

## Quick Start

### 1. Run Migration
```bash
python manage.py migrate
```

### 2. Add Form to Template
```html
<form id="newsletterForm">
    {% csrf_token %}
    <input type="email" id="newsletterEmail" name="email" required>
    <button type="submit">اشترك</button>
    <div id="newsletterMessage"></div>
</form>
```

### 3. Include JavaScript
```html
<script src="{% static 'js/newsletter.js' %}"></script>
```

### 4. Start Django-Q2
```bash
python manage.py qcluster
```

### 5. Send Newsletter
```bash
# Email
python manage.py send_newsletter \
    --subject "Newsletter" \
    --html-file template.html

# SMS (requires SMS provider)
python manage.py send_newsletter \
    --method sms \
    --sms-message "Your message"
```

## Features

✅ **Email Subscriptions**
- HTML email templates
- Confirmation emails
- Batch sending with BCC privacy
- Customizable sender

✅ **SMS Support** (Optional)
- Twilio integration ready
- Phone number tracking
- Preference-based sending

✅ **Background Processing**
- Django-Q2 task queue
- Confirmation emails queued asynchronously
- Scheduled task framework

✅ **Admin Interface**
- Subscriber management
- Test email sending
- Activation/deactivation
- Engagement tracking

✅ **Security**
- CSRF protection
- Email validation
- IP address tracking
- User agent logging
- Unique email constraint

✅ **i18n Support**
- Full Arabic translation
- RTL email templates
- Multilingual confirmation emails

## API Endpoint

```
POST /ar/api/newsletter/subscribe/
Content-Type: application/x-www-form-urlencoded

email=user@example.com

Response:
{
    "success": true,
    "message": "شكراً لاشتراكك في نشرتنا البريدية!"
}
```

## Database Schema

```
Newsletter
├── id (BigAutoField)
├── email (EmailField, unique, indexed)
├── phone (CharField, optional)
├── receive_email (BooleanField, default=True)
├── receive_sms (BooleanField, default=False)
├── country (ForeignKey to Country)
├── is_active (BooleanField, indexed)
├── ip_address (GenericIPAddressField)
├── user_agent (TextField)
├── created_at (DateTimeField, indexed)
├── updated_at (DateTimeField)
└── last_notification_sent (DateTimeField)
```

## Configuration Examples

### Email Backend (Gmail)
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"
DEFAULT_FROM_EMAIL = "noreply@idrissimart.com"
```

### SMS Provider (Twilio)
```python
SMS_PROVIDER = "twilio"
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "your-token"
TWILIO_FROM_NUMBER = "+1234567890"
```

### Scheduled Newsletter (Weekly Monday 9 AM)
```python
Q_CLUSTER = {
    'scheduled_tasks': [
        {
            'name': 'content.tasks.send_newsletter_scheduled_task',
            'schedule': 'cron',
            'repeats': -1,
            'cron': '0 9 * * 1',  # Every Monday at 9:00 AM
        },
    ],
}
```

## Management Commands

### Send Email Newsletter
```bash
python manage.py send_newsletter \
    --subject "Your Subject" \
    --html-file path/to/template.html \
    --text-file path/to/template.txt
```

### Send Test Email
```bash
python manage.py send_newsletter \
    --subject "Test Newsletter" \
    --html-file path/to/template.html \
    --test
```

### Send SMS
```bash
python manage.py send_newsletter \
    --method sms \
    --sms-message "Your SMS text (max 160 chars)"
```

### Send Both Email and SMS
```bash
python manage.py send_newsletter \
    --method both \
    --subject "Newsletter" \
    --html-file template.html \
    --sms-message "SMS content"
```

## Admin Actions

1. **Activate Selected** - Enable inactive subscriptions
2. **Deactivate Selected** - Disable active subscriptions  
3. **Send Test Email** - Send confirmation email to 5 selected subscribers

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "No subscribers found" | Add subscribers via form or admin |
| Email not sending | Check SMTP credentials in settings |
| CSRF token error | Ensure form includes `{% csrf_token %}` |
| Django-Q2 not running | Start with `python manage.py qcluster` |
| SMS not sending | Configure SMS_PROVIDER in settings |
| Permission denied | User must be superuser for admin access |

## Performance Tips

- Use `--test` flag for development
- Monitor Django-Q2: `python manage.py qcluster`
- Check logs for errors: `tail -f logs/django.log`
- Use BCC for privacy with large lists
- Consider rate limiting on subscription endpoint

## Next Steps

1. ✅ Run migrations
2. ✅ Configure email backend
3. ✅ Add form to template
4. ✅ Include JavaScript
5. ✅ Start Django-Q2
6. ✅ Test subscription
7. ✅ Create email templates
8. ✅ Send newsletters

## Support

For detailed documentation, see: `docs/NEWSLETTER_SYSTEM.md`
