# Fix Arabic Slugs - Management Command

## الوصف / Description

أمر إدارة Django لإصلاح جميع الـ slugs للفئات (Categories) والإعلانات المبوبة (ClassifiedAds) بحيث تدعم اللغة العربية بشكل صحيح وتعمل الفلترة كما ينبغي.

This Django management command fixes all slugs for Categories and ClassifiedAds to properly support Arabic text and enable correct filtering.

## الميزات / Features

- ✅ إصلاح slugs للفئات من الاسم العربي
- ✅ إصلاح slugs للإعلانات من العنوان
- ✅ دعم كامل للنصوص العربية في الـ URLs
- ✅ التأكد من عدم تكرار الـ slugs
- ✅ معالجة الـ slug_ar للفئات أيضاً
- ✅ وضع Dry Run للمعاينة قبل التنفيذ
- ✅ خيارات لإصلاح الفئات فقط أو الإعلانات فقط
- ✅ معالجة دفعية (batch processing) للأداء الأفضل

## الاستخدام / Usage

### 1. إصلاح كل شيء (الفئات والإعلانات)
```bash
python manage.py fix_arabic_slugs
```

### 2. معاينة التغييرات قبل التنفيذ (Dry Run)
```bash
python manage.py fix_arabic_slugs --dry-run
```

### 3. إصلاح الفئات فقط
```bash
python manage.py fix_arabic_slugs --categories-only
```

### 4. إصلاح الإعلانات فقط
```bash
python manage.py fix_arabic_slugs --ads-only
```

### 5. معاينة الفئات فقط
```bash
python manage.py fix_arabic_slugs --categories-only --dry-run
```

## الخيارات / Options

| Option | Description |
|--------|-------------|
| `--dry-run` | معاينة التغييرات بدون حفظها / Preview changes without saving |
| `--categories-only` | إصلاح الفئات فقط / Only fix categories |
| `--ads-only` | إصلاح الإعلانات فقط / Only fix ads |

## مثال على المخرجات / Output Example

```
======================================================================
📁 FIXING CATEGORY SLUGS
======================================================================

Found 25 categories to process

✓ الوظائف المساندة
  Old: support-jobs → New: الوظائف-المساندة
  Arabic slug: support-jobs-ar → الوظائف-المساندة

✓ الخدمات المساندة
  Old: support-services → New: الخدمات-المساندة

📊 Category Results: 23 fixed, 2 already correct

======================================================================
📢 FIXING CLASSIFIED AD SLUGS
======================================================================

Found 150 classified ads to process

✓ إعلان عن وظيفة مهندس مساحة...
  Old: job-surveyor → New: إعلان-عن-وظيفة-مهندس-مساحة

  Progress: 100/150 ads...

📊 Classified Ad Results: 145 fixed, 5 already correct

✅ All slugs have been fixed successfully!
```

## ملاحظات هامة / Important Notes

1. **النسخ الاحتياطي**: يُنصح بعمل نسخة احتياطية من قاعدة البيانات قبل التشغيل
2. **وضع Dry Run**: استخدم `--dry-run` أولاً للتأكد من النتائج
3. **الأداء**: الأمر يعالج الإعلانات دفعياً (100 إعلان في كل دفعة) لتحسين الأداء
4. **التفرد**: الأمر يتأكد من عدم تكرار الـ slugs تلقائياً بإضافة أرقام عند الحاجة
5. **الترميز**: يستخدم `allow_unicode=True` لدعم الأحرف العربية في الـ URLs

## كيف يعمل / How It Works

1. **للفئات**:
   - يستخدم `name_ar` إذا كان موجوداً، وإلا يستخدم `name`
   - يُحدّث `slug` و `slug_ar` إذا كانا موجودين
   - يعالج الفئات حسب مستواها في الشجرة

2. **للإعلانات**:
   - يستخدم `title` لتوليد الـ slug
   - يعالج الإعلانات دفعياً (100 إعلان في كل دفعة)
   - يعرض عينة من التغييرات لتجنب إغراق المخرجات

3. **ضمان التفرد**:
   - عند تكرار slug، يضيف رقماً (`-1`, `-2`, etc.)
   - يتحقق من عدم التعارض مع slugs موجودة

## متى تستخدم هذا الأمر / When To Use

- ✅ بعد استيراد بيانات جديدة
- ✅ عند تغيير نظام الـ slugs
- ✅ عند وجود مشاكل في الفلترة حسب الفئة
- ✅ عند ترقية النظام لدعم الأحرف العربية في URLs
- ✅ عند ظهور أخطاء 404 في روابط الفئات أو الإعلانات

## استكشاف الأخطاء / Troubleshooting

### المشكلة: "No categories found"
**الحل**: تأكد من وجود فئات في قاعدة البيانات

### المشكلة: slugs لا تزال بالإنجليزية
**الحل**: تأكد من وجود حقل `name_ar` مملوء للفئات

### المشكلة: أخطاء في التفرد
**الحل**: الأمر يعالج هذا تلقائياً بإضافة أرقام

## الأداء / Performance

- معالجة ~1000 فئة: **< 30 ثانية**
- معالجة ~10,000 إعلان: **< 5 دقائق**
- يستخدم معاملات (transactions) لضمان سلامة البيانات

## Related Files

- `main/models.py` - نماذج Category و ClassifiedAd
- `main/views.py` - Views التي تستخدم الفلترة بالـ slug
- `templates/pages/categories.html` - صفحة الفئات

## الدعم / Support

إذا واجهت أي مشاكل، تحقق من:
1. السجلات (logs)
2. إعدادات Django للغة
3. تكوين قاعدة البيانات (charset UTF-8)
