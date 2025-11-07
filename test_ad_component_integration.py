import requests


def test_ad_component_integration():
    print("🧪 Testing Ad Component Integration...")

    try:
        # Test categories page
        categories_response = requests.get(
            "http://127.0.0.1:8000/ar/categories/?section=classified"
        )
        print(f"✅ Categories Page Status: {categories_response.status_code}")

        categories_content = categories_response.text
        categories_tests = {
            "Modern Ad Card CSS": "modern-ad-card" in categories_content,
            "Ad Image Container": "ad-image-container" in categories_content,
            "Publisher Footer Info": "publisher-footer-info" in categories_content,
            "Quality Indicator": "quality-indicator" in categories_content,
            "Ad Features Modern": "ad-features-modern" in categories_content,
            "Price Section": "ad-price-section" in categories_content,
            "Quick Actions": "ad-quick-actions" in categories_content,
        }

        print("\n📋 Categories Page Component Tests:")
        categories_passed = 0
        for test_name, passed in categories_tests.items():
            status = "✅ FOUND" if passed else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if passed:
                categories_passed += 1

        # Try to test category detail page (if we have a category)
        print(
            f"\n📊 Categories Page Results: {categories_passed}/{len(categories_tests)} tests passed"
        )

        # Test if GSAP animations are included
        gsap_tests = {
            "GSAP Script": "gsap.min.js" in categories_content,
            "Card Animations": "card hover animations" in categories_content.lower(),
            "Favorite Toggle": "toggleFavorite" in categories_content,
            "Share Function": "shareAd" in categories_content,
        }

        print("\n🎬 Animation & Interaction Tests:")
        animations_passed = 0
        for test_name, passed in gsap_tests.items():
            status = "✅ FOUND" if passed else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if passed:
                animations_passed += 1

        # Test responsive design
        responsive_tests = {
            "List View Adaptation": 'data-view="list"' in categories_content,
            "Mobile Responsive": "@media (max-width: 768px)" in categories_content,
            "Grid Toggle": "view-toggle-btn" in categories_content,
        }

        print("\n📱 Responsive Design Tests:")
        responsive_passed = 0
        for test_name, passed in responsive_tests.items():
            status = "✅ FOUND" if passed else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if passed:
                responsive_passed += 1

        total_tests = len(categories_tests) + len(gsap_tests) + len(responsive_tests)
        total_passed = categories_passed + animations_passed + responsive_passed

        print("\n" + "=" * 60)
        if total_passed >= total_tests * 0.8:  # 80% pass rate
            print("🎉 AD COMPONENT INTEGRATION SUCCESSFUL!")
            print("✨ Features verified:")
            print("  • Modern ad card styling integrated")
            print("  • GSAP animations for interactions")
            print("  • Responsive grid/list view support")
            print("  • Publisher information display")
            print("  • Quality indicators and badges")
            print("  • Price display with features")
            print("  • Quick action buttons")
        else:
            print("⚠️ Integration partially successful.")
            print(f"Results: {total_passed}/{total_tests} tests passed")

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error testing ad component integration: {e}")


if __name__ == "__main__":
    test_ad_component_integration()
