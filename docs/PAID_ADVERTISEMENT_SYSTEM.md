# نظام الإعلانات المدفوعة - Paid Advertisement System

## نظرة عامة | Overview

نظام الإعلانات المدفوعة يسمح لك بإضافة وإدارة إعلانات ترويجية مدفوعة يمكن عرضها على:
- **الصفحة الرئيسية** (عام - General)
- **صفحات الأقسام المحددة** (Category-specific)
- **صفحات الأقسام الفرعية** (Subcategory-specific)

The Paid Advertisement System allows you to add and manage promotional paid ads that can be displayed on:
- **Homepage** (General)
- **Specific Category Pages**
- **Specific Subcategory Pages**

---

## الميزات الرئيسية | Key Features

### 1. أنواع الإعلانات | Ad Types
- **بانر إعلاني (Banner)**: عرض كامل في أعلى/أسفل الصفحة
- **إعلان جانبي (Sidebar)**: إعلان جانبي صغير
- **نافذة منبثقة (Popup)**: نافذة منبثقة (قيد التطوير)
- **صندوق مميز (Featured Box)**: إعلان مميز بتصميم خاص

### 2. الاستهداف | Targeting
- **استهداف الدولة** (Country-specific)
- **الصفحة الرئيسية** (Homepage - General)
- **قسم محدد** (Specific Category)
- **قسم فرعي محدد** (Specific Subcategory)
- **أقسام متعددة** (Multiple Categories)

### 3. الإحصائيات | Analytics
- **عدد المشاهدات** (Views Count)
- **عدد النقرات** (Clicks Count)
- **معدل النقر إلى الظهور** (CTR - Click Through Rate)

### 4. الجدولة | Scheduling
- **تاريخ البدء** (Start Date)
- **تاريخ الانتهاء** (End Date)
- **التفعيل التلقائي** (Auto-activation)
- **الانتهاء التلقائي** (Auto-expiration)

---

## كيفية الإضافة | How to Add

### عبر لوحة الإدارة | Through Admin Panel

1. **انتقل إلى لوحة الإدارة**
   - URL: `/admin/`
   - القسم: **الإعلانات المدفوعة** (Paid Advertisements)

2. **اضغط على "إضافة إعلان مدفوع"**
   - Click "Add Paid Advertisement"

3. **املأ المعلومات الأساسية:**
   ```
   العنوان (Title): عنوان الإعلان
   العنوان بالعربية (Title AR): النسخة العربية
   الوصف (Description): وصف مختصر
   الحالة (Status): نشط/مسودة/منتهي
   ```

4. **معلومات المعلن:**
   ```
   المعلن (Advertiser): اختر المستخدم
   اسم الشركة (Company Name): اسم الشركة المعلنة
   بريد التواصل (Contact Email)
   هاتف التواصل (Contact Phone)
   ```

5. **المحتوى المرئي:**
   ```
   صورة الإعلان (Ad Image): 1200x600px موصى به للبانر
   صورة الموبايل (Mobile Image): اختياري للأجهزة المحمولة
   نوع الإعلان (Ad Type): بانر/جانبي/صندوق مميز
   ```

6. **الرابط والإجراء:**
   ```
   رابط الإعلان (Target URL): الرابط المستهدف
   نص زر الإجراء (CTA Text): "المزيد" / "اطلب الآن"
   فتح في تبويب جديد (Open in New Tab): نعم/لا
   ```

7. **الموضع والاستهداف:**
   ```
   نوع الموضع (Placement Type):
   - عام (General) → الصفحة الرئيسية
   - قسم محدد (Category) → اختر القسم
   - قسم فرعي (Subcategory) → اختر القسم الفرعي
   
   الدولة (Country): الدولة المستهدفة
   أقسام متعددة (Categories): اختر عدة أقسام (اختياري)
   ```

8. **الجدولة:**
   ```
   تاريخ البدء (Start Date): متى يبدأ العرض
   تاريخ الانتهاء (End Date): متى ينتهي العرض
   ```

9. **الأولوية والترتيب:**
   ```
   الأولوية (Priority): الرقم الأكبر = أولوية أعلى
   الترتيب (Order): ترتيب العرض
   ```

10. **التسعير والدفع:**
    ```
    السعر (Price): تكلفة الإعلان
    العملة (Currency): EGP/USD/SAR
    حالة الدفع (Payment Status): مدفوع/غير مدفوع
    مرجع الدفع (Payment Reference): رقم مرجع الدفع
    ```

---

## العرض في القوالب | Display in Templates

### 1. عرض في الصفحة الرئيسية | Homepage Display

