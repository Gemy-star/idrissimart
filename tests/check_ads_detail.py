from main.models import Category, ClassifiedAd
from django.utils import timezone

slug = 'إعلانات-مبوبة'
cat = Category.objects.filter(slug=slug).first()

if cat:
    print(f'الفئة: {cat.name_ar} (ID: {cat.id})')
    descendants = cat.get_descendants(include_self=True)
    print(f'عدد الفئات الفرعية: {descendants.count()}')
    
    # جميع الإعلانات
    all_ads = ClassifiedAd.objects.filter(category__in=descendants)
    print(f'\nجميع الإعلانات: {all_ads.count()}')
    
    # الإعلانات النشطة
    active_ads = all_ads.filter(status='active')
    print(f'الإعلانات النشطة: {active_ads.count()}')
    
    # الإعلانات حسب الدولة
    print('\nالإعلانات حسب الدولة:')
    for country_code in ['EG', 'SA', 'AE', 'MA']:
        count = active_ads.filter(country__code=country_code).count()
        if count > 0:
            print(f'  {country_code}: {count} إعلان')
    
    # الإعلانات بدون دولة
    no_country = active_ads.filter(country__isnull=True).count()
    print(f'  بدون دولة: {no_country} إعلان')
    
    # عرض أول 5 إعلانات
    print('\nأول 5 إعلانات نشطة:')
    for ad in active_ads[:5]:
        country = ad.country.code if ad.country else 'None'
        print(f'  - {ad.title[:50]} | Country: {country} | Status: {ad.status}')
