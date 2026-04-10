"""
Management command to fix custom field labels that have English text in label_ar field.
This swaps the labels and provides Arabic translations for common field names.

Usage:
    python manage.py fix_custom_field_labels --dry-run  # Preview changes
    python manage.py fix_custom_field_labels            # Apply changes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import CustomField, CustomFieldOption


class Command(BaseCommand):
    help = "Fix custom field labels - swap English text from label_ar to label_en and add Arabic translations"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )

    # Common translations mapping
    TRANSLATIONS = {
        # Service/Business Fields
        'Service Type': 'نوع الخدمة',
        'Brands Supported': 'الماركات المدعومة',
        'Turnaround Time': 'وقت التنفيذ',
        'Certification Provided': 'الشهادة المقدمة',
        'Warranty Period': 'فترة الضمان',
        'Pickup Delivery': 'التوصيل والاستلام',
        
        # Product Fields
        'Brand': 'الماركة',
        'Model': 'الموديل',
        'Condition': 'الحالة',
        'Year': 'السنة',
        'Color': 'اللون',
        'Size': 'المقاس',
        'Material': 'المادة',
        'Weight': 'الوزن',
        'Dimensions': 'الأبعاد',
        'Warranty': 'الضمان',
        'Warranty Included': 'يتضمن ضمان',
        
        # Vehicle Fields
        'Mileage': 'المسافة المقطوعة',
        'Transmission': 'ناقل الحركة',
        'Fuel Type': 'نوع الوقود',
        'Engine Size': 'حجم المحرك',
        'Doors': 'الأبواب',
        'Seats': 'المقاعد',
        'Body Type': 'نوع الهيكل',
        
        # Real Estate Fields
        'Property Type': 'نوع العقار',
        'Bedrooms': 'غرف النوم',
        'Bathrooms': 'الحمامات',
        'Area': 'المساحة',
        'Furnished': 'مفروش',
        'Parking': 'موقف سيارات',
        'Floor': 'الطابق',
        'Age': 'عمر البناء',
        
        # Electronics Fields
        'RAM': 'الذاكرة العشوائية',
        'Storage': 'التخزين',
        'Screen Size': 'حجم الشاشة',
        'Processor': 'المعالج',
        'Graphics Card': 'كرت الشاشة',
        'Operating System': 'نظام التشغيل',
        'Battery Life': 'عمر البطارية',
        'Camera': 'الكاميرا',
        
        # Common Options
        'New': 'جديد',
        'Used': 'مستعمل',
        'Like New': 'مثل الجديد',
        'Good': 'جيد',
        'Fair': 'مقبول',
        'Yes': 'نعم',
        'No': 'لا',
        'Available': 'متاح',
        'Not Available': 'غير متاح',
        'Included': 'مشمول',
        'Not Included': 'غير مشمول',
        
        # Time periods
        '1 Year': 'سنة واحدة',
        '2 Years': 'سنتان',
        '3 Years': 'ثلاث سنوات',
        '1 Month': 'شهر واحد',
        '3 Months': '3 شهور',
        '6 Months': '6 شهور',
        '1-2 Days': '1-2 أيام',
        '2-3 Days': '2-3 أيام',
        '3-5 Days': '3-5 أيام',
        '1 Week': 'أسبوع واحد',
    }

    def is_english_text(self, text):
        """Check if text is primarily English (contains mostly ASCII characters)"""
        if not text:
            return False
        
        # Count ASCII alphabetic characters
        ascii_count = sum(1 for c in text if c.isascii() and c.isalpha())
        arabic_count = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        
        # If more than 60% is ASCII and very little Arabic, consider it English
        total_alpha = ascii_count + arabic_count
        if total_alpha == 0:
            return False
        
        return ascii_count / total_alpha > 0.6 and arabic_count < 3

    def get_translation(self, english_text):
        """Get Arabic translation for common English field names"""
        # Direct match
        if english_text in self.TRANSLATIONS:
            return self.TRANSLATIONS[english_text]
        
        # Case-insensitive match
        for key, value in self.TRANSLATIONS.items():
            if key.lower() == english_text.lower():
                return value
        
        # Return None if no translation found
        return None

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write('')
        
        # Fix CustomField labels
        self.stdout.write(self.style.HTTP_INFO('Checking CustomField labels...'))
        custom_fields = CustomField.objects.all()
        fields_fixed = 0
        fields_needs_manual = []
        
        for field in custom_fields:
            label_ar = field.label_ar or ''
            label_en = field.label_en or ''
            
            # Check if label_ar contains English text
            if self.is_english_text(label_ar):
                arabic_translation = self.get_translation(label_ar)
                
                if arabic_translation:
                    self.stdout.write(
                        f'  Field: {field.name}'
                    )
                    self.stdout.write(
                        f'    Current: label_ar="{label_ar}", label_en="{label_en}"'
                    )
                    self.stdout.write(
                        f'    → New:   label_ar="{arabic_translation}", label_en="{label_ar}"'
                    )
                    
                    if not dry_run:
                        # Move English text to label_en if it's empty
                        if not label_en:
                            field.label_en = label_ar
                        # Set Arabic translation
                        field.label_ar = arabic_translation
                        field.save(update_fields=['label_ar', 'label_en'])
                    
                    fields_fixed += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Field: {field.name} - No translation found for "{label_ar}"'
                        )
                    )
                    fields_needs_manual.append((field.name, label_ar))
        
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Checking CustomFieldOption labels...'))
        options = CustomFieldOption.objects.all()
        options_fixed = 0
        options_needs_manual = []
        
        for option in options:
            label_ar = option.label_ar or ''
            label_en = option.label_en or ''
            
            # Check if label_ar contains English text
            if self.is_english_text(label_ar):
                arabic_translation = self.get_translation(label_ar)
                
                if arabic_translation:
                    self.stdout.write(
                        f'  Option: {option.custom_field.name} - {option.value}'
                    )
                    self.stdout.write(
                        f'    Current: label_ar="{label_ar}", label_en="{label_en}"'
                    )
                    self.stdout.write(
                        f'    → New:   label_ar="{arabic_translation}", label_en="{label_ar}"'
                    )
                    
                    if not dry_run:
                        # Move English text to label_en if it's empty
                        if not label_en:
                            option.label_en = label_ar
                        # Set Arabic translation
                        option.label_ar = arabic_translation
                        option.save(update_fields=['label_ar', 'label_en'])
                    
                    options_fixed += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Option: {option.custom_field.name} - No translation for "{label_ar}"'
                        )
                    )
                    options_needs_manual.append((option.custom_field.name, option.value, label_ar))
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'CustomFields fixed: {fields_fixed}')
        self.stdout.write(f'CustomFieldOptions fixed: {options_fixed}')
        
        if fields_needs_manual:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'CustomFields needing manual translation ({len(fields_needs_manual)}):'))
            for name, text in fields_needs_manual:
                self.stdout.write(f'  - {name}: "{text}"')
        
        if options_needs_manual:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'CustomFieldOptions needing manual translation ({len(options_needs_manual)}):'))
            for field_name, value, text in options_needs_manual:
                self.stdout.write(f'  - {field_name} ({value}): "{text}"')
        
        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes were made'))
            self.stdout.write(self.style.WARNING('Remove --dry-run flag to apply changes'))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✓ Changes applied successfully!'))
            
            if fields_needs_manual or options_needs_manual:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('⚠ Some fields need manual translation in the admin panel'))