```django
{% load static %}

<!-- Banner Ads -->
{% for ad in homepage_paid_ads %}
    {% if ad.ad_type == 'banner' %}
        {% include 'components/paid_ads/banner.html' with ad=ad %}
    {% endif %}
{% endfor %}

<!-- Featured Box -->
{% for ad in homepage_paid_ads %}
    {% if ad.ad_type == 'featured_box' %}
        {% include 'components/paid_ads/featured_box.html' with ad=ad %}
    {% endif %}
{% endfor %}
```

### 2. عرض في صفحات الأقسام | Category Pages

```django
{% load static %}

<!-- Get category-specific ads -->
{% if category %}
    {% for ad in category.paid_advertisements.all %}
        {% if ad.is_currently_active %}
            {% if ad.ad_type == 'banner' %}
                {% include 'components/paid_ads/banner.html' with ad=ad %}
            {% endif %}
        {% endif %}
    {% endfor %}
{% endif %}
```

### 3. عرض في الشريط الجانبي | Sidebar Display

```django
{% load static %}

<div class="sidebar">
    <!-- Sidebar Ads -->
    {% for ad in sidebar_paid_ads %}
        {% include 'components/paid_ads/sidebar.html' with ad=ad %}
    {% endfor %}
</div>
```

### 4. عرض يدوي بفلاتر مخصصة | Custom Display

```python
# في الـ View
from main.models import PaidAdvertisement

def my_view(request):
    # Get ads for specific category
    category = Category.objects.get(id=1)
    country_code = request.session.get('selected_country', 'EG')
    
    category_ads = PaidAdvertisement.get_category_ads(
        category=category,
        country_code=country_code
    )
    
    # Get homepage ads
    homepage_ads = PaidAdvertisement.get_homepage_ads(
        country_code=country_code
    )
    
    return render(request, 'template.html', {
        'category_ads': category_ads,
        'homepage_ads': homepage_ads,
    })
```

---

## API Endpoints

### 1. تتبع المشاهدات | Track Views
```bash
POST /api/paid-ads/<ad_id>/view/
```

**Response:**
```json
{
    "success": true,
    "views_count": 125
}
```

### 2. تتبع النقرات | Track Clicks
```bash
POST /api/paid-ads/<ad_id>/click/
```

**Response:**
```json
{
    "success": true,
    "clicks_count": 15,
    "ctr": 12.0
}
```

### 3. الحصول على إعلانات قسم محدد | Get Category Ads
```bash
GET /api/paid-ads/category/<category_id>/
```

**Response:**
```json
{
    "success": true,
    "ads": [
        {
            "id": 1,
            "title": "إعلان رائع",
            "image_url": "/media/paid_ads/2024/04/ad1.jpg",
            "target_url": "https://example.com",
            "ad_type": "banner",
            "cta_text": "اطلب الآن"
        }
    ],
    "count": 1
}
```

---

## استعلامات البرمجة | Programmatic Queries

### الحصول على إعلانات نشطة | Get Active Ads

```python
from main.models import PaidAdvertisement

# Get all active ads for a country
active_ads = PaidAdvertisement.get_active_ads(
    country_code='EG',
    placement_type=PaidAdvertisement.PlacementType.GENERAL
)

# Get homepage ads
homepage_ads = PaidAdvertisement.get_homepage_ads(country_code='SA')

# Get category-specific ads
from main.models import Category
category = Category.objects.get(slug='electronics')
category_ads = PaidAdvertisement.get_category_ads(category, 'EG')

# Check if ad is currently active
if ad.is_currently_active:
    print(f"Ad is active with {ad.days_remaining} days remaining")

# Get CTR (Click Through Rate)
print(f"CTR: {ad.ctr}%")
```

### تحديث الإحصائيات | Update Analytics

```python
# Increment views
ad.increment_views()

# Increment clicks
ad.increment_clicks()

# Get current stats
print(f"Views: {ad.views_count}")
print(f"Clicks: {ad.clicks_count}")
print(f"CTR: {ad.ctr}%")
```

### الموافقة والتحكم | Approval & Control

```python
# Approve ad
ad.approve(admin_user=request.user)

# Pause ad
ad.pause()

# Resume ad
ad.resume()
```

---

## إجراءات الإدارة | Admin Actions

من لوحة الإدارة، يمكنك تنفيذ الإجراءات التالية على الإعلانات المحددة:

1. **الموافقة على الإعلانات** (Approve Ads)
2. **إيقاف الإعلانات مؤقتاً** (Pause Ads)
3. **استئناف الإعلانات** (Resume Ads)
4. **تحديد كمدفوع** (Mark as Paid)
5. **تحديد كمنتهي** (Mark as Expired)

---

## الفلاتر والبحث | Filters & Search

### في لوحة الإدارة:

**فلاتر متاحة:**
- الحالة (Status)
- حالة الدفع (Payment Status)
- نوع الإعلان (Ad Type)
- نوع الموضع (Placement Type)
- الدولة (Country)
- نشط/غير نشط (Active/Inactive)
- تاريخ البدء/الانتهاء (Start/End Date)

