"""
Management command to clear all custom fields from categories.
Usage: python manage.py clear_custom_fields
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import CustomField, CustomFieldOption, CategoryCustomField


class Command(BaseCommand):
    help = "Clear all custom fields and their associations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm deletion (required to actually delete)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        confirm = options.get("confirm")

        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    "⚠ This will delete all custom fields, options, and category associations."
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "Run with --confirm flag to actually perform the deletion."
                )
            )
            self.stdout.write(
                "\nExample: python manage.py clear_custom_fields --confirm"
            )
            return

        # Count before deletion
        fields_count = CustomField.objects.count()
        options_count = CustomFieldOption.objects.count()
        associations_count = CategoryCustomField.objects.count()

        self.stdout.write("\nDeleting custom fields...")
        self.stdout.write(f"  - Custom Fields: {fields_count}")
        self.stdout.write(f"  - Field Options: {options_count}")
        self.stdout.write(f"  - Category Associations: {associations_count}")

        # Delete all
        CategoryCustomField.objects.all().delete()
        CustomFieldOption.objects.all().delete()
        CustomField.objects.all().delete()

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("✓ All custom fields have been deleted"))
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Deleted {fields_count} fields, {options_count} options, and {associations_count} associations"
            )
        )
