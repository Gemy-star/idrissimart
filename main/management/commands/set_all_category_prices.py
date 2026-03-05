from decimal import Decimal
import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from main.models import Category


class Command(BaseCommand):
    help = "Set ad_creation_price to 300 for all categories and subcategories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--price",
            type=str,
            default="300",
            metavar="AMOUNT",
            help="Price to set for all categories (default: 300)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without saving to the database",
        )
        parser.add_argument(
            "--include-roots",
            action="store_true",
            help="Also update root/parent categories (default: only subcategories)",
        )
        parser.add_argument(
            "--section-type",
            type=str,
            choices=[c.value for c in Category.SectionType],
            metavar="TYPE",
            help="Filter categories by section type (job, course, service, product, classified)",
        )

    def handle(self, *args, **options):
        # Display current settings module
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'Unknown')
        db_name = settings.DATABASES['default']['NAME']
        debug_mode = settings.DEBUG

        self.stdout.write(
            self.style.WARNING(
                f"\n{'='*80}\n"
                f"Settings Module: {settings_module}\n"
                f"Database: {db_name}\n"
                f"DEBUG Mode: {debug_mode}\n"
                f"{'='*80}\n"
            )
        )

        # Safety check for production
        if not debug_mode and not options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  WARNING: Running on PRODUCTION database!\n"
                    "This will modify real data. Use --dry-run first to preview changes.\n"
                )
            )
            confirm = input("Are you sure you want to continue? Type 'yes' to proceed: ")
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR("\nOperation cancelled."))
                return

        # Parse price
        try:
            price = Decimal(options["price"])
            if price < 0:
                self.stdout.write(self.style.ERROR("Price cannot be negative."))
                return
        except Exception:
            self.stdout.write(
                self.style.ERROR(f"Invalid price value: '{options['price']}'")
            )
            return

        # Build queryset
        if options["include_roots"]:
            # All categories
            qs = Category.objects.filter(is_active=True)
            msg = "all categories"
        else:
            # Only subcategories (have a parent)
            qs = Category.objects.filter(parent__isnull=False, is_active=True)
            msg = "subcategories only"

        # Apply section type filter if specified
        if options["section_type"]:
            qs = qs.filter(section_type=options["section_type"])
            msg += f" (section_type={options['section_type']})"

        qs = qs.select_related("parent").order_by("parent__name", "name")

        if not qs.exists():
            self.stdout.write(self.style.WARNING("No categories found matching criteria."))
            return

        # Show summary
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN — no changes will be saved.\n")
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSetting ad_creation_price to {price} for {msg}"
            )
        )
        self.stdout.write(f"Found {qs.count()} categories to update.\n")

        # Show preview
        self._print_table(qs, price)

        # Update prices
        if not dry_run:
            self.stdout.write("\nApplying changes...")

            updated = 0
            skipped = 0

            with transaction.atomic():
                for category in qs:
                    old_price = category.ad_creation_price
                    if old_price == price:
                        skipped += 1
                        continue

                    category.ad_creation_price = price
                    category.save(update_fields=["ad_creation_price"])
                    updated += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Updated {updated} categories, skipped {skipped} (already had target price)"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nDry run complete. Use without --dry-run to apply changes."
                )
            )

    def _print_table(self, qs, new_price):
        """Display categories in a formatted table"""
        self.stdout.write(
            f"\n{'ID':<6} {'Parent':<30} {'Category':<35} {'Current':>10} {'New':>10}"
        )
        self.stdout.write("-" * 95)

        current_parent = None
        for cat in qs:
            if cat.parent and current_parent != cat.parent_id:
                current_parent = cat.parent_id
                self.stdout.write("")  # blank line between parent groups

            parent_name = cat.parent.name if cat.parent else "ROOT"
            current_price = f"{cat.ad_creation_price:.2f}"
            new_price_str = f"{new_price:.2f}"
            change_indicator = "→" if cat.ad_creation_price != new_price else "="

            self.stdout.write(
                f"{cat.id:<6} {parent_name:<30} {cat.name:<35} {current_price:>10} {change_indicator} {new_price_str:>8}"
            )

        self.stdout.write("-" * 95)
        self.stdout.write(f"Total: {qs.count()} categories\n")
