from django.core.management.base import BaseCommand
from django.utils.text import slugify
from content.models import Blog


class Command(BaseCommand):
    help = "Fix blogs with empty or invalid slugs"

    def handle(self, *args, **kwargs):
        # Find blogs with empty slugs
        empty_slug_blogs = Blog.objects.filter(slug="") | Blog.objects.filter(
            slug__isnull=True
        )

        if not empty_slug_blogs.exists():
            self.stdout.write(self.style.SUCCESS("No blogs with empty slugs found."))
            return

        self.stdout.write(
            f"Found {empty_slug_blogs.count()} blog(s) with empty slugs:\n"
        )

        for blog in empty_slug_blogs:
            self.stdout.write(f'ID: {blog.id}, Title: "{blog.title}"')

            if blog.title:
                # Generate slug from title with Unicode support
                new_slug = slugify(blog.title, allow_unicode=True)
                if not new_slug:
                    # If title produces empty slug, use ID
                    new_slug = f"blog-{blog.id}"

                # Ensure uniqueness
                original_slug = new_slug
                counter = 1
                while Blog.objects.filter(slug=new_slug).exclude(id=blog.id).exists():
                    new_slug = f"{original_slug}-{counter}"
                    counter += 1

                blog.slug = new_slug
                blog.save()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Fixed: Generated slug "{new_slug}"')
                )
            else:
                # No title, use ID-based slug
                new_slug = f"blog-{blog.id}"
                blog.slug = new_slug
                blog.save()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Fixed: Generated slug "{new_slug}"')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully fixed {empty_slug_blogs.count()} blog(s)."
            )
        )
