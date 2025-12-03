# Test Script for Custom Fields Card Display Feature

"""
This script tests the new show_on_card feature for custom fields.

Usage:
    python test_custom_fields_card.py
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
django.setup()

from main.models import (
    CustomField,
    CustomFieldOption,
    CategoryCustomField,
    Category,
    ClassifiedAd,
)


def test_show_on_card_field():
    """Test that show_on_card field exists and works"""
    print("=" * 60)
    print("Testing show_on_card field...")
    print("=" * 60)

    # Get a random category
    category = Category.objects.first()
    if not category:
        print("❌ No categories found. Please create at least one category.")
        return

    print(f"✓ Using category: {category.name}")

    # Check if there are any custom fields
    cat_fields = CategoryCustomField.objects.filter(category=category)
    print(f"✓ Found {cat_fields.count()} custom fields for this category")

    for cf in cat_fields:
        print(f"\n  Field: {cf.custom_field.label}")
        print(f"    - show_on_card: {cf.show_on_card}")
        print(f"    - is_required: {cf.is_required}")
        print(f"    - order: {cf.order}")

    print("\n" + "=" * 60)


def test_get_custom_fields_for_card():
    """Test the get_custom_fields_for_card method"""
    print("\nTesting get_custom_fields_for_card() method...")
    print("=" * 60)

    # Get first active ad
    ad = ClassifiedAd.objects.filter(status="active").first()
    if not ad:
        print("❌ No active ads found. Please create at least one ad.")
        return

    print(f"✓ Using ad: {ad.title}")
    print(f"✓ Category: {ad.category.name}")
    print(f"✓ Custom fields data: {ad.custom_fields}")

    # Get fields for card
    fields_for_card = ad.get_custom_fields_for_card()

    print(f"\n✓ Fields to display on card: {len(fields_for_card)}")

    if fields_for_card:
        for field in fields_for_card:
            print(f"\n  {field['label']}: {field['value']}")
            print(f"    - Icon: {field['icon']}")
    else:
        print("\n⚠ No fields marked for card display")

    print("\n" + "=" * 60)


def test_template_integration():
    """Test template integration"""
    print("\nTemplate Integration Check...")
    print("=" * 60)

    from django.template import Template, Context

    # Get first active ad
    ad = ClassifiedAd.objects.filter(status="active").first()
    if not ad:
        print("❌ No active ads found.")
        return

    template_code = """
    {% with custom_fields_for_card=ad.get_custom_fields_for_card %}
        {% for field in custom_fields_for_card %}
            {{ field.label }}: {{ field.value }}
        {% endfor %}
    {% endwith %}
    """

    template = Template(template_code)
    context = Context({"ad": ad})
    rendered = template.render(context)

    print("✓ Template rendered successfully")
    print(f"\nRendered output:\n{rendered.strip()}")

    print("\n" + "=" * 60)


def main():
    print("\n" + "=" * 60)
    print("CUSTOM FIELDS CARD DISPLAY - TEST SUITE")
    print("=" * 60)

    try:
        test_show_on_card_field()
        test_get_custom_fields_for_card()
        test_template_integration()

        print("\n✅ All tests completed!")
        print("\nNext steps:")
        print("1. Go to Admin > Categories > Manage Custom Fields")
        print("2. Enable 'على البطاقة' (show_on_card) for specific fields")
        print("3. Create/edit an ad with those fields")
        print("4. View the ad in listings to see fields on the card")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
