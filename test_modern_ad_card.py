"""
Test script to verify the modern ad card functionality
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
django.setup()

from main.models import Ad, Category, Country
from main.utils import (
    format_ad_price,
    get_ad_urgency_badge,
    get_ad_time_display,
    calculate_ad_score,
    get_ad_image_url,
)
from main.templatetags.ad_tags import (
    ad_price_formatted,
    ad_urgency_badge,
    ad_time_display,
    ad_verification_status,
)


def test_utility_functions():
    """Test the utility functions for ad processing"""
    print("=== Testing Utility Functions ===")

    # Test price formatting
    test_price = Decimal("1234.50")
    formatted_price = format_ad_price(test_price, "USD")
    print(f"✓ Price formatting: {test_price} USD → {formatted_price}")

    # Test urgency badge
    class MockAd:
        is_featured = True
        urgency = "high"

    mock_ad = MockAd()
    urgency_data = get_ad_urgency_badge(mock_ad)
    print(f"✓ Urgency badge: {urgency_data}")

    # Test time display
    from django.utils import timezone
    from datetime import timedelta

    # Create a test time (2 hours ago)
    test_time = timezone.now() - timedelta(hours=2)
    time_display = get_ad_time_display(test_time)
    print(f"✓ Time display: {time_display}")

    print()


def test_template_tags():
    """Test the template tags functionality"""
    print("=== Testing Template Tags ===")

    try:
        # Create a mock ad object for testing
        class MockAd:
            price = Decimal("999.99")
            currency = "USD"
            is_featured = True
            urgency = "high"
            created_at = None
            is_verified = True

        mock_ad = MockAd()

        # Test template tag functions
        formatted_price = ad_price_formatted(mock_ad)
        print(f"✓ Template tag price: {formatted_price}")

        urgency_badge = ad_urgency_badge(mock_ad)
        print(f"✓ Template tag urgency: {urgency_badge}")

        verification = ad_verification_status(mock_ad)
        print(f"✓ Template tag verification: {verification}")

    except Exception as e:
        print(f"⚠ Template tag test error: {e}")

    print()


def test_ad_scoring():
    """Test the ad quality scoring system"""
    print("=== Testing Ad Quality Scoring ===")

    # Create mock ad data
    ad_data = {
        "has_images": True,
        "description_length": 250,
        "has_phone": True,
        "is_verified": True,
        "view_count": 150,
        "is_featured": True,
    }

    score = calculate_ad_score(ad_data)
    print(f"✓ Ad quality score: {score}/100")

    if score >= 80:
        quality = "High Quality ⭐"
    elif score >= 60:
        quality = "Good Quality ✓"
    else:
        quality = "Standard Quality"

    print(f"✓ Quality indicator: {quality}")
    print()


def test_database_ads():
    """Test with real ads from database if available"""
    print("=== Testing with Database Ads ===")

    try:
        # Get a few ads for testing
        ads = Ad.objects.all()[:3]

        if ads:
            for ad in ads:
                print(f"✓ Ad: {ad.title[:50]}...")
                print(f"  Price: {format_ad_price(ad.price, ad.currency)}")
                print(f"  Created: {get_ad_time_display(ad.created_at)}")

                # Test image URL
                image_url = get_ad_image_url(ad)
                print(f"  Image: {'Available' if image_url else 'Placeholder'}")
                print()
        else:
            print("⚠ No ads found in database")

    except Exception as e:
        print(f"⚠ Database test error: {e}")


def main():
    """Run all tests"""
    print("🧪 Modern Ad Card Functionality Test")
    print("=" * 50)

    test_utility_functions()
    test_template_tags()
    test_ad_scoring()
    test_database_ads()

    print("✅ Testing completed!")
    print("\n💡 To see the modern ad card in action:")
    print("   1. Visit http://127.0.0.1:8000/ in your browser")
    print("   2. Check any page with ad listings")
    print("   3. Look for enhanced styling, badges, and interactions")


if __name__ == "__main__":
    main()
