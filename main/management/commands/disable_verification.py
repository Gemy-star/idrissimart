"""
Management command to disable email and phone verification requirements.
"""

from django.core.management.base import BaseCommand
from constance import config


class Command(BaseCommand):
    help = "Disable email and phone verification requirements (SiteConfiguration + constance)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email-only",
            action="store_true",
            help="Disable only email verification",
        )
        parser.add_argument(
            "--phone-only",
            action="store_true",
            help="Disable only phone verification",
        )
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Enable verification instead of disabling",
        )
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show current verification settings",
        )

    def handle(self, *args, **options):
        from content.site_config import SiteConfiguration

        site_config = SiteConfiguration.get_solo()

        if options["status"]:
            self._show_status(site_config)
            return

        enable = options["enable"]
        do_email = not options["phone_only"]
        do_phone = not options["email_only"]

        if do_email:
            site_config.require_email_verification = enable
        if do_phone:
            site_config.require_phone_verification = enable
            config.ENABLE_MOBILE_VERIFICATION = enable

        site_config.save()

        action = "ENABLED" if enable else "DISABLED"
        if do_email:
            self.stdout.write(
                self.style.SUCCESS(
                    f"SiteConfiguration.require_email_verification -> {enable}"
                )
            )
        if do_phone:
            self.stdout.write(
                self.style.SUCCESS(
                    f"SiteConfiguration.require_phone_verification -> {enable}"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"constance ENABLE_MOBILE_VERIFICATION -> {enable}"
                )
            )

        self.stdout.write(self.style.SUCCESS(f"\nVerification {action} successfully."))

    def _show_status(self, site_config):
        email_sc = site_config.require_email_verification
        phone_sc = site_config.require_phone_verification
        phone_constance = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)

        self.stdout.write("Current verification settings:")
        self.stdout.write(
            f"  SiteConfiguration.require_email_verification : {email_sc}"
        )
        self.stdout.write(
            f"  SiteConfiguration.require_phone_verification : {phone_sc}"
        )
        self.stdout.write(
            f"  constance ENABLE_MOBILE_VERIFICATION         : {phone_constance}"
        )
