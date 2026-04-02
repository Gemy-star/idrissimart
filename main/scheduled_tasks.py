"""
Django Q Scheduled Tasks
تعريف المهام المجدولة التي تعمل تلقائياً باستخدام Django Q
"""

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from main.models import ClassifiedAd, Notification
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


def expire_ads_task():
    """
    Task to expire ads that have passed their expiration date
    مهمة لإنهاء صلاحية الإعلانات التي انتهى وقتها

    Schedule: Daily at 2:00 AM
    """
    try:
        now = timezone.now()

        # Find active ads that have expired
        expired_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE,
            expires_at__isnull=False,
            expires_at__lte=now,
        ).select_related("user", "category")

        count = expired_ads.count()

        if count == 0:
            logger.info("✅ No expired ads found")
            return {"success": True, "count": 0, "message": "No expired ads"}

        # Update ads to expired status
        updated = expired_ads.update(status=ClassifiedAd.AdStatus.EXPIRED)

        logger.info(f"✅ Expired {updated} ads automatically")

        return {
            "success": True,
            "count": updated,
            "message": f"Successfully expired {updated} ads",
        }

    except Exception as e:
        logger.error(f"❌ Error in expire_ads_task: {str(e)}")
        return {"success": False, "error": str(e), "message": "Failed to expire ads"}


def send_expiration_notifications_task(days=3):
    """
    Task to send notifications for ads expiring soon
    مهمة لإرسال إشعارات للإعلانات القريبة من الانتهاء

    Args:
        days: Number of days before expiry to send notification

    Schedule: Daily at 10:00 AM (for 3 days) and 11:00 AM (for 7 days)
    """
    try:
        # Get ads expiring soon
        expiring_ads = ClassifiedAd.objects.expiring_soon(days=days)

        count = expiring_ads.count()

        if count == 0:
            logger.info(f"✅ No ads expiring within {days} days")
            return {
                "success": True,
                "count": 0,
                "message": f"No ads expiring within {days} days",
            }

        notifications_sent = 0
        emails_sent = 0

        for ad in expiring_ads:
            days_left = ad.days_until_expiry()

            # Create in-app notification
            try:
                notification_created = _create_notification(ad, days_left)
                if notification_created:
                    notifications_sent += 1
            except Exception as e:
                logger.error(f"Error creating notification for ad {ad.id}: {str(e)}")

            # Send email notification
            try:
                if ad.user.email and getattr(
                    ad.user, "email_notifications_enabled", True
                ):
                    email_sent = _send_email_notification(ad, days_left)
                    if email_sent:
                        emails_sent += 1
            except Exception as e:
                logger.error(f"Error sending email for ad {ad.id}: {str(e)}")

        logger.info(
            f"✅ Sent {notifications_sent} in-app notifications and "
            f"{emails_sent} emails for ads expiring in {days} days"
        )

        return {
            "success": True,
            "count": count,
            "notifications_sent": notifications_sent,
            "emails_sent": emails_sent,
            "message": f"Sent notifications for {count} ads",
        }

    except Exception as e:
        logger.error(f"❌ Error in send_expiration_notifications_task: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send expiration notifications",
        }


def send_7day_expiration_notifications_task():
    """
    Task to send 7-day expiration notifications
    مهمة لإرسال إشعارات قبل 7 أيام من الانتهاء

    Schedule: Daily at 11:00 AM
    """
    return send_expiration_notifications_task(days=7)


def _create_notification(ad, days_left):
    """Create in-app notification for user"""
    # Check if notification already sent for this ad recently
    existing = Notification.objects.filter(
        user=ad.user,
        notification_type="ad_expiring",
        related_ad=ad,
        created_at__gte=timezone.now() - timezone.timedelta(hours=24),
    ).exists()

    if existing:
        return False

    message_ar = f'إعلانك "{ad.title}" سينتهي خلال {days_left} يوم. قم بتجديده الآن لتجنب إيقاف ظهوره.'
    message_en = f'Your ad "{ad.title}" will expire in {days_left} day(s). Renew it now to keep it active.'

    Notification.objects.create(
        user=ad.user,
        notification_type="ad_expiring",
        message_ar=message_ar,
        message_en=message_en,
        related_ad=ad,
        action_url=f"/publisher/ads/{ad.id}/renew-options/",
    )

    return True


