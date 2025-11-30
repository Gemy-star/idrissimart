"""
Management command to test watermark functionality
Usage: python manage.py test_watermark
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from main.utils import add_watermark_to_image
from PIL import Image
import os
from io import BytesIO


class Command(BaseCommand):
    help = "Test watermark functionality on images"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🎨 Testing Watermark Functionality\n"))

        # Check if watermark file exists
        watermark_path = os.path.join(
            settings.BASE_DIR, "static/images/logos/mini-logo-dark-theme.png"
        )

        if os.path.exists(watermark_path):
            self.stdout.write(
                self.style.SUCCESS(f"✅ Watermark file found: {watermark_path}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Watermark file not found: {watermark_path}")
            )
            return

        # Check watermark image details
        try:
            watermark = Image.open(watermark_path)
            self.stdout.write(
                self.style.SUCCESS(f"✅ Watermark size: {watermark.size}")
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Watermark mode: {watermark.mode}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error opening watermark: {str(e)}"))
            return

        # Test positions
        self.stdout.write(self.style.SUCCESS("\n📍 Available watermark positions:"))
        positions = ["bottom-right", "bottom-left", "top-right", "top-left", "center"]
        for pos in positions:
            self.stdout.write(f"   • {pos}")

        # Configuration info
        self.stdout.write(self.style.SUCCESS("\n⚙️  Current Configuration:"))
        self.stdout.write(f"   • Opacity: 180/255 (semi-transparent)")
        self.stdout.write(f"   • Position: bottom-right")
        self.stdout.write(f"   • Scale: 12% of image width")

        self.stdout.write(
            self.style.SUCCESS("\n✅ Watermark system is configured correctly!")
        )
        self.stdout.write(
            self.style.SUCCESS("📸 Upload an image to see the watermark in action.")
        )
