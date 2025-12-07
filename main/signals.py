from constance import config
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging

from .models import AdPackage, ClassifiedAd, Notification, User, UserPackage, Order
from .services.email_service import EmailService
from .services.sms_service import SMSService

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
    Assign default ad package to new DEFAULT users if it exists
    DEFAULT users get the is_default package
    PUBLISHER users don't need initial package (they purchase their own)
    """
    if created and instance.profile_type == User.ProfileType.DEFAULT:
        try:
            # Get the default ad package (is_default=True)
            default_package = AdPackage.objects.filter(
                is_default=True, is_active=True
            ).first()

            if default_package:
                # Assign the default package to the user
                from datetime import timedelta

                UserPackage.objects.create(
                    user=instance,
                    package=default_package,
                    ads_remaining=default_package.ad_count,  # Use ad_count field
                    expiry_date=timezone.now()
                    + timedelta(days=default_package.duration_days),
                )

                # Create welcome notification with package info
                Notification.objects.create(
                    user=instance,
                    title=_("مرحباً بك في إدريسي مارت!"),
                    message=_(
                        "تم منحك باقة {package_name} مع {ad_count} إعلان مجاني! يمكنك الترقية إلى ناشر لنشر إعلانات بدون موافقة الإدارة."
                    ).format(
                        package_name=default_package.name,
                        ad_count=default_package.ad_count,
                    ),
                    notification_type=Notification.NotificationType.GENERAL,
                )

                logger.info(
                    f"Assigned default package '{default_package.name}' to user {instance.username}"
                )
            else:
                # No default package found - create basic free entry
                from datetime import timedelta

                UserPackage.objects.create(
                    user=instance,
                    package=None,  # No package linked
                    ads_remaining=1,  # 1 free ad as fallback
                    expiry_date=timezone.now() + timedelta(days=365),
                )

                Notification.objects.create(
                    user=instance,
                    title=_("مرحباً بك في إدريسي مارت!"),
                    message=_(
                        "تم منحك إعلان واحد مجاني! يمكنك الترقية إلى ناشر أو شراء باقات لنشر المزيد من الإعلانات."
                    ),
                    notification_type=Notification.NotificationType.GENERAL,
                )

                logger.warning(
                    f"No default package found. Created basic free ad for user {instance.username}"
                )

        except Exception as e:
            # Log error but don't fail user registration
            logger.error(
                f"Error assigning default package to user {instance.username}: {e}"
            )


# ============================================
# ORDER SIGNALS
# ============================================


@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Send email and SMS notifications when order is created or status changes
    """
    if created:
        # New order created - notify customer and admin
        try:
            # 1. Send customer notification
            Notification.objects.create(
                user=instance.user,
                title=_("تم إنشاء طلبك بنجاح"),
                message=_(
                    "طلبك رقم {order_number} بمبلغ {amount} ريال تم إنشاؤه بنجاح."
                ).format(
                    order_number=instance.order_number, amount=instance.total_amount
                ),
                link=f"/orders/{instance.id}/",
                notification_type=Notification.NotificationType.GENERAL,
            )

            # 2. Send customer email
            if EmailService.is_enabled():
                try:
                    from django.conf import settings

                    # Get site URL from settings or use default
                    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")

                    email_service = EmailService()
                    email_service.send_template_email(
                        to_emails=[instance.user.email],
                        subject=_("تأكيد الطلب - {order_number}").format(
                            order_number=instance.order_number
                        ),
                        template_name="emails/order_created.html",
                        context={
                            "order": instance,
                            "user": instance.user,
                            "items": instance.items.all(),
                            "site_url": site_url,
                        },
                    )
                except Exception as e:
                    logger.error(f"Failed to send order creation email: {str(e)}")

            # 3. Send customer SMS
            if SMSService.is_enabled() and instance.phone:
                try:
                    sms_service = SMSService()
                    message = _(
                        "تم إنشاء طلبك {order_number} بنجاح. المبلغ: {amount} ريال. سنتواصل معك قريباً."
                    ).format(
                        order_number=instance.order_number, amount=instance.total_amount
                    )
                    sms_service.send_sms(instance.phone, message)
                except Exception as e:
                    logger.error(f"Failed to send order creation SMS: {str(e)}")

            # 4. Notify admin about new order
            superusers = User.objects.filter(is_superuser=True)
            for admin in superusers:
                Notification.objects.create(
                    user=admin,
                    title=_("طلب جديد - {order_number}").format(
                        order_number=instance.order_number
                    ),
                    message=_("طلب جديد من {customer} بمبلغ {amount} ريال").format(
                        customer=instance.full_name, amount=instance.total_amount
                    ),
                    link=f"/admin/orders/{instance.id}/",
                    notification_type=Notification.NotificationType.GENERAL,
                )

            # 5. Notify publishers whose items are in the order
            publishers = User.objects.filter(
                classifieds__order_items__order=instance
            ).distinct()

            for publisher in publishers:
                publisher_items = instance.items.filter(ad__user=publisher)
                publisher_revenue = sum(
                    item.get_total_price() for item in publisher_items
                )

                Notification.objects.create(
                    user=publisher,
                    title=_("طلب جديد يحتوي على منتجاتك"),
                    message=_(
                        "طلب رقم {order_number} - إيراداتك: {revenue} ريال"
                    ).format(
                        order_number=instance.order_number, revenue=publisher_revenue
                    ),
                    link=f"/publisher/orders/{instance.id}/",
                    notification_type=Notification.NotificationType.GENERAL,
                )

        except Exception as e:
            logger.error(f"Error sending order creation notifications: {str(e)}")


