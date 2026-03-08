"""
Management command to check for expired orders and auto-cancel them.
This helps clean up unpaid/pending orders that have exceeded their expiration time.
This should be run hourly or daily via cron job or django-q2 scheduler.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import Order, Notification
from main.services.sms_service import SMSService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Check for orders that have expired and auto-cancel them.
    Expired orders are those with expires_at in the past and status still 'pending'.
    """

    help = "Finds and auto-cancels expired orders that haven't been paid"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, the command will only show what would be cancelled without actually cancelling.",
        )
        parser.add_argument(
            "--notify-users",
            action="store_true",
            help="Send notifications to users about their cancelled orders.",
        )
        parser.add_argument(
            "--send-sms",
            action="store_true",
            help="Send SMS alerts to users about cancelled orders (requires --notify-users).",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        now = timezone.now()
        dry_run = kwargs["dry_run"]
        notify_users = kwargs["notify_users"]
        send_sms = kwargs["send_sms"]

        self.stdout.write(
            self.style.NOTICE(
                f"Checking for expired orders as of {now.strftime('%Y-%m-%d %H:%M')}..."
            )
        )

        # Find all pending/unpaid orders that have expired
        expired_orders = Order.objects.filter(
            expires_at__lt=now,
            status='pending',
            payment_status__in=['unpaid', 'partial']
        ).select_related('user')

        count = expired_orders.count()

        if count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would cancel {count} expired order(s)."
                    )
                )

                # Show the orders that would be affected
                for order in expired_orders[:10]:  # Show first 10
                    expired_str = order.expires_at.strftime('%Y-%m-%d %H:%M') if order.expires_at else 'N/A'
                    self.stdout.write(
                        f"  - Order #{order.order_number}, User: {order.user.username}, "
                        f"Expired: {expired_str}, "
                        f"Amount: {order.total_amount} {order.currency}"
                    )
                if count > 10:
                    self.stdout.write(f"  ... and {count - 10} more")
            else:
                cancelled_count = 0
                notification_count = 0
                sms_count = 0

                for order in expired_orders:
                    try:
                        # Update order status to cancelled
                        order.status = 'cancelled'
                        order.save(update_fields=['status'])
                        cancelled_count += 1

                        # Create notification for user if requested
                        if notify_users:
                            Notification.objects.create(
                                user=order.user,
                                notification_type='order_cancelled',
                                title="تم إلغاء طلبك - Order Cancelled",
                                message=f"تم إلغاء الطلب #{order.order_number} تلقائياً بسبب انتهاء المهلة. - Order #{order.order_number} was automatically cancelled due to expiration.",
                                is_read=False
                            )
                            notification_count += 1

                            # Send SMS if enabled and user has phone
                            if send_sms and SMSService.is_enabled() and order.user.phone:
                                try:
                                    sms_message = f"تم إلغاء الطلب #{order.order_number} بسبب انتهاء المهلة. المبلغ: {order.total_amount} {order.currency}"
                                    if SMSService.send_sms(order.user.phone, sms_message):
                                        sms_count += 1
                                except Exception as sms_error:
                                    logger.error(f"Failed to send SMS to {order.user.username}: {sms_error}")
                    except Exception as e:
                        logger.error(f"Failed to cancel order {order.order_number}: {e}")

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully cancelled {cancelled_count} expired order(s)."
                    )
                )

                if notify_users:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created {notification_count} notification(s)."
                        )
                    )

                    if send_sms:
                        if SMSService.is_enabled():
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✓ Sent {sms_count} SMS alert(s)."
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    "⚠ SMS service not enabled (Twilio not configured)."
                                )
                            )

                # Log the action
                logger.info(f"Auto-cancelled {cancelled_count} expired orders")
        else:
            self.stdout.write(
                self.style.SUCCESS("No expired orders found.")
            )
