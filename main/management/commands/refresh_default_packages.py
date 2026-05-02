from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import User, UserPackage, AdPackage


class Command(BaseCommand):
    help = "Assign a fresh default package to DEFAULT users who have no active ads remaining"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            help="Refresh only a specific user (optional)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        target_username = options.get("username")

        default_package = AdPackage.objects.filter(is_default=True, is_active=True).first()
        if not default_package:
            self.stdout.write(self.style.ERROR("No default package found. Run setup_default_package first."))
            return

        now = timezone.now()
        users_qs = User.objects.filter(profile_type=User.ProfileType.DEFAULT)
        if target_username:
            users_qs = users_qs.filter(username=target_username)

        refreshed = 0
        for user in users_qs:
            has_active = UserPackage.objects.filter(
                user=user,
                expiry_date__gte=now,
                ads_remaining__gt=0,
            ).exists()

            if not has_active:
                self.stdout.write(f"  → {user.username}: no active ads remaining, assigning fresh package")
                if not dry_run:
                    UserPackage.objects.create(
                        user=user,
                        package=default_package,
                        ads_remaining=default_package.ad_count,
                        expiry_date=now + timedelta(days=default_package.duration_days),
                    )
                refreshed += 1

        verb = "Would refresh" if dry_run else "Refreshed"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} {refreshed} user(s) with default package '{default_package.name}' "
            f"(ad_count={default_package.ad_count}, duration={default_package.duration_days} days)"
        ))
