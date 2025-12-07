"""
Quick test to verify ClassifiedAd URLs work with Arabic slugs
Run with: python manage.py shell < test_ad_urls.py
"""

from main.models import ClassifiedAd
from django.urls import reverse

print("\n" + "=" * 60)
print("Testing ClassifiedAd URLs with Arabic Slugs")
print("=" * 60 + "\n")

ads = ClassifiedAd.objects.all()[:5]

for ad in ads:
    if ad.slug:
        print(f"Title: {ad.title}")
        print(f"Slug:  {ad.slug}")
        try:
            url = reverse("main:ad_detail", kwargs={"slug": ad.slug})
            print(f"URL:   {url}")
            print("✅ Success\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    else:
        print(f"⚠️  Ad #{ad.id} has no slug\n")

print("=" * 60)
print("Test completed!")
print("=" * 60)
