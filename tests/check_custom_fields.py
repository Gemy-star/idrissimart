#!/usr/bin/env python
"""Check custom fields for category"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings.local')
django.setup()

from main.models import Category, CategoryCustomField, CustomField

# Find the category
cat = Category.objects.filter(slug='إعلانات-مبوبة').first()
if not cat:
    print("❌ Category not found!")
    exit(1)

print(f"✓ Category: {cat.name_ar or cat.name} (ID: {cat.id})")
print(f"  Level: {cat.level}")
print(f"  Active: {cat.is_active}")

# Get descendants
descendants = cat.get_descendants(include_self=True)
print(f"\n✓ Descendants (including self): {len(descendants)}")
for desc in descendants:
    print(f"  - {desc.name_ar or desc.name} (ID: {desc.id}, Level: {desc.level})")

# Check CategoryCustomField
print("\n📋 CategoryCustomField entries:")
cat_fields = CategoryCustomField.objects.filter(category__in=descendants)
print(f"  Total: {cat_fields.count()}")
for cf in cat_fields:
    print(f"  - Category: {cf.category.name_ar or cf.category.name}")
    print(f"    Field: {cf.custom_field.label_ar or cf.custom_field.label}")
    print(f"    Active: {cf.is_active}")
    print(f"    Show in filters: {cf.show_in_filters}")
    print()

# Check with filters
filtered_fields = CategoryCustomField.objects.filter(
    category__in=descendants, 
    is_active=True, 
    show_in_filters=True
)
print(f"\n✓ Filtered custom fields (active + show_in_filters): {filtered_fields.count()}")
for cf in filtered_fields:
    print(f"  - {cf.custom_field.label_ar or cf.custom_field.label} ({cf.category.name_ar})")

# Check all CustomField objects
print("\n📋 All CustomField objects in database:")
all_fields = CustomField.objects.all()
print(f"  Total: {all_fields.count()}")
for field in all_fields[:10]:  # Show first 10
    print(f"  - {field.label_ar or field.label} (Name: {field.name}, Active: {field.is_active})")
