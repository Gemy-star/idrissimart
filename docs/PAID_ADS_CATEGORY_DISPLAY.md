# عرض الإعلانات المدفوعة في صفحات الأقسام
# Display Paid Ads in Category/Subcategory Pages

## ✅ التحديثات | Updates Applied

تم تحديث **CategoryDetailView** و **SubcategoryDetailView** في `main/views.py` لتضمين الإعلانات المدفوعة المرتبطة بكل قسم.

**CategoryDetailView** and **SubcategoryDetailView** in `main/views.py` have been updated to include paid advertisements linked to each category.

---

## 📊 المتغيرات المتاحة | Available Variables

في قوالب صفحات الأقسام، أصبح لديك الآن:
In category page templates, you now have:

```python
category_paid_ads  # Paid advertisements for this specific category/subcategory
```

---

## 🎨 كيفية العرض | How to Display

### 1. في صفحة القسم (Category Detail Page)

في `templates/pages/category_detail.html`:

#### مثال: عرض بانر بعد العنوان الرئيسي
```django
{% extends 'base.html' %}
{% load static i18n %}

{% block content %}
    <!-- Hero Section -->
    <section class="categories-hero">
        <div class="container">
            <h1 class="hero-title">{{ category.name }}</h1>
        </div>
    </section>

    <!-- Paid Advertisement Banner -->
    {% if category_paid_ads %}
        <div class="container my-4">
            {% for ad in category_paid_ads %}
                {% if ad.ad_type == 'banner' %}
                    {% include 'components/paid_ads/banner.html' with ad=ad %}
                {% endif %}
            {% endfor %}
        </div>
    {% endif %}

    <!-- Category Content -->
    <div class="container">
        <!-- Your existing category content -->
    </div>
{% endblock %}
```

#### مثال: عرض Featured Box قبل قائمة الإعلانات
```django
<!-- After filters, before ads listing -->
<div class="container my-5">
    <!-- Paid Featured Box Ads -->
    {% for ad in category_paid_ads %}
        {% if ad.ad_type == 'featured_box' %}
            {% include 'components/paid_ads/featured_box.html' with ad=ad %}
        {% endif %}
    {% endfor %}
</div>

<!-- Ads listing -->
<div class="ads-grid">
    {% for ad in ads %}
        <!-- Regular classified ads -->
    {% endfor %}
</div>
```

### 2. في الشريط الجانبي (Sidebar)

```django
<!-- Sidebar -->
<aside class="col-lg-3">
    <!-- Filters -->
    <div class="filters-section">
        <!-- Your filters -->
    </div>

    <!-- Paid Sidebar Ads -->
    <div class="sidebar-ads-section mt-4">
        <h5 class="mb-3">{% trans "إعلانات مميزة" %}</h5>
        {% for ad in category_paid_ads %}
            {% if ad.ad_type == 'sidebar' %}
                {% include 'components/paid_ads/sidebar.html' with ad=ad %}
            {% endif %}
        {% endfor %}
    </div>
</aside>
```

### 3. بين الإعلانات (Between Classified Ads)

```django
<div class="ads-grid row">
    {% for ad in ads %}
        <!-- Regular ad -->
        <div class="col-md-4">
            {% include 'components/ad_card.html' with ad=ad %}
        </div>

        <!-- Insert paid ad after every 6 regular ads -->
        {% if forloop.counter|divisibleby:6 and category_paid_ads %}
            <div class="col-12 my-3">
                {% with ad_index=forloop.counter0|add:1|floatformat:0|add:1 %}
                    {% if category_paid_ads|length >= ad_index %}
                        {% with paid_ad=category_paid_ads|slice:ad_index|first %}
                            {% if paid_ad.ad_type == 'banner' %}
                                {% include 'components/paid_ads/banner.html' with ad=paid_ad %}
                            {% endif %}
                        {% endwith %}
                    {% endif %}
                {% endwith %}
            </div>
        {% endif %}
    {% endfor %}
</div>
```

---

## 📍 مواضع العرض الموصى بها | Recommended Placements

### صفحة القسم (Category Page)

```
┌─────────────────────────────────────┐
│         Hero Section                │
│        (Category Name)              │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│    PAID AD: Banner (Type 1)         │  ← بعد Hero مباشرة
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│      Subcategories Grid             │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  PAID AD: Featured Box (Type 2)     │  ← قبل الإعلانات
└─────────────────────────────────────┘
            ↓
┌───────────────────┬─────────────────┐
│   Filters         │  Ads Grid       │
│   Sidebar         │                 │
│   ┌─────────┐     │  [Ad] [Ad] [Ad]│
│   │ PAID AD │     │  [Ad] [Ad] [Ad]│  ← إعلانات عادية
│   │ Sidebar │     │  [Ad] [Ad] [Ad]│
│   └─────────┘     │                 │
└───────────────────┴─────────────────┘
```

