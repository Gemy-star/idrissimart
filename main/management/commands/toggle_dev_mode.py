"""
Management command to enable Twilio development mode
"""

from django.core.management.base import BaseCommand
from constance import config


class Command(BaseCommand):
    help = "Enable Twilio development mode for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Enable development mode",
        )
        parser.add_argument(
            "--disable",
            action="store_true",
            help="Disable development mode",
        )

    def handle(self, *args, **options):
        if options["enable"]:
            config.TWILIO_DEVELOPMENT_MODE = True
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Development mode ENABLED - OTP will be printed to console"
                )
            )
        elif options["disable"]:
            config.TWILIO_DEVELOPMENT_MODE = False
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Development mode DISABLED - OTP will be sent via Twilio SMS"
                )
            )
        else:
            current = config.TWILIO_DEVELOPMENT_MODE
            status = "ENABLED" if current else "DISABLED"
            self.stdout.write(f"Current status: Development mode is {status}")
            self.stdout.write("\nUsage:")
            self.stdout.write("  python manage.py toggle_dev_mode --enable")
            self.stdout.write("  python manage.py toggle_dev_mode --disable")
