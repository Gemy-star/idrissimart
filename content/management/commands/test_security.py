from django.core.management.base import BaseCommand
from content.models import Blog
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Test sanitization with dangerous content"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        author = User.objects.first()

        if not author:
            self.stdout.write(
                self.style.ERROR("No users found. Cannot create test blog.")
            )
            return

        # Create test blog with dangerous content
        dangerous_content = """
        <h2>Test Blog</h2>
        <p>This is normal content.</p>
        <script>
        let counter = 0;
        function addPoint(x="", y="") {
            counter++;
            alert("This should be removed!");
        }
        </script>
        <button onclick="alert('danger')">Click Me</button>
        <iframe src="https://evil.com"></iframe>
        <p onload="alert('loaded')">More content</p>
        """

        blog = Blog(
            title="Security Test Blog",
            author=author,
            content=dangerous_content,
            is_published=False,
        )
        blog.save()

        self.stdout.write(f"\nCreated test blog ID: {blog.id}")
        self.stdout.write("\nOriginal content length: " + str(len(blog.content)))
        self.stdout.write("\nOriginal content contains:")
        self.stdout.write(f'  <script>: {"✗" if "<script>" in blog.content else "✓"}')
        self.stdout.write(f'  onclick: {"✗" if "onclick" in blog.content else "✓"}')
        self.stdout.write(f'  <iframe>: {"✗" if "<iframe>" in blog.content else "✓"}')
        self.stdout.write(f'  onload: {"✗" if "onload" in blog.content else "✓"}')

        safe_content = blog.get_safe_content()

        self.stdout.write("\n\nSanitized content length: " + str(len(safe_content)))
        self.stdout.write("\nSanitized content contains:")
        self.stdout.write(
            f'  <script>: {self.style.ERROR("✗ FAIL") if "<script>" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )
        self.stdout.write(
            f'  onclick: {self.style.ERROR("✗ FAIL") if "onclick" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )
        self.stdout.write(
            f'  <iframe>: {self.style.ERROR("✗ FAIL") if "<iframe>" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )
        self.stdout.write(
            f'  onload: {self.style.ERROR("✗ FAIL") if "onload" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )

        self.stdout.write("\n\nSanitized content:")
        self.stdout.write(safe_content)

        # Clean up
        blog.delete()
        self.stdout.write(self.style.SUCCESS("\n\nTest blog deleted."))
