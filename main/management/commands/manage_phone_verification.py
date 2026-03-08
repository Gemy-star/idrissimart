"""
Management command to manage phone verification settings.

This command controls phone verification requirements across both:
1. Django-constance: ENABLE_MOBILE_VERIFICATION
2. SiteConfiguration: require_phone_verification

Usage:
    # Check current status
    python manage.py manage_phone_verification --status

    # Enable phone verification (both settings)
    python manage.py manage_phone_verification --enable

    # Disable phone verification (both settings)
    python manage.py manage_phone_verification --disable

    # Enable only constance setting
    python manage.py manage_phone_verification --enable --constance-only

    # Enable only site config setting
    python manage.py manage_phone_verification --enable --site-config-only

    # Force enable without confirmation
    python manage.py manage_phone_verification --enable --yes

    # Use specific settings module (production, docker, etc.)
    python manage.py manage_phone_verification --enable --settings=idrissimart.settings.production
    python manage.py manage_phone_verification --status --settings=idrissimart.settings.docker

    # Or use environment variable
    DJANGO_SETTINGS_MODULE=idrissimart.settings.production python manage.py manage_phone_verification --enable
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from constance import config
from content.site_config import SiteConfiguration


class Command(BaseCommand):
    help = (
        "Manage phone verification settings (django-constance and SiteConfiguration). "
        "Supports --settings for different environments (e.g., --settings=idrissimart.settings.production)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Enable phone verification",
        )
        parser.add_argument(
            "--disable",
            action="store_true",
            help="Disable phone verification",
        )
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show current phone verification status",
        )
        parser.add_argument(
            "--constance-only",
            action="store_true",
            help="Only update django-constance setting (ENABLE_MOBILE_VERIFICATION)",
        )
        parser.add_argument(
            "--site-config-only",
            action="store_true",
            help="Only update SiteConfiguration setting (require_phone_verification)",
        )
        parser.add_argument(
            "--yes",
            "-y",
            action="store_true",
            help="Skip confirmation prompts",
        )

    def handle(self, *args, **options):
        enable = options.get("enable")
        disable = options.get("disable")
        status = options.get("status")
        constance_only = options.get("constance_only")
        site_config_only = options.get("site_config_only")
        skip_confirmation = options.get("yes")

        # Check for conflicting options
        if sum([enable, disable, status]) > 1:
            raise CommandError("Cannot use --enable, --disable, and --status together")

        if sum([enable, disable, status]) == 0:
            raise CommandError(
                "Please specify one of: --enable, --disable, or --status"
            )

        if constance_only and site_config_only:
            raise CommandError(
                "Cannot use --constance-only and --site-config-only together"
            )

        # Show status
        if status:
            self.show_status()
            return

        # Get current values
        try:
            constance_value = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)
        except AttributeError:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  ENABLE_MOBILE_VERIFICATION not found in django-constance"
                )
            )
            constance_value = None

        try:
            site_config = SiteConfiguration.get_solo()
            site_config_value = site_config.require_phone_verification
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"⚠️  Error accessing SiteConfiguration: {e}"
                )
            )
            site_config_value = None

        # Determine action
        action = "enable" if enable else "disable"
        new_value = enable  # True for enable, False for disable

        # Show what will change
        from django.conf import settings as django_settings

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.HTTP_INFO(f"Phone Verification Settings - {action.upper()}")
        )
        self.stdout.write("=" * 60 + "\n")

        # Show current settings module
        settings_module = django_settings.SETTINGS_MODULE
        self.stdout.write(
            f"\n  🔧 Settings Module: {self.style.WARNING(settings_module)}\n"
        )

        changes = []

        if not site_config_only and constance_value is not None:
            if constance_value != new_value:
                changes.append(
                    f"  • Django-constance (ENABLE_MOBILE_VERIFICATION): {constance_value} → {new_value}"
                )
            else:
                self.stdout.write(
                    f"  • Django-constance: Already {new_value} ✓"
                )

        if not constance_only and site_config_value is not None:
            if site_config_value != new_value:
                changes.append(
                    f"  • SiteConfiguration (require_phone_verification): {site_config_value} → {new_value}"
                )
            else:
                self.stdout.write(
                    f"  • SiteConfiguration: Already {new_value} ✓"
                )

        if not changes:
            self.stdout.write("\n")
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Phone verification is already {action}d. No changes needed."
                )
            )
            return

        # Show changes
        self.stdout.write("\nChanges to be made:")
        for change in changes:
            self.stdout.write(self.style.WARNING(change))

        # Confirm
        if not skip_confirmation:
            self.stdout.write("\n")
            confirm = input(
                f"Are you sure you want to {action} phone verification? [y/N]: "
            )
            if confirm.lower() not in ["y", "yes"]:
                self.stdout.write(self.style.ERROR("\n❌ Operation cancelled."))
                return

        # Apply changes
        self.stdout.write("\n")
        with transaction.atomic():
            updated_count = 0

            # Update constance
            if not site_config_only and constance_value is not None and constance_value != new_value:
                try:
                    config.ENABLE_MOBILE_VERIFICATION = new_value
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Updated django-constance: ENABLE_MOBILE_VERIFICATION = {new_value}"
                        )
                    )
                    updated_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Failed to update django-constance: {e}"
                        )
                    )

            # Update site config
            if not constance_only and site_config_value is not None and site_config_value != new_value:
                try:
                    site_config.require_phone_verification = new_value
                    site_config.save(update_fields=["require_phone_verification"])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Updated SiteConfiguration: require_phone_verification = {new_value}"
                        )
                    )
                    updated_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Failed to update SiteConfiguration: {e}"
                        )
                    )

        # Final message
        self.stdout.write("\n" + "=" * 60)
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Successfully {action}d phone verification!"
                )
            )
            self.stdout.write(
                f"\n📱 Phone verification is now: {self.style.SUCCESS('ENABLED') if new_value else self.style.ERROR('DISABLED')}"
            )
        else:
            self.stdout.write(
                self.style.WARNING("\n⚠️  No settings were updated.")
            )
        self.stdout.write("\n")

    def show_status(self):
        """Display current status of phone verification settings"""
        from django.conf import settings as django_settings

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.HTTP_INFO("Phone Verification Status")
        )
        self.stdout.write("=" * 60 + "\n")

        # Show current settings module
        settings_module = django_settings.SETTINGS_MODULE
        self.stdout.write(
            f"\n  🔧 Settings Module: {self.style.WARNING(settings_module)}\n"
        )

        # Check constance
        try:
            constance_value = getattr(config, "ENABLE_MOBILE_VERIFICATION", None)
            if constance_value is None:
                self.stdout.write(
                    "  • Django-constance (ENABLE_MOBILE_VERIFICATION): "
                    + self.style.WARNING("NOT FOUND")
                )
            else:
                status_style = self.style.SUCCESS if constance_value else self.style.ERROR
                self.stdout.write(
                    f"  • Django-constance (ENABLE_MOBILE_VERIFICATION): {status_style(constance_value)}"
                )
        except Exception as e:
            self.stdout.write(
                f"  • Django-constance: {self.style.ERROR(f'ERROR - {e}')}"
            )

        # Check site config
        try:
            site_config = SiteConfiguration.get_solo()
            site_config_value = site_config.require_phone_verification
            status_style = self.style.SUCCESS if site_config_value else self.style.ERROR
            self.stdout.write(
                f"  • SiteConfiguration (require_phone_verification): {status_style(site_config_value)}"
            )
        except Exception as e:
            self.stdout.write(
                f"  • SiteConfiguration: {self.style.ERROR(f'ERROR - {e}')}"
            )

        # Overall status
        try:
            constance_enabled = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)
            site_config = SiteConfiguration.get_solo()
            site_config_enabled = site_config.require_phone_verification

            overall_enabled = constance_enabled or site_config_enabled

            self.stdout.write("\n" + "-" * 60)
            if overall_enabled:
                self.stdout.write(
                    "\n📱 Overall Status: " + self.style.SUCCESS("PHONE VERIFICATION ENABLED")
                )
                self.stdout.write(
                    "\n   (At least one setting is enabled - users must verify phone)"
                )
            else:
                self.stdout.write(
                    "\n📱 Overall Status: " + self.style.ERROR("PHONE VERIFICATION DISABLED")
                )
                self.stdout.write(
                    "\n   (Both settings are disabled - verification not required)"
                )
        except:
            pass

        self.stdout.write("\n" + "=" * 60 + "\n")
