from django.core.management.base import BaseCommand
from content.models import Blog


class Command(BaseCommand):
    help = "Test blog content sanitization"

    def handle(self, *args, **kwargs):
        # Get a blog with script content
        blogs = Blog.objects.all()

        if not blogs.exists():
            self.stdout.write(self.style.WARNING("No blogs found in database."))
            return

        self.stdout.write(f"Testing sanitization on {blogs.count()} blog(s):\n")

        for blog in blogs[:5]:
            self.stdout.write(f"\nBlog ID: {blog.id}, Title: {blog.title[:50]}")

            # Check if content has scripts
            if "<script" in blog.content.lower():
                self.stdout.write(self.style.WARNING("  ⚠ Contains <script> tag"))
            if "onclick" in blog.content.lower() or "onload" in blog.content.lower():
                self.stdout.write(
                    self.style.WARNING("  ⚠ Contains on* event attributes")
                )

            # Get safe content
            safe_content = blog.get_safe_content()

            # Check if sanitized
            if "<script" in safe_content.lower():
                self.stdout.write(
                    self.style.ERROR("  ✗ FAILED: Still contains <script>")
                )
            else:
                self.stdout.write(self.style.SUCCESS("  ✓ <script> tags removed"))

            if "onclick" in safe_content.lower() or "onload" in safe_content.lower():
                self.stdout.write(
                    self.style.ERROR("  ✗ FAILED: Still contains on* attributes")
                )
            else:
                self.stdout.write(self.style.SUCCESS("  ✓ on* attributes removed"))

            # Show content length comparison
            orig_len = len(blog.content)
            safe_len = len(safe_content)
            if orig_len != safe_len:
                self.stdout.write(
                    f"  📊 Content reduced from {orig_len} to {safe_len} chars ({orig_len - safe_len} removed)"
                )
