# نظام الإعلانات المدفوعة - دليل سريع
# Paid Advertisement System - Quick Start Guide

## ✅ ما تم إضافته | What Was Added

### 1. النموذج (Model)
✅ **PaidAdvertisement** - نموذج كامل للإعلانات المدفوعة في `main/models.py`

**الميزات:**
- استهداف الدولة (Country targeting)
- استهداف القسم/القسم الفرعي (Category/Subcategory targeting)
- دعم الصفحة الرئيسية (Homepage support)
- أقسام متعددة (Multiple categories)
- تتبع المشاهدات والنقرات (Views & Clicks tracking)
- الجدولة التلقائية (Auto scheduling)
- 4 أنواع إعلانات (4 ad types)

### 2. لوحة الإدارة (Admin Interface)
✅ **PaidAdvertisementAdmin** - واجهة إدارة متكاملة في `main/admin.py`

**الميزات:**
- عرض بصري للحالة والأنواع (Visual status badges)
- فلاتر متعددة (Multiple filters)
- بحث متقدم (Advanced search)
- إجراءات جماعية (Bulk actions)
- عرض الإحصائيات (Analytics display)

### 3. قوالب العرض (Display Templates)
✅ 3 قوالب جاهزة في `templates/components/paid_ads/`:
- **banner.html** - إعلان بانر كامل
- **sidebar.html** - إعلان جانبي
- **featured_box.html** - صندوق مميز

### 4. API Endpoints
✅ مسارات API في `main/urls.py`:
- `POST /api/paid-ads/<id>/view/` - تتبع المشاهدات
- `POST /api/paid-ads/<id>/click/` - تتبع النقرات
- `GET /api/paid-ads/category/<id>/` - الحصول على إعلانات القسم

### 5. Context Processor
✅ **paid_advertisements** - في `content/context_processors.py`

متغيرات متاحة في جميع القوالب:
- `homepage_paid_ads` - إعلانات الصفحة الرئيسية
- `sidebar_paid_ads` - إعلانات جانبية
- `banner_paid_ads` - إعلانات بانر

### 6. الوثائق (Documentation)
✅ **PAID_ADVERTISEMENT_SYSTEM.md** - وثائق شاملة بالعربي والإنجليزي

---

## 🚀 البدء السريع | Quick Start

### الخطوة 1: تطبيق الهجرة (Apply Migration)
```bash
source .venv/bin/activate
python manage.py migrate
```

### الخطوة 2: الوصول للوحة الإدارة (Access Admin)
```
URL: /admin/
القسم: الإعلانات المدفوعة (Paid Advertisements)
```

### الخطوة 3: إضافة أول إعلان (Add First Ad)
1. اضغط "إضافة إعلان مدفوع"
2. املأ المعلومات الأساسية
3. اختر نوع الموضع:
   - **عام (General)** → الصفحة الرئيسية
   - **قسم محدد (Category)** → اختر القسم
4. رفع صورة الإعلان
5. حدد التواريخ والأولوية
6. احفظ

### الخطوة 4: عرض في القالب (Display in Template)
```django
{# في أي قالب #}
{% for ad in homepage_paid_ads %}
    {% if ad.ad_type == 'banner' %}
        {% include 'components/paid_ads/banner.html' with ad=ad %}
    {% endif %}
{% endfor %}
```

---

## 📊 أمثلة الاستخدام | Usage Examples

### عرض في الصفحة الرئيسية | Homepage Display
```django
<!-- في templates/index.html -->
<section class="paid-ads-section">
    {% for ad in homepage_paid_ads %}
        {% if ad.ad_type == 'banner' %}
            {% include 'components/paid_ads/banner.html' with ad=ad %}
        {% endif %}
    {% endfor %}
</section>
```

### عرض في الشريط الجانبي | Sidebar Display
```django
<!-- في قالب الشريط الجانبي -->
<aside class="sidebar">
    <h4>إعلانات مميزة</h4>
    {% for ad in sidebar_paid_ads %}
        {% include 'components/paid_ads/sidebar.html' with ad=ad %}
    {% endfor %}
</aside>
```

### عرض في صفحة القسم | Category Page Display
```django
<!-- في صفحة القسم -->
{% if category %}
    {% for ad in category.paid_advertisements.all %}
        {% if ad.is_currently_active and ad.ad_type == 'featured_box' %}
            {% include 'components/paid_ads/featured_box.html' with ad=ad %}
        {% endif %}
    {% endfor %}
{% endif %}
```

---

## 🎯 حالات الاستخدام الشائعة | Common Use Cases

### 1. إعلان للصفحة الرئيسية فقط
```
Placement Type: General (عام)
Country: مصر (EG)
Ad Type: Banner
Priority: 10
```

### 2. إعلان لقسم الإلكترونيات
```
Placement Type: Category (قسم محدد)
Category: الإلكترونيات
Country: السعودية (SA)
Ad Type: Sidebar
```

### 3. إعلان لعدة أقسام
```
Placement Type: Category (قسم محدد)
Categories: (اختر عدة أقسام من القائمة المتعددة)
Country: مصر (EG)
Ad Type: Featured Box
```

### 4. إعلان مجدول
```
Start Date: 2026-04-10 00:00
End Date: 2026-05-10 23:59
Status: Active
Payment Status: Paid
```

---

## 📱 أنواع الإعلانات | Ad Types

