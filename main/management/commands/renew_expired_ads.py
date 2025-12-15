from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from main.models import ClassifiedAd


class Command(BaseCommand):
    """
    A custom management command to renew expired ads by extending their expiration date.
    This is useful for keeping ads active and preventing them from expiring.

    Usage:
        python manage.py renew_expired_ads --days 30
        python manage.py renew_expired_ads --days 30 --status active
        python manage.py renew_expired_ads --days 30 --dry-run
    """

    help = "Renews expired ads by extending their expiration date"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to extend the expiration date (default: 30)',
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['active', 'expired', 'all'],
            default='active',
            help='Status of ads to renew: active (expired but still marked active), expired, or all (default: active)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be renewed without actually updating the database',
        )

    def handle(self, *args, **options):
        """The main logic for the command."""
        now = timezone.now()
        days = options['days']
        status_filter = options['status']
        dry_run = options['dry_run']

        future_date = now + timedelta(days=days)

        self.stdout.write(
            self.style.NOTICE(
                f"Checking for ads to renew as of {now.strftime('%Y-%m-%d %H:%M')}..."
            )
        )

        # Build the queryset based on status filter
        if status_filter == 'active':
            # Ads marked as active but with expired expiration date
            queryset = ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.ACTIVE,
                expires_at__lt=now
            ).exclude(expires_at__isnull=True)
        elif status_filter == 'expired':
            # Ads marked as expired status
            queryset = ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.EXPIRED
            ).exclude(expires_at__isnull=True)
        else:  # all
            # Both active with past expiry and expired status
            queryset = ClassifiedAd.objects.filter(
                expires_at__lt=now
            ).exclude(expires_at__isnull=True).filter(
                status__in=[ClassifiedAd.AdStatus.ACTIVE, ClassifiedAd.AdStatus.EXPIRED]
            )

        count = queryset.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f"No ads found to renew with status filter: {status_filter}")
            )
            return

        # Show details of ads to be renewed
        self.stdout.write(
            self.style.WARNING(f"Found {count} ad(s) to renew:")
        )

        for ad in queryset[:10]:  # Show first 10 as preview
            self.stdout.write(
                f"  - Ad #{ad.id}: {ad.title[:50]} (expires: {ad.expires_at.strftime('%Y-%m-%d')}, status: {ad.status})"
            )

        if count > 10:
            self.stdout.write(f"  ... and {count - 10} more ads")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Would extend expiration date by {days} days to {future_date.strftime('%Y-%m-%d %H:%M')}"
                )
            )
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] Would update {count} ad(s)")
            )
        else:
            # Actually update the ads
            updated = queryset.update(
                expires_at=future_date,
                status=ClassifiedAd.AdStatus.ACTIVE  # Always set to active when renewing
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully renewed {updated} ad(s) with new expiration date: {future_date.strftime('%Y-%m-%d %H:%M')}"
                )
            )

            if status_filter in ['expired', 'all']:
                self.stdout.write(
                    self.style.SUCCESS(f"Ads have been reactivated (status changed to ACTIVE)")
                )
