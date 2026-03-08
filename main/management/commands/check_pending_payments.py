"""
Management command to check for stale pending payments and mark them as failed.
Pending payments that remain in that state for too long should be considered failed.
This should be run daily via cron job or django-q2 scheduler.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import Payment
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Check for pending payments older than a threshold and mark them as failed.
    This helps clean up stuck payment records.
    """

    help = "Marks old pending payments as failed after a timeout period"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Mark pending payments as failed after this many hours (default: 24)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, the command will only show what would be updated without actually updating.",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        hours = kwargs["hours"]
        dry_run = kwargs["dry_run"]

        cutoff_time = timezone.now() - timedelta(hours=hours)

        self.stdout.write(
            self.style.NOTICE(
                f"Checking for pending payments older than {cutoff_time.strftime('%Y-%m-%d %H:%M')}..."
            )
        )

        # Find pending payments that are too old
        stale_payments = Payment.objects.filter(
            status=Payment.PaymentStatus.PENDING,
            created_at__lt=cutoff_time
        ).select_related('user')

        count = stale_payments.count()

        if count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would mark {count} pending payment(s) as failed."
                    )
                )

                # Show the payments that would be affected
                total_amount = sum(payment.amount for payment in stale_payments)

                self.stdout.write(
                    f"\nTotal amount in stale payments: {total_amount:.2f}"
                )

                # Show sample
                for payment in stale_payments[:10]:  # Show first 10
                    self.stdout.write(
                        f"  - Payment ID: {payment.pk}, User: {payment.user.username}, "
                        f"Amount: {payment.amount} {payment.currency}, "
                        f"Created: {payment.created_at.strftime('%Y-%m-%d %H:%M')}, "
                        f"Provider: {payment.provider}"
                    )
                if count > 10:
                    self.stdout.write(f"  ... and {count - 10} more")
            else:
                failed_count = 0

                for payment in stale_payments:
                    try:
                        # Mark payment as failed
                        payment.status = Payment.PaymentStatus.FAILED
                        if 'failure_reason' not in payment.metadata:
                            payment.metadata['failure_reason'] = f'Payment timeout after {hours} hours'
                            payment.metadata['auto_failed_at'] = timezone.now().isoformat()
                        payment.save(update_fields=['status', 'metadata'])
                        failed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to mark payment {payment.pk} as failed: {e}")

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully marked {failed_count} pending payment(s) as failed."
                    )
                )

                # Log the action
                logger.info(f"Auto-failed {failed_count} pending payments (older than {hours} hours)")
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"No stale pending payments found (older than {hours} hours)."
                )
            )
