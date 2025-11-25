"""
Management command to test ClassifiedAd 404 handling
"""

from django.core.management.base import BaseCommand
from django.test.client import Client
from django.urls import reverse


class Command(BaseCommand):
    help = "Test ClassifiedAd 404 error handling"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ad-id",
            type=int,
            default=42,
            help="ClassifiedAd ID to test (default: 42)",
        )

    def handle(self, *args, **options):
        ad_id = options["ad_id"]

        # Test the URL that's causing issues in production
        url = reverse("main:ad_detail", kwargs={"pk": ad_id})

        self.stdout.write(f"Testing URL: {url}")

        client = Client()
        try:
            response = client.get(url)
            self.stdout.write(f"Response status: {response.status_code}")

            if response.status_code == 404:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Correctly returned 404 for non-existent ad {ad_id}"
                    )
                )
            elif response.status_code == 200:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Ad {ad_id} exists and returned 200")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Unexpected status code: {response.status_code}"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Exception occurred: {str(e)}"))
