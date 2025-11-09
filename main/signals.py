from constance import config
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import AdPackage, ClassifiedAd, Notification, User, UserPackage


@receiver(post_save, sender=ClassifiedAd)
def notify_admin_new_ad(sender, instance, created, **kwargs):
    """
    إرسال إشعار للإدارة عند إنشاء إعلان جديد
    Send notification to admin when a new ad is created
    """
    if created:
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
                        'تمت الموافقة على إعلانك "{ad_title}" وهو الآن مباشر.'
                    ).format(ad_title=instance.title),
                    link=instance.get_absolute_url(),
                )

                # 2. Send an email notification
                current_site = Site.objects.get_current()
                subject = config.AD_APPROVAL_EMAIL_SUBJECT.format(
                    ad_title=instance.title
                )
                context = {
                    "user": instance.user,
                    "ad": instance,
                    "site_url": f"https://{current_site.domain}",
                }
                html_message = render_to_string(
                    "emails/ad_approval_notification.html", context
                )

                send_mail(
                    subject=subject,
                    message="",
                    from_email=config.AD_APPROVAL_FROM_EMAIL,
                    recipient_list=[instance.user.email],
                    html_message=html_message,
                )
        except ClassifiedAd.DoesNotExist:
            pass  # This is a new ad, so no status change to handle


@receiver(post_save, sender=User)
def assign_default_package_to_new_user(sender, instance, created, **kwargs):
    """
    إعطاء باقة مجانية افتراضية عند تسجيل مستخدم جديد
    Assign default free package to newly registered users
    """
    if created:
        # Get the default package
        try:
            default_package = AdPackage.objects.filter(
                is_default=True, is_active=True, price=0  # Must be free
            ).first()

            if default_package:
                # Create user package
                UserPackage.objects.create(user=instance, package=default_package)

                # Create welcome notification
                Notification.objects.create(
                    user=instance,
                    title=_("مرحباً بك في إدريسي مارت!"),
                    message=_(
                        'تم منحك باقة "{package_name}" المجانية. '
                        "يمكنك الآن نشر {ad_count} إعلانات!"
                    ).format(
                        package_name=default_package.name,
                        ad_count=default_package.ad_count,
                    ),
                    notification_type=Notification.NotificationType.PACKAGE_EXPIRED,
                )
        except Exception as e:
            # Log error but don't fail user registration
            print(f"Error assigning default package to user {instance.username}: {e}")
