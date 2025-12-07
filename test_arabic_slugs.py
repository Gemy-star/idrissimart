"""
Test Arabic slug support across the application
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings")
django.setup()

from django.utils.text import slugify
from main.models import ClassifiedAd, Category
from content.models import Blog


def test_slugify():
    """Test slugify with Arabic text"""
    print("=" * 60)
    print("Testing slugify() with Arabic text")
    print("=" * 60)

    test_cases = [
        "كتاب الفوتوغراميتري والاستشعار عن بعد",
        "سيارة مرسيدس 2020",
        "عقارات للبيع في الرياض",
        "Electronics جديد",  # Mixed
        "iPhone 15 Pro Max",  # English
    ]

    for text in test_cases:
        slug = slugify(text, allow_unicode=True)
        print(f"\nOriginal: {text}")
        print(f"Slug:     {slug}")
        print(f"Valid:    {bool(slug)}")


def test_classified_ads():
    """Test ClassifiedAd slugs"""
    print("\n" + "=" * 60)
    print("Testing ClassifiedAd slugs")
    print("=" * 60)

    ads = ClassifiedAd.objects.all()[:5]
    for ad in ads:
        print(f"\nID: {ad.id}")
        print(f"Title: {ad.title}")
        print(f"Slug:  {ad.slug}")
        try:
            url = ad.get_absolute_url()
            print(f"URL:   {url}")
            print("✅ URL generated successfully")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_categories():
    """Test Category slugs"""
    print("\n" + "=" * 60)
    print("Testing Category slugs")
    print("=" * 60)

    categories = Category.objects.all()[:5]
    for cat in categories:
        print(f"\nID: {cat.id}")
        print(f"Name AR: {cat.name_ar}")
        print(f"Slug:    {cat.slug}")
        print(f"Slug AR: {cat.slug_ar}")
        try:
            from django.urls import reverse

            url = reverse("main:category_detail", kwargs={"slug": cat.slug})
            print(f"URL:     {url}")
            print("✅ URL generated successfully")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_blogs():
    """Test Blog slugs"""
    print("\n" + "=" * 60)
    print("Testing Blog slugs")
    print("=" * 60)

    blogs = Blog.objects.all()[:5]
    for blog in blogs:
        print(f"\nID: {blog.id}")
        print(f"Title: {blog.title}")
        print(f"Slug:  {blog.slug}")
        try:
            url = blog.get_absolute_url()
            print(f"URL:   {url}")
            print("✅ URL generated successfully")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_url_patterns():
    """Test URL pattern matching"""
    print("\n" + "=" * 60)
    print("Testing URL pattern matching")
    print("=" * 60)

    import re

    # Pattern used in urls.py
    pattern = r"^(?P<slug>[\w\-\u0600-\u06FF]+)$"

    test_slugs = [
        "كتاب-الفوتوغراميتري-والاستشعار-عن-بعد",
        "سيارة-مرسيدس-2020",
        "electronics-جديد",
        "iphone-15-pro-max",
        "عقارات",
    ]

    for slug in test_slugs:
        match = re.match(pattern, slug)
        status = "✅" if match else "❌"
        print(f"{status} {slug}")


if __name__ == "__main__":
    print("\n🚀 Starting Arabic Slug Support Tests\n")

    test_slugify()
    test_url_patterns()

    # Test actual database records if available
    try:
        test_classified_ads()
    except Exception as e:
        print(f"\n⚠️  Could not test ClassifiedAds: {e}")

    try:
        test_categories()
    except Exception as e:
        print(f"\n⚠️  Could not test Categories: {e}")

    try:
        test_blogs()
    except Exception as e:
        print(f"\n⚠️  Could not test Blogs: {e}")

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
