#!/usr/bin/env python3
"""
Test script to validate the classified section fixes for categories page
"""
import re
import sys
from pathlib import Path


def test_classified_section():
    """Test the classified section implementation"""

    # Read the template file
    template_path = Path("templates/pages/categories.html")

    if not template_path.exists():
        print("❌ Template file not found")
        return False

    content = template_path.read_text(encoding="utf-8")

    tests = [
        {
            "name": "Hero section conditional for classified",
            "pattern": r"{% if not request\.GET\.section or request\.GET\.section == \'classified\' %}",
            "expected": True,
            "description": "Hero section should show when section=classified",
        },
        {
            "name": "Classified ads section without content_items dependency",
            "pattern": r'{% if request\.GET\.section == \'classified\' %}.*<div class="classified-ads-section',
            "expected": True,
            "description": "Classified ads section should show when section=classified regardless of content_items",
        },
        {
            "name": "Price filter only for classified",
            "pattern": r"{% if request\.GET\.section == \'classified\' %}.*price-filter-group",
            "expected": True,
            "description": "Price filter should only appear in classified section",
        },
        {
            "name": "Location filter for classified",
            "pattern": r"{% if request\.GET\.section == \'classified\' %}.*location-filter-group",
            "expected": True,
            "description": "Location filter should appear in classified section",
        },
        {
            "name": "View toggle for classified",
            "pattern": r"{% if request\.GET\.section == \'classified\' %}.*view-toggle-container",
            "expected": True,
            "description": "View toggle should only appear in classified section",
        },
        {
            "name": "Ad card component inclusion",
            "pattern": r"{% include 'partials/_ad_card_component\.html'",
            "expected": True,
            "description": "Modern ad card component should be included",
        },
        {
            "name": "Fallback for ads variable",
            "pattern": r"{% if ads %}.*{% elif content_items %}",
            "expected": True,
            "description": "Should handle both ads and content_items variables",
        },
        {
            "name": "Grid system styling",
            "pattern": r'ads-grid.*data-view="grid"',
            "expected": True,
            "description": "Grid system should be properly implemented",
        },
    ]

    results = []
    for test in tests:
        pattern = test["pattern"]
        found = bool(re.search(pattern, content, re.DOTALL))

        status = "✅" if found == test["expected"] else "❌"
        results.append(
            {
                "name": test["name"],
                "passed": found == test["expected"],
                "description": test["description"],
            }
        )
        print(f"{status} {test['name']}: {test['description']}")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    print(f"\n📊 Summary: {passed}/{total} tests passed")

    if passed == total:
        print(
            "🎉 All tests passed! The classified section fixes are working correctly."
        )
        return True
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        return False


def test_template_structure():
    """Test template structure and syntax"""

    template_path = Path("templates/pages/categories.html")
    content = template_path.read_text(encoding="utf-8")

    # Check for balanced Django template tags
    open_tags = content.count("{% if")
    close_tags = content.count("{% endif %}")

    print(f"\n🏗️  Template Structure Analysis:")
    print(f"   - Open if tags: {open_tags}")
    print(f"   - Close endif tags: {close_tags}")

    if open_tags == close_tags:
        print("   ✅ Django template tags are balanced")
        return True
    else:
        print("   ❌ Django template tags are not balanced")
        return False


if __name__ == "__main__":
    print("🧪 Testing Classified Section Implementation\n")

    # Change to the correct directory
    import os

    os.chdir(Path(__file__).parent)

    success1 = test_classified_section()
    success2 = test_template_structure()

    if success1 and success2:
        print("\n✨ All validations passed! You can now test the page at:")
        print("   - Main categories: /categories/")
        print("   - Classified ads: /categories/?section=classified")
        sys.exit(0)
    else:
        print("\n💥 Some validations failed.")
        sys.exit(1)
