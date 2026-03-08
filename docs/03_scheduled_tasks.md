# 🕒 Scheduled Tasks (Cron Jobs)

This document explains how to set up automated tasks to perform regular maintenance on the Idrissi Mart application. These tasks are run using a scheduler like `cron` on a Linux server.

---

## 📋 Available Maintenance Commands

We have created several management commands to keep the application data clean and up-to-date.

### Core Expiration & Cleanup Commands

1.  **`check_expired_ads`**
    -   **Purpose**: Finds active ads that have passed their `expires_at` date and updates their status to `expired`.
    -   **Usage**: `python manage.py check_expired_ads`
    -   **Schedule**: Daily

2.  **`check_expired_subscriptions`**
    -   **Purpose**: Finds users with an active `is_premium` status whose `subscription_end` date has passed and sets their premium status to `False`. Also deactivates expired `UserSubscription` records.
    -   **Usage**: `python manage.py check_expired_subscriptions [--dry-run]`
    -   **Schedule**: Daily

3.  **`check_expired_packages`**
    -   **Purpose**: Reports on expired user ad packages and optionally notifies users who have unused ads in expired packages.
    -   **Usage**: `python manage.py check_expired_packages [--dry-run] [--notify-users]`
    -   **Schedule**: Daily

4.  **`check_expired_orders`**
    -   **Purpose**: Auto-cancels orders that have expired (passed their `expires_at` date) and are still in pending/unpaid status.
    -   **Usage**: `python manage.py check_expired_orders [--dry-run] [--notify-users]`
    -   **Schedule**: Hourly or Daily

5.  **`clear_expired_features`**
    -   **Purpose**: Deletes expired `AdFeature` records from the database.
    -   **Usage**: `python manage.py clear_expired_features [--dry-run]`
    -   **Schedule**: Daily

6.  **`clearsessions`**
    -   **Purpose**: A built-in Django command that clears expired user sessions from the database.
    -   **Usage**: `python manage.py clearsessions`
    -   **Schedule**: Daily

### Database Maintenance Commands

7.  **`cleanup_old_notifications`**
    -   **Purpose**: Deletes old read notifications to keep the database clean and improve performance.
    -   **Usage**: `python manage.py cleanup_old_notifications [--days 30] [--dry-run] [--keep-unread]`
    -   **Schedule**: Weekly
    -   **Default**: Deletes read notifications older than 30 days

8.  **`check_pending_payments`**
    -   **Purpose**: Marks stale pending payments as failed after a timeout period (default 24 hours).
    -   **Usage**: `python manage.py check_pending_payments [--hours 24] [--dry-run]`
    -   **Schedule**: Daily
    -   **Default**: Fails payments pending for more than 24 hours

### Notification & Admin Commands

9.  **`send_expiration_notifications`**
    -   **Purpose**: Sends notifications to users about ads expiring soon.
    -   **Usage**: `python manage.py send_expiration_notifications [--days 3] [--dry-run]`
    -   **Schedule**: Daily
    -   **Default**: Notifies users 3 days before ad expiration

10. **`process_facebook_share_requests`**
    -   **Purpose**: Processes pending Facebook share requests, notifies admins, and auto-rejects old requests.
    -   **Usage**: `python manage.py process_facebook_share_requests [--auto-reject-days 30] [--notify-admins] [--dry-run]`
    -   **Schedule**: Daily
    -   **Default**: Auto-rejects requests older than 30 days

---

## ⚙️ Setting Up Scheduled Tasks with Django-Q2

We use `django-q2` to manage background and scheduled tasks. This provides a robust, database-backed queue that is managed directly within the Django project.

### 1. Installation & Configuration

-   **Install**: `django-q2` is included in `pyproject.toml`. Install it with `pip install django-q2`.
-   **Configure**: Add `'django_q'` to `INSTALLED_APPS` in your settings and configure the `Q_CLUSTER` dictionary. We use the ORM as a broker, so no external services like Redis are needed.
-   **Migrate**: Run `python manage.py migrate` to create the necessary database tables for `django-q2`.

### 2. Running the Cluster

To process tasks, you must run a cluster worker process. In a separate terminal, run:

```bash
python manage.py qcluster
```

