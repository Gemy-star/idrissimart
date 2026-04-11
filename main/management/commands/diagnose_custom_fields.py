"""
Diagnostic command to show all custom field labels and their content.
This helps identify why labels are showing in English.

Usage:
    python manage.py diagnose_custom_fields
"""

from django.core.management.base import BaseCommand
from main.models import CustomField, CustomFieldOption


class Command(BaseCommand):
    help = "Diagnose custom field labels - show what's actually stored"

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('CUSTOM FIELDS DIAGNOSIS'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write('')
        
        # Show all custom fields
        fields = CustomField.objects.all().order_by('name')
        
        if not fields:
            self.stdout.write(self.style.WARNING('No custom fields found in database'))
            return
        
        self.stdout.write(f'Found {fields.count()} custom field(s)')
        self.stdout.write('')
        
        for field in fields:
            self.stdout.write(self.style.SUCCESS(f'Field: {field.name}'))
            self.stdout.write(f'  ID: {field.id}')
            self.stdout.write(f'  label_ar: "{field.label_ar}"')
            self.stdout.write(f'  label_en: "{field.label_en}"')
            self.stdout.write(f'  field_type: {field.field_type}')
            self.stdout.write(f'  is_active: {field.is_active}')
            
            # Check character composition
            if field.label_ar:
                ascii_chars = sum(1 for c in field.label_ar if c.isascii() and c.isalpha())
                arabic_chars = sum(1 for c in field.label_ar if '\u0600' <= c <= '\u06FF')
                total = ascii_chars + arabic_chars
                
                if total > 0:
                    ascii_pct = (ascii_chars / total) * 100
                    arabic_pct = (arabic_chars / total) * 100
                    self.stdout.write(f'  label_ar composition: {ascii_pct:.0f}% ASCII, {arabic_pct:.0f}% Arabic')
                    
                    if ascii_pct > 60:
                        self.stdout.write(self.style.WARNING('    ⚠ label_ar appears to be in English!'))
            
            # Show options if any
            options = field.field_options.filter(is_active=True).order_by('order')
            if options.exists():
                self.stdout.write(f'  Options ({options.count()}):')
                for opt in options:
                    self.stdout.write(f'    - value: "{opt.value}"')
                    self.stdout.write(f'      label_ar: "{opt.label_ar}"')
                    self.stdout.write(f'      label_en: "{opt.label_en}"')
                    
                    # Check option label composition
                    if opt.label_ar:
                        ascii_chars = sum(1 for c in opt.label_ar if c.isascii() and c.isalpha())
                        arabic_chars = sum(1 for c in opt.label_ar if '\u0600' <= c <= '\u06FF')
                        total = ascii_chars + arabic_chars
                        
                        if total > 0 and ascii_chars / total > 0.6:
                            self.stdout.write(self.style.WARNING(f'      ⚠ label_ar appears to be in English!'))
            
            # Show which categories use this field
            categories = field.categories.all()
            if categories.exists():
                cat_names = ', '.join([c.name_ar or c.name for c in categories[:3]])
                if categories.count() > 3:
                    cat_names += f' (+{categories.count() - 3} more)'
                self.stdout.write(f'  Used in categories: {cat_names}')
            
            self.stdout.write('')
        
        # Summary
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('RECOMMENDATIONS'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        
        # Count fields with English in label_ar
        english_in_ar = []
        for field in fields:
            if field.label_ar:
                ascii_chars = sum(1 for c in field.label_ar if c.isascii() and c.isalpha())
                arabic_chars = sum(1 for c in field.label_ar if '\u0600' <= c <= '\u06FF')
                total = ascii_chars + arabic_chars
                
                if total > 0 and ascii_chars / total > 0.6:
                    english_in_ar.append(field)
        
        if english_in_ar:
            self.stdout.write(self.style.WARNING(f'\n⚠ {len(english_in_ar)} field(s) have English text in label_ar:'))
            for field in english_in_ar:
                self.stdout.write(f'  - {field.name}: "{field.label_ar}"')
            self.stdout.write('\nRun: python manage.py fix_custom_field_labels')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ All fields appear to have Arabic in label_ar'))
        
        # Check empty label_en
        empty_en = [f for f in fields if not f.label_en]
        if empty_en:
            self.stdout.write(self.style.WARNING(f'\n⚠ {len(empty_en)} field(s) have empty label_en:'))
            for field in empty_en:
                self.stdout.write(f'  - {field.name}')
            self.stdout.write('\nConsider adding English translations for bilingual support')
