# management/commands/populate_countries.py
from django.core.management.base import BaseCommand

from content.models import Country


class Command(BaseCommand):
    help = "Populate countries with default data"

    def handle(self, *args, **options):
        countries_data = Country.get_default_countries()

        created_count = 0
        updated_count = 0

        for country_data in countries_data:
            country, created = Country.objects.update_or_create(
                code=country_data["code"], defaults=country_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {country.name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated: {country.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {created_count} created, {updated_count} updated"
            )
        )
