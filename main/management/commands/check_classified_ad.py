"""
Management command to check ClassifiedAd status in database
"""

from django.core.management.base import BaseCommand
from main.models import ClassifiedAd


class Command(BaseCommand):
    help = "Check ClassifiedAd status in database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ad-id",
            type=int,
            default=42,
            help="ClassifiedAd ID to check (default: 42)",
        )

    def handle(self, *args, **options):
        ad_id = options["ad_id"]

        self.stdout.write(f"Checking ClassifiedAd with ID: {ad_id}")

        try:
            ad = ClassifiedAd.objects.get(pk=ad_id)
            self.stdout.write(self.style.SUCCESS(f"✓ Ad {ad_id} exists:"))
            self.stdout.write(f"  Title: {ad.title}")
            self.stdout.write(f"  Status: {ad.get_status_display()}")
            self.stdout.write(f"  Created: {ad.created_at}")
            self.stdout.write(f"  User: {ad.user}")

            if ad.status == ClassifiedAd.AdStatus.ACTIVE:
                self.stdout.write(f"  ✓ Ad is ACTIVE and should be accessible")
            else:
                self.stdout.write(
                    f"  ⚠ Ad is {ad.get_status_display()} - will return 404 to public"
                )

        except ClassifiedAd.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"⚠ Ad {ad_id} does not exist in database")
            )
            self.stdout.write("This explains the 404 errors in production logs.")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error checking ad {ad_id}: {str(e)}")
            )

        # Also check recent ads for context
        self.stdout.write("\nRecent ClassifiedAds:")
        recent_ads = ClassifiedAd.objects.all().order_by("-id")[:5]
        for ad in recent_ads:
            self.stdout.write(
                f"  ID {ad.id}: {ad.title[:50]} - {ad.get_status_display()}"
            )
