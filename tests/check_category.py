#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idrissimart.settings')
django.setup()

from main.models import Category, ClassifiedAd

# البحث عن الفئة
slug = 'إعلانات-مبوبة'
print(f'البحث عن فئة بـ slug: {slug}')
cat = Category.objects.filter(slug=slug).first()

if cat:
    print(f'✓ تم العثور على الفئة: {cat.name_ar} (ID: {cat.id})')
    print(f'  Section Type: {cat.section_type}')
    print(f'  عدد الفئات الفرعية: {cat.get_children().count()}')
    
    # البحث عن الإعلانات المباشرة
    direct_ads = ClassifiedAd.objects.filter(category=cat, status='active').count()
    print(f'  إعلانات مباشرة في هذه الفئة: {direct_ads}')
    
    # البحث في جميع الفئات الفرعية
    descendants = cat.get_descendants(include_self=True)
    print(f'  عدد الفئات (شاملة الفرعية): {descendants.count()}')
    all_ads = ClassifiedAd.objects.filter(category__in=descendants, status='active').count()
    print(f'  إجمالي الإعلانات النشطة (شاملة الفرعية): {all_ads}')
    
    # جميع الإعلانات بغض النظر عن الحالة
    all_ads_any_status = ClassifiedAd.objects.filter(category__in=descendants).count()
    print(f'  إجمالي جميع الإعلانات (أي حالة): {all_ads_any_status}')
    
    # عرض أسماء الفئات الفرعية
    print('\nالفئات الفرعية:')
    for child in descendants[:10]:
        ads_count = ClassifiedAd.objects.filter(category=child, status='active').count()
        print(f'  - {child.name_ar} ({child.slug}) - {ads_count} إعلان')
else:
    print('✗ لم يتم العثور على الفئة')
