"""
Management command to send notifications for ads expiring soon
Run this command via cron job daily
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from main.models import ClassifiedAd, Notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "إرسال إشعارات للأعضاء بقرب انتهاء إعلاناتهم - Send expiration notifications to users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=3,
            help="عدد الأيام قبل الانتهاء لإرسال الإشعار - Days before expiry to send notification (default: 3)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="عرض النتائج فقط بدون إرسال إشعارات - Show results without sending notifications",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        # Get ads expiring soon
        expiring_ads = ClassifiedAd.objects.expiring_soon(days=days)

        count = expiring_ads.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ لا توجد إعلانات ستنتهي خلال {days} أيام"
                    f"\n✅ No ads expiring within {days} days"
                )
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"⚠️  تم العثور على {count} إعلان سينتهي خلال {days} أيام"
                f"\n⚠️  Found {count} ads expiring within {days} days"
            )
        )

        notifications_sent = 0
        emails_sent = 0

        for ad in expiring_ads:
            days_left = ad.days_until_expiry()

            self.stdout.write(
                f"  - [{ad.id}] {ad.title[:50]} "
                f"(باقي {days_left} يوم - {days_left} days left) "
                f"- المالك: {ad.user.username}"
            )

            if dry_run:
                continue

            # Create in-app notification
            try:
                notification_created = self.create_notification(ad, days_left)
                if notification_created:
                    notifications_sent += 1
            except Exception as e:
                logger.error(f"Error creating notification for ad {ad.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"    ❌ فشل إنشاء الإشعار: {str(e)}")
                )

            # Send email notification
            try:
                if ad.user.email and ad.user.email_notifications_enabled:
                    email_sent = self.send_email_notification(ad, days_left)
                    if email_sent:
                        emails_sent += 1
            except Exception as e:
                logger.error(f"Error sending email for ad {ad.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"    ❌ فشل إرسال البريد: {str(e)}")
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n🔍 وضع التجربة فعّال - لم يتم إرسال أي إشعارات"
                    "\n🔍 Dry run mode - No notifications sent"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ تم إرسال {notifications_sent} إشعار داخلي و {emails_sent} بريد إلكتروني"
                    f"\n✅ Sent {notifications_sent} in-app notifications and {emails_sent} emails"
                )
            )

    def create_notification(self, ad, days_left):
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
            action_url=f"/dashboard/ads/{ad.id}/renew/",
        )

        return True

    def send_email_notification(self, ad, days_left):
        """Send email notification to user"""
        try:
            subject = f'⏰ إعلانك "{ad.title[:40]}" سينتهي قريباً'

            # Prepare context for email template
            context = {
                "ad": ad,
                "days_left": days_left,
                "renewal_url": f"{settings.SITE_URL}/dashboard/ads/{ad.id}/renew/",
                "dashboard_url": f"{settings.SITE_URL}/dashboard/",
            }

            # Render email body (you would create this template)
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
