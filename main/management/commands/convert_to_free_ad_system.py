"""
Management command to convert existing users to new free ad system
This is optional - run only if you want to reset existing users
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import User, UserPackage, AdPackage


class Command(BaseCommand):
    help = "Convert existing users to new one free ad system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-all",
            action="store_true",
            help="Reset all users to 1 free ad (WARNING: Deletes existing packages)",
        )
        parser.add_argument(
            "--only-new",
            action="store_true",
            help="Only apply to users without any packages",
        )

    def handle(self, *args, **options):
        reset_all = options["reset_all"]
        only_new = options["only_new"]

        if reset_all:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  WARNING: This will DELETE all existing user packages and give each user 1 free ad!"
                )
            )
            confirm = input('Are you sure? Type "yes" to continue: ')
            if confirm.lower() != "yes":
                self.stdout.write(self.style.ERROR("Operation cancelled."))
                return

            # Delete all existing user packages
            deleted_count = UserPackage.objects.all().delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f"✅ Deleted {deleted_count} existing packages")
            )

            # Give all users 1 free ad
            users = User.objects.all()
            created_count = 0

            for user in users:
                UserPackage.objects.create(
                    user=user,
                    package=None,
                    ads_remaining=1,
                    expiry_date=timezone.now() + timedelta(days=365),
                )
                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Created {created_count} free ad packages for all users"
                )
            )

        elif only_new:
            # Only create for users without any packages
            users_without_packages = User.objects.exclude(
                ad_packages__isnull=False
            ).distinct()

            created_count = 0
            for user in users_without_packages:
                UserPackage.objects.create(
                    user=user,
                    package=None,
                    ads_remaining=1,
                    expiry_date=timezone.now() + timedelta(days=365),
                )
                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Created {created_count} free ad packages for users without packages"
                )
            )

        else:
            self.stdout.write(
                self.style.WARNING("No option selected. Use --reset-all or --only-new")
            )
            self.stdout.write("")
            self.stdout.write("Examples:")
            self.stdout.write("  python manage.py convert_to_free_ad_system --only-new")
            self.stdout.write(
                "  python manage.py convert_to_free_ad_system --reset-all"
            )

        # Show statistics
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("📊 Current Statistics:"))

        total_users = User.objects.count()
        users_with_packages = (
            User.objects.filter(ad_packages__isnull=False).distinct().count()
        )
        free_ads = UserPackage.objects.filter(package__isnull=True).count()
        paid_packages = UserPackage.objects.filter(package__isnull=False).count()

        self.stdout.write(f"  Total Users: {total_users}")
        self.stdout.write(f"  Users with Packages: {users_with_packages}")
        self.stdout.write(f"  Free Ads: {free_ads}")
        self.stdout.write(f"  Paid Packages: {paid_packages}")
