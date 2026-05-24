"""
Management command: fix_bad_phones
Finds users with phone numbers that fail E.164 validation and reports (or fixes) them.

Usage:
    python manage.py fix_bad_phones           # dry-run: report only
    python manage.py fix_bad_phones --fix     # apply fixes where possible
"""
import re
import logging

from django.core.management.base import BaseCommand

from main.models import User
from main.services.sms_service import _validate_e164

logger = logging.getLogger(__name__)

_COUNTRY_STRIP = {
    "+966": (r"^(\+?966|0)?(5\d{8})$", "+966"),   # SA: must be 5xxxxxxxx
    "+971": (r"^(\+?971|0)?(5\d{8})$", "+971"),   # UAE
    "+20":  (r"^(\+?20|0)?(1\d{9})$",  "+20"),    # EG: must be 1xxxxxxxxx
    "+965": (r"^(\+?965)?(\d{8})$",     "+965"),   # KW
    "+974": (r"^(\+?974)?(\d{8})$",     "+974"),   # QA
    "+973": (r"^(\+?973)?(\d{8})$",     "+973"),   # BH
    "+968": (r"^(\+?968)?(\d{8})$",     "+968"),   # OM
    "+962": (r"^(\+?962|0)?(7\d{8})$",  "+962"),   # JO
}


def _try_recover(phone):
    """Try to extract the local part and match a known country pattern."""
    digits = re.sub(r"\D", "", phone)
    for prefix, (pattern, code) in _COUNTRY_STRIP.items():
        # Try stripping the country code prefix and matching
        bare = re.sub(r"^\D*" + re.escape(prefix.lstrip("+")), "", digits)
        bare = bare.lstrip("0")
        m = re.match(r"^(" + pattern.split("(")[-1], bare) if "(" in pattern else None
        # Simpler: try matching the last 8-10 digits with the country pattern
        for n in (10, 9, 8):
            tail = digits[-n:] if len(digits) >= n else digits
            candidate = code + tail
            if _validate_e164(candidate):
                return candidate
    return None


class Command(BaseCommand):
    help = "Find (and optionally fix) users with invalid E.164 phone numbers"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Attempt to auto-correct recoverable numbers (writes to DB)",
        )
        parser.add_argument(
            "--field",
            default="all",
            choices=["phone", "mobile", "whatsapp", "all"],
            help="Which phone field to check (default: all)",
        )

    def handle(self, *args, **options):
        do_fix = options["fix"]
        field = options["field"]
        fields = ["phone", "mobile", "whatsapp"] if field == "all" else [field]

        bad = []
        for user in User.objects.exclude(phone="").exclude(phone__isnull=True) | \
                     User.objects.exclude(mobile="").exclude(mobile__isnull=True):
            for f in fields:
                val = getattr(user, f, None)
                if not val:
                    continue
                if not _validate_e164(val):
                    recovered = _try_recover(val)
                    bad.append((user.pk, user.username, f, val, recovered))

        if not bad:
            self.stdout.write(self.style.SUCCESS("✓ No invalid phone numbers found."))
            return

        self.stdout.write(
            self.style.WARNING(f"Found {len(bad)} invalid phone number(s):\n")
        )
        fixed = 0
        for pk, username, field_name, val, recovered in bad:
            status = ""
            if do_fix and recovered:
                User.objects.filter(pk=pk).update(**{field_name: recovered})
                status = f"  → FIXED to {recovered}"
                fixed += 1
            elif recovered:
                status = f"  → can fix to {recovered} (run with --fix)"
            else:
                status = "  → cannot auto-recover (manual fix needed)"
            self.stdout.write(
                f"  user={username!r} (pk={pk}) | field={field_name} | "
                f"current={val!r}{status}"
            )

        if do_fix:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Fixed {fixed} of {len(bad)} records.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\nRun with --fix to auto-correct recoverable numbers."
                )
            )
