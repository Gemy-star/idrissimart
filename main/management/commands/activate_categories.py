"""
Management command to activate inactive categories in a production-safe way.

Usage:
    # Dry run (recommended first)
    python manage.py activate_categories --dry-run

    # Activate all inactive classified categories
    python manage.py activate_categories

    # Activate specific section type
    python manage.py activate_categories --section-type job

    # Activate only root categories (no subcategories)
    python manage.py activate_categories --roots-only

    # Production mode (uses docker settings)
    DJANGO_SETTINGS_MODULE=idrissimart.settings.docker python manage.py activate_categories
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from main.models import Category


class Command(BaseCommand):
    help = "Activate inactive categories (production-safe with confirmations)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be activated without making changes",
        )
        parser.add_argument(
            "--section-type",
            type=str,
            default="classified",
            help='Section type to activate (default: "classified")',
        )
        parser.add_argument(
            "--roots-only",
            action="store_true",
            help="Only activate root categories (no subcategories)",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip confirmation prompt (use with caution)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        section_type = options["section_type"]
        roots_only = options["roots_only"]
        auto_confirm = options["yes"]

        # Detect environment
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'idrissimart.settings')
        is_production = 'docker' in settings_module or not settings.DEBUG
        db_name = connection.settings_dict.get('NAME', 'Unknown')

        # Show current environment
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.WARNING("ENVIRONMENT INFORMATION"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"Settings Module: {settings_module}")
        self.stdout.write(f"Database: {db_name}")
        self.stdout.write(f"DEBUG Mode: {settings.DEBUG}")

        if is_production:
            self.stdout.write(self.style.ERROR("Environment: PRODUCTION ⚠️"))
        else:
            self.stdout.write(self.style.SUCCESS("Environment: DEVELOPMENT"))

        self.stdout.write("")
        self.stdout.write(f"Section Type: {section_type}")
        self.stdout.write(f"Roots Only: {roots_only}")
        self.stdout.write(f"Dry Run: {dry_run}")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Query for inactive categories
        query = Category.objects.filter(
            section_type=section_type,
            is_active=False,
        )

        if roots_only:
            query = query.filter(parent__isnull=True)

        inactive_categories = query.select_related('parent').order_by('name')
        count = inactive_categories.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ No inactive {section_type} categories found!"
                )
            )
            return

        # Show what will be activated
        self.stdout.write(
            self.style.WARNING(
                f"\nFound {count} inactive {section_type} categories:"
            )
        )
        self.stdout.write("=" * 70)

        for cat in inactive_categories:
            parent_info = f"(Subcategory of: {cat.parent.name})" if cat.parent else "(Root Category)"
            subcats_count = cat.get_children().count() if not cat.parent else 0
            subcats_info = f" | {subcats_count} subcategories" if subcats_count > 0 else ""

            self.stdout.write(
                f"\n  ID {cat.id}: {cat.name} / {cat.name_ar}"
            )
            self.stdout.write(f"    {parent_info}{subcats_info}")
            self.stdout.write(f"    Price: {cat.ad_creation_price}")

        self.stdout.write("\n" + "=" * 70)

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ DRY RUN: Would activate {count} categories"
                )
            )
            self.stdout.write(
                "\nRun without --dry-run to actually activate these categories."
            )
            return

        # Production safety check
        if is_production and not auto_confirm:
            self.stdout.write("\n" + "=" * 70)
            self.stdout.write(
                self.style.ERROR(
                    "⚠️  WARNING: PRODUCTION DATABASE MODIFICATION"
                )
            )
            self.stdout.write("=" * 70)
            self.stdout.write(f"Database: {db_name}")
            self.stdout.write(f"Settings: {settings_module}")
            self.stdout.write(f"Categories to activate: {count}")
            self.stdout.write("=" * 70)
            self.stdout.write(
                self.style.WARNING(
                    "\nThis will permanently activate these categories in production."
                )
            )
            self.stdout.write("")
            confirm = input("Type 'yes' to continue: ")
            if confirm.lower() != "yes":
                self.stdout.write(
                    self.style.ERROR("\n✗ Operation cancelled by user")
                )
                return

        # Perform activation
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.WARNING("ACTIVATING CATEGORIES..."))
        self.stdout.write("=" * 70)

        activated_count = 0
        for cat in inactive_categories:
            cat.is_active = True
            cat.save(update_fields=['is_active'])
            activated_count += 1
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Activated: {cat.name} / {cat.name_ar}")
            )

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ SUCCESS: Activated {activated_count} categories!"
            )
        )
        self.stdout.write("=" * 70)

        # Show summary
        total_active = Category.objects.filter(
            section_type=section_type,
            is_active=True,
        ).count()

        if roots_only:
            root_active = Category.objects.filter(
                section_type=section_type,
                is_active=True,
                parent__isnull=True,
            ).count()
            self.stdout.write(
                f"\nRoot categories active: {root_active}"
            )
        else:
            self.stdout.write(
                f"\nTotal {section_type} categories active: {total_active}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "\n✓ Categories are now visible in ad_form (after browser refresh)"
            )
        )
