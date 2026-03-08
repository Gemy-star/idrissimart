"""
Management command to process pending Facebook share requests.
This command sends notifications to admins about pending requests
and can optionally mark old requests as rejected.
This should be run daily via cron job or django-q2 scheduler.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from main.models import FacebookShareRequest, Notification
from main.services.sms_service import SMSService
from constance import config
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    """
    Process Facebook share requests:
    - Notify admins about pending requests
    - Auto-reject very old pending requests
    """

    help = "Processes Facebook share requests and notifies admins"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--auto-reject-days",
            type=int,
            default=30,
            help="Auto-reject pending requests older than this many days (default: 30, 0 to disable)",
        )
        parser.add_argument(
            "--notify-admins",
            action="store_true",
            help="Send notifications to admins about pending requests",
        )
        parser.add_argument(
            "--send-sms",
            action="store_true",
            help="Send SMS alerts to admin phone (requires ADMIN_ALERT_PHONE in config)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, the command will only show what would be done without actually doing it.",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        auto_reject_days = kwargs["auto_reject_days"]
        notify_admins = kwargs["notify_admins"]
        send_sms = kwargs["send_sms"]
        dry_run = kwargs["dry_run"]

        self.stdout.write(
            self.style.NOTICE(
                f"Processing Facebook share requests..."
            )
        )

        # Find all pending requests
        pending_requests = FacebookShareRequest.objects.filter(
            status=FacebookShareRequest.Status.PENDING
        ).select_related('user', 'ad').order_by('requested_at')

        total_pending = pending_requests.count()

        if total_pending > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ Found {total_pending} pending Facebook share request(s)."
                )
            )

            # Auto-reject old requests if enabled
            rejected_count = 0
            if auto_reject_days > 0:
                cutoff_date = timezone.now() - timedelta(days=auto_reject_days)
                old_requests = pending_requests.filter(requested_at__lt=cutoff_date)
                old_count = old_requests.count()

                if old_count > 0:
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f"DRY RUN: Would auto-reject {old_count} old request(s) (older than {auto_reject_days} days)."
                            )
                        )
                    else:
                        for request in old_requests:
                            try:
                                request.status = FacebookShareRequest.Status.REJECTED
                                request.processed_at = timezone.now()
                                request.save(update_fields=['status', 'processed_at'])

                                # Notify user
                                Notification.objects.create(
                                    user=request.user,
                                    notification_type='facebook_share_rejected',
                                    title="تم رفض طلب النشر على فيسبوك - Facebook Share Request Rejected",
                                    message=f"تم رفض طلب نشر الإعلان '{request.ad.title}' على فيسبوك بسبب انتهاء المهلة. - Your Facebook share request for ad '{request.ad.title}' was rejected due to timeout.",
                                    is_read=False
                                )
                                rejected_count += 1
                            except Exception as e:
                                logger.error(f"Failed to reject Facebook request {request.pk}: {e}")

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Auto-rejected {rejected_count} old request(s)."
                            )
                        )
                        logger.info(f"Auto-rejected {rejected_count} old Facebook share requests")

            # Notify admins about remaining pending requests
            remaining_pending = total_pending - rejected_count

            if notify_admins and remaining_pending > 0:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"DRY RUN: Would notify admins about {remaining_pending} pending request(s)."
                        )
                    )
                else:
                    # Get all admin/staff users
                    admins = User.objects.filter(is_staff=True, is_active=True)
                    admin_count = admins.count()

                    if admin_count > 0:
                        notification_count = 0
                        for admin in admins:
                            try:
                                Notification.objects.create(
                                    user=admin,
                                    notification_type='admin_facebook_pending',
                                    title=f"طلبات نشر فيسبوك قيد الانتظار - Pending Facebook Share Requests",
                                    message=f"لديك {remaining_pending} طلب نشر على فيسبوك قيد الانتظار. - You have {remaining_pending} pending Facebook share request(s) awaiting review.",
                                    is_read=False
                                )
                                notification_count += 1
                            except Exception as e:
                                logger.error(f"Failed to notify admin {admin.username}: {e}")

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Notified {admin_count} admin(s) about pending requests."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "⚠ No active admin users found to notify."
                            )
                        )

                    # Send SMS alert to admin if enabled
                    if send_sms and SMSService.is_enabled() and remaining_pending > 0:
                        try:
                            admin_phone = getattr(config, 'ADMIN_ALERT_PHONE', None)

                            if admin_phone:
                                sms_message = f"{config.SITE_NAME}: {remaining_pending} طلب نشر فيسبوك قيد الانتظار"
                                if SMSService.send_sms(admin_phone, sms_message):
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f"✓ SMS alert sent to admin."
                                        )
                                    )
                        except Exception as sms_error:
                            logger.error(f"Failed to send SMS alert: {sms_error}")
                    elif send_sms and not SMSService.is_enabled():
                        self.stdout.write(
                            self.style.WARNING(
                                "⚠ SMS service not enabled (Twilio not configured)."
                            )
                        )

            # Show statistics
            self.stdout.write("\nPending requests by age:")
            now = timezone.now()
            age_ranges = [
                (1, "< 1 day"),
                (7, "1-7 days"),
                (30, "1-4 weeks"),
                (float('inf'), "> 1 month")
            ]

            prev_days = 0
            for days, label in age_ranges:
                if days == float('inf'):
                    count = pending_requests.filter(
                        requested_at__lt=now - timedelta(days=prev_days)
                    ).count()
                else:
                    count = pending_requests.filter(
                        requested_at__gte=now - timedelta(days=days),
                        requested_at__lt=now - timedelta(days=prev_days) if prev_days > 0 else now
                    ).count()
                if count > 0:
                    self.stdout.write(f"  - {label}: {count}")
                prev_days = days if days != float('inf') else prev_days

        else:
            self.stdout.write(
                self.style.SUCCESS("✓ No pending Facebook share requests found.")
            )

        # Show overall statistics
        self.stdout.write("\n📊 Overall Statistics:")
        total_requests = FacebookShareRequest.objects.count()
        completed = FacebookShareRequest.objects.filter(status=FacebookShareRequest.Status.COMPLETED).count()
        in_progress = FacebookShareRequest.objects.filter(status=FacebookShareRequest.Status.IN_PROGRESS).count()
        rejected = FacebookShareRequest.objects.filter(status=FacebookShareRequest.Status.REJECTED).count()

        self.stdout.write(f"  Total requests: {total_requests}")
        self.stdout.write(f"  Pending: {total_pending}")
        self.stdout.write(f"  In progress: {in_progress}")
        self.stdout.write(f"  Completed: {completed}")
        self.stdout.write(f"  Rejected: {rejected}")
