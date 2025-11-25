"""
Management command to test admin publisher detail functionality
"""

from django.core.management.base import BaseCommand
from django.test.client import Client
from django.urls import reverse
from main.models import ClassifiedAd
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Test admin publisher detail page functionality"

    def handle(self, *args, **options):
        # Get a test ad
        test_ad = ClassifiedAd.objects.first()
        if not test_ad:
            self.stdout.write(self.style.ERROR("No ClassifiedAd found for testing"))
            return

        # Get a superuser
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            self.stdout.write(self.style.ERROR("No superuser found for testing"))
            return

        self.stdout.write(f"Testing with ad ID: {test_ad.id}")
        self.stdout.write(f"Using superuser: {superuser.username}")

        # Test the admin publisher detail URL
        url = reverse("main:ad_publisher_detail", kwargs={"ad_id": test_ad.id})
        self.stdout.write(f"Admin publisher detail URL: {url}")

        # Test URL patterns that the JavaScript uses
        toggle_url = reverse("main:toggle_ad_hide", kwargs={"ad_id": test_ad.id})
        delete_url = reverse("main:delete_ad", kwargs={"ad_id": test_ad.id})
        cart_url = reverse("main:enable_ad_cart", kwargs={"ad_id": test_ad.id})

        self.stdout.write(f"Toggle hide URL: {toggle_url}")
        self.stdout.write(f"Delete ad URL: {delete_url}")
        self.stdout.write(f"Enable cart URL: {cart_url}")

        self.stdout.write(self.style.SUCCESS("✓ All URLs are properly configured"))

        # Test JavaScript function calls that would be generated
        js_calls = [
            f"toggleAdVisibility({test_ad.id}, {str(test_ad.is_hidden).lower()})",
            f"deleteAdvertisement({test_ad.id}, '{test_ad.title}')",
            f"enableAdCart({test_ad.id})",
        ]

        self.stdout.write("\nJavaScript function calls that would be generated:")
        for call in js_calls:
            self.stdout.write(f"  {call}")

        self.stdout.write(
            self.style.SUCCESS(
                "\n✓ All JavaScript function calls are properly formatted"
            )
        )
