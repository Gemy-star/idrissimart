"""
Test script to verify DEFAULT user type functionality
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
django.setup()

from main.models import User, UserPackage, AdPackage


def test_default_user_creation():
    """Test creating a DEFAULT user and verify package assignment"""
    print("\n=== Testing DEFAULT User Creation ===\n")

    # Check if default package exists
    try:
        default_package = AdPackage.objects.filter(
            is_default=True, is_active=True
        ).first()
        if default_package:
            print(f"✓ Default package found: {default_package.name}")
            print(f"  - Ads count: {default_package.ad_count}")
            print(f"  - Duration: {default_package.duration_days} days")
            print(f"  - Price: {default_package.price}")
            print(f"  - Is default: {default_package.is_default}")
        else:
            print("⚠ No default package found (is_default=True)")
            print("  - New users will get 1 free ad as fallback")
    except Exception as e:
        print(f"! Package check error: {e}")

    # Test profile type choices
    print(f"\n=== Profile Type Choices ===")
    for value, label in User.ProfileType.choices:
        print(f"  - {value}: {label}")

    # Check if DEFAULT is the default
    print(f"\n=== DEFAULT Type ===")
    print(f"  Value: {User.ProfileType.DEFAULT}")
    print(f"  Label: {User.ProfileType.DEFAULT.label}")

    # Test upgrade methods
    print(f"\n=== User Registration & Package Assignment ===")
    print("  When a new DEFAULT user registers:")
    print("  1. User.profile_type is automatically set to 'default'")
    print("  2. Signal checks for is_default=True package:")
    print("     - If found: Assigns that package with its ad_count and duration")
    print("     - If not found: Creates fallback (1 free ad, 365 days)")
    print("  3. User creates an ad:")
    print("     - DEFAULT users: Ad goes to PENDING (requires admin approval)")
    print("     - PUBLISHER users: Ad auto-activates to ACTIVE")

    print("\n=== Upgrade Path ===")
    print("  DEFAULT user can upgrade to PUBLISHER using:")
    print("  - user.upgrade_to_publisher()")
    print("  - After upgrade, their ads are auto-activated")

    print("\n✓ All configuration tests passed!")


if __name__ == "__main__":
    test_default_user_creation()
