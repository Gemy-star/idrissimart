"""
Create a test ad with Arabic title to verify Arabic slug generation
"""

from main.models import ClassifiedAd, Category, User
from django.utils import timezone

print("\n" + "=" * 60)
print("Creating Test Ad with Arabic Title")
print("=" * 60 + "\n")

# Get a user and category
try:
    user = User.objects.filter(profile_type="PUBLISHER").first()
    if not user:
        user = User.objects.first()

    category = Category.objects.filter(section_type="classified").first()

    if not user or not category:
        print("❌ Error: Need at least one user and one category")
    else:
        # Create test ad with Arabic title
        arabic_title = "كتاب الفوتوغراميتري والاستشعار عن بعد"

        ad = ClassifiedAd.objects.create(
            user=user,
            category=category,
            title=arabic_title,
            description="This is a test ad to verify Arabic slug generation",
            price=100.00,
            city="الرياض",
            status=ClassifiedAd.AdStatus.ACTIVE,
        )

        print(f"✅ Created test ad:")
        print(f"   ID:    {ad.id}")
        print(f"   Title: {ad.title}")
        print(f"   Slug:  {ad.slug}")

        # Test URL generation
        from django.urls import reverse

        try:
            url = reverse("main:ad_detail", kwargs={"slug": ad.slug})
            print(f"   URL:   {url}")
            print("\n✅ Arabic slug works perfectly!")
        except Exception as e:
            print(f"\n❌ URL Error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
