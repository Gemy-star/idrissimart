"""
Django management command to diagnose production issues.
Usage: python manage.py diagnose_issues
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
import traceback


class Command(BaseCommand):
    help = "Diagnose common production issues"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔍 Starting production diagnostics..."))

        # Check database connection
        self.check_database_connection()

        # Check for pending migrations
        self.check_migrations()

        # Check model integrity
        self.check_models()

        # Check specific ClassifiedAd with ID 42
        self.check_classified_ad()

        self.stdout.write(self.style.SUCCESS("✅ Diagnostics completed!"))

    def check_database_connection(self):
        """Check if database connection is working"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    self.stdout.write(self.style.SUCCESS("✅ Database connection: OK"))
                else:
                    self.stdout.write(
                        self.style.ERROR("❌ Database connection: Failed")
                    )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Database connection error: {e}"))

    def check_migrations(self):
        """Check if there are pending migrations"""
        try:
            from django.core.management import call_command
            from io import StringIO

            output = StringIO()
            call_command("showmigrations", "--plan", stdout=output)
            migrations_output = output.getvalue()

            if "[ ]" in migrations_output:
                self.stdout.write(self.style.WARNING("⚠️  Pending migrations detected:"))
                for line in migrations_output.split("\n"):
                    if "[ ]" in line:
                        self.stdout.write(f"   {line}")
            else:
                self.stdout.write(self.style.SUCCESS("✅ All migrations applied"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Migration check error: {e}"))

    def check_models(self):
        """Check model loading and field validation"""
        try:
            from main.models import ClassifiedAd, User, Category

            # Try to access model meta
            self.stdout.write("🔍 Checking model definitions...")

            models_to_check = [ClassifiedAd, User, Category]
            for model in models_to_check:
                try:
                    # Check if model can be accessed
                    model._meta.get_fields()
                    self.stdout.write(self.style.SUCCESS(f"✅ {model.__name__}: OK"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ {model.__name__}: {e}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Model check error: {e}"))

    def check_classified_ad(self):
        """Check specific ClassifiedAd with ID 42"""
        try:
            from main.models import ClassifiedAd

            self.stdout.write("🔍 Checking ClassifiedAd ID 42...")

            try:
                ad = ClassifiedAd.objects.get(id=42)
                self.stdout.write(self.style.SUCCESS(f"✅ Found ad: {ad.title}"))

                # Check related objects
                if ad.user:
                    self.stdout.write(f"   User: {ad.user.username}")
                if ad.category:
                    self.stdout.write(f"   Category: {ad.category.name}")

                # Check for potential issues
                if not ad.title or len(ad.title.strip()) == 0:
                    self.stdout.write(self.style.WARNING("⚠️  Empty title detected"))

                if ad.price is None:
                    self.stdout.write(self.style.WARNING("⚠️  Null price detected"))

            except ClassifiedAd.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING("⚠️  ClassifiedAd with ID 42 not found")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error accessing ClassifiedAd 42: {e}")
                )
                self.stdout.write(f"   Traceback: {traceback.format_exc()}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ ClassifiedAd check error: {e}"))

    def check_field_warnings(self):
        """Check for field definition warnings"""
        try:
            import warnings
            from django.db import models

            # Capture warnings
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                # Import models to trigger any warnings
                from main.models import ClassifiedAd

                if w:
                    self.stdout.write(
                        self.style.WARNING("⚠️  Model field warnings detected:")
                    )
                    for warning in w:
                        self.stdout.write(f"   {warning.message}")
                else:
                    self.stdout.write(
                        self.style.SUCCESS("✅ No field warnings detected")
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Field warning check error: {e}"))
