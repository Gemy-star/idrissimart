# -*- coding: utf-8 -*-
"""
Test creating an ad with Arabic title via Django ORM
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings")
django.setup()

from main.models import ClassifiedAd, Category, User
from django.urls import reverse

print("=" * 60)
print("Creating Arabic Title Ad Test")
print("=" * 60)

try:
    # Get user and category
    user = User.objects.first()
    category = Category.objects.filter(section_type="classified").first()

    if not user or not category:
        print("Error: Need user and category")
        sys.exit(1)

    # Create ad with Arabic title
    arabic_title = "كتاب الفوتوغراميتري والاستشعار عن بعد"

    ad = ClassifiedAd(
        user=user,
        category=category,
        title=arabic_title,
        description="Test ad with Arabic slug",
        price=100.00,
        city="الرياض",
        status=ClassifiedAd.AdStatus.ACTIVE,
    )
    ad.save()

    print(f"\nCreated Ad:")
    print(f"ID:    {ad.id}")
    print(f"Title: {ad.title}")
    print(f"Slug:  {ad.slug}")

    # Test URL
    try:
        url = reverse("main:ad_detail", kwargs={"slug": ad.slug})
        print(f"URL:   {url}")
        print("\n✅ Arabic slug works!")
    except Exception as e:
        print(f"\n❌ URL Error: {e}")

    # Clean up
    ad.delete()
    print("\n(Test ad deleted)")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()

print("=" * 60)
