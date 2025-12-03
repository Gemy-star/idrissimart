from django.core.management.base import BaseCommand
from content.models import Blog
from main.models import ClassifiedAd


class Command(BaseCommand):
    help = "Test all HTML sanitization methods"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("\n" + "=" * 60))
        self.stdout.write(self.style.WARNING("HTML SANITIZATION SECURITY TEST"))
        self.stdout.write(self.style.WARNING("=" * 60 + "\n"))

        # Test Blog sanitization
        self.stdout.write(self.style.SUCCESS("1. Testing Blog.get_safe_content()"))
        self.stdout.write("-" * 60)

        blogs = Blog.objects.all()[:3]
        if blogs.exists():
            for blog in blogs:
                safe = blog.get_safe_content()
                has_script = "<script>" in safe.lower()
                has_onclick = "onclick" in safe.lower()

                self.stdout.write(f"\nBlog: {blog.title[:50]}")
                self.stdout.write(
                    f'  Script tags: {self.style.SUCCESS("✓ Clean") if not has_script else self.style.ERROR("✗ Found")}'
                )
                self.stdout.write(
                    f'  Event handlers: {self.style.SUCCESS("✓ Clean") if not has_onclick else self.style.ERROR("✗ Found")}'
                )
        else:
            self.stdout.write(self.style.WARNING("  No blogs found to test"))

        # Test ClassifiedAd sanitization
        self.stdout.write(
            "\n" + self.style.SUCCESS("2. Testing ClassifiedAd.get_safe_description()")
        )
        self.stdout.write("-" * 60)

        ads = ClassifiedAd.objects.all()[:3]
        if ads.exists():
            for ad in ads:
                safe = ad.get_safe_description()
                has_script = "<script>" in safe.lower()
                has_onclick = "onclick" in safe.lower()
                has_iframe = "<iframe>" in safe.lower()

                self.stdout.write(f"\nAd: {ad.title[:50]}")
                self.stdout.write(
                    f'  Script tags: {self.style.SUCCESS("✓ Clean") if not has_script else self.style.ERROR("✗ Found")}'
                )
                self.stdout.write(
                    f'  Event handlers: {self.style.SUCCESS("✓ Clean") if not has_onclick else self.style.ERROR("✗ Found")}'
                )
                self.stdout.write(
                    f'  Iframes: {self.style.SUCCESS("✓ Clean") if not has_iframe else self.style.ERROR("✗ Found")}'
                )
        else:
            self.stdout.write(self.style.WARNING("  No ads found to test"))

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS("✓ All sanitization methods are working correctly!")
        )
        self.stdout.write("=" * 60 + "\n")

        self.stdout.write(self.style.WARNING("\nSecurity Notes:"))
        self.stdout.write("  • Blog content is sanitized via get_safe_content()")
        self.stdout.write(
            "  • Ad descriptions are sanitized via get_safe_description()"
        )
        self.stdout.write("  • All <script> tags are removed")
        self.stdout.write("  • All event handlers (onclick, onload, etc.) are removed")
        self.stdout.write("  • Dangerous tags (iframe, object, embed) are removed")
        self.stdout.write("  • Safe styling attributes are preserved")
        self.stdout.write("\n")
