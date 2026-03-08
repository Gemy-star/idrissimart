# 🤖 Automated Tasks & Jobs - Implementation Summary

## Overview

This document summarizes all automated tasks and jobs implemented for the Idrissi Mart platform to ensure efficient operation and maintenance.

## ✅ Implemented Management Commands

### 1. Core Expiration Commands

#### `check_expired_ads`
- **Location**: `main/management/commands/check_expired_ads.py`
- **Purpose**: Marks active ads as expired when their `expires_at` date passes
- **Schedule**: Daily at 2:00 AM
- **Impact**: Maintains ad listing integrity

#### `check_expired_subscriptions` ⭐ NEW
- **Location**: `main/management/commands/check_expired_subscriptions.py`
- **Purpose**: Deactivates premium subscriptions for users whose `subscription_end` date has passed
- **Features**:
  - Updates `User.is_premium` to False
  - Deactivates `UserSubscription` records
  - Supports `--dry-run` mode
- **Schedule**: Daily at 2:10 AM
- **Impact**: Ensures users lose premium access when subscription expires

#### `check_expired_packages` ⭐ NEW
- **Location**: `main/management/commands/check_expired_packages.py`
- **Purpose**: Reports expired user packages and notifies users about unused ads
- **Features**:
  - Identifies packages with remaining ads that expired
  - Optional user notifications with `--notify-users`
  - Tracks wasted ad inventory
- **Schedule**: Daily at 2:20 AM
- **Impact**: User awareness, inventory insights

#### `check_expired_orders` ⭐ NEW
- **Location**: `main/management/commands/check_expired_orders.py`
- **Purpose**: Auto-cancels unpaid orders that have passed their expiration time
- **Features**:
  - Cancels pending orders with `expires_at` in the past
  - Optional user notifications with `--notify-users`
  - Frees up reserved inventory
- **Schedule**: Hourly
- **Impact**: Automatic inventory management

#### `clear_expired_features`
- **Location**: `main/management/commands/clear_expired_features.py`
- **Purpose**: Deletes expired `AdFeature` records
- **Schedule**: Daily at 3:00 AM
- **Impact**: Database cleanup

### 2. Database Maintenance Commands

#### `cleanup_old_notifications` ⭐ NEW
- **Location**: `main/management/commands/cleanup_old_notifications.py`
- **Purpose**: Deletes old read notifications to keep database lean
- **Features**:
  - Default: 30 days retention for read notifications
  - Keeps unread notifications by default
  - Configurable with `--days` parameter
- **Schedule**: Weekly (Sunday at 3:00 AM)
- **Impact**: Improved database performance

#### `check_pending_payments` ⭐ NEW
- **Location**: `main/management/commands/check_pending_payments.py`
- **Purpose**: Marks stale pending payments as failed
- **Features**:
  - Default: 24-hour timeout
  - Configurable with `--hours` parameter
  - Adds failure reason to metadata
- **Schedule**: Daily at 2:30 AM
- **Impact**: Clean payment records

#### `clearsessions`
- **Built-in Django command**
- **Purpose**: Clears expired user sessions
- **Schedule**: Daily at 4:00 AM
- **Impact**: Reduces session table bloat

### 3. Notification Commands

#### `send_expiration_notifications`
- **Location**: `main/management/commands/send_expiration_notifications.py`
- **Purpose**: Sends notifications to users about ads expiring soon
- **Features**:
  - Default: 3 days before expiration
  - Configurable with `--days` parameter
  - Email and in-app notifications
- **Schedule**: Daily at 9:00 AM
- **Impact**: User engagement, retention

#### `process_facebook_share_requests` ⭐ NEW
- **Location**: `main/management/commands/process_facebook_share_requests.py`
- **Purpose**: Processes pending Facebook share requests
- **Features**:
  - Notifies admins about pending requests with `--notify-admins`
  - Auto-rejects old requests (default: 30 days)
  - Provides statistics and age breakdown
- **Schedule**: Daily at 10:00 AM
- **Impact**: Admin workflow efficiency

## 📊 Automation Impact

### Business Logic
- ✅ Premium subscriptions auto-expire
- ✅ Ads auto-expire when past due date
- ✅ Orders auto-cancel when unpaid
- ✅ Payments auto-fail after timeout

### Database Hygiene
- ✅ Old notifications cleaned weekly
- ✅ Expired features removed daily
- ✅ Sessions cleared daily
- ✅ Stale payments marked as failed

### User Experience
- ✅ Expiration notifications keep users informed
- ✅ Package expiration alerts prevent waste
- ✅ Order cancellation notifications