---

## 🎯 أمثلة حسب نوع الإعلان | Examples by Ad Type

### 1. عرض البانرات فقط (Banners Only)
```django
{% if category_paid_ads %}
    <section class="paid-ads-section container my-4">
        {% for ad in category_paid_ads %}
            {% if ad.ad_type == 'banner' %}
                {% include 'components/paid_ads/banner.html' with ad=ad %}
            {% endif %}
        {% endfor %}
    </section>
{% endif %}
```

### 2. عرض الصناديق المميزة فقط (Featured Boxes Only)
```django
{% if category_paid_ads %}
    <section class="featured-ads-section container my-5">
        <div class="row">
            {% for ad in category_paid_ads %}
                {% if ad.ad_type == 'featured_box' %}
                    <div class="col-12 mb-4">
                        {% include 'components/paid_ads/featured_box.html' with ad=ad %}
                    </div>
                {% endif %}
            {% endfor %}
        </div>
    </section>
{% endif %}
```

### 3. عرض جميع الأنواع (All Types)
```django
{% if category_paid_ads %}
    <!-- Banners at top -->
    <div class="container my-4">
        {% for ad in category_paid_ads %}
            {% if ad.ad_type == 'banner' %}
                {% include 'components/paid_ads/banner.html' with ad=ad %}
            {% endif %}
        {% endfor %}
    </div>

    <!-- Featured boxes in middle -->
    <div class="container my-5">
        {% for ad in category_paid_ads %}
            {% if ad.ad_type == 'featured_box' %}
                {% include 'components/paid_ads/featured_box.html' with ad=ad %}
            {% endif %}
        {% endfor %}
    </div>

    <!-- Sidebar ads in sidebar (if applicable) -->
    {% for ad in category_paid_ads %}
        {% if ad.ad_type == 'sidebar' %}
            {% include 'components/paid_ads/sidebar.html' with ad=ad %}
        {% endif %}
    {% endfor %}
{% endif %}
```

---

## 🔄 عرض ديناميكي حسب الأولوية | Dynamic Display by Priority

الإعلانات مرتبة تلقائياً حسب الأولوية (priority) والترتيب (order):

```django
<!-- Display only top 3 highest priority ads -->
{% with top_ads=category_paid_ads|slice:":3" %}
    {% for ad in top_ads %}
        {% if ad.ad_type == 'banner' %}
            {% include 'components/paid_ads/banner.html' with ad=ad %}
        {% endif %}
    {% endfor %}
{% endwith %}
```

---

## 🎨 تخصيص العرض | Custom Styling

### إضافة تصميم خاص لمنطقة الإعلانات المدفوعة
```django
<style>
    .category-paid-ads-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        padding: 2rem 0;
        margin: 3rem 0;
    }

    [data-theme='dark'] .category-paid-ads-section {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }

    .paid-ad-label {
        text-align: center;
        color: #6c757d;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
</style>

<section class="category-paid-ads-section">
    <div class="container">
        <p class="paid-ad-label">{% trans "إعلانات مميزة" %}</p>
        {% for ad in category_paid_ads %}
            {% if ad.ad_type == 'featured_box' %}
                {% include 'components/paid_ads/featured_box.html' with ad=ad %}
            {% endif %}
        {% endfor %}
    </div>
</section>
```

---

## 🔍 فلترة الإعلانات | Filtering Ads

### عرض إعلان واحد فقط (أعلى أولوية)
```django
{% with top_ad=category_paid_ads|first %}
    {% if top_ad %}
        {% include 'components/paid_ads/featured_box.html' with ad=top_ad %}
    {% endif %}
{% endwith %}
```

### عرض إعلانات البانر فقط (أول 2)
```django
{% for ad in category_paid_ads %}
    {% if ad.ad_type == 'banner' and forloop.counter <= 2 %}
        {% include 'components/paid_ads/banner.html' with ad=ad %}
    {% endif %}
{% endfor %}
```

---

## 📱 عرض متجاوب | Responsive Display

```django
<!-- Desktop: Banner -->
<div class="d-none d-md-block">
    {% for ad in category_paid_ads %}
        {% if ad.ad_type == 'banner' %}
            {% include 'components/paid_ads/banner.html' with ad=ad %}
        {% endif %}
    {% endfor %}
</div>

<!-- Mobile: Featured Box (more compact) -->
<div class="d-block d-md-none">
    {% for ad in category_paid_ads %}
        {% if ad.ad_type == 'featured_box' %}
            {% include 'components/paid_ads/featured_box.html' with ad=ad %}
        {% endif %}
    {% endfor %}
</div>
```

