from django.core.management.base import BaseCommand
from content.models import Blog


class Command(BaseCommand):
    help = "Test blog creation with various titles"

    def handle(self, *args, **kwargs):
        test_cases = [
            "Test English Title",
            "عنوان عربي فقط",
            "مختلط Mixed Title",
            "!!!###",  # Only special chars
            "",  # Empty (though this shouldn't happen)
        ]

        self.stdout.write("Testing blog creation with various titles:\n")

        # Get a test author (first user)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        author = User.objects.first()

        if not author:
            self.stdout.write(
                self.style.ERROR(
                    "No users found in database. Cannot create test blogs."
                )
            )
            return

        for title in test_cases:
            if not title:
                continue

            try:
                blog = Blog(
                    title=title,
                    author=author,
                    content="Test content",
                    is_published=False,  # Don't publish test blogs
                )
                blog.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: Title="{title}" -> Slug="{blog.slug}" (ID: {blog.id})'
                    )
                )

                # Verify get_absolute_url works
                url = blog.get_absolute_url()
                self.stdout.write(f"  URL: {url}")

                # Clean up test blog
                blog.delete()

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed: Title="{title}" - {str(e)}')
                )
