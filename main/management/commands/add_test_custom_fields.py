"""
Management command to add test custom fields to categories.
Usage: python manage.py add_test_custom_fields
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Category, CustomField, CustomFieldOption, CategoryCustomField


class Command(BaseCommand):
    help = "Add test custom fields to categories for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--category-id",
            type=int,
            help="Category ID to add custom fields to (optional, adds to all if not specified)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing custom fields before adding new ones",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        category_id = options.get("category_id")
        clear_existing = options.get("clear")

        if clear_existing:
            self.stdout.write("Clearing existing custom fields...")
            CustomField.objects.all().delete()
            CategoryCustomField.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared existing custom fields"))

        # Get categories
        if category_id:
            categories = Category.objects.filter(pk=category_id)
            if not categories.exists():
                self.stdout.write(
                    self.style.ERROR(f"Category with ID {category_id} not found")
                )
                return
        else:
            # Get all leaf categories (categories without children)
            categories = Category.objects.filter(
                section_type=Category.SectionType.CLASSIFIED, is_active=True
            )

        if not categories.exists():
            self.stdout.write(self.style.ERROR("No categories found"))
            return

        self.stdout.write(f"Found {categories.count()} categories")

        # Create custom fields
        custom_fields_data = [
            {
                "name": "brand",
                "label_ar": "العلامة التجارية",
                "field_type": "select",
                "help_text": "اختر العلامة التجارية",
                "placeholder": "",
                "options": [
                    {"value": "samsung", "label_ar": "سامسونج"},
                    {"value": "apple", "label_ar": "أبل"},
                    {"value": "huawei", "label_ar": "هواوي"},
                    {"value": "xiaomi", "label_ar": "شاومي"},
                    {"value": "other", "label_ar": "أخرى"},
                ],
            },
            {
                "name": "condition",
                "label_ar": "الحالة",
                "field_type": "radio",
                "help_text": "حالة المنتج",
                "placeholder": "",
                "options": [
                    {"value": "new", "label_ar": "جديد"},
                    {"value": "used_like_new", "label_ar": "مستعمل - كالجديد"},
                    {"value": "used_good", "label_ar": "مستعمل - جيد"},
                    {"value": "used_fair", "label_ar": "مستعمل - مقبول"},
                ],
            },
            {
                "name": "color",
                "label_ar": "اللون",
                "field_type": "select",
                "help_text": "اختر اللون",
                "placeholder": "",
                "options": [
                    {"value": "black", "label_ar": "أسود"},
                    {"value": "white", "label_ar": "أبيض"},
                    {"value": "blue", "label_ar": "أزرق"},
                    {"value": "red", "label_ar": "أحمر"},
                    {"value": "gold", "label_ar": "ذهبي"},
                    {"value": "silver", "label_ar": "فضي"},
                ],
            },
            {
                "name": "storage",
                "label_ar": "السعة التخزينية",
                "field_type": "select",
                "help_text": "سعة التخزين",
                "placeholder": "",
                "options": [
                    {"value": "64gb", "label_ar": "64 جيجا"},
                    {"value": "128gb", "label_ar": "128 جيجا"},
                    {"value": "256gb", "label_ar": "256 جيجا"},
                    {"value": "512gb", "label_ar": "512 جيجا"},
                    {"value": "1tb", "label_ar": "1 تيرا"},
                ],
            },
            {
                "name": "year",
                "label_ar": "سنة الصنع",
                "field_type": "number",
                "help_text": "أدخل سنة الصنع",
                "placeholder": "مثال: 2024",
                "options": [],
            },
            {
                "name": "warranty",
                "label_ar": "الضمان",
                "field_type": "radio",
                "help_text": "هل يوجد ضمان؟",
                "placeholder": "",
                "options": [
                    {"value": "yes", "label_ar": "نعم"},
                    {"value": "no", "label_ar": "لا"},
                ],
            },
            {
                "name": "accessories",
                "label_ar": "الملحقات المتوفرة",
                "field_type": "checkbox",
                "help_text": "اختر الملحقات المتوفرة",
                "placeholder": "",
                "options": [
                    {"value": "charger", "label_ar": "شاحن"},
                    {"value": "headphones", "label_ar": "سماعات"},
                    {"value": "case", "label_ar": "جراب"},
                    {"value": "screen_protector", "label_ar": "واقي شاشة"},
                    {"value": "box", "label_ar": "العلبة الأصلية"},
                ],
            },
            {
                "name": "model",
                "label_ar": "الموديل",
                "field_type": "text",
                "help_text": "أدخل موديل المنتج",
                "placeholder": "مثال: iPhone 15 Pro Max",
                "options": [],
            },
            {
                "name": "specifications",
                "label_ar": "المواصفات الإضافية",
                "field_type": "textarea",
                "help_text": "أدخل المواصفات التفصيلية",
                "placeholder": "اكتب المواصفات هنا...",
                "options": [],
            },
        ]

        created_count = 0
        for category in categories:
            self.stdout.write(f"\nProcessing category: {category.name}")

            for field_data in custom_fields_data:
                # Create or get custom field
                custom_field, created = CustomField.objects.get_or_create(
                    name=field_data["name"],
                    defaults={
                        "label_ar": field_data["label_ar"],
                        "field_type": field_data["field_type"],
                        "help_text": field_data["help_text"],
                        "placeholder": field_data["placeholder"],
                        "is_active": True,
                    },
                )

                if created:
                    self.stdout.write(
                        f"  ✓ Created custom field: {custom_field.label_ar}"
                    )
                else:
                    self.stdout.write(
                        f"  - Using existing field: {custom_field.label_ar}"
                    )

                # Create options if any
                if field_data["options"]:
                    for idx, option_data in enumerate(field_data["options"]):
                        option, opt_created = CustomFieldOption.objects.get_or_create(
                            custom_field=custom_field,
                            value=option_data["value"],
                            defaults={
                                "label_ar": option_data["label_ar"],
                                "order": idx,
                                "is_active": True,
                            },
                        )
                        if opt_created:
                            self.stdout.write(f"    + Added option: {option.label_ar}")

                # Link to category
                cat_field, cf_created = CategoryCustomField.objects.get_or_create(
                    category=category,
                    custom_field=custom_field,
                    defaults={
                        "is_required": field_data["name"]
                        in ["brand", "condition"],  # Make some fields required
                        "order": custom_fields_data.index(field_data),
                        "is_active": True,
                    },
                )

                if cf_created:
                    created_count += 1
                    self.stdout.write(
                        f"  ✓ Linked field to category: {custom_field.label_ar}"
                    )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Successfully added {created_count} custom field associations"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Processed {categories.count()} categories with {len(custom_fields_data)} custom fields each"
            )
        )
        self.stdout.write("\nYou can now test custom fields in the ad creation form!")
