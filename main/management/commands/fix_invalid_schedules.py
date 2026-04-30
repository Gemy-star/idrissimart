"""
Management command to find and optionally remove Schedule entries whose
`args` or `kwargs` fields cannot be parsed by ast.literal_eval.

Usage:
    python manage.py fix_invalid_schedules          # list bad schedules
    python manage.py fix_invalid_schedules --delete  # delete bad schedules
"""

import ast

from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Find (and optionally delete) Django-Q schedules with un-parseable args/kwargs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete bad schedules instead of just listing them",
        )

    def handle(self, *args, **options):
        delete = options["delete"]
        bad = []

        for s in Schedule.objects.all():
            reasons = []

            if s.args:
                try:
                    ast.literal_eval(s.args)
                except (SyntaxError, ValueError) as exc:
                    reasons.append(f"args={s.args!r} → {exc}")

            if s.kwargs:
                try:
                    ast.literal_eval(s.kwargs)
                except (SyntaxError, ValueError):
                    # try the kwarg-syntax fallback that Django-Q itself uses
                    try:
                        parsed = ast.parse(f"f({s.kwargs})").body[0].value.keywords
                        for kw in parsed:
                            ast.literal_eval(kw.value)
                    except (SyntaxError, ValueError) as exc:
                        reasons.append(f"kwargs={s.kwargs!r} → {exc}")

            if reasons:
                bad.append((s, reasons))

        if not bad:
            self.stdout.write(self.style.SUCCESS("✅ All schedules have valid args/kwargs."))
            return

        self.stdout.write(
            self.style.WARNING(f"⚠️  Found {len(bad)} schedule(s) with invalid args/kwargs:\n")
        )
        for s, reasons in bad:
            self.stdout.write(
                self.style.ERROR(f"  • [{s.id}] {s.name!r}  func={s.func}")
            )
            for r in reasons:
                self.stdout.write(f"      {r}")

        if delete:
            ids = [s.id for s, _ in bad]
            deleted, _ = Schedule.objects.filter(id__in=ids).delete()
            self.stdout.write(
                self.style.SUCCESS(f"\n🗑️  Deleted {deleted} bad schedule(s).")
            )
            self.stdout.write(
                self.style.WARNING(
                    "Re-run `python manage.py setup_scheduled_tasks` to recreate them."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nRun with --delete to remove them, or fix them manually in the admin."
                )
            )
