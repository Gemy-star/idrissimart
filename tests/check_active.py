from main.models import Category

cat = Category.objects.filter(slug='إعلانات-مبوبة').first()
if cat:
    print(f'الفئة: {cat.name_ar}')
    print(f'  is_active: {cat.is_active}')
    print(f'  ID: {cat.id}')
    
    print('\nالفئات الفرعية:')
    for child in cat.get_descendants(include_self=True):
        print(f'  - {child.name_ar}: is_active={child.is_active}')