This process will listen for and execute tasks from the queue. In production, you would run this as a background service using a process manager like `systemd` or `supervisor`.

### 3. Creating a Scheduled Task

You can schedule management commands to run at specific intervals directly from the Django admin interface.

1.  Go to your Django admin panel and navigate to **Django Q > Scheduled tasks**.
2.  Click **"Add scheduled task"**.
3.  Fill out the form as follows for the `check_expired_ads` command:
    -   **Name**: `Daily Expired Ads Check`
    -   **Func**: `django.core.management.call_command`
    -   **Args**: `check_expired_ads` (Enter the name of the command here)
    -   **Schedule Type**: `Daily`
    -   **Repeats**: `-1` (to repeat indefinitely)
    -   **Next Run**: Set the date and time for the first run (e.g., tomorrow at 2:00 AM).

4.  Click **"Save"**.

Repeat this process for the other maintenance commands:

| Command | Admin Task Name | `Args` Field | Schedule Type | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `check_expired_ads` | Daily Expired Ads Check | `check_expired_ads` | Daily | Run at 2:00 AM |
| `check_expired_subscriptions` | Daily Subscription Check | `check_expired_subscriptions` | Daily | Run at 2:10 AM |
| `check_expired_packages` | Daily Package Check | `check_expired_packages` | Daily | Run at 2:20 AM |
| `check_expired_orders` | Hourly Order Expiration Check | `check_expired_orders` | Hourly | Run every hour |
| `clear_expired_features` | Daily Expired Features Cleanup | `clear_expired_features` | Daily | Run at 3:00 AM |
| `clearsessions` | Daily Session Cleanup | `clearsessions` | Daily | Run at 4:00 AM |
| `cleanup_old_notifications` | Weekly Notification Cleanup | `cleanup_old_notifications` | Weekly | Run on Sunday at 3:00 AM |
| `check_pending_payments` | Daily Payment Timeout Check | `check_pending_payments` | Daily | Run at 2:30 AM |
| `send_expiration_notifications` | Daily Expiration Reminders | `send_expiration_notifications` | Daily | Run at 9:00 AM |
| `process_facebook_share_requests` | Daily Facebook Request Processing | `process_facebook_share_requests,--notify-admins` | Daily | Run at 10:00 AM |

**Note**: The `Args` field can include command arguments. For example: `process_facebook_share_requests,--notify-admins` will pass the `--notify-admins` flag to the command.

Once saved, `django-q2` will automatically queue these commands to run at their scheduled times, as long as the `qcluster` process is running.

---

## 📝 Command Details & Best Practices

### Testing Commands

All commands support `--dry-run` mode to preview what would happen without making changes:

```bash
# Test what would be cleaned up
python manage.py cleanup_old_notifications --dry-run
python manage.py check_expired_orders --dry-run
python manage.py check_pending_payments --hours 48 --dry-run
```

### Command Options

#### check_expired_orders
- `--notify-users`: Send notifications to users about cancelled orders

#### check_expired_packages
- `--notify-users`: Send notifications to users about expired packages with remaining ads

#### cleanup_old_notifications
- `--days 30`: Delete notifications older than specified days (default: 30)
- `--keep-unread`: Keep unread notifications regardless of age (default: True)

#### check_pending_payments
- `--hours 24`: Mark payments as failed after specified hours (default: 24)

#### send_expiration_notifications
- `--days 3`: Send notifications X days before expiration (default: 3)

#### process_facebook_share_requests
- `--auto-reject-days 30`: Auto-reject requests older than specified days (default: 30)
- `--notify-admins`: Send notifications to admins about pending requests

### Recommended Schedule

#### Critical (Daily)
These commands should run daily to maintain core functionality:
- `check_expired_ads` - Expire old ads
- `check_expired_subscriptions` - Deactivate expired premium subscriptions
- `check_pending_payments` - Clean up stale payment records
- `send_expiration_notifications` - Notify users about expiring ads
- `clearsessions` - Clear expired sessions

#### Moderate (Daily/Hourly)
- `check_expired_orders` - Can run hourly to quickly cancel expired reservations
- `check_expired_packages` - Daily to track expired packages
- `clear_expired_features` - Daily to clean up expired ad features
- `process_facebook_share_requests` - Daily to notify admins

