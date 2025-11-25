"""
Management command to test inactive ad display
"""

from django.core.management.base import BaseCommand
from main.models import ClassifiedAd
from django.test.client import Client
from django.urls import reverse
from django.conf import settings


class Command(BaseCommand):
    help = "Test inactive ad display functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--make-inactive",
            type=int,
            help="Make a specific ad ID inactive for testing (will set to EXPIRED)",
        )
        parser.add_argument(
            "--test-ad",
            type=int,
            help="Test accessing a specific ad ID",
        )

    def handle(self, *args, **options):
        if options.get("make_inactive"):
            ad_id = options["make_inactive"]
            try:
                ad = ClassifiedAd.objects.get(pk=ad_id)
                old_status = ad.status
                ad.status = ClassifiedAd.AdStatus.EXPIRED
                ad.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Changed ad {ad_id} status from {old_status} to EXPIRED"
                    )
                )
            except ClassifiedAd.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"✗ Ad {ad_id} does not exist"))

        if options.get("test_ad"):
            ad_id = options["test_ad"]

            # Add testserver to ALLOWED_HOSTS temporarily
            original_allowed_hosts = settings.ALLOWED_HOSTS[:]
            if "testserver" not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append("testserver")

            try:
                url = reverse("main:ad_detail", kwargs={"pk": ad_id})
                client = Client()
                response = client.get(url, HTTP_HOST="testserver")

                self.stdout.write(f"Testing URL: {url}")
                self.stdout.write(f"Response status: {response.status_code}")

                if response.status_code == 200:
                    # Check if the response contains inactive ad warning
                    content = response.content.decode("utf-8")
                    if "ad_inactive" in content or "إعلان منتهي الصلاحية" in content:
                        self.stdout.write(
                            self.style.SUCCESS("✓ Inactive ad displayed with warning")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "⚠ Ad displayed normally (might be active)"
                            )
                        )
                elif response.status_code == 404:
                    self.stdout.write(
                        self.style.WARNING("⚠ Ad returned 404 (does not exist)")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Unexpected status: {response.status_code}")
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error testing ad: {str(e)}"))
            finally:
                # Restore original ALLOWED_HOSTS
                settings.ALLOWED_HOSTS[:] = original_allowed_hosts

        # Show current ad statuses
        self.stdout.write("\nCurrent ad statuses:")
        for ad in ClassifiedAd.objects.all().order_by("-id")[:5]:
            self.stdout.write(f"  ID {ad.id}: {ad.get_status_display()}")