| النوع | الاستخدام | الحجم الموصى به |
|------|----------|-----------------|
| **Banner** | عرض كامل أعلى/أسفل الصفحة | 1200×600px |
| **Sidebar** | إعلان جانبي صغير | 300×600px |
| **Featured Box** | إعلان مميز بتصميم خاص | 1200×800px |
| **Popup** | نافذة منبثقة (قيد التطوير) | 600×400px |

---

## 🔧 نصائح تقنية | Technical Tips

### 1. تحسين الأداء
```python
# استخدم select_related و prefetch_related
ads = PaidAdvertisement.objects.select_related(
    'country', 'category', 'advertiser'
).filter(
    is_active=True,
    status='active'
)
```

### 2. التحقق من النشاط
```python
# استخدم خاصية is_currently_active
if ad.is_currently_active:
    # عرض الإعلان
    pass
```

### 3. الحصول على إعلانات محددة
```python
# استخدم الـ class methods الجاهزة
homepage_ads = PaidAdvertisement.get_homepage_ads('EG')
category_ads = PaidAdvertisement.get_category_ads(category, 'SA')
```

---

## ⚠️ ملاحظات هامة | Important Notes

1. **الهجرة (Migration)**: يجب تطبيق الهجرة قبل الاستخدام
   ```bash
   python manage.py migrate
   ```

2. **Context Processor**: مضاف تلقائياً في `settings/common.py`

3. **الصور**: يجب رفع صور بالأحجام الموصى بها

4. **الأولوية**: الأرقام الأكبر = أولوية أعلى (100 > 10)

5. **التواريخ**: تأكد من تحديد start_date و end_date

6. **الحالة**: يجب أن تكون الحالة "Active" ومدفوع "Paid" للعرض

---

## 📖 المصادر | Resources

- **الوثائق الكاملة**: `docs/PAID_ADVERTISEMENT_SYSTEM.md`
- **الكود المصدري**:
  - Model: `main/models.py` (PaidAdvertisement)
  - Admin: `main/admin.py` (PaidAdvertisementAdmin)
  - Views: `main/paid_ad_views.py`
  - URLs: `main/urls.py`
  - Templates: `templates/components/paid_ads/`
  - Context Processor: `content/context_processors.py`

---

## ✨ الميزات المتقدمة | Advanced Features

### 1. تتبع تلقائي للمشاهدات والنقرات
```javascript
// التتبع يعمل تلقائياً عند استخدام القوالب الجاهزة
// يتم تسجيل المشاهدة عند تحميل الصفحة
// يتم تسجيل النقرة عند الضغط على الإعلان
```

### 2. معدل النقر (CTR)
```python
# يتم حسابه تلقائياً
ctr = ad.ctr  # (clicks / views) * 100
```

### 3. الموافقة الإدارية
```python
# موافقة الإدارة على الإعلان
ad.approve(admin_user=request.user)
```

### 4. الإيقاف والاستئناف
```python
# إيقاف مؤقت
ad.pause()

# استئناف
ad.resume()
```

---

## 🎨 التخصيص | Customization

يمكنك تخصيص تصميم القوالب في:
- `templates/components/paid_ads/banner.html`
- `templates/components/paid_ads/sidebar.html`
- `templates/components/paid_ads/featured_box.html`

كل قالب يحتوي على:
- ✅ CSS مخصص
- ✅ JavaScript للتتبع
- ✅ دعم الوضع الليلي (Dark Mode)
- ✅ تصميم متجاوب (Responsive)
- ✅ دعم RTL للعربية

---

## 🔄 التكامل مع الموقع | Site Integration

### الخطوة 1: إضافة في الصفحة الرئيسية
```django
<!-- في templates/index.html -->
<!-- بعد قسم البحث أو الـ Hero Section -->
<section class="container my-5">
    {% for ad in homepage_paid_ads %}
        {% if ad.ad_type == 'banner' %}
            {% include 'components/paid_ads/banner.html' with ad=ad %}
        {% endif %}
    {% endfor %}
</section>
```

### الخطوة 2: إضافة في صفحات الأقسام
```django
<!-- في templates/category_page.html -->
<!-- قبل قائمة الإعلانات -->
{% for ad in category.paid_advertisements.all %}
    {% if ad.is_currently_active %}
        {% include 'components/paid_ads/featured_box.html' with ad=ad %}
    {% endif %}
{% endfor %}
```

### الخطوة 3: إضافة في الشريط الجانبي
```django
<!-- في templates/base.html أو sidebar.html -->
<aside class="col-lg-3">
    {% for ad in sidebar_paid_ads %}
        {% include 'components/paid_ads/sidebar.html' with ad=ad %}
    {% endfor %}
</aside>
```

---

## 📞 الدعم | Support

للحصول على المساعدة:
1. راجع الوثائق الكاملة في `docs/PAID_ADVERTISEMENT_SYSTEM.md`
2. تحقق من أمثلة الكود المرفقة
3. استخدم لوحة الإدارة لإدارة الإعلانات

---

**تم بنجاح! ✅**
**Successfully Implemented! ✅**

Now you can:
- ✅ إضافة إعلانات مدفوعة (Add paid ads)
- ✅ استهداف دول وأقسام محددة (Target countries & categories)
- ✅ عرض إعلانات في الصفحة الرئيسية (Display on homepage)
- ✅ تتبع المشاهدات والنقرات (Track views & clicks)
- ✅ إدارة كاملة من لوحة الإدارة (Full admin management)

🎉 **Happy Advertising!** 🎉
