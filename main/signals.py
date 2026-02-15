from constance import config
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging

from .models import (
    AdPackage,
    ClassifiedAd,
    Notification,
    User,
    UserPackage,
    Order,
    Payment,
)
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
    Send a notification, email, and SMS to the user when their ad is approved or rejected.
    """
    if instance.pk:
        try:
            old_instance = ClassifiedAd.objects.get(pk=instance.pk)

            # Check if the status is changing from 'pending' to 'active' (APPROVED)
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
                email_notifications_enabled = EmailService.is_enabled()

                if email_notifications_enabled:
                    try:
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
                        logger.error(f"Failed to send approval email: {str(e)}")

                # 3. Send SMS notification for ad approval
                if SMSService.is_enabled():
                    try:
                        user_phone = getattr(instance.user, "mobile", None) or getattr(
                            instance.user, "phone", None
                        )
                        if user_phone:
                            SMSService.send_ad_notification(
                                phone_number=user_phone,
                                ad_title=instance.title[:30],  # Truncate for SMS
                                status=_("تمت الموافقة على إعلانك وهو الآن نشط"),
                            )
                    except Exception as e:
                        logger.error(f"Failed to send ad approval SMS: {str(e)}")

            # Check if the status is changing from 'pending' to 'rejected' (REJECTED)
            elif (
                old_instance.status == ClassifiedAd.AdStatus.PENDING
                and instance.status == ClassifiedAd.AdStatus.REJECTED
            ):
                # 1. Create an in-app notification for rejection
                rejection_reason = getattr(instance, "rejection_reason", "") or _(
                    "يرجى مراجعة شروط النشر"
                )
                Notification.objects.create(
                    user=instance.user,
                    message=_(
                        'للأسف، تم رفض إعلانك "{ad_title}". السبب: {reason}'
                    ).format(ad_title=instance.title, reason=rejection_reason),
                    link="/my-ads/",
                    notification_type=Notification.NotificationType.GENERAL,
                )

                # 2. Send SMS notification for ad rejection
                if SMSService.is_enabled():
                    try:
                        user_phone = getattr(instance.user, "mobile", None) or getattr(
                            instance.user, "phone", None
                        )
                        if user_phone:
                            SMSService.send_ad_notification(
                                phone_number=user_phone,
                                ad_title=instance.title[:30],
                                status=_("تم رفض إعلانك. يرجى مراجعة التفاصيل"),
                            )
                    except Exception as e:
                        logger.error(f"Failed to send ad rejection SMS: {str(e)}")

        except ClassifiedAd.DoesNotExist:
            pass  # This is a new ad, so no status change to handle


@receiver(post_save, sender=User)
def assign_default_package_to_new_user(sender, instance, created, **kwargs):
    """
    Assign default ad package to new DEFAULT users if it exists
    DEFAULT users get the is_default package
    PUBLISHER users don't need initial package (they purchase their own)

    Note: If verification is required for free package, the package will be
    assigned only after email and phone verification is complete.
    """
    if created and instance.profile_type == User.ProfileType.DEFAULT:
        try:
            from content.verification_utils import is_free_package_verification_required

            # Check if verification is required for free package
            verification_required = is_free_package_verification_required()

            # If verification is required, check if user is verified
            if verification_required:
                is_verified = instance.is_email_verified and instance.is_mobile_verified
                if not is_verified:
                    # Don't assign package yet - will be assigned after verification
                    logger.info(
                        f"Skipping package assignment for user {instance.username} - verification required"
                    )

                    # Create notification about verification requirement
                    Notification.objects.create(
                        user=instance,
                        title=_("مرحباً بك في إدريسي مارت!"),
                        message=_(
                            "للحصول على باقتك المجانية، يجب عليك التحقق من البريد الإلكتروني ورقم الموبايل أولاً."
                        ),
                        notification_type=Notification.NotificationType.GENERAL,
                    )
                    return

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


@receiver(pre_save, sender=User)
def assign_package_after_verification(sender, instance, **kwargs):
    """
    Assign free package to user after they complete verification
    This is triggered when is_email_verified or is_mobile_verified changes to True
    """
    if instance.pk:  # Only for existing users (not new registrations)
        try:
            from content.verification_utils import is_free_package_verification_required

            # Check if verification is required for free package
            verification_required = is_free_package_verification_required()

            if not verification_required:
                return  # Feature not enabled

            # Get the old user state from database
            try:
                old_user = User.objects.get(pk=instance.pk)
            except User.DoesNotExist:
                return

            # Check if user just became fully verified
            old_verified = old_user.is_email_verified and old_user.is_mobile_verified
            new_verified = instance.is_email_verified and instance.is_mobile_verified

            # Only proceed if user just became verified
            if not old_verified and new_verified:
                # Check if user already has a package
                has_package = UserPackage.objects.filter(user=instance).exists()

                if not has_package:
                    # Get the default ad package
                    default_package = AdPackage.objects.filter(
                        is_default=True, is_active=True
                    ).first()

                    if default_package:
                        from datetime import timedelta

                        UserPackage.objects.create(
                            user=instance,
                            package=default_package,
                            ads_remaining=default_package.ad_count,
                            expiry_date=timezone.now()
                            + timedelta(days=default_package.duration_days),
                        )

                        Notification.objects.create(
                            user=instance,
                            title=_("تم تفعيل باقتك المجانية!"),
                            message=_(
                                "تم التحقق من حسابك بنجاح! تم منحك باقة {package_name} مع {ad_count} إعلان مجاني."
                            ).format(
                                package_name=default_package.name,
                                ad_count=default_package.ad_count,
                            ),
                            notification_type=Notification.NotificationType.GENERAL,
                        )

                        logger.info(
                            f"Assigned free package to verified user {instance.username}"
                        )
                    else:
                        # No default package - create basic free entry
                        from datetime import timedelta

                        UserPackage.objects.create(
                            user=instance,
                            package=None,
                            ads_remaining=1,
                            expiry_date=timezone.now() + timedelta(days=365),
                        )

                        Notification.objects.create(
                            user=instance,
                            title=_("تم تفعيل باقتك المجانية!"),
                            message=_(
                                "تم التحقق من حسابك بنجاح! تم منحك إعلان واحد مجاني."
                            ),
                            notification_type=Notification.NotificationType.GENERAL,
                        )

                        logger.info(
                            f"Assigned basic free ad to verified user {instance.username}"
                        )

        except Exception as e:
            logger.error(
                f"Error assigning package after verification for user {instance.username}: {e}"
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
            # Get currency from order's ad
            currency = "ج.م"
            if instance.items.exists():
                first_item = instance.items.first()
                if first_item.ad and first_item.ad.country:
                    currency = first_item.ad.country.currency_symbol

            # 1. Send customer notification
            Notification.objects.create(
                user=instance.user,
                title=_("تم إنشاء طلبك بنجاح"),
                message=_(
                    "طلبك رقم {order_number} بمبلغ {amount} {currency} تم إنشاؤه بنجاح."
                ).format(
                    order_number=instance.order_number,
                    amount=instance.total_amount,
                    currency=currency,
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
                        "تم إنشاء طلبك {order_number} بنجاح. المبلغ: {amount} {currency}. سنتواصل معك قريباً."
                    ).format(
                        order_number=instance.order_number,
                        amount=instance.total_amount,
                        currency=currency,
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
                    message=_(
                        "طلب جديد من {customer} بمبلغ {amount} {currency}"
                    ).format(
                        customer=instance.full_name,
                        amount=instance.total_amount,
                        currency=currency,
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
                        "طلب رقم {order_number} - إيراداتك: {revenue} {currency}"
                    ).format(
                        order_number=instance.order_number,
                        revenue=publisher_revenue,
                        currency=currency,
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

                # Send email notification for order status update
                if EmailService.is_enabled():
                    try:
                        # Get currency from order's ad
                        currency = "ج.م"
                        if instance.items.exists():
                            first_item = instance.items.first()
                            if first_item.ad and first_item.ad.country:
                                currency = first_item.ad.country.currency_symbol

                        email_service = EmailService()
                        email_service.send_template_email(
                            to_emails=[instance.user.email],
                            subject=_("تحديث حالة الطلب - {order_number}").format(
                                order_number=instance.order_number
                            ),
                            template_name="emails/order_status_update.html",
                            context={
                                "order": instance,
                                "currency": currency,
                                "site_name": config.SITE_NAME,
                                "site_url": config.SITE_URL,
                            },
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to send order status update email: {str(e)}"
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
                    # Get currency from order's ad
                    currency = "ج.م"
                    if instance.items.exists():
                        first_item = instance.items.first()
                        if first_item.ad and first_item.ad.country:
                            currency = first_item.ad.country.currency_symbol

                    # Notify customer of full payment
                    Notification.objects.create(
                        user=instance.user,
                        title=_("تم استلام الدفع - {order_number}").format(
                            order_number=instance.order_number
                        ),
                        message=_(
                            "تم استلام الدفع الكامل لطلبك بمبلغ {amount} {currency}"
                        ).format(amount=instance.total_amount, currency=currency),
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
                            "تم استلام {paid} {currency}. المبلغ المتبقي: {remaining} {currency}"
                        ).format(
                            paid=instance.paid_amount,
                            remaining=instance.remaining_amount,
                            currency=currency,
                        ),
                        link=f"/orders/{instance.id}/",
                        notification_type=Notification.NotificationType.GENERAL,
                    )

                # Clean up the flag
                del instance._payment_status_changed
                del instance._old_payment_status

            except Exception as e:
                logger.error(f"Error sending payment status notifications: {str(e)}")


@receiver(post_save, sender=Payment)
def activate_package_on_payment_completion(sender, instance, created, **kwargs):
    """
    تفعيل الباقة تلقائياً عند اكتمال الدفع
    Automatically activate package when payment is marked as completed

    This handles both:
    - Electronic payments (auto-approved)
    - Manual payments (admin approved via InstaPay/Wallet)
    """
    # Only trigger if payment was just completed
    if instance.status == Payment.PaymentStatus.COMPLETED:
        # Check if UserPackage already exists for this payment
        existing_package = UserPackage.objects.filter(payment=instance).first()

        if not existing_package:
            # Get package info from metadata
            package_id = instance.metadata.get("package_id")

            if package_id:
                try:
                    package = AdPackage.objects.get(id=package_id)

                    # Create UserPackage
                    user_package = UserPackage.objects.create(
                        user=instance.user,
                        payment=instance,
                        package=package,
                        ads_remaining=package.ad_count,
                        expiry_date=timezone.now()
                        + timezone.timedelta(days=package.duration_days),
                    )

                    logger.info(
                        f"UserPackage created for payment #{instance.id}: "
                        f"{package.name} for user {instance.user.username}"
                    )

                    # Create notification for user
                    Notification.objects.create(
                        user=instance.user,
                        title=_("تم تفعيل باقتك - Package Activated"),
                        message=_(
                            'تم تفعيل باقة "{package_name}" بنجاح! لديك {ad_count} إعلان متاح.'
                        ).format(package_name=package.name, ad_count=package.ad_count),
                        link="/publisher/dashboard/",
                        notification_type=Notification.NotificationType.GENERAL,
                    )

                    # Send email notification
                    if EmailService.is_enabled():
                        try:
                            email_service = EmailService()
                            email_service.send_template_email(
                                to_emails=[instance.user.email],
                                subject=_("تم تفعيل باقتك - Package Activated"),
                                template_name="emails/package_activated.html",
                                context={
                                    "user": instance.user,
                                    "package": package,
                                    "user_package": user_package,
                                    "payment_amount": instance.amount,
                                    "site_name": config.SITE_NAME,
                                    "site_url": config.SITE_URL,
                                },
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to send package activation email: {str(e)}"
                            )

                    # Send SMS notification for package activation
                    if SMSService.is_enabled():
                        try:
                            user_phone = getattr(
                                instance.user, "mobile", None
                            ) or getattr(instance.user, "phone", None)
                            if user_phone:
                                sms_message = _(
                                    "تم تفعيل باقتك {package_name}! لديك {ad_count} إعلان. مبلغ: {amount}"
                                ).format(
                                    package_name=package.name[:15],
                                    ad_count=package.ad_count,
                                    amount=instance.amount,
                                )
                                SMSService.send_sms(user_phone, sms_message)
                        except Exception as e:
                            logger.error(
                                f"Failed to send package activation SMS: {str(e)}"
                            )

                except AdPackage.DoesNotExist:
                    logger.error(
                        f"AdPackage with id {package_id} not found for payment #{instance.id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error creating UserPackage for payment #{instance.id}: {str(e)}"
                    )
            else:
                logger.warning(f"Payment #{instance.id} has no package_id in metadata")
