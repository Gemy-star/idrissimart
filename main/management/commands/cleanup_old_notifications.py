"""
Management command to clean up old read notifications.
This helps keep the notifications table clean and improves performance.
This should be run weekly via cron job or django-q2 scheduler.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import Notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Delete old read notifications to keep the database clean.
    By default, deletes read notifications older than 30 days.
    """

    help = "Deletes old read notifications from the database"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Delete read notifications older than this many days (default: 30)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, the command will only show what would be deleted without actually deleting.",
        )
        parser.add_argument(
            "--keep-unread",
            action="store_true",
            default=True,
            help="Keep unread notifications regardless of age (default: True)",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        days = kwargs["days"]
        dry_run = kwargs["dry_run"]
        keep_unread = kwargs["keep_unread"]

        cutoff_date = timezone.now() - timedelta(days=days)

        self.stdout.write(
            self.style.NOTICE(
                f"Looking for read notifications older than {cutoff_date.strftime('%Y-%m-%d')}..."
            )
        )

        # Find old read notifications
        query = Notification.objects.filter(
            created_at__lt=cutoff_date
        )

        if keep_unread:
            query = query.filter(is_read=True)

        old_notifications = query

        count = old_notifications.count()

        if count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would delete {count} old notification(s)."
                    )
                )

                # Show statistics
                stats_by_type = {}
                for notif in old_notifications[:100]:  # Sample first 100
                    notif_type = notif.notification_type or 'general'
                    stats_by_type[notif_type] = stats_by_type.get(notif_type, 0) + 1

                self.stdout.write("\nNotifications by type (sample):")
                for notif_type, type_count in stats_by_type.items():
                    self.stdout.write(f"  - {notif_type}: {type_count}")
            else:
                deleted_count, _ = old_notifications.delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully deleted {deleted_count} old notification(s)."
                    )
                )

                # Log the action
                logger.info(f"Deleted {deleted_count} old notifications (older than {days} days)")
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"No old notifications found (older than {days} days)."
                )
            )
