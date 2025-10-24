from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from main.models import AdFeature


class Command(BaseCommand):
    """
    A custom management command to clear expired ad features from the database.
    This can be run periodically (e.g., via a cron job) to maintain database hygiene.

    Example usage:
    python manage.py clear_expired_features
    """

    help = _("Deletes ad features that have passed their end_date.")

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="If set, the command will only show what would be deleted without actually deleting anything.",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        now = timezone.now()
        self.stdout.write(
            self.style.NOTICE(
                f"Checking for expired ad features as of {now.strftime('%Y-%m-%d %H:%M')}..."
            )
        )

        # Find all AdFeature objects where the end_date is in the past
        expired_features = AdFeature.objects.filter(end_date__lt=now)
        dry_run = kwargs["dry_run"]

        count = expired_features.count()

        if count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would delete {count} expired ad feature(s)."
                    )
                )
            else:
                expired_features.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully deleted {count} expired ad feature(s)."
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS("No expired ad features found."))