def _send_email_notification(ad, days_left):
    """Send email notification to user"""
    try:
        subject = f'⏰ إعلانك "{ad.title[:40]}" سينتهي قريباً'

        # Prepare context for email template
        context = {
            "ad": ad,
            "days_left": days_left,
            "renewal_url": f"{settings.SITE_URL}/publisher/ads/{ad.id}/renew-options/",
            "dashboard_url": f"{settings.SITE_URL}/dashboard/",
            "user": ad.user,
        }

        # Render email body
        message = f"""
مرحباً {ad.user.get_full_name() or ad.user.username},

إعلانك "{ad.title}" سينتهي خلال {days_left} يوم.

لتجنب إيقاف ظهور إعلانك، قم بتجديده الآن:
{context['renewal_url']}

تتوفر خيارات تجديد متعددة:
- تجديد مجاني لمدة 30 يوم
- تجديد مدفوع لمدد أطول
- تجديد مع تمييز للحصول على مزيد من المشاهدات

مع تحياتنا,
فريق إدريسي مارت
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ad.user.email],
            fail_silently=False,
        )

        return True

    except Exception as e:
        logger.error(f"Failed to send email to {ad.user.email}: {str(e)}")
        return False


def cleanup_old_notifications_task():
    """
    Task to cleanup old read notifications
    مهمة لحذف الإشعارات القديمة المقروءة

    Schedule: Weekly on Sunday at 3:00 AM
    """
    try:
        # Delete read notifications older than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)

        deleted_count, _ = Notification.objects.filter(
            is_read=True, created_at__lt=cutoff_date
        ).delete()

        logger.info(f"✅ Deleted {deleted_count} old read notifications")

        return {
            "success": True,
            "count": deleted_count,
            "message": f"Deleted {deleted_count} old notifications",
        }

    except Exception as e:
        logger.error(f"❌ Error in cleanup_old_notifications_task: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to cleanup notifications",
        }


def check_upgrade_expiry_task():
    """
    Task to check and deactivate expired ad upgrades
    مهمة للتحقق من انتهاء صلاحية تمييزات الإعلانات

    Schedule: Every 6 hours
    """
    try:
        from main.models import AdUpgradeHistory

        # Find active upgrades that have expired
        expired_upgrades = AdUpgradeHistory.objects.filter(
            is_active=True, end_date__lt=timezone.now()
        ).select_related("ad")

        count = expired_upgrades.count()

        if count == 0:
            logger.info("✅ No expired upgrades found")
            return {"success": True, "count": 0}

        # Deactivate expired upgrades
        for upgrade in expired_upgrades:
            upgrade.deactivate()

        logger.info(f"✅ Deactivated {count} expired upgrades")

        return {
            "success": True,
            "count": count,
            "message": f"Deactivated {count} expired upgrades",
        }

    except Exception as e:
        logger.error(f"❌ Error in check_upgrade_expiry_task: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check upgrade expiry",
        }


def send_daily_admin_report_task():
    """
    Task to send a daily summary report to the admin email.
    مهمة لإرسال تقرير يومي ملخص إلى بريد المسؤول

    Schedule: Daily at 8:00 AM
    """
    try:
        from constance import config
        from main.models import User

        now = timezone.now()
        since = now - timedelta(hours=24)

        # --- Last 24h stats ---
        new_users = User.objects.filter(created_at__gte=since).count()
        new_ads = ClassifiedAd.objects.filter(created_at__gte=since).count()
        expired_today = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.EXPIRED,
            updated_at__gte=since,
        ).count()
        rejected_today = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.REJECTED,
            updated_at__gte=since,
        ).count()
        sold_today = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.SOLD,
            updated_at__gte=since,
        ).count()
        new_verification_requests = User.objects.filter(
            verification_status=User.VerificationStatus.PENDING,
            updated_at__gte=since,
        ).count()

        # --- Pending actions ---
        pending_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.PENDING
        ).count()
        pending_verifications = User.objects.filter(
            verification_status=User.VerificationStatus.PENDING
        ).count()

        # --- Platform totals ---
        total_active_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE
        ).count()
        total_users = User.objects.filter(is_active=True).count()
        premium_users = User.objects.filter(is_premium=True).count()

        admin_email = getattr(config, "ADMIN_NOTIFICATION_EMAIL", None) or getattr(
            settings, "ADMINS", [("Admin", "admin@idrissimart.com")]
        )[0][1]

        site_url = getattr(config, "SITE_URL", getattr(settings, "SITE_URL", ""))
        admin_url = f"{site_url}/admin/"
        site_name = getattr(config, "SITE_NAME", "إدريسي مارت")

        context = {
            "report_date": now.strftime("%Y-%m-%d"),
            "new_users": new_users,
            "new_ads": new_ads,
            "expired_today": expired_today,
            "rejected_today": rejected_today,
            "sold_today": sold_today,
            "new_verification_requests": new_verification_requests,
            "pending_ads": pending_ads,
            "pending_verifications": pending_verifications,
            "total_active_ads": total_active_ads,
            "total_users": total_users,
            "premium_users": premium_users,
            "admin_url": admin_url,
            "site_name": site_name,
        }

        from main.services.email_service import EmailService

        sent = EmailService.send_template_email(
            to_emails=[admin_email],
            subject=f"[{site_name}] التقرير اليومي - {context['report_date']}",
            template_name="emails/daily_admin_report.html",
            context=context,
        )

        if sent:
            logger.info(f"✅ Daily admin report sent to {admin_email}")
            return {"success": True, "recipient": admin_email}
        else:
            logger.error("❌ Failed to send daily admin report")
            return {"success": False, "error": "Email send failed"}

    except Exception as e:
        logger.error(f"❌ Error in send_daily_admin_report_task: {str(e)}")
        return {"success": False, "error": str(e)}


# =======================
# Task Registration
# =======================
# These tasks should be registered in Django admin or via django-q schedule
# Or use this function to register them programmatically


def register_scheduled_tasks():
    """
    Register all scheduled tasks with Django Q
    يجب تشغيل هذه الدالة مرة واحدة لتسجيل المهام

    Usage:
        python manage.py shell
        >>> from main.scheduled_tasks import register_scheduled_tasks
        >>> register_scheduled_tasks()
    """
    from django_q.models import Schedule

    tasks = [
        {
            "func": "main.scheduled_tasks.expire_ads_task",
            "name": "Expire Ads Daily",
            "schedule_type": Schedule.DAILY,
            "repeats": -1,  # Infinite repeats
            "next_run": timezone.now().replace(hour=2, minute=0, second=0),
        },
        {
            "func": "main.scheduled_tasks.send_expiration_notifications_task",
            "name": "Send 3-Day Expiration Notifications",
            "schedule_type": Schedule.DAILY,
            "repeats": -1,
            "next_run": timezone.now().replace(hour=10, minute=0, second=0),
        },
        {
            "func": "main.scheduled_tasks.send_7day_expiration_notifications_task",
            "name": "Send 7-Day Expiration Notifications",
            "schedule_type": Schedule.DAILY,
            "repeats": -1,
            "next_run": timezone.now().replace(hour=11, minute=0, second=0),
        },
        {
            "func": "main.scheduled_tasks.cleanup_old_notifications_task",
            "name": "Cleanup Old Notifications",
            "schedule_type": Schedule.WEEKLY,
            "repeats": -1,
            "next_run": timezone.now().replace(hour=3, minute=0, second=0),
        },
        {
            "func": "main.scheduled_tasks.check_upgrade_expiry_task",
            "name": "Check Upgrade Expiry",
            "schedule_type": Schedule.HOURLY,
            "repeats": -1,
            "minutes": 360,  # Every 6 hours
        },
        {
            "func": "main.scheduled_tasks.send_daily_admin_report_task",
            "name": "Send Daily Admin Report",
            "schedule_type": Schedule.DAILY,
            "repeats": -1,
            "next_run": timezone.now().replace(hour=8, minute=0, second=0, microsecond=0),
        },
    ]

    for task_config in tasks:
        # Check if task already exists
        existing = Schedule.objects.filter(func=task_config["func"]).first()

        if existing:
            logger.info(f"Task {task_config['name']} already exists, updating...")
            for key, value in task_config.items():
                if key != "func":
                    setattr(existing, key, value)
            existing.save()
        else:
            logger.info(f"Creating task {task_config['name']}...")
            Schedule.objects.create(**task_config)

    logger.info("✅ All scheduled tasks registered successfully")
    return True
