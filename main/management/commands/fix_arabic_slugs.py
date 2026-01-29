"""
Management command to fix slugs for Categories and ClassifiedAds
Creates Arabic-friendly slugs for proper filtering and URL generation
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from main.models import Category, ClassifiedAd


class Command(BaseCommand):
    help = "Fix slugs for all Categories and ClassifiedAds to support Arabic properly"

    def add_arguments(self, parser):
        parser.add_argument(
            "--categories-only",
            action="store_true",
            help="Only fix category slugs",
        )
        parser.add_argument(
            "--ads-only",
            action="store_true",
            help="Only fix classified ad slugs",
        )
        parser.add_argument(
            "--fix-country",
            action="store_true",
            help="Fix country for ads (set to Egypt for ads without country)",
        )
        parser.add_argument(
            "--country-code",
            type=str,
            default="EG",
            help="Country code to use when fixing ads (default: EG)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without actually changing anything",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        categories_only = options.get("categories_only", False)
        ads_only = options.get("ads_only", False)
        fix_country = options.get("fix_country", False)
        country_code = options.get("country_code", "EG")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN MODE - No changes will be saved\n")
            )

        # Fix categories unless ads_only flag is set
        if not ads_only:
            self.fix_category_slugs(dry_run)

        # Fix ads unless categories_only flag is set
        if not categories_only:
            self.fix_ad_slugs(dry_run, fix_country, country_code)

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS("\n✅ All slugs have been fixed successfully!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  This was a dry run. Run without --dry-run to apply changes."
                )
            )

    def fix_category_slugs(self, dry_run=False):
        """Fix slugs for all categories"""
        self.stdout.write(self.style.HTTP_INFO("\n" + "=" * 70))
        self.stdout.write(self.style.HTTP_INFO("📁 FIXING CATEGORY SLUGS"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70 + "\n"))

        categories = Category.objects.all().order_by("level", "id")
        total = categories.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No categories found."))
            return

        self.stdout.write(f"Found {total} categories to process\n")

        fixed_count = 0
        skipped_count = 0

        with transaction.atomic():
            for category in categories:
                try:
                    # Determine which name to use for slug generation
                    name_for_slug = category.name_ar or category.name

                    # Generate new slug with Unicode support for Arabic
                    new_slug = slugify(name_for_slug, allow_unicode=True)

                    # Fallback if slugify returns empty
                    if not new_slug:
                        new_slug = f"category-{category.id}"

                    # Ensure uniqueness for main slug
                    if new_slug != category.slug:
                        original_slug = new_slug
                        counter = 1
                        while (
                            Category.objects.filter(slug=new_slug)
                            .exclude(id=category.id)
                            .exists()
                        ):
                            new_slug = f"{original_slug}-{counter}"
                            counter += 1

                        old_slug = category.slug
                        display_name = category.name_ar or category.name

                        if not dry_run:
                            category.slug = new_slug
                            category.save(update_fields=["slug"])

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ {display_name}\n"
                                f"  Old: {old_slug} → New: {new_slug}"
                            )
                        )
                        fixed_count += 1
                    else:
                        skipped_count += 1

                    # Also fix slug_ar if it exists and is different
                    if hasattr(category, "slug_ar") and category.name_ar:
                        new_slug_ar = slugify(category.name_ar, allow_unicode=True)

                        if not new_slug_ar:
                            new_slug_ar = f"category-ar-{category.id}"

                        # Ensure uniqueness for Arabic slug
                        if new_slug_ar != category.slug_ar:
                            original_slug_ar = new_slug_ar
                            counter = 1
                            while (
                                Category.objects.filter(slug_ar=new_slug_ar)
                                .exclude(id=category.id)
                                .exists()
                            ):
                                new_slug_ar = f"{original_slug_ar}-{counter}"
                                counter += 1

                            if not dry_run:
                                category.slug_ar = new_slug_ar
                                category.save(update_fields=["slug_ar"])

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  Arabic slug: {category.slug_ar} → {new_slug_ar}"
                                )
                            )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Error fixing category {category.id}: {str(e)}"
                        )
                    )

            if dry_run:
                # Rollback in dry run mode
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Category Results: {fixed_count} fixed, {skipped_count} already correct"
            )
        )

    def fix_ad_slugs(self, dry_run=False, fix_country=False, country_code="EG"):
        """Fix slugs for all classified ads"""
        self.stdout.write(self.style.HTTP_INFO("\n" + "=" * 70))
        self.stdout.write(self.style.HTTP_INFO("📢 FIXING CLASSIFIED AD SLUGS"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70 + "\n"))

        ads = ClassifiedAd.objects.all().order_by("id")
        total = ads.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No classified ads found."))
            return

        self.stdout.write(f"Found {total} classified ads to process\n")
        
        if fix_country:
            self.stdout.write(
                self.style.WARNING(f"🌍 Will also fix country (set to {country_code} for ads without country)\n")
            )

        fixed_slug_count = 0
        skipped_slug_count = 0
        fixed_country_count = 0

        # Process in batches for better performance
        batch_size = 100
        processed = 0

        # Get the country object
        country_obj = None
        if fix_country:
            from content.models import Country
            try:
                country_obj = Country.objects.get(code=country_code)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Found country: {country_obj.name} ({country_code})\n")
                )
            except Country.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"✗ Country with code '{country_code}' not found!")
                )
                return

        with transaction.atomic():
            for ad in ads:
                try:
                    changed = False
                    update_fields = []
                    
                    # Fix slug
                    new_slug = slugify(ad.title, allow_unicode=True)

                    # Fallback if slugify returns empty
                    if not new_slug:
                        new_slug = f"ad-{ad.id}"

                    # Ensure uniqueness
                    if new_slug != ad.slug:
                        original_slug = new_slug
                        counter = 1
                        while (
                            ClassifiedAd.objects.filter(slug=new_slug)
                            .exclude(id=ad.id)
                            .exists()
                        ):
                            new_slug = f"{original_slug}-{counter}"
                            counter += 1

                        old_slug = ad.slug
                        
                        if not dry_run:
                            ad.slug = new_slug
                            update_fields.append("slug")
                        
                        changed = True
                        
                        # Show only a sample of changes to avoid flooding output
                        if fixed_slug_count < 10 or fixed_slug_count % 100 == 0:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✓ {ad.title[:50]}...\n"
                                    f"  Old slug: {old_slug} → New: {new_slug}"
                                )
                            )
                        fixed_slug_count += 1
                    else:
                        skipped_slug_count += 1
                    
                    # Fix country if requested
                    if fix_country and country_obj:
                        if ad.country is None or ad.country.code != country_code:
                            old_country = ad.country.code if ad.country else "None"
                            
                            if not dry_run:
                                ad.country = country_obj
                                if "country" not in update_fields:
                                    update_fields.append("country")
                            
                            if fixed_country_count < 10 or fixed_country_count % 100 == 0:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"  🌍 Country: {old_country} → {country_code}"
                                    )
                                )
                            fixed_country_count += 1
                            changed = True
                    
                    # Save the ad if any changes were made
                    if not dry_run and changed and update_fields:
                        ad.save(update_fields=update_fields)

                    processed += 1
                    if processed % batch_size == 0:
                        self.stdout.write(f"  Progress: {processed}/{total} ads...")

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Error fixing ad {ad.id}: {str(e)}")
                    )

            if dry_run:
                # Rollback in dry run mode
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Classified Ad Results:\n"
                f"  - Slugs: {fixed_slug_count} fixed, {skipped_slug_count} already correct"
            )
        )
        
        if fix_country:
            self.stdout.write(
                self.style.SUCCESS(
                    f"  - Countries: {fixed_country_count} fixed to {country_code}"
                )
            )
