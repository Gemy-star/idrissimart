"""
Management command to check for expired user packages.
This should be run daily via cron job or django-q2 scheduler.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import UserPackage
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Check for user packages that have expired and log them.
    Note: UserPackage model has is_active() and is_expired() methods for checking status.
    This command helps identify expired packages for reporting and cleanup purposes.
    """

    help = "Finds and reports expired user ad packages"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, the command will only show what would be reported without taking action.",
        )
        parser.add_argument(
            "--notify-users",
            action="store_true",
            help="Send notifications to users about their expired packages.",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        now = timezone.now()
        dry_run = kwargs["dry_run"]
        notify_users = kwargs["notify_users"]

        self.stdout.write(
            self.style.NOTICE(
                f"Checking for expired packages as of {now.strftime('%Y-%m-%d %H:%M')}..."
            )
        )

        # Find all packages that have expired
        expired_packages = UserPackage.objects.filter(
            expiry_date__lt=now
        ).select_related('user', 'package')

        # Filter to only those with ads_remaining > 0 (unused ads in expired packages)
        expired_with_remaining = expired_packages.filter(ads_remaining__gt=0)

        total_count = expired_packages.count()
        wasted_count = expired_with_remaining.count()

        if total_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Found {total_count} expired package(s)."
                )
            )

            if wasted_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ {wasted_count} expired package(s) still have unused ads!"
                    )
                )

            # Calculate statistics
            total_wasted_ads = sum(pkg.ads_remaining for pkg in expired_with_remaining)

            self.stdout.write(
                self.style.WARNING(
                    f"Total wasted ads: {total_wasted_ads}"
                )
            )

            if not dry_run and notify_users:
                from main.models import Notification
                from django.contrib.contenttypes.models import ContentType

                notification_count = 0

                for package in expired_with_remaining[:50]:  # Limit to avoid overload
                    # Create notification for user
                    try:
                        Notification.objects.create(
                            user=package.user,
                            notification_type='package_expired',
                            title=f"انتهت صلاحية باقتك - Your Package Expired",
                            message=f"انتهت صلاحية باقة '{package.package.name if package.package else 'إعلان مجاني'}' ولديك {package.ads_remaining} إعلان متبقي. - Your package has expired with {package.ads_remaining} ads remaining.",
                            is_read=False
                        )
                        notification_count += 1
                    except Exception as e:
                        logger.error(f"Failed to create notification for user {package.user.username}: {e}")

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created {notification_count} notification(s) for users with expired packages."
                    )
                )

            # Show sample of expired packages
            self.stdout.write("\nExpired packages (first 10):")
            for package in expired_packages[:10]:
                package_name = package.package.name if package.package else "Free Ad"
                self.stdout.write(
                    f"  - User: {package.user.username}, Package: {package_name}, "
                    f"Expired: {package.expiry_date.strftime('%Y-%m-%d')}, "
                    f"Remaining ads: {package.ads_remaining}/{package.total_ads()}"
                )

            if total_count > 10:
                self.stdout.write(f"  ... and {total_count - 10} more")

            # Log the action
            logger.info(
                f"Found {total_count} expired packages, {wasted_count} with unused ads ({total_wasted_ads} total wasted ads)"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("No expired packages found.")
            )