### Admin Efficiency
- ✅ Facebook request notifications
- ✅ Automatic old request rejection
- ✅ Comprehensive task monitoring

## 🚀 Quick Setup

### 1. Install Django-Q2
```bash
pip install django-q2
python manage.py migrate
```

### 2. Setup All Scheduled Tasks
```bash
# Development
python manage.py setup_scheduled_tasks

# Production (with specific settings)
python manage.py setup_scheduled_tasks --task-settings=idrissimart.settings.production

# Reset and recreate all tasks
python manage.py setup_scheduled_tasks --reset --task-settings=idrissimart.settings.production
```

### 3. Start the Worker
```bash
# Development
python manage.py qcluster

# Production (systemd)
sudo systemctl start idrissimart-qcluster
```

## 📋 Task Schedule Summary

| Time | Command | Frequency | Purpose |
|------|---------|-----------|---------|
| 02:00 | check_expired_ads | Daily | Expire old ads |
| 02:10 | check_expired_subscriptions | Daily | Deactivate subscriptions |
| 02:20 | check_expired_packages | Daily | Report expired packages |
| 02:30 | check_pending_payments | Daily | Fail stale payments |
| 03:00 | clear_expired_features | Daily | Clean up features |
| 03:00 | cleanup_old_notifications | Weekly | Delete old notifications |
| 04:00 | clearsessions | Daily | Clear sessions |
| 09:00 | send_expiration_notifications | Daily | Notify users |
| 10:00 | process_facebook_share_requests | Daily | Process FB requests |
| Every hour | check_expired_orders | Hourly | Cancel expired orders |

## 🔍 Testing Commands

All commands support `--dry-run` mode:

```bash
# Preview what would be cleaned up
python manage.py cleanup_old_notifications --dry-run
python manage.py check_expired_orders --dry-run
python manage.py check_pending_payments --hours 48 --dry-run
python manage.py process_facebook_share_requests --dry-run
```

## 📈 Monitoring

### Django Admin
- Navigate to **Django Q > Scheduled tasks** for active tasks
- Check **Django Q > Successful tasks** for history
- Review **Django Q > Failed tasks** for errors

### Command Line
```bash
# Watch qcluster logs
python manage.py qcluster

# Systemd logs
sudo journalctl -u idrissimart-qcluster -f
```

### Manual Execution
```bash
# Run any command manually
python manage.py check_expired_subscriptions
python manage.py cleanup_old_notifications --days 60
```

## 🔧 Customization

### Adjust Timeouts
```python
# In Django Admin or via command options
--hours 48          # For check_pending_payments
--days 60           # For cleanup_old_notifications
--auto-reject-days 14  # For process_facebook_share_requests
```

### Enable Notifications
```bash
# Add flags when scheduling
python manage.py check_expired_orders --notify-users --send-sms
python manage.py process_facebook_share_requests --notify-admins --send-sms
python manage.py check_expired_subscriptions --send-sms
```

### Configure SMS Alerts
```bash
# In Django Admin > Constance > Config
# Set these values:
ADMIN_ALERT_PHONE = "+966512345678"  # Admin phone for alerts
TWILIO_ENABLED = True
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "+12605822569"
```

## ⚠️ Important: SMS Configuration

**Before deploying to production**, configure these settings in Django Admin > Constance:

```
ADMIN_ALERT_PHONE = "+966512345678"  # Required for SMS alerts
TWILIO_ENABLED = True
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "+12605822569"
```

**Scheduled tasks are pre-configured with SMS alerts enabled.** If Twilio is not configured, commands will log errors but continue running.

## 📚 Documentation

- Full documentation: [docs/03_scheduled_tasks.md](docs/03_scheduled_tasks.md)
- Setup guide: Run `python manage.py setup_scheduled_tasks --help`
- Individual command help: `python manage.py <command> --help`

## ✨ Key Benefits

1. **Zero Manual Intervention**: All critical business logic automated
2. **Database Performance**: Regular cleanup prevents bloat
3. **User Engagement**: Timely notifications keep users informed
4. **Admin Efficiency**: Automated request processing and notifications
5. **Data Integrity**: Consistent state management across all models
6. **Scalability**: Handles growing data volumes automatically

## 🎯 Next Steps

1. Run `python manage.py setup_scheduled_tasks` to create all tasks
2. Start qcluster: `python manage.py qcluster`
3. Monitor Django Admin for task execution
4. Adjust schedules and parameters as needed
5. Set up systemd service for production

---

**Last Updated**: March 2026
**Status**: ✅ All automated tasks implemented and documented