---

## ⚙️ كيف يعمل النظام | How It Works

### في الـ Views (تم التطبيق تلقائياً)

```python
# CategoryDetailView.get_context_data()
# SubcategoryDetailView.get_context_data()

from main.models import PaidAdvertisement

# Get paid ads for this specific category
category_paid_ads = PaidAdvertisement.get_category_ads(
    category=self.category,  # Current category/subcategory
    country_code=selected_country
)

# Add to context
context['category_paid_ads'] = category_paid_ads
```

### ما يتم إرجاعه | What Gets Returned

```python
# Filtered automatically by:
- is_active=True
- status='active'
- start_date <= now <= end_date
- country matches selected country
- category matches current category OR is in categories (ManyToMany)
- placement_type='category' or 'subcategory'

# Ordered by:
- priority (DESC) - higher priority first
- order (ASC) - lower order number first
```

---

## 💡 نصائح مهمة | Important Tips

### 1. تحقق من وجود الإعلانات أولاً
```django
{% if category_paid_ads %}
    <!-- Display ads -->
{% endif %}
```

### 2. استخدم الأنواع المناسبة
- **Banner**: مناسب لأعلى/أسفل الصفحة
- **Featured Box**: مناسب بين المحتوى
- **Sidebar**: مناسب للشريط الجانبي

### 3. لا تعرض كل الإعلانات دفعة واحدة
```django
<!-- Good: Display top 2-3 ads -->
{% for ad in category_paid_ads|slice:":3" %}
    ...
{% endfor %}

<!-- Avoid: Displaying all ads at once -->
```

### 4. احترم تجربة المستخدم
- لا تضع أكثر من بانر واحد في الأعلى
- اترك مساحة كافية بين الإعلانات والمحتوى
- تأكد من التصميم المتجاوب

---

## 📋 Checklist للتطبيق | Implementation Checklist

- [x] تحديث Views (تم تلقائياً)
- [ ] إضافة الإعلانات في `category_detail.html`
- [ ] إضافة الإعلانات في قالب الأقسام الفرعية
- [ ] اختبار العرض على Desktop
- [ ] اختبار العرض على Mobile
- [ ] إضافة إعلانات تجريبية من لوحة الإدارة
- [ ] تحديد placement_type = "category"
- [ ] تحديد category المناسب
- [ ] اختيار ad_type المناسب

---

## 🎯 مثال كامل | Complete Example

```django
{% extends 'base.html' %}
{% load static i18n %}

{% block content %}
<!-- Hero Section -->
<section class="categories-hero">
    <div class="container">
        <h1>{{ category.name }}</h1>
    </div>
</section>

<!-- PAID AD: Top Banner -->
{% if category_paid_ads %}
    <div class="container my-4">
        {% with top_banner=category_paid_ads|first %}
            {% if top_banner and top_banner.ad_type == 'banner' %}
                {% include 'components/paid_ads/banner.html' with ad=top_banner %}
            {% endif %}
        {% endwith %}
    </div>
{% endif %}

<!-- Main Content -->
<div class="container my-5">
    <div class="row">
        <!-- Sidebar -->
        <aside class="col-lg-3">
            <!-- Filters -->
            <div class="filters">...</div>
            
            <!-- PAID AD: Sidebar -->
            {% for ad in category_paid_ads %}
                {% if ad.ad_type == 'sidebar' %}
                    <div class="my-3">
                        {% include 'components/paid_ads/sidebar.html' with ad=ad %}
                    </div>
                {% endif %}
            {% endfor %}
        </aside>

        <!-- Main Content -->
        <main class="col-lg-9">
            <!-- PAID AD: Featured Box -->
            {% for ad in category_paid_ads %}
                {% if ad.ad_type == 'featured_box' %}
                    <div class="mb-4">
                        {% include 'components/paid_ads/featured_box.html' with ad=ad %}
                    </div>
                {% endif %}
            {% endfor %}

            <!-- Classified Ads Grid -->
            <div class="ads-grid row">
                {% for ad in ads %}
                    <div class="col-md-4">
                        <!-- Regular ad -->
                    </div>
                {% endfor %}
            </div>
        </main>
    </div>
</div>
{% endblock %}
```

---

## 🚀 الخطوات التالية | Next Steps

1. **أضف الإعلانات في القوالب** باستخدام الأمثلة أعلاه
2. **أنشئ إعلان تجريبي** من `/admin/`
3. **اختبر العرض** في صفحة قسم محدد
4. **راجع المظهر** على Desktop و Mobile
5. **اضبط التصميم** حسب احتياجاتك

---

✅ **الآن يمكنك عرض الإعلانات المدفوعة في صفحات الأقسام!**
✅ **Now you can display paid advertisements on category pages!**
