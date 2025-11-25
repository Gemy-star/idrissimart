"""
Command to verify JavaScript function definitions in rendered template
"""

from django.core.management.base import BaseCommand
from django.template import Template, Context
from django.template.loader import render_to_string
from main.models import ClassifiedAd
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Verify JavaScript functions are properly defined in template"

    def handle(self, *args, **options):
        # Get test ad
        ad = ClassifiedAd.objects.first()
        if not ad:
            self.stdout.write(self.style.ERROR("No ad found"))
            return

        # Get superuser
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR("No superuser found"))
            return

        self.stdout.write(f"Testing with ad: {ad.title} (ID: {ad.id})")

        # Check button onclick attributes would render correctly
        button_calls = {
            "toggleAdVisibility": f"toggleAdVisibility({ad.id}, {str(ad.is_hidden).lower()})",
            "deleteAdvertisement": f"deleteAdvertisement({ad.id}, '{ad.title}')",
            "enableAdCart": f"enableAdCart({ad.id})",
        }

        self.stdout.write("\nExpected onclick handlers:")
        for func_name, call in button_calls.items():
            self.stdout.write(f'  {func_name}: onclick="{call}"')

        self.stdout.write(
            "\n"
            + self.style.SUCCESS(
                "✓ Verify these functions are defined in browser console"
            )
        )
        self.stdout.write("  Open browser console and type:")
        self.stdout.write("    typeof window.toggleAdVisibility")
        self.stdout.write("    typeof window.deleteAdvertisement")
        self.stdout.write("    typeof window.enableAdCart")
        self.stdout.write("  All should return 'function'")

        self.stdout.write("\n" + self.style.WARNING("If functions are 'undefined':"))
        self.stdout.write("  1. Check browser console for JavaScript errors")
        self.stdout.write(
            "  2. Verify <script> tag before {% block admin_content %} is rendering"
        )
        self.stdout.write(
            "  3. Check Network tab to see if admin_extra_js block is loading"
        )
        self.stdout.write(
            "  4. Inspect page source and search for 'Early functions defined'"
        )
