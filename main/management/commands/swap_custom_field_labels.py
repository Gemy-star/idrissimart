"""
Management command to swap English/Arabic labels in custom fields.
When label_ar contains English text, it swaps it to label_en and adds proper Arabic.

Usage:
    python manage.py swap_custom_field_labels --dry-run    # Preview changes
    python manage.py swap_custom_field_labels              # Apply changes
    python manage.py swap_custom_field_labels --field-name "Service Type"  # Fix specific field
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import CustomField, CustomFieldOption


class Command(BaseCommand):
    help = "Swap custom field labels when label_ar contains English text"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )
        parser.add_argument(
            '--field-name',
            type=str,
            help='Fix only a specific field by its label_ar value (e.g., "Service Type")',
        )

    # Translation dictionary for common field names
    TRANSLATIONS = {
        # Service/Business Fields
        'Service Type': 'نوع الخدمة',
        'service type': 'نوع الخدمة',
        'Brands Supported': 'الماركات المدعومة',
        'brands supported': 'الماركات المدعومة',
        'Turnaround Time': 'وقت التنفيذ',
        'turnaround time': 'وقت التنفيذ',
        'Certification Provided': 'الشهادة المقدمة',
        'certification provided': 'الشهادة المقدمة',
        'Warranty Period': 'فترة الضمان',
        'warranty period': 'فترة الضمان',
        'Pickup Delivery': 'التوصيل والاستلام',
        'pickup delivery': 'التوصيل والاستلام',
        'Installation Service': 'خدمة التركيب',
        'installation service': 'خدمة التركيب',
        'Service Area': 'منطقة الخدمة',
        'service area': 'منطقة الخدمة',
        
        # Product Fields
        'Brand': 'الماركة',
        'brand': 'الماركة',
        'Model': 'الموديل',
        'model': 'الموديل',
        'Model Number': 'رقم الموديل',
        'model number': 'رقم الموديل',
        'Condition': 'الحالة',
        'condition': 'الحالة',
        'Year': 'السنة',
        'year': 'السنة',
        'Color': 'اللون',
        'color': 'اللون',
        'Size': 'المقاس',
        'size': 'المقاس',
        'Material': 'المادة',
        'material': 'المادة',
        'Weight': 'الوزن',
        'weight': 'الوزن',
        'Dimensions': 'الأبعاد',
        'dimensions': 'الأبعاد',
        'Warranty': 'الضمان',
        'warranty': 'الضمان',
        'Warranty Included': 'يتضمن ضمان',
        'warranty included': 'يتضمن ضمان',
        'Quantity': 'الكمية',
        'quantity': 'الكمية',
        'Stock': 'المخزون',
        'stock': 'المخزون',
        
        # Vehicle Fields
        'Mileage': 'المسافة المقطوعة',
        'mileage': 'المسافة المقطوعة',
        'Transmission': 'ناقل الحركة',
        'transmission': 'ناقل الحركة',
        'Fuel Type': 'نوع الوقود',
        'fuel type': 'نوع الوقود',
        'Engine Size': 'حجم المحرك',
        'engine size': 'حجم المحرك',
        'Doors': 'الأبواب',
        'doors': 'الأبواب',
        'Seats': 'المقاعد',
        'seats': 'المقاعد',
        'Body Type': 'نوع الهيكل',
        'body type': 'نوع الهيكل',
        
        # Real Estate Fields
        'Property Type': 'نوع العقار',
        'property type': 'نوع العقار',
        'Bedrooms': 'غرف النوم',
        'bedrooms': 'غرف النوم',
        'Bathrooms': 'الحمامات',
        'bathrooms': 'الحمامات',
        'Area': 'المساحة',
        'area': 'المساحة',
        'Furnished': 'مفروش',
        'furnished': 'مفروش',
        'Parking': 'موقف سيارات',
        'parking': 'موقف سيارات',
        'Floor': 'الطابق',
        'floor': 'الطابق',
        'Building Age': 'عمر البناء',
        'building age': 'عمر البناء',
        'Age': 'العمر',
        'age': 'العمر',
        
        # Electronics Fields
        'RAM': 'الذاكرة العشوائية',
        'ram': 'الذاكرة العشوائية',
        'Storage': 'التخزين',
        'storage': 'التخزين',
        'Screen Size': 'حجم الشاشة',
        'screen size': 'حجم الشاشة',
        'Processor': 'المعالج',
        'processor': 'المعالج',
        'Graphics Card': 'كرت الشاشة',
        'graphics card': 'كرت الشاشة',
        'Operating System': 'نظام التشغيل',
        'operating system': 'نظام التشغيل',
        'Battery Life': 'عمر البطارية',
        'battery life': 'عمر البطارية',
        'Camera': 'الكاميرا',
        'camera': 'الكاميرا',
        
        # Common Options
        'New': 'جديد',
        'new': 'جديد',
        'Used': 'مستعمل',
        'used': 'مستعمل',
        'Like New': 'مثل الجديد',
        'like new': 'مثل الجديد',
        'Excellent': 'ممتاز',
        'excellent': 'ممتاز',
        'Good': 'جيد',
        'good': 'جيد',
        'Fair': 'مقبول',
        'fair': 'مقبول',
        'Poor': 'سيء',
        'poor': 'سيء',
        'Yes': 'نعم',
        'yes': 'نعم',
        'No': 'لا',
        'no': 'لا',
        'Available': 'متاح',
        'available': 'متاح',
        'Not Available': 'غير متاح',
        'not available': 'غير متاح',
        'Included': 'مشمول',
        'included': 'مشمول',
        'Not Included': 'غير مشمول',
        'not included': 'غير مشمول',
        
        # Time periods
        '1 Year': 'سنة واحدة',
        '1 year': 'سنة واحدة',
        '2 Years': 'سنتان',
        '2 years': 'سنتان',
        '3 Years': 'ثلاث سنوات',
        '3 years': 'ثلاث سنوات',
        '1 Month': 'شهر واحد',
        '1 month': 'شهر واحد',
        '3 Months': '3 شهور',
        '3 months': '3 شهور',
        '6 Months': '6 شهور',
        '6 months': '6 شهور',
        '1-2 Days': '1-2 أيام',
        '1-2 days': '1-2 أيام',
        '2-3 Days': '2-3 أيام',
        '2-3 days': '2-3 أيام',
        '3-5 Days': '3-5 أيام',
        '3-5 days': '3-5 أيام',
        '1 Week': 'أسبوع واحد',
        '1 week': 'أسبوع واحد',
        '2 Weeks': 'أسبوعان',
        '2 weeks': 'أسبوعان',
    }

    def is_mainly_english(self, text):
        """Check if text is primarily English (more than 50% ASCII letters)"""
        if not text or not text.strip():
            return False
        
        # Count ASCII alphabetic characters vs Arabic characters
        ascii_count = sum(1 for c in text if c.isascii() and c.isalpha())
        arabic_count = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        total_alpha = ascii_count + arabic_count
        
        # If no alphabetic characters, can't determine
        if total_alpha == 0:
            return False
        
        # Consider it English if more than 50% is ASCII
        return ascii_count / total_alpha > 0.5

    def get_arabic_translation(self, english_text):
        """Get Arabic translation for English text"""
        # Try direct match (case-sensitive)
        if english_text in self.TRANSLATIONS:
            return self.TRANSLATIONS[english_text]
        
        # Try case-insensitive match
        english_lower = english_text.lower()
        if english_lower in self.TRANSLATIONS:
            return self.TRANSLATIONS[english_lower]
        
        # Try trimmed version
        trimmed = english_text.strip()
        if trimmed in self.TRANSLATIONS:
            return self.TRANSLATIONS[trimmed]
        
        return None

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        specific_field = options.get('field_name')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=' * 70))
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write(self.style.WARNING('=' * 70))
            self.stdout.write('')
        
        # Get fields to process
        if specific_field:
            fields = CustomField.objects.filter(label_ar=specific_field)
            if not fields.exists():
                self.stdout.write(self.style.ERROR(f'No field found with label_ar="{specific_field}"'))
                return
        else:
            fields = CustomField.objects.all()
        
        # Process CustomField labels
        self.stdout.write(self.style.HTTP_INFO('Processing CustomField labels...'))
        self.stdout.write('')
        
        fields_fixed = 0
        fields_skipped = 0
        fields_no_translation = []
        
        for field in fields:
            label_ar = field.label_ar or ''
            label_en = field.label_en or ''
            
            # Skip if label_ar is already Arabic
            if not self.is_mainly_english(label_ar):
                fields_skipped += 1
                continue
            
            # Get Arabic translation
            arabic_translation = self.get_arabic_translation(label_ar)
            
            if arabic_translation:
                self.stdout.write(self.style.SUCCESS(f'✓ Field: {field.name}'))
                self.stdout.write(f'  Current:')
                self.stdout.write(f'    label_ar = "{label_ar}"')
                self.stdout.write(f'    label_en = "{label_en}"')
                self.stdout.write(f'  New:')
                self.stdout.write(f'    label_ar = "{arabic_translation}"')
                self.stdout.write(f'    label_en = "{label_ar}"')
                
                if not dry_run:
                    # Swap: Move English to label_en, set Arabic in label_ar
                    old_label_ar = field.label_ar
                    field.label_en = old_label_ar
                    field.label_ar = arabic_translation
                    field.save(update_fields=['label_ar', 'label_en'])
                
                fields_fixed += 1
                self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Field: {field.name}'))
                self.stdout.write(f'  No translation found for: "{label_ar}"')
                self.stdout.write(f'  Please add manually or extend the translations dictionary')
                fields_no_translation.append((field.name, label_ar))
                self.stdout.write('')
        
        # Process CustomFieldOption labels
        self.stdout.write(self.style.HTTP_INFO('Processing CustomFieldOption labels...'))
        self.stdout.write('')
        
        options_fixed = 0
        options_skipped = 0
        options_no_translation = []
        
        for option in CustomFieldOption.objects.all():
            label_ar = option.label_ar or ''
            label_en = option.label_en or ''
            
            # Skip if label_ar is already Arabic
            if not self.is_mainly_english(label_ar):
                options_skipped += 1
                continue
            
            # Get Arabic translation
            arabic_translation = self.get_arabic_translation(label_ar)
            
            if arabic_translation:
                self.stdout.write(self.style.SUCCESS(f'✓ Option: {option.custom_field.name} → {option.value}'))
                self.stdout.write(f'  Current:')
                self.stdout.write(f'    label_ar = "{label_ar}"')
                self.stdout.write(f'    label_en = "{label_en}"')
                self.stdout.write(f'  New:')
                self.stdout.write(f'    label_ar = "{arabic_translation}"')
                self.stdout.write(f'    label_en = "{label_ar}"')
                
                if not dry_run:
                    # Swap: Move English to label_en, set Arabic in label_ar
                    old_label_ar = option.label_ar
                    option.label_en = old_label_ar
                    option.label_ar = arabic_translation
                    option.save(update_fields=['label_ar', 'label_en'])
                
                options_fixed += 1
                self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Option: {option.custom_field.name} → {option.value}'))
                self.stdout.write(f'  No translation found for: "{label_ar}"')
                options_no_translation.append((option.custom_field.name, option.value, label_ar))
                self.stdout.write('')
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'CustomFields:')
        self.stdout.write(f'  ✓ Fixed: {fields_fixed}')
        self.stdout.write(f'  → Skipped (already Arabic): {fields_skipped}')
        self.stdout.write(f'  ⚠ No translation: {len(fields_no_translation)}')
        self.stdout.write('')
        self.stdout.write(f'CustomFieldOptions:')
        self.stdout.write(f'  ✓ Fixed: {options_fixed}')
        self.stdout.write(f'  → Skipped (already Arabic): {options_skipped}')
        self.stdout.write(f'  ⚠ No translation: {len(options_no_translation)}')
        
        if fields_no_translation:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Fields needing manual translation:'))
            for name, text in fields_no_translation:
                self.stdout.write(f'  - {name}: "{text}"')
        
        if options_no_translation:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Options needing manual translation:'))
            for field_name, value, text in options_no_translation:
                self.stdout.write(f'  - {field_name} ({value}): "{text}"')
        
        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('=' * 70))
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes were made'))
            self.stdout.write(self.style.WARNING('Remove --dry-run flag to apply changes'))
            self.stdout.write(self.style.WARNING('=' * 70))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✓✓✓ Changes applied successfully! ✓✓✓'))
            
            if fields_no_translation or options_no_translation:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('Note: Some fields still need manual translation via admin panel'))
