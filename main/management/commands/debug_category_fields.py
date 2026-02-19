"""
Management command to debug category-custom field relationships
"""
from django.core.management.base import BaseCommand
from main.models import ClassifiedAd, CategoryCustomField, Category


class Command(BaseCommand):
    help = "Debug category and custom field relationships"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n=== Category Relationships Debug ===\n"))

        # Get a specific ad
        ad = ClassifiedAd.objects.filter(id=22).first()
        if not ad:
            self.stdout.write("Ad not found")
            return

        self.stdout.write(f"Ad: {ad.title}")
        self.stdout.write(f"Category: {ad.category.name} (ID: {ad.category.id})")
        self.stdout.write(f"Custom fields in ad: {list(ad.custom_fields.keys())}")

        # Get category ancestors
        ancestors = list(ad.category.get_ancestors())
        self.stdout.write(f"\nCategory ancestors:")
        for anc in ancestors:
            self.stdout.write(f"  - {anc.name} (ID: {anc.id})")

        # Check all categories
        categories_to_check = [ad.category] + ancestors
        self.stdout.write(f"\nSearching for CategoryCustomField in these categories:")
        for cat in categories_to_check:
            self.stdout.write(f"  - {cat.name} (ID: {cat.id})")

            # Find CategoryCustomField for this category
            ccf = CategoryCustomField.objects.filter(
                category=cat,
                is_active=True
            )

            self.stdout.write(f"    Found {ccf.count()} CategoryCustomField entries")
            for cf in ccf:
                self.stdout.write(f"      - {cf.custom_field.name} ({cf.custom_field.label})")

        # Check if there are any CategoryCustomFields with the field names in the ad
        self.stdout.write("\n--- Checking specific fields from ad ---")
        for field_name in ad.custom_fields.keys():
            ccf = CategoryCustomField.objects.filter(
                custom_field__name=field_name,
                is_active=True
            )
            self.stdout.write(f"\nField '{field_name}':")
            self.stdout.write(f"  Found in {ccf.count()} categories:")
            for cf in ccf:
                self.stdout.write(f"    - Category: {cf.category.name} (ID: {cf.category.id})")

        self.stdout.write(self.style.SUCCESS("\n=== Debug Complete ===\n"))
