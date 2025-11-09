"""
Management command to check production deployment health
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from constance import config
import sys


class Command(BaseCommand):
    help = "Check production deployment health and configuration"

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("=" * 60))
        self.stdout.write(self.style.HTTP_INFO("PRODUCTION HEALTH CHECK"))
        self.stdout.write(self.style.HTTP_INFO("=" * 60))

        errors = []
        warnings = []

        # 1. Check DEBUG mode
        self.stdout.write("\n1. Checking DEBUG mode...")
        if settings.DEBUG:
            errors.append("DEBUG is True - MUST be False in production!")
            self.stdout.write(self.style.ERROR("   ✗ DEBUG = True (CRITICAL)"))
        else:
            self.stdout.write(self.style.SUCCESS("   ✓ DEBUG = False"))

        # 2. Check ALLOWED_HOSTS
        self.stdout.write("\n2. Checking ALLOWED_HOSTS...")
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ["*"]:
            errors.append("ALLOWED_HOSTS not properly configured")
            self.stdout.write(self.style.ERROR("   ✗ ALLOWED_HOSTS not configured"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"   ✓ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
            )

        # 3. Check Database Connection
        self.stdout.write("\n3. Checking database connection...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("   ✓ Database connection successful"))
        except Exception as e:
            errors.append(f"Database connection failed: {e}")
            self.stdout.write(self.style.ERROR(f"   ✗ Database error: {e}"))

        # 4. Check Static Files
        self.stdout.write("\n4. Checking static files configuration...")
        if not settings.STATIC_ROOT:
            errors.append("STATIC_ROOT not configured")
            self.stdout.write(self.style.ERROR("   ✗ STATIC_ROOT not set"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"   ✓ STATIC_ROOT = {settings.STATIC_ROOT}")
            )

        # 5. Check Media Files
        self.stdout.write("\n5. Checking media files configuration...")
        if not settings.MEDIA_ROOT:
            errors.append("MEDIA_ROOT not configured")
            self.stdout.write(self.style.ERROR("   ✗ MEDIA_ROOT not set"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"   ✓ MEDIA_ROOT = {settings.MEDIA_ROOT}")
            )

        # 6. Check Secret Key
        self.stdout.write("\n6. Checking SECRET_KEY...")
        if "insecure" in settings.SECRET_KEY:
            errors.append("Using default insecure SECRET_KEY")
            self.stdout.write(self.style.ERROR("   ✗ Using insecure SECRET_KEY"))
        else:
            self.stdout.write(self.style.SUCCESS("   ✓ SECRET_KEY is set"))

        # 7. Check Security Settings
        self.stdout.write("\n7. Checking security settings...")
        security_checks = []

        if hasattr(settings, "SECURE_SSL_REDIRECT") and settings.SECURE_SSL_REDIRECT:
            self.stdout.write(self.style.SUCCESS("   ✓ SECURE_SSL_REDIRECT enabled"))
        else:
            warnings.append("SECURE_SSL_REDIRECT not enabled")
            self.stdout.write(self.style.WARNING("   ! SECURE_SSL_REDIRECT disabled"))

        if (
            hasattr(settings, "SESSION_COOKIE_SECURE")
            and settings.SESSION_COOKIE_SECURE
        ):
            self.stdout.write(self.style.SUCCESS("   ✓ SESSION_COOKIE_SECURE enabled"))
        else:
            warnings.append("SESSION_COOKIE_SECURE not enabled")
            self.stdout.write(self.style.WARNING("   ! SESSION_COOKIE_SECURE disabled"))

        if hasattr(settings, "CSRF_COOKIE_SECURE") and settings.CSRF_COOKIE_SECURE:
            self.stdout.write(self.style.SUCCESS("   ✓ CSRF_COOKIE_SECURE enabled"))
        else:
            warnings.append("CSRF_COOKIE_SECURE not enabled")
            self.stdout.write(self.style.WARNING("   ! CSRF_COOKIE_SECURE disabled"))

        # 8. Check Constance Config
        self.stdout.write("\n8. Checking Constance configuration...")
        try:
            site_name = config.SITE_NAME
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✓ Constance config accessible (SITE_NAME: {site_name})"
                )
            )
        except Exception as e:
            errors.append(f"Constance config error: {e}")
            self.stdout.write(self.style.ERROR(f"   ✗ Constance error: {e}"))

        # 9. Check Middleware
        self.stdout.write("\n9. Checking middleware...")
        required_middleware = [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "main.middleware.BlockMaliciousRequestsMiddleware",
        ]
        for mw in required_middleware:
            if mw in settings.MIDDLEWARE:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {mw.split(".")[-1]}'))
            else:
                warnings.append(f"Missing middleware: {mw}")
                self.stdout.write(
                    self.style.WARNING(f'   ! {mw.split(".")[-1]} not found')
                )

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.HTTP_INFO("SUMMARY"))
        self.stdout.write("=" * 60)

        if errors:
            self.stdout.write(
                self.style.ERROR(f"\n❌ {len(errors)} CRITICAL ERROR(S):")
            )
            for error in errors:
                self.stdout.write(self.style.ERROR(f"   • {error}"))

        if warnings:
            self.stdout.write(self.style.WARNING(f"\n⚠️  {len(warnings)} WARNING(S):"))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f"   • {warning}"))

        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS("\n✅ All checks passed!"))

        self.stdout.write("\n" + "=" * 60)

        # Exit with error code if critical errors found
        if errors:
            sys.exit(1)
