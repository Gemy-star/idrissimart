"""
Management command to check Twilio configuration
"""

from django.core.management.base import BaseCommand
from constance import config


class Command(BaseCommand):
    help = "Check Twilio configuration from Constance"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n=== Twilio Configuration ===\n"))

        account_sid = getattr(config, "TWILIO_ACCOUNT_SID", "NOT SET")
        auth_token = getattr(config, "TWILIO_AUTH_TOKEN", "NOT SET")
        phone_number = getattr(config, "TWILIO_PHONE_NUMBER", "NOT SET")
        dev_mode = getattr(config, "TWILIO_DEVELOPMENT_MODE", "NOT SET")

        self.stdout.write(
            f"Account SID: {account_sid[:10]}...{account_sid[-4:]}"
            if account_sid != "NOT SET"
            else "Account SID: NOT SET"
        )
        self.stdout.write(
            f"Auth Token: {auth_token[:5]}...{auth_token[-4:]}"
            if auth_token != "NOT SET"
            else "Auth Token: NOT SET"
        )
        self.stdout.write(f"Phone Number: {phone_number}")
        self.stdout.write(f"Development Mode: {dev_mode}")

        self.stdout.write(self.style.SUCCESS("\n=== Raw Values ===\n"))
        self.stdout.write(f"Full Account SID: {account_sid}")
        self.stdout.write(f"Full Auth Token: {auth_token}")

        # Check if credentials are valid (not placeholder)
        if account_sid == "ACbda2c87d81ac899a614f26b69c25c8af":
            self.stdout.write(
                self.style.SUCCESS("\n✓ Account SID matches your provided value")
            )
        else:
            self.stdout.write(self.style.ERROR("\n✗ Account SID does NOT match"))

        if auth_token == "f8cad167753ac2bacca2c70db8a4f541":
            self.stdout.write(
                self.style.SUCCESS("✓ Auth Token matches your provided value")
            )
        else:
            self.stdout.write(self.style.ERROR("✗ Auth Token does NOT match"))

        if phone_number == "+12605822569":
            self.stdout.write(
                self.style.SUCCESS("✓ Phone Number matches your provided value")
            )
        else:
            self.stdout.write(self.style.ERROR("✗ Phone Number does NOT match"))

        self.stdout.write("\n")