**البحث:**
- العنوان (Title)
- الوصف (Description)
- اسم الشركة (Company Name)
- اسم/بريد المعلن (Advertiser Username/Email)

---

## أمثلة عملية | Practical Examples

### مثال 1: إعلان بانر للصفحة الرئيسية

```python
ad = PaidAdvertisement.objects.create(
    title="عرض خاص لفترة محدودة",
    title_ar="عرض خاص لفترة محدودة",
    description="احصل على خصم 50% على جميع المنتجات",
    advertiser=user,
    company_name="متجر الإلكترونيات",
    image="path/to/banner.jpg",
    target_url="https://mystore.com/sale",
    cta_text="اشتري الآن",
    ad_type=PaidAdvertisement.AdType.BANNER,
    placement_type=PaidAdvertisement.PlacementType.GENERAL,
    country=Country.objects.get(code='EG'),
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=30),
    price=500.00,
    currency='EGP',
    priority=10,
    order=1,
    status=PaidAdvertisement.Status.ACTIVE,
    payment_status='paid',
)
```

### مثال 2: إعلان جانبي لقسم محدد

```python
electronics_category = Category.objects.get(slug='electronics')

ad = PaidAdvertisement.objects.create(
    title="أحدث الهواتف الذكية",
    title_ar="أحدث الهواتف الذكية",
    advertiser=user,
    company_name="موبايل شوب",
    image="path/to/sidebar_ad.jpg",
    target_url="https://mobileshop.com",
    ad_type=PaidAdvertisement.AdType.SIDEBAR,
    placement_type=PaidAdvertisement.PlacementType.CATEGORY,
    category=electronics_category,
    country=Country.objects.get(code='SA'),
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=14),
    price=200.00,
    currency='SAR',
    status=PaidAdvertisement.Status.ACTIVE,
    payment_status='paid',
)
```

### مثال 3: إعلان لعدة أقسام

```python
ad = PaidAdvertisement.objects.create(
    title="خدمة التوصيل السريع",
    title_ar="خدمة التوصيل السريع",
    advertiser=user,
    company_name="شركة التوصيل",
    image="path/to/featured_box.jpg",
    target_url="https://delivery.com",
    ad_type=PaidAdvertisement.AdType.FEATURED_BOX,
    placement_type=PaidAdvertisement.PlacementType.CATEGORY,
    country=Country.objects.get(code='EG'),
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=60),
    price=1000.00,
    currency='EGP',
    priority=20,
    status=PaidAdvertisement.Status.ACTIVE,
    payment_status='paid',
)

# Add to multiple categories
electronics = Category.objects.get(slug='electronics')
furniture = Category.objects.get(slug='furniture')
clothing = Category.objects.get(slug='clothing')

ad.categories.add(electronics, furniture, clothing)
ad.save()
```

---

## الأحجام الموصى بها للصور | Recommended Image Sizes

- **بانر (Banner)**: 1200 × 600 بكسل
- **بانر موبايل (Mobile Banner)**: 800 × 600 بكسل
- **جانبي (Sidebar)**: 300 × 600 بكسل
- **صندوق مميز (Featured Box)**: 1200 × 800 بكسل

---

## الحالات والأولويات | Status & Priority

### الحالات (Status):
- **مسودة (Draft)**: الإعلان قيد التحضير
- **نشط (Active)**: الإعلان يعرض حالياً
- **متوقف مؤقتاً (Paused)**: الإعلان متوقف مؤقتاً
- **منتهي (Expired)**: الإعلان انتهت صلاحيته
- **قيد المراجعة (Pending)**: بانتظار موافقة الإدارة

### الأولوية (Priority):
- الأرقام الأكبر = أولوية أعلى
- مثال: Priority 100 يظهر قبل Priority 10

---

## الدعم الفني | Technical Support

لأي استفسارات أو مشاكل تقنية، يرجى التواصل مع فريق الدعم الفني.

For any inquiries or technical issues, please contact the technical support team.

---

## الملاحظات الهامة | Important Notes

1. ✅ **التحقق من المحتوى**: يجب مراجعة جميع الإعلانات قبل الموافقة عليها
2. ✅ **الأحجام المناسبة**: استخدم الأحجام الموصى بها للصور
3. ✅ **الاستهداف الدقيق**: اختر الموضع المناسب لجمهورك المستهدف
4. ✅ **المتابعة**: راقب الإحصائيات بانتظام لتحسين الأداء
5. ✅ **التاريخ**: تأكد من تحديد تواريخ البدء والانتهاء بشكل صحيح

---

تم إنشاء هذا النظام بواسطة GitHub Copilot 🚀
Created by GitHub Copilot 🚀
