"""
Management command to check custom fields in ads
"""
from django.core.management.base import BaseCommand
from main.models import ClassifiedAd, CategoryCustomField, CustomField


class Command(BaseCommand):
    help = "Check custom fields in classified ads"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n=== Checking Custom Fields ===\n"))

        # Check active ads
        active_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE
        )[:5]

        self.stdout.write(f"Checking first 5 active ads...\n")

        for ad in active_ads:
            self.stdout.write(f"\n--- Ad: {ad.title} (ID: {ad.id}) ---")
            self.stdout.write(f"Category: {ad.category.name if ad.category else 'No category'}")
            self.stdout.write(f"Custom fields data: {ad.custom_fields}")

            # Try to get custom fields for card
            card_fields = ad.get_custom_fields_for_card()
            self.stdout.write(f"Custom fields for card: {len(card_fields)} fields")
            for field in card_fields:
                self.stdout.write(f"  - {field['label']}: {field['value']}")

            # Try to get custom fields for detail
            detail_fields = ad.get_custom_fields_for_detail()
            self.stdout.write(f"Custom fields for detail: {len(detail_fields)} fields")
            for field in detail_fields:
                self.stdout.write(f"  - {field['label']}: {field['value']}")

        # Check CategoryCustomField configuration
        self.stdout.write("\n--- CategoryCustomField Configuration ---")
        cat_custom_fields = CategoryCustomField.objects.filter(is_active=True)
        self.stdout.write(f"Total active CategoryCustomFields: {cat_custom_fields.count()}")

        for ccf in cat_custom_fields[:10]:
            self.stdout.write(
                f"Category: {ccf.category.name} | "
                f"Field: {ccf.custom_field.name} ({ccf.custom_field.label}) | "
                f"Show on card: {ccf.show_on_card} | "
                f"Order: {ccf.order}"
            )

        self.stdout.write(self.style.SUCCESS("\n=== Check Complete ===\n"))
