from constance import config
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging

from .models import AdPackage, ClassifiedAd, Notification, User, UserPackage
from .services.email_service import EmailService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ClassifiedAd)
def notify_admin_new_ad(sender, instance, created, **kwargs):
    """
    إرسال إشعار للإدارة عند إنشاء إعلان جديد
    Send notification to admin when a new ad is created
    """
    if created:
        # Check if admin notifications are enabled
        notify_enabled = getattr(config, "NOTIFY_ADMIN_NEW_ADS", False)
        if not notify_enabled:
            return

        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)

        for admin in superusers:
            Notification.objects.create(
                user=admin,
                title=_("إعلان جديد تم إنشاؤه"),
                message=_('تم إنشاء إعلان جديد "{ad_title}" من قبل {username}').format(
                    ad_title=instance.title, username=instance.user.username
                ),
                link=f"/admin/classifieds/ads/{instance.pk}/",
                notification_type=Notification.NotificationType.AD_APPROVED,
            )


@receiver(pre_save, sender=ClassifiedAd)
def auto_approve_verified_users(sender, instance, **kwargs):
    """
    الموافقة التلقائية على إعلانات الأعضاء الموثقين
    Auto-approve ads from verified users if category allows
    """
    if not instance.pk:  # New ad
        # Check if user is verified and category doesn't require approval
        if instance.user.verification_status == User.VerificationStatus.VERIFIED:
            if (
                hasattr(instance.category, "require_admin_approval")
                and not instance.category.require_admin_approval
            ):
                instance.status = ClassifiedAd.AdStatus.ACTIVE
                instance.reviewed_at = timezone.now()
                instance.require_review = False


@receiver(pre_save, sender=ClassifiedAd)
def send_ad_approval_notification(sender, instance, **kwargs):
    """
    Send a notification and email to the user when their ad is approved.
    """
    if instance.pk:
        try:
            old_instance = ClassifiedAd.objects.get(pk=instance.pk)
            # Check if the status is changing from 'pending' to 'active'
            if (
                old_instance.status == ClassifiedAd.AdStatus.PENDING
                and instance.status == ClassifiedAd.AdStatus.ACTIVE
            ):
                # 1. Create an in-app notification
                Notification.objects.create(
                    user=instance.user,
                    message=_(
                        'تهانينا! تمت الموافقة على إعلانك "{ad_title}" وهو الآن نشط على المنصة.'
                    ).format(ad_title=instance.title),
                    link=instance.get_absolute_url(),
                )

                # 2. Send an email notification
                # Check if email notifications are enabled
                email_notifications_enabled = EmailService.is_enabled()

                if email_notifications_enabled:
                    try:
                        # Send email using EmailService
                        email_service = EmailService()
                        success = email_service.send_ad_approved_email(
                            user=instance.user,
                            ad_title=instance.title,
                            ad_url=instance.get_absolute_url(),
                        )

                        if not success:
                            logger.error(
                                f"Failed to send approval email to {instance.user.email}"
                            )

                    except Exception as e:
                        # Log error but don't block the save operation
                        logger.error(f"Failed to send approval email: {str(e)}")

        except ClassifiedAd.DoesNotExist:
            pass  # This is a new ad, so no status change to handle


@receiver(post_save, sender=User)
def assign_default_package_to_new_user(sender, instance, created, **kwargs):
    """
    منح كل مستخدم جديد إعلان واحد مجاني
    Give each new user one free ad - they must buy a package after using it
    """
    if created:
        try:
            # Create a one-time free ad package for the new user
            # This is not based on any AdPackage - it's a standalone gift
            from datetime import timedelta

            UserPackage.objects.create(
                user=instance,
                package=None,  # No associated package - this is a free gift
                ads_remaining=1,  # Only 1 free ad
                expiry_date=timezone.now() + timedelta(days=365),  # Valid for 1 year
            )

            # Create welcome notification
            Notification.objects.create(
                user=instance,
                title=_("مرحباً بك في إدريسي مارت!"),
                message=_(
                    "تم منحك إعلان واحد مجاني! بعد استخدامه، يمكنك شراء باقة لنشر المزيد من الإعلانات."
                ),
                notification_type=Notification.NotificationType.GENERAL,
            )
        except Exception as e:
            # Log error but don't fail user registration
            print(f"Error assigning free ad to user {instance.username}: {e}")
