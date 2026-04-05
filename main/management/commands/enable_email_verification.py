"""
Management command to enable email verification via Constance
"""

from django.core.management.base import BaseCommand
from constance import config


class Command(BaseCommand):
    help = "Enable email OTP verification for user registration"

    def handle(self, *args, **options):
        try:
            # Enable email verification
            config.ENABLE_EMAIL_VERIFICATION = True
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Email verification enabled successfully"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ENABLE_EMAIL_VERIFICATION = {config.ENABLE_EMAIL_VERIFICATION}"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  OTP_EXPIRY_MINUTES = {config.OTP_EXPIRY_MINUTES}"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  MAX_OTP_ATTEMPTS = {config.MAX_OTP_ATTEMPTS}"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to enable email verification: {e}")
            )
            raise
