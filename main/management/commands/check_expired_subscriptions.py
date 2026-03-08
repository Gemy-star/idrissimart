"""
Management command to check for expired premium subscriptions and deactivate them.
This should be run daily via cron job or django-q2 scheduler.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from main.models import User, UserSubscription
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Check for users with expired premium subscriptions and deactivate them.
    """

    help = "Finds users with expired premium subscriptions and sets their premium status to False"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, the command will only show what would be updated without actually updating anything.",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        today = timezone.now().date()
        dry_run = kwargs["dry_run"]

        self.stdout.write(
            self.style.NOTICE(
                f"Checking for expired subscriptions as of {today.strftime('%Y-%m-%d')}..."
            )
        )

        # Find users with premium status but expired subscription_end date
        expired_users = User.objects.filter(
            is_premium=True,
            subscription_end__lt=today
        )

        user_count = expired_users.count()

        # Also update UserSubscription records
        expired_subscriptions = UserSubscription.objects.filter(
            is_active=True,
            end_date__lt=today
        )

        subscription_count = expired_subscriptions.count()

        if user_count > 0 or subscription_count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would deactivate premium status for {user_count} user(s)."
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would deactivate {subscription_count} subscription record(s)."
                    )
                )

                # Show the users that would be affected
                for user in expired_users[:10]:  # Show first 10
                    self.stdout.write(
                        f"  - {user.username} (subscription ended: {user.subscription_end})"
                    )
                if user_count > 10:
                    self.stdout.write(f"  ... and {user_count - 10} more")
            else:
                # Update users
                expired_users.update(is_premium=False)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully deactivated premium status for {user_count} user(s)."
                    )
                )

                # Update subscription records
                expired_subscriptions.update(is_active=False)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully marked {subscription_count} subscription(s) as inactive."
                    )
                )

                # Log the action
                logger.info(
                    f"Expired {user_count} premium subscriptions and {subscription_count} subscription records"
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("No expired subscriptions found.")
            )
