"""
Management command to debug why ads are not showing on /categories/
"""
from django.core.management.base import BaseCommand
from main.models import ClassifiedAd, Category
from content.models import Country


class Command(BaseCommand):
    help = "Check ads and categories status for debugging /categories/ page"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n=== Checking Ads and Categories ===\n"))

        # Check total ads
        total_ads = ClassifiedAd.objects.count()
        self.stdout.write(f"Total ads in database: {total_ads}")

        # Check active ads
        active_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE
        ).count()
        self.stdout.write(f"Active ads: {active_ads}")

        # Check ads by status
        self.stdout.write("\n--- Ads by Status ---")
        for status_choice in ClassifiedAd.AdStatus.choices:
            count = ClassifiedAd.objects.filter(status=status_choice[0]).count()
            self.stdout.write(f"{status_choice[1]}: {count}")

        # Check countries
        self.stdout.write("\n--- Countries ---")
        countries = Country.objects.filter(is_active=True)
        for country in countries:
            ad_count = ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.ACTIVE, country=country
            ).count()
            self.stdout.write(f"{country.name} ({country.code}): {ad_count} active ads")

        # Check if ads have valid countries
        ads_without_country = ClassifiedAd.objects.filter(country__isnull=True).count()
        self.stdout.write(f"\nAds without country: {ads_without_country}")

        # Check categories
        self.stdout.write("\n--- Categories ---")
        total_categories = Category.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()
        self.stdout.write(f"Total categories: {total_categories}")
        self.stdout.write(f"Active categories: {active_categories}")

        # Check ads without categories
        ads_without_category = ClassifiedAd.objects.filter(
            category__isnull=True
        ).count()
        self.stdout.write(f"Ads without category: {ads_without_category}")

        # Sample active ads
        self.stdout.write("\n--- Sample Active Ads ---")
        sample_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE
        )[:5]
        for ad in sample_ads:
            country_name = ad.country.name if ad.country else "No country"
            category_name = ad.category.name if ad.category else "No category"
            self.stdout.write(
                f"ID: {ad.id} | {ad.title} | "
                f"Country: {country_name} | Category: {category_name}"
            )

        self.stdout.write(
            self.style.SUCCESS("\n=== Debugging Complete ===\n")
        )
