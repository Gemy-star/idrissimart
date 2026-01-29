from main.models import Category, ClassifiedAd

slug = 'إعلانات-مبوبة'
print(f'البحث عن فئة بـ slug: {slug}')
cat = Category.objects.filter(slug=slug).first()

if cat:
    print(f'✓ تم العثور على الفئة: {cat.name_ar} (ID: {cat.id})')
    print(f'  Section Type: {cat.section_type}')
    print(f'  عدد الفئات الفرعية: {cat.get_children().count()}')
    
    direct_ads = ClassifiedAd.objects.filter(category=cat, status='active').count()
    print(f'  إعلانات مباشرة في هذه الفئة: {direct_ads}')
    
    descendants = cat.get_descendants(include_self=True)
    print(f'  عدد الفئات (شاملة الفرعية): {descendants.count()}')
    all_ads = ClassifiedAd.objects.filter(category__in=descendants, status='active').count()
    print(f'  إجمالي الإعلانات النشطة: {all_ads}')
    
    all_ads_any = ClassifiedAd.objects.filter(category__in=descendants).count()
    print(f'  إجمالي جميع الإعلانات: {all_ads_any}')
    
    print('\nالفئات الفرعية (أول 10):')
    for child in descendants[:10]:
        ads_count = ClassifiedAd.objects.filter(category=child, status='active').count()
        print(f'  - {child.name_ar} ({child.slug}) - {ads_count} إعلان')
else:
    print('✗ لم يتم العثور على الفئة')
