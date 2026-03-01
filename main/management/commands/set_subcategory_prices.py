from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from main.models import Category


class Command(BaseCommand):
    help = "View and set ad_creation_price for subcategories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all subcategories with their current prices",
        )
        parser.add_argument(
            "--price",
            type=str,
            metavar="AMOUNT",
            help="Price to set (e.g. 10.00). Use 0 to reset to free/inherited.",
        )
        parser.add_argument(
            "--parent",
            type=str,
            metavar="SLUG",
            help="Only affect subcategories of this parent category (slug)",
        )
        parser.add_argument(
            "--section-type",
            type=str,
            choices=[c.value for c in Category.SectionType],
            metavar="TYPE",
            help="Filter subcategories by section type (job, course, service, product, classified)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without saving to the database",
        )

    def handle(self, *args, **options):
        # Build queryset: only subcategories (have a parent)
        qs = Category.objects.filter(parent__isnull=False).select_related("parent")

        if options["parent"]:
            try:
                parent = Category.objects.get(slug=options["parent"])
            except Category.DoesNotExist:
                raise CommandError(
                    f"Parent category with slug '{options['parent']}' not found."
                )
            qs = qs.filter(parent=parent)
            self.stdout.write(f"Filtering to subcategories of: {parent.name}")

        if options["section_type"]:
            qs = qs.filter(section_type=options["section_type"])
            self.stdout.write(f"Filtering by section type: {options['section_type']}")

        qs = qs.order_by("parent__name", "order", "name")

        if not qs.exists():
            self.stdout.write(self.style.WARNING("No subcategories found."))
            return

        # --list mode
        if options["list"] or not options["price"]:
            self._print_table(qs)
            if not options["price"]:
                self.stdout.write(
                    "\nUse --price AMOUNT to set prices. Use --parent SLUG to target a specific parent."
                )
            return

        # Parse price
        try:
            price = Decimal(options["price"])
            if price < 0:
                raise CommandError("Price cannot be negative.")
        except InvalidOperation:
            raise CommandError(f"Invalid price value: '{options['price']}'")

        # Preview or apply
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be saved.\n"))

        updated = 0
        skipped = 0

        with transaction.atomic():
            for subcat in qs:
                old_price = subcat.ad_creation_price
                if old_price == price:
                    skipped += 1
                    continue

                action = f"{old_price} → {price}"
                self.stdout.write(
                    f"  {'[DRY RUN] ' if dry_run else ''}"
                    f"{subcat.parent.name} > {subcat.name}: {action}"
                )

                if not dry_run:
                    subcat.ad_creation_price = price
                    subcat.save(update_fields=["ad_creation_price"])
                updated += 1

            if dry_run:
                transaction.set_rollback(True)

        verb = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{verb} {updated} subcategorie(s). Skipped {skipped} (already at target price)."
            )
        )

    def _print_table(self, qs):
        self.stdout.write(
            f"\n{'Parent':<30} {'Subcategory':<30} {'Section':<12} {'Own Price':>10} {'Effective Price':>15}"
        )
        self.stdout.write("-" * 100)

        current_parent = None
        for subcat in qs:
            if current_parent != subcat.parent_id:
                current_parent = subcat.parent_id
                self.stdout.write("")  # blank line between parent groups

            own_price = subcat.ad_creation_price
            effective = subcat.get_effective_ad_creation_price()
            inherited = " (inherited)" if subcat.is_price_inherited() else ""

            own_str = f"{own_price:.2f}" if own_price else "—"
            eff_str = f"{effective:.2f}{inherited}"

            self.stdout.write(
                f"{subcat.parent.name:<30} {subcat.name:<30} {subcat.section_type:<12} {own_str:>10} {eff_str:>15}"
            )
        self.stdout.write("")
