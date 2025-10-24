# 🕒 Scheduled Tasks (Cron Jobs)

This document explains how to set up automated tasks to perform regular maintenance on the Idrissi Mart application. These tasks are run using a scheduler like `cron` on a Linux server.

---

## 📋 Available Maintenance Commands

We have created several management commands to keep the application data clean and up-to-date.

1.  **`check_expired_ads`**
    -   **Purpose**: Finds active ads that have passed their `expires_at` date and updates their status to `expired`.
    -   **Usage**: `python manage.py check_expired_ads`

2.  **`check_expired_subscriptions`**
    -   **Purpose**: Finds users with an active `is_premium` status whose `subscription_end` date has passed and sets their premium status to `False`.
    -   **Usage**: `python manage.py check_expired_subscriptions`

3.  **`clear_expired_features`**
    -   **Purpose**: Deletes expired `AdFeature` records from the database.
    -   **Usage**: `python manage.py clear_expired_features`

4.  **`clearsessions`**
    -   **Purpose**: A built-in Django command that clears expired user sessions from the database.
    -   **Usage**: `python manage.py clearsessions`

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

| Command | Admin Task Name | `Args` Field | Schedule Type |
| :--- | :--- | :--- | :--- |
| `check_expired_ads` | Daily Expired Ads Check | `check_expired_ads` | Daily |
| `check_expired_subscriptions` | Daily Subscription Check | `check_expired_subscriptions` | Daily |
| `clear_expired_features` | Daily Expired Features Cleanup | `clear_expired_features` | Daily |
| `clearsessions` | Daily Session Cleanup | `clearsessions` | Daily |

Once saved, `django-q2` will automatically queue these commands to run at their scheduled times, as long as the `qcluster` process is running.
