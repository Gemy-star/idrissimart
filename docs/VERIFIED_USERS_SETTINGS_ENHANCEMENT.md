# Verified Users Settings Enhancement

## Overview
Enhanced the `/dashboard/settings/` page to provide additional settings and features exclusively for verified users, giving them more control and premium features compared to normal users.

## Changes Made

### 1. View Updates (`main/views.py`)
- **PublisherSettingsView**: Added `is_verified` context variable to distinguish verified users in templates
- **New Verified-Only Endpoints**:
  - `publisher_update_business_profile`: Handle business profile updates (tax number, commercial register, specialization)
  - `publisher_update_advanced_notifications`: Manage advanced notification preferences
  - `publisher_update_auto_publish_settings`: Control auto-renewal and auto-boost features
  - `publisher_update_analytics_settings`: Enable/disable analytics and weekly reports

### 2. URL Patterns (`main/urls.py`)
Added new URL endpoints for verified-user settings:
- `/dashboard/settings/update-business-profile/`
- `/dashboard/settings/update-advanced-notifications/`
- `/dashboard/settings/update-auto-publish-settings/`
- `/dashboard/settings/update-analytics-settings/`

### 3. Template Updates (`templates/dashboard/publisher_settings.html`)
Added two new accordion sections visible only to verified users:

#### A. Advanced Settings (للموثقين)
- **Business Profile**: Tax number, commercial register, specialization
- **Advanced Notifications**: 
  - New messages alerts
  - Ad views statistics
  - Price alerts for similar products
- **Auto-Publish Settings**:
  - Auto-renew expired ads
  - Auto-boost ads during peak hours
- **Priority Support**: Access to premium support with faster response times

#### B. Business Analytics (للموثقين)
- **Performance Reports**: View total ad views, engagement rate, and average rating
- **Analytics Settings**:
  - Enable/disable advanced analytics
  - Weekly email reports option

### 4. Database Model Updates (`main/models.py`)
Added new fields to User model for verified users:

**Advanced Notifications:**
- `notify_new_messages` (Boolean, default=True)
- `notify_ad_views` (Boolean, default=False)
- `notify_price_alerts` (Boolean, default=False)

**Auto-Publish Settings:**
- `auto_renew_ads` (Boolean, default=False)
- `auto_boost_ads` (Boolean, default=False)

**Analytics Settings:**
- `enable_analytics` (Boolean, default=True)
- `weekly_reports` (Boolean, default=False)
- `total_ad_views` (Integer, default=0)
- `engagement_rate` (Decimal, default=0)

### 5. Migration File
Created migration `0999_add_verified_user_settings.py` to add all new fields to the database.

## Features for Verified Users

### Normal Users Can:
- Edit basic profile information
- Update notification preferences (email only)
- Change password and email
- Manage account settings
- Request verification

### Verified Users Additionally Get:
- ✅ Business profile management (tax info, commercial register)
- ✅ Advanced notification controls (3 types)
- ✅ Auto-publish settings (auto-renew, auto-boost)
- ✅ Priority support access
- ✅ Advanced analytics dashboard
- ✅ Weekly performance reports
- ✅ Profile image upload capability
- ✅ Auto-publish without manual review

## Security
All verified-only endpoints check user verification status before allowing changes:
```python
if not user.is_verified:
    return JsonResponse({
        "success": False,
        "message": _("يتطلب هذا الإعداد حساباً موثقاً"),
    }, status=403)
```

## UI/UX Enhancements
- Verified-only sections clearly marked with badge: **للموثقين** (For Verified Users)
- Accordion-style interface for better organization
- Real-time AJAX updates without page refresh
- Visual feedback with toast notifications
- Responsive design for mobile devices

## Next Steps
1. Run migration: `python manage.py migrate`
2. Test with both verified and unverified user accounts
3. Implement analytics tracking logic (if not already present)
4. Set up email notifications for weekly reports
5. Configure auto-renewal and auto-boost background tasks

## Files Modified
- `/Users/kriko/works/idrissimart/main/views.py`
- `/Users/kriko/works/idrissimart/main/urls.py`
- `/Users/kriko/works/idrissimart/main/models.py`
- `/Users/kriko/works/idrissimart/templates/dashboard/publisher_settings.html`
- `/Users/kriko/works/idrissimart/main/migrations/0999_add_verified_user_settings.py` (new)
