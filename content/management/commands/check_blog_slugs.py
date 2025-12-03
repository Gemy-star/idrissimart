from django.core.management.base import BaseCommand
from content.models import Blog


class Command(BaseCommand):
    help = "Check blog slugs for issues"

    def handle(self, *args, **kwargs):
        blogs = Blog.objects.all()
        self.stdout.write(f"Total blogs: {blogs.count()}\n")

        for blog in blogs:
            self.stdout.write(
                f'ID: {blog.id}, Title: {blog.title[:50]}, Slug: "{blog.slug}"'
            )

            # Check for empty or None slug
            if not blog.slug:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR: Empty slug for blog ID {blog.id}")
                )

            # Check for invalid characters
            if blog.slug and (
                " " in blog.slug or "\n" in blog.slug or "\t" in blog.slug
            ):
                self.stdout.write(
                    self.style.ERROR(
                        f"  ERROR: Invalid characters in slug for blog ID {blog.id}"
                    )
                )

        # Try to get absolute URL for each
        self.stdout.write("\nTesting get_absolute_url() for each blog:")
        for blog in blogs:
            try:
                url = blog.get_absolute_url()
                self.stdout.write(
                    self.style.SUCCESS(f"  OK: Blog ID {blog.id} -> {url}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR: Blog ID {blog.id} - {str(e)}")
                )
