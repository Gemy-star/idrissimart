from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import User


class Command(BaseCommand):
    """
    A command to check for users with expired premium subscriptions and
    revert their `is_premium` status to False.
    This is intended to be run as a daily cron job.
    """

    help = "Deactivates premium status for users whose subscription has expired."

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        today = timezone.now().date()
        self.stdout.write(
            self.style.NOTICE(
                f"Checking for expired subscriptions as of {today.strftime('%Y-%m-%d')}..."
            )
        )

        # Find all premium users whose subscription end date is in the past
        expired_users_qs = User.objects.filter(
            is_premium=True, subscription_end__lt=today
        )

        count = expired_users_qs.count()

        if count > 0:
            updated_count, _ = expired_users_qs.update(is_premium=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deactivated premium status for {updated_count} user(s)."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("No expired user subscriptions found.")
            )
