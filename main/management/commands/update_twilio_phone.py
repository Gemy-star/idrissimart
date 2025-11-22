"""
Management command to update Twilio phone number
"""

from django.core.management.base import BaseCommand
from constance import config


class Command(BaseCommand):
    help = "Update Twilio phone number to correct value"

    def handle(self, *args, **options):
        self.stdout.write("Updating Twilio phone number...")

        # Update the phone number
        config.TWILIO_PHONE_NUMBER = "+12605822569"

        # Verify
        phone = config.TWILIO_PHONE_NUMBER

        if phone == "+12605822569":
            self.stdout.write(
                self.style.SUCCESS(f"✓ Phone number updated successfully: {phone}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to update. Current value: {phone}")
            )
