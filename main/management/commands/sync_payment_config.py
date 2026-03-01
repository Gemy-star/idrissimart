"""
Management command to sync payment gateway config from environment variables
into django-constance (which stores values in the database).

Usage:
    python manage.py sync_payment_config          # show current status
    python manage.py sync_payment_config --apply  # write env values to DB
"""
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sync Paymob/PayPal config from environment variables into constance (DB)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write the environment values into the constance database (without this flag the command only shows status)",
        )

    def handle(self, *args, **options):
        from constance import config as constance

        keys = [
            # (constance key, env var, cast)
            ("PAYMOB_ENABLED",        None,                          bool),
            ("PAYMOB_API_KEY",        "PAYMOB_API_KEY",              str),
            ("PAYMOB_SECRET_KEY",     "PAYMOB_SECRET_KEY",           str),
            ("PAYMOB_PUBLIC_KEY",     "PAYMOB_PUBLIC_KEY",           str),
            ("PAYMOB_INTEGRATION_ID", "PAYMOB_INTEGRATION_ID",       str),
            ("PAYMOB_IFRAME_ID",      "PAYMOB_IFRAME_ID",            str),
            ("PAYMOB_HMAC_SECRET",    "PAYMOB_HMAC_SECRET",          str),
            ("PAYPAL_CLIENT_ID",      "PAYPAL_CLIENT_ID",            str),
            ("PAYPAL_CLIENT_SECRET",  "PAYPAL_CLIENT_SECRET",        str),
            ("PAYPAL_MODE",           "PAYPAL_MODE",                 str),
        ]

        apply = options["apply"]

        self.stdout.write("\n--- Payment gateway constance config ---\n")

        for constance_key, env_key, cast in keys:
            db_val = getattr(constance, constance_key, None)
            env_val = os.getenv(env_key, "") if env_key else None

            if constance_key == "PAYMOB_ENABLED":
                status = self.style.SUCCESS("✔ ENABLED") if db_val else self.style.ERROR("✘ DISABLED")
                self.stdout.write(f"  {constance_key:<30} DB={db_val!r:10} {status}")
                continue

            db_display  = repr(db_val[:30] + "…") if isinstance(db_val, str) and len(db_val) > 30 else repr(db_val)
            env_display = repr(env_val[:30] + "…") if isinstance(env_val, str) and len(env_val) > 30 else repr(env_val)
            match = "✔" if db_val == env_val else "≠"
            self.stdout.write(f"  {constance_key:<30} DB={db_display:<35} ENV={env_display:<35} {match}")

        # Check if Paymob would be enabled
        from main.services.paymob_service import PaymobService
        enabled = PaymobService.is_enabled()
        self.stdout.write(
            "\n  PaymobService.is_enabled() → "
            + (self.style.SUCCESS("True") if enabled else self.style.ERROR("False"))
        )
        if not enabled:
            self.stdout.write(self.style.WARNING(
                "  Reasons it may be disabled:\n"
                "    • PAYMOB_ENABLED is False in DB\n"
                "    • PAYMOB_API_KEY is empty in DB\n"
                "    • PAYMOB_INTEGRATION_ID is empty in DB\n"
            ))

        if not apply:
            self.stdout.write(
                self.style.WARNING("\nRun with --apply to write ENV values into the constance DB.\n")
            )
            return

        # Apply: push env values into constance DB
        self.stdout.write("\nApplying environment values to constance DB …")
        constance.PAYMOB_ENABLED = True  # always enable when applying

        for constance_key, env_key, cast in keys:
            if env_key is None:
                continue
            env_val = os.getenv(env_key, "")
            if env_val:
                setattr(constance, constance_key, env_val)
                self.stdout.write(f"  SET {constance_key}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  SKIP {constance_key} (env var {env_key!r} is empty)")
                )

        # Re-check
        enabled = PaymobService.is_enabled()
        self.stdout.write(
            "\n  PaymobService.is_enabled() after apply → "
            + (self.style.SUCCESS("True ✔") if enabled else self.style.ERROR("False ✘"))
        )
        self.stdout.write("")
