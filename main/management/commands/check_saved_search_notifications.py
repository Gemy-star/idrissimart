"""
Management command to check and display SavedSearch email notification settings
"""

from django.core.management.base import BaseCommand
from main.models import SavedSearch


class Command(BaseCommand):
    help = "Check SavedSearch email notification settings"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\n=== Saved Search Email Notifications Status ===\n")
        )

        searches = SavedSearch.objects.select_related("user").all()

        if not searches.exists():
            self.stdout.write(self.style.WARNING("No saved searches found in database"))
            return

        self.stdout.write(f"Total saved searches: {searches.count()}\n")

        for search in searches:
            status_icon = "✓" if search.email_notifications else "✗"
            status_color = (
                self.style.SUCCESS if search.email_notifications else self.style.ERROR
            )

            self.stdout.write(
                f"{status_color(status_icon)} [{search.pk}] {search.name} "
                f"(User: {search.user.username}) - "
                f"Notifications: {search.email_notifications}"
            )

        # Summary
        enabled_count = searches.filter(email_notifications=True).count()
        disabled_count = searches.filter(email_notifications=False).count()

        self.stdout.write(f'\n{self.style.SUCCESS("Enabled:")} {enabled_count}')
        self.stdout.write(f'{self.style.ERROR("Disabled:")} {disabled_count}')
        self.stdout.write(self.style.SUCCESS("\n=== Check Complete ===\n"))
