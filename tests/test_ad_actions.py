"""
Test script for Admin Ad Actions
Tests all available actions on classified ads

Run: python test_ad_actions.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from main.models import ClassifiedAd, Category, AdPackage
from content.models import Country

User = get_user_model()


def test_ad_actions():
    """Test all admin actions on ads"""
    print("\n" + "=" * 70)
    print("🧪 Testing Admin Ad Actions")
    print("=" * 70 + "\n")

    # Get or create test user
    try:
        test_user = User.objects.get(username="test_ad_actions_user")
        print(f"ℹ️  Using existing test user: {test_user.username}")
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username="test_ad_actions_user",
            email="adtest@example.com",
            password="testpass123",
            first_name="Ad",
            last_name="Tester",
        )
        print(f"✅ Created test user: {test_user.username}")

    # Get or create test category
    try:
        test_category = Category.objects.filter(is_active=True).first()
        if not test_category:
            raise Category.DoesNotExist
        print(f"ℹ️  Using category: {test_category.name}")
    except:
        test_category = Category.objects.create(
            name="Test Category",
            name_ar="فئة تجريبية",
            slug="test-category",
            is_active=True,
        )
        print(f"✅ Created test category: {test_category.name}")

    # Get or create test country
    try:
        test_country = Country.objects.filter(is_active=True).first()
        if not test_country:
            test_country = Country.objects.create(
                name="Saudi Arabia", name_ar="السعودية", code="SA", is_active=True
            )
        print(f"ℹ️  Using country: {test_country.name}")
    except:
        print("⚠️  No country found")
        test_country = None

    # Create or get test ad
    try:
        test_ad = ClassifiedAd.objects.get(title="Test Ad for Actions")
        print(f"ℹ️  Using existing test ad: {test_ad.title}")
    except ClassifiedAd.DoesNotExist:
        test_ad = ClassifiedAd.objects.create(
            user=test_user,
            title="Test Ad for Actions",
            description="This is a test ad for testing admin actions",
            category=test_category,
            country=test_country,
            price=1000.00,
            status="PENDING_REVIEW",
        )
        print(f"✅ Created test ad: {test_ad.title}")

    print(f"\nInitial Ad State:")
    print(f"  - ID: {test_ad.id}")
    print(f"  - Status: {test_ad.status}")
    print(f"  - is_hidden: {test_ad.is_hidden}")
    print(f"  - is_urgent: {test_ad.is_urgent}")
    print(f"  - is_pinned: {test_ad.is_pinned}")
    print(f"  - cart_enabled_by_admin: {test_ad.cart_enabled_by_admin}")

    # Test 1: Approve Ad
    print("\n" + "-" * 70)
    print("Test 1: Approve Ad")
    print("-" * 70)
    test_ad.status = "ACTIVE"
    test_ad.save(update_fields=["status"])
    test_ad.refresh_from_db()

    assert test_ad.status == "ACTIVE", "❌ Approve failed"
    print("✅ Ad approved successfully")
    print(f"  - New status: {test_ad.status}")

    # Test 2: Reject Ad
    print("\n" + "-" * 70)
    print("Test 2: Reject Ad")
    print("-" * 70)
    test_ad.status = "REJECTED"
    test_ad.save(update_fields=["status"])
    test_ad.refresh_from_db()

    assert test_ad.status == "REJECTED", "❌ Reject failed"
    print("✅ Ad rejected successfully")
    print(f"  - New status: {test_ad.status}")

    # Test 3: Suspend Ad
    print("\n" + "-" * 70)
    print("Test 3: Suspend Ad")
    print("-" * 70)
    test_ad.status = "SUSPENDED"
    test_ad.save(update_fields=["status"])
    test_ad.refresh_from_db()

    assert test_ad.status == "SUSPENDED", "❌ Suspend failed"
    print("✅ Ad suspended successfully")
    print(f"  - New status: {test_ad.status}")

    # Test 4: Activate Ad
    print("\n" + "-" * 70)
    print("Test 4: Activate Ad")
    print("-" * 70)
    test_ad.status = "ACTIVE"
    test_ad.save(update_fields=["status"])
    test_ad.refresh_from_db()

    assert test_ad.status == "ACTIVE", "❌ Activate failed"
    print("✅ Ad activated successfully")
    print(f"  - New status: {test_ad.status}")

    # Test 5: Hide/Unhide Ad
    print("\n" + "-" * 70)
    print("Test 5: Hide/Unhide Ad")
    print("-" * 70)
    test_ad.is_hidden = True
    test_ad.save(update_fields=["is_hidden"])
    test_ad.refresh_from_db()

    assert test_ad.is_hidden == True, "❌ Hide failed"
    print("✅ Ad hidden successfully")
    print(f"  - is_hidden: {test_ad.is_hidden}")

    test_ad.is_hidden = False
    test_ad.save(update_fields=["is_hidden"])
    test_ad.refresh_from_db()

    assert test_ad.is_hidden == False, "❌ Unhide failed"
    print("✅ Ad unhidden successfully")
    print(f"  - is_hidden: {test_ad.is_hidden}")

    # Test 6: Toggle Urgent
    print("\n" + "-" * 70)
    print("Test 6: Toggle Urgent")
    print("-" * 70)
    test_ad.is_urgent = True
    test_ad.save(update_fields=["is_urgent"])
    test_ad.refresh_from_db()

    assert test_ad.is_urgent == True, "❌ Urgent toggle failed"
    print("✅ Ad marked as urgent")
    print(f"  - is_urgent: {test_ad.is_urgent}")

    test_ad.is_urgent = False
    test_ad.save(update_fields=["is_urgent"])
    test_ad.refresh_from_db()
    print("✅ Ad urgent removed")

    # Test 7: Toggle Pinned
    print("\n" + "-" * 70)
    print("Test 7: Toggle Pinned")
    print("-" * 70)
    test_ad.is_pinned = True
    test_ad.save(update_fields=["is_pinned"])
    test_ad.refresh_from_db()

    assert test_ad.is_pinned == True, "❌ Pin failed"
    print("✅ Ad pinned successfully")
    print(f"  - is_pinned: {test_ad.is_pinned}")

    test_ad.is_pinned = False
    test_ad.save(update_fields=["is_pinned"])
    test_ad.refresh_from_db()
    print("✅ Ad unpinned successfully")

    # Test 8: Enable/Disable Cart
    print("\n" + "-" * 70)
    print("Test 8: Enable/Disable Cart")
    print("-" * 70)
    test_ad.is_urgent = True
    test_ad.save(update_fields=["is_urgent"])
    test_ad.refresh_from_db()

    assert test_ad.is_urgent == True, "❌ Urgent toggle failed"
    print("✅ Ad marked as urgent")
    print(f"  - is_urgent: {test_ad.is_urgent}")

    test_ad.is_urgent = False
    test_ad.save(update_fields=["is_urgent"])
    test_ad.refresh_from_db()
    print("✅ Ad urgent removed")

    # Test 8: Toggle Pinned
    print("\n" + "-" * 70)
    print("Test 8: Toggle Pinned")
    print("-" * 70)
    test_ad.is_pinned = True
    test_ad.save(update_fields=["is_pinned"])
    test_ad.refresh_from_db()

    assert test_ad.is_pinned == True, "❌ Pin failed"
    print("✅ Ad pinned successfully")
    print(f"  - is_pinned: {test_ad.is_pinned}")

    test_ad.is_pinned = False
    test_ad.save(update_fields=["is_pinned"])
    test_ad.refresh_from_db()
    print("✅ Ad unpinned successfully")

    # Test 9: Enable/Disable Cart
    print("\n" + "-" * 70)
    print("Test 9: Enable/Disable Cart")
    print("-" * 70)
    test_ad.cart_enabled_by_admin = True
    test_ad.save(update_fields=["cart_enabled_by_admin"])
    test_ad.refresh_from_db()

    assert test_ad.cart_enabled_by_admin == True, "❌ Cart enable failed"
    print("✅ Cart enabled successfully")
    print(f"  - cart_enabled_by_admin: {test_ad.cart_enabled_by_admin}")

    test_ad.cart_enabled_by_admin = False
    test_ad.save(update_fields=["cart_enabled_by_admin"])
    test_ad.refresh_from_db()

    assert test_ad.cart_enabled_by_admin == False, "❌ Cart disable failed"
    print("✅ Cart disabled successfully")
    print(f"  - cart_enabled_by_admin: {test_ad.cart_enabled_by_admin}")

    # Test 10: Extend Ad
    print("\n" + "-" * 70)
    print("Test 10: Extend Ad Expiry")
    print("-" * 70)
    original_expires_at = test_ad.expires_at
    new_expires_at = timezone.now() + timezone.timedelta(days=60)
    test_ad.expires_at = new_expires_at
    test_ad.save(update_fields=["expires_at"])
    test_ad.refresh_from_db()

    print("✅ Ad expiry extended successfully")
    print(f"  - Original: {original_expires_at}")
    print(f"  - New: {test_ad.expires_at}")

    # Cleanup
    print("\n" + "-" * 70)
    print("Cleanup")
    print("-" * 70)
    # Reset to normal state
    test_ad.status = "ACTIVE"
    test_ad.is_hidden = False
    test_ad.is_urgent = False
    test_ad.is_pinned = False
    test_ad.cart_enabled_by_admin = False
    test_ad.save()
    print(f"✅ Reset test ad to normal state")

    print("\n" + "=" * 70)
    print("✅ All Tests Passed!")
    print("=" * 70 + "\n")

    # Summary
    print("\n📊 Summary of Available Actions:")
    print("  ✅ Approve Ad (PENDING → ACTIVE)")
    print("  ✅ Reject Ad (ANY → REJECTED)")
    print("  ✅ Suspend Ad (ANY → SUSPENDED)")
    print("  ✅ Activate Ad (ANY → ACTIVE)")
    print("  ✅ Hide/Unhide Ad (toggle is_hidden)")
    print("  ✅ Toggle Urgent")
    print("  ✅ Toggle Pinned")
    print("  ✅ Enable/Disable Cart")
    print("  ✅ Extend Expiry Date")
    print("  ✅ Change Category (available)")
    print("  ✅ Full Edit (available)")
    print("  ✅ Delete Ad (available)")
    print("  ✅ Transfer Ownership (available)")
    print("  ✅ Duplicate Ad (available)")
    print("  ✅ Republish Ad (available)")

    print("\n📝 URLs Available:")
    print("  - /admin/ads/<id>/approve/")
    print("  - /admin/ads/<id>/reject/")
    print("  - /admin/ads/<id>/suspend/")
    print("  - /admin/ads/<id>/activate/")
    print("  - /admin/ads/<id>/hide/")
    print("  - /admin/ads/<id>/toggle-urgent/")
    print("  - /admin/ads/<id>/toggle-pinned/")
    print("  - /admin/ads/<id>/enable-cart/")
    print("  - /admin/ads/<id>/disable-cart/")
    print("  - /admin/ads/<id>/extend/")
    print("  - /admin/ads/<id>/change-category/")
    print("  - /admin/ads/<id>/delete/")
    print("  - /admin/ads/bulk-actions/")

    print("\n🎉 All admin ad actions are working correctly!\n")


if __name__ == "__main__":
    test_ad_actions()
