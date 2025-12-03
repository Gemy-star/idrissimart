#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings")
django.setup()

from content.models import Blog

blogs = Blog.objects.all()
print(f"Total blogs: {blogs.count()}")
print("\nFirst 10 blogs:")
for b in blogs[:10]:
    print(f'ID: {b.id}, Title: {b.title[:50]}, Slug: "{b.slug}"')

print("\nChecking for problematic slugs...")
for b in blogs:
    if not b.slug or b.slug.strip() == "":
        print(f"EMPTY SLUG: ID {b.id}, Title: {b.title}")
    elif " " in b.slug:
        print(f'SPACE IN SLUG: ID {b.id}, Slug: "{b.slug}"')