@receiver(pre_save, sender=Order)
def track_order_status_changes(sender, instance, **kwargs):
    """
    Track order status changes and send notifications
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)

            # Check if status changed
            if old_instance.status != instance.status:
                # Store old status for use in post_save
                instance._status_changed = True
                instance._old_status = old_instance.status

            # Check if payment status changed
            if old_instance.payment_status != instance.payment_status:
                instance._payment_status_changed = True
                instance._old_payment_status = old_instance.payment_status

        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Order)
def send_order_status_notifications(sender, instance, created, **kwargs):
    """
    Send notifications when order status or payment status changes
    """
    if not created:
        # Check if status changed
        if hasattr(instance, "_status_changed") and instance._status_changed:
            try:
                status_messages = {
                    "processing": _("طلبك قيد المعالجة"),
                    "shipped": _("تم شحن طلبك"),
                    "delivered": _("تم تسليم طلبك بنجاح"),
                    "cancelled": _("تم إلغاء طلبك"),
                    "refunded": _("تم استرداد مبلغ طلبك"),
                }

                status_msg = status_messages.get(
                    instance.status, _("تم تحديث حالة طلبك")
                )

                # Notify customer
                Notification.objects.create(
                    user=instance.user,
                    title=_("تحديث حالة الطلب - {order_number}").format(
                        order_number=instance.order_number
                    ),
                    message=status_msg,
                    link=f"/orders/{instance.id}/",
                    notification_type=Notification.NotificationType.GENERAL,
                )

                # Send SMS for important status changes
                if (
                    SMSService.is_enabled()
                    and instance.phone
                    and instance.status in ["shipped", "delivered"]
                ):
                    try:
                        sms_service = SMSService()
                        message = _("طلبك {order_number}: {status}").format(
                            order_number=instance.order_number, status=status_msg
                        )
                        sms_service.send_sms(instance.phone, message)
                    except Exception as e:
                        logger.error(f"Failed to send order status SMS: {str(e)}")

                # Clean up the flag
                del instance._status_changed
                del instance._old_status

            except Exception as e:
                logger.error(f"Error sending order status notifications: {str(e)}")

        # Check if payment status changed
        if (
            hasattr(instance, "_payment_status_changed")
            and instance._payment_status_changed
        ):
            try:
                if instance.payment_status == "paid":
                    # Notify customer of full payment
                    Notification.objects.create(
                        user=instance.user,
                        title=_("تم استلام الدفع - {order_number}").format(
                            order_number=instance.order_number
                        ),
                        message=_(
                            "تم استلام الدفع الكامل لطلبك بمبلغ {amount} ريال"
                        ).format(amount=instance.total_amount),
                        link=f"/orders/{instance.id}/",
                        notification_type=Notification.NotificationType.GENERAL,
                    )

                    # Send SMS
                    if SMSService.is_enabled() and instance.phone:
                        try:
                            sms_service = SMSService()
                            message = _(
                                "تم استلام الدفع الكامل لطلبك {order_number}. شكراً لك!"
                            ).format(order_number=instance.order_number)
                            sms_service.send_sms(instance.phone, message)
                        except Exception as e:
                            logger.error(
                                f"Failed to send payment confirmation SMS: {str(e)}"
                            )

                elif instance.payment_status == "partial":
                    # Notify customer of partial payment
                    Notification.objects.create(
                        user=instance.user,
                        title=_("تم استلام دفعة جزئية - {order_number}").format(
                            order_number=instance.order_number
                        ),
                        message=_(
                            "تم استلام {paid} ريال. المبلغ المتبقي: {remaining} ريال"
                        ).format(
                            paid=instance.paid_amount,
                            remaining=instance.remaining_amount,
                        ),
                        link=f"/orders/{instance.id}/",
                        notification_type=Notification.NotificationType.GENERAL,
                    )

                # Clean up the flag
                del instance._payment_status_changed
                del instance._old_payment_status

            except Exception as e:
                logger.error(f"Error sending payment status notifications: {str(e)}")