#### Light (Weekly)
- `cleanup_old_notifications` - Weekly is sufficient for notification cleanup

---

## 🔧 Automation Setup Script

You can also set up all scheduled tasks programmatically. The project includes a setup command:

```bash
# Basic setup (uses default settings)
python manage.py setup_scheduled_tasks

# Setup with specific Django settings module (for production)
python manage.py setup_scheduled_tasks --settings=idrissimart.settings.production

# Reset all tasks and recreate them
python manage.py setup_scheduled_tasks --reset

# Reset with specific settings
python manage.py setup_scheduled_tasks --reset --settings=idrissimart.settings.production
```

**Options:**
- `--reset`: Delete all existing scheduled tasks and recreate them
- `--settings`: Specify Django settings module for scheduled tasks (e.g., `idrissimart.settings.production`)

When you specify `--settings`, the command will automatically append the settings argument to all scheduled tasks, ensuring they use the correct configuration when running.

This will create all the scheduled tasks in Django-Q2 automatically.

---

## 📊 Monitoring Scheduled Tasks

### Via Django Admin

1. Go to **Django Q > Scheduled tasks** to view all scheduled tasks
2. Go to **Django Q > Successful tasks** to see completed task history
3. Go to **Django Q > Failed tasks** to troubleshoot any failures

### Via Command Line

Check the qcluster logs:

```bash
# If running qcluster manually
python manage.py qcluster

# If running as systemd service
sudo journalctl -u idrissimart-qcluster -f
```

### Manual Testing

Run any command manually to test:

```bash
# Test with dry-run first
python manage.py check_expired_subscriptions --dry-run

# Then run for real
python manage.py check_expired_subscriptions
```

---

## 🚀 Production Deployment

### Running qcluster as a Service

Create a systemd service file `/etc/systemd/system/idrissimart-qcluster.service`:

```ini
[Unit]
Description=Idrissi Mart Django-Q Cluster
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/WORK/idrissimart
Environment="PATH=/opt/WORK/idrissimart/venv/bin"
ExecStart=/opt/WORK/idrissimart/venv/bin/python manage.py qcluster
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable idrissimart-qcluster
sudo systemctl start idrissimart-qcluster
sudo systemctl status idrissimart-qcluster
```

---

## 🛠️ Troubleshooting

### Tasks Not Running

1. **Check if qcluster is running:**
   ```bash
   sudo systemctl status idrissimart-qcluster
   ```

2. **Check scheduled task configuration in Django admin:**
   - Verify the task is enabled
   - Check the next run time
   - Verify the function name is correct: `django.core.management.call_command`

3. **Check for errors in failed tasks:**
   - Go to Django Admin > Django Q > Failed tasks
   - Review error messages

### Performance Issues

If scheduled tasks are causing performance issues:

1. **Stagger task execution times** - Don't run all tasks at once
2. **Use `--dry-run` to estimate impact** before scheduling
3. **Adjust cleanup intervals** - Weekly instead of daily for heavy tasks
4. **Monitor database size** - Regular cleanup commands help maintain performance

### Common Issues

**Issue**: `check_expired_subscriptions` command not found
- **Solution**: Make sure the file exists at `main/management/commands/check_expired_subscriptions.py`

**Issue**: Tasks run but don't work
- **Solution**: Check if the command works when run manually first

**Issue**: Notifications not being created
- **Solution**: Ensure the `--notify-users` or `--notify-admins` flags are passed when needed

---

## 📈 Impact & Benefits

### Automated Cleanup
- **Old notifications**: Keeps database lean, improves query performance
- **Expired sessions**: Reduces session table bloat
- **Stale payments**: Cleans up abandoned payment records

### Business Logic Automation
- **Subscription expiration**: Ensures users lose premium access when subscription ends
- **Order cancellation**: Frees up reserved inventory automatically
- **Ad expiration**: Maintains integrity of active listings

### User Experience
- **Expiration notifications**: Keeps users informed about their ads
- **Package notifications**: Alerts users about unused ads before they expire
- **Order notifications**: Informs users about cancelled reservations

### Admin Efficiency
- **Facebook request notifications**: Admins don't miss pending requests
- **Auto-rejection**: Old requests don't pile up indefinitely
- **Payment cleanup**: Failed payments are clearly marked

---
