from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import ClassifiedAd


class Command(BaseCommand):
    """
    A custom management command to check for and expire ads that have passed
    their `expires_at` date. This is intended to be run as a daily cron job.
    """

    help = "Finds and marks active classified ads as expired if their expiry date has passed."

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        now = timezone.now()
        self.stdout.write(
            self.style.NOTICE(
                f"Checking for expired ads as of {now.strftime('%Y-%m-%d %H:%M')}..."
            )
        )

        # Find all active ads where the expiry date is in the past
        expired_ads_qs = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE, expires_at__lt=now
        )

        count = expired_ads_qs.count()

        if count > 0:
            updated_count, _ = expired_ads_qs.update(
                status=ClassifiedAd.AdStatus.EXPIRED
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully marked {updated_count} ad(s) as expired."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("No active ads to expire."))
