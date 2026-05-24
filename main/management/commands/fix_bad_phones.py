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

# Known country dial codes → expected total digit count after +
_COUNTRY_CODE_DIGIT_LENGTHS = {
    "+966": 12,  # Saudi Arabia:  966 + 9 digits
    "+971": 12,  # UAE:           971 + 9 digits
    "+965": 11,  # Kuwait:        965 + 8 digits
    "+974": 11,  # Qatar:         974 + 8 digits
    "+973": 11,  # Bahrain:       973 + 8 digits
    "+968": 11,  # Oman:          968 + 8 digits
    "+962": 12,  # Jordan:        962 + 9 digits
    "+20":  12,  # Egypt:          20 + 10 digits
}

# Longest prefix first so +966 is matched before a shorter hypothetical prefix
_SORTED_PREFIXES = sorted(_COUNTRY_CODE_DIGIT_LENGTHS.keys(), key=len, reverse=True)


def _normalize_with_prefix(plus_number):
    """
    Given a string that already starts with '+', try to fix it to valid E.164.
    Handles the common case where the subscriber part has a stray leading 0
    (e.g. +20 01XXXXXXXXX → +20 1XXXXXXXXX).
    Returns the fixed string or None.
    """
    for prefix in _SORTED_PREFIXES:
        if plus_number.startswith(prefix):
            subscriber = plus_number[len(prefix):]
            # Try as-is first
            if _validate_e164(plus_number):
                return plus_number
            # Subscriber has a leading 0 — strip it
            if subscriber.startswith("0"):
                candidate = prefix + subscriber[1:]
                if _validate_e164(candidate):
                    return candidate
            return None  # Known country but unfixable — don't guess another country
    # Unknown country code
    if _validate_e164(plus_number):
        return plus_number
    return None


def _try_recover(phone, user=None):
    """
    Try to recover a phone number to valid E.164.

    Strategy (in order):
      1. Strip non-digit/+ characters and whitespace
      2. Convert 00CCXXXXXXX international prefix to +CCXXXXXXX
      3. If number already has +, fix via _normalize_with_prefix
      4. Bare digits: try user's country code (from user.country.phone_code)
      5. Bare digits: try all known country codes by expected digit count
    """
    # Step 1: strip whitespace and junk (keep digits and +)
    cleaned = re.sub(r"[^\d+]", "", phone.strip())

    # Normalize stray + signs: a + anywhere except position 0 is junk (e.g. "01234 +")
    if cleaned.startswith("+"):
        cleaned = "+" + cleaned[1:].replace("+", "")
    else:
        cleaned = cleaned.replace("+", "")

    # Step 2: 00-prefix → +
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    # Step 3: already has country code
    if cleaned.startswith("+"):
        return _normalize_with_prefix(cleaned)

    # Bare digits from here on
    digits = cleaned.lstrip("0")  # strip local trunk prefix (leading 0s)

    # Step 4: user's own country
    if user is not None:
        try:
            country = user.country
            if country and country.phone_code:
                code = country.phone_code.strip()
                if not code.startswith("+"):
                    code = "+" + code
                candidate = code + digits
                if _validate_e164(candidate):
                    return candidate
        except Exception:
            pass

    # Step 5: try all known country codes — match by expected length
    for prefix, expected_len in _COUNTRY_CODE_DIGIT_LENGTHS.items():
        subscriber_len = expected_len - len(prefix) + 1  # +1 for the leading +
        if len(digits) == subscriber_len:
            candidate = prefix + digits
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
        qs = (
            User.objects.exclude(phone="").exclude(phone__isnull=True)
            | User.objects.exclude(mobile="").exclude(mobile__isnull=True)
        ).select_related("country").distinct()

        for user in qs:
            for f in fields:
                val = getattr(user, f, None)
                if not val:
                    continue
                if not _validate_e164(val):
                    recovered = _try_recover(val, user=user)
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
