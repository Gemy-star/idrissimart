# نظام تسعير المميزات حسب الباقة
## Package-Based Feature Pricing System

## المشكلة | Problem

كانت أسعار مميزات الإعلان (تمييز، عاجل، تثبيت، تواصل للسعر) **ثابتة** من إعدادات الموقع (`SiteConfiguration`)، بغض النظر عن الباقة التي يستخدمها المستخدم.

Feature prices (highlighted, urgent, pinned, contact_for_price) were **fixed** from site settings (`SiteConfiguration`), regardless of which package the user is using.

## الحل | Solution

الآن أسعار المميزات **مرتبطة بالباقة** - كل باقة لها أسعارها الخاصة للمميزات.

Now feature prices are **package-specific** - each package has its own prices for features.

---

## كيف يعمل النظام | How It Works

### 1. حقول الأسعار في AdPackage Model

```python
class AdPackage(models.Model):
    # ... other fields ...

    # أسعار تمييز الإعلان (Feature Prices)
    feature_pinned_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر التثبيت"),
        help_text=_("سعر إضافي لتثبيت الإعلان"),
    )
    feature_urgent_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر العاجل"),
        help_text=_("سعر إضافي لجعل الإعلان عاجل"),
    )
    feature_highlighted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر التمييز"),
        help_text=_("سعر إضافي لتمييز الإعلان"),
    )
    feature_contact_for_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر ميزة 'تواصل ليصلك عرض سعر'"),
        help_text=_("سعر إضافي لإخفاء السعر وعرض زر 'تواصل ليصلك عرض سعر'"),
    )
```

**الفائدة:**
- كل باقة يمكن أن يكون لها أسعار مختلفة
- الباقات الأغلى يمكن أن توفر مميزات أرخص (أو مجانية)
- الباقات الأرخص يمكن أن تفرض أسعار أعلى للمميزات

---

## التغييرات في الكود | Code Changes

### 1. ClassifiedAdCreateView.get_context_data()

**القديم (Old):**
```python
context["site_config"] = SiteConfiguration.get_solo()
return context
```

**الجديد (New):**
```python
context["site_config"] = SiteConfiguration.get_solo()

# Get user's active package to determine feature prices
if self.request.user.is_authenticated:
    active_package = (
        UserPackage.objects.filter(
            user=self.request.user,
            expiry_date__gte=timezone.now(),
        )
        .order_by("expiry_date")
        .first()
    )

    # Pass feature prices based on package or site defaults
    if active_package and active_package.package:
        package = active_package.package
        context["feature_prices"] = {
            "highlighted": package.feature_highlighted_price,
            "urgent": package.feature_urgent_price,
            "pinned": package.feature_pinned_price,
            "contact_for_price": package.feature_contact_for_price,
        }
        context["pricing_source"] = "package"
        context["active_package"] = active_package
    else:
        # Use site default prices
        context["feature_prices"] = {
            "highlighted": context["site_config"].featured_ad_price,
            "urgent": context["site_config"].urgent_ad_price,
            "pinned": context["site_config"].pinned_ad_price,
            "contact_for_price": 0,  # Free or unavailable without package
        }
        context["pricing_source"] = "site_default"

return context
```

**الفوائد:**
- القالب يحصل على الأسعار الصحيحة حسب باقة المستخدم
- إذا لم يكن لدى المستخدم باقة، يتم استخدام أسعار الموقع الافتراضية
- سهل التتبع: `pricing_source` يخبرك ما إذا كانت الأسعار من الباقة أو الإعدادات

---

### 2. ClassifiedAdCreateView.form_valid()

**القديم (Old):**
```python
# Calculate features cost
features_cost = Decimal("0.00")
if feature_highlighted:
    features_cost += Decimal(str(site_config.featured_ad_price))
if feature_urgent:
    features_cost += Decimal(str(site_config.urgent_ad_price))
if feature_pinned:
    features_cost += Decimal(str(site_config.pinned_ad_price))
# ... contact_for_price with separate query ...

# Check if user has free ads in package
active_package = UserPackage.objects.filter(...)  # Query again!
```

**الجديد (New):**
```python
# Check if user has active package (for both pricing and free ads check)
active_package = (
    UserPackage.objects.filter(
        user=self.request.user,
        expiry_date__gte=timezone.now(),
    )
    .order_by("expiry_date")
    .first()
)

# Calculate features cost based on package-specific pricing
features_cost = Decimal("0.00")

# Determine which pricing to use (package or site default)
if active_package and active_package.package:
    # Use package-specific pricing
    package = active_package.package
    if feature_highlighted:
        features_cost += Decimal(str(package.feature_highlighted_price))
    if feature_urgent:
        features_cost += Decimal(str(package.feature_urgent_price))
    if feature_pinned:
        features_cost += Decimal(str(package.feature_pinned_price))
    if feature_contact_for_price:
        features_cost += Decimal(str(package.feature_contact_for_price))
else:
    # User has no package, use site default pricing
    if feature_highlighted:
        features_cost += Decimal(str(site_config.featured_ad_price))
    if feature_urgent:
        features_cost += Decimal(str(site_config.urgent_ad_price))
    if feature_pinned:
        features_cost += Decimal(str(site_config.pinned_ad_price))
    if feature_contact_for_price:
        features_cost += Decimal("0.00")  # Free for non-package users

# Determine base fee (publishing cost)
base_fee = Decimal("0.00")
# Check if user has free ads remaining in package
if not active_package or active_package.ads_remaining <= 0:
    # No package or no ads remaining, user must pay base fee
    base_fee = Decimal(str(site_config.ad_base_fee))
```

**التحسينات:**
- ✅ استعلام واحد للباقة النشطة (بدلاً من اثنين)
- ✅ استخدام أسعار الباقة إذا كانت متاحة
- ✅ الرجوع إلى أسعار الموقع إذا لم يكن لدى المستخدم باقة
- ✅ كود أنظف وأسهل للصيانة

---

### 3. Template Updates (ad_form.html)

**القديم (Old):**
```html
<div class="card h-100 feature-card" data-feature="highlighted"
     data-price="{{ site_config.featured_ad_price|default:'50' }}">
    <!-- ... -->
    <span class="badge bg-primary feature-price">
        {{ site_config.featured_ad_price|default:'50' }} ج.م
    </span>
</div>
```

**الجديد (New):**
```html
<div class="card h-100 feature-card" data-feature="highlighted"
     data-price="{{ feature_prices.highlighted|default:'50' }}">
    <!-- ... -->
    <span class="badge bg-primary feature-price">
        {{ feature_prices.highlighted|default:'50' }} ج.م
    </span>
</div>
```

**في JavaScript:**

**القديم:**
```javascript
const featuredPrice = parseFloat('{{ site_config.featured_ad_price|default:"50" }}');
const urgentPrice = parseFloat('{{ site_config.urgent_ad_price|default:"30" }}');
const pinnedPrice = parseFloat('{{ site_config.pinned_ad_price|default:"100" }}');
```

**الجديد:**
```javascript
const featuredPrice = parseFloat('{{ feature_prices.highlighted|default:"50" }}');
const urgentPrice = parseFloat('{{ feature_prices.urgent|default:"30" }}');
const pinnedPrice = parseFloat('{{ feature_prices.pinned|default:"100" }}');
```

---

## أمثلة الاستخدام | Usage Examples

### مثال 1: باقة مجانية (Free Package)

```python
free_package = AdPackage.objects.create(
    name="باقة مجانية",
    price=0,
    ad_count=3,
    duration_days=30,

    # أسعار المميزات (Features are expensive)
    feature_highlighted_price=100,  # غالي
    feature_urgent_price=75,        # غالي
    feature_pinned_price=150,       # غالي جداً
    feature_contact_for_price=50,   # متوسط
)
```

**السيناريو:**
```
User: لديه الباقة المجانية
User: يريد نشر إعلان مع تمييز (highlighted)
System: السعر = 100 ج.م (من الباقة)
```

---

### مثال 2: باقة قياسية (Standard Package)

```python
standard_package = AdPackage.objects.create(
    name="باقة قياسية",
    price=200,
    ad_count=10,
    duration_days=60,

    # أسعار المميزات (Features are moderate)
    feature_highlighted_price=50,   # متوسط
    feature_urgent_price=30,        # متوسط
    feature_pinned_price=75,        # متوسط
    feature_contact_for_price=25,   # رخيص
)
```

**السيناريو:**
```
User: لديه الباقة القياسية
User: يريد نشر إعلان مع تمييز (highlighted)
System: السعر = 50 ج.م (من الباقة - أرخص من المجانية)
```

---

### مثال 3: باقة بريميوم (Premium Package)

```python
premium_package = AdPackage.objects.create(
    name="باقة بريميوم",
    price=500,
    ad_count=50,
    duration_days=90,

    # أسعار المميزات (Features are cheap/free)
    feature_highlighted_price=0,    # مجاني!
    feature_urgent_price=0,         # مجاني!
    feature_pinned_price=25,        # رخيص جداً
    feature_contact_for_price=0,    # مجاني!
)
```

**السيناريو:**
```
User: لديه الباقة البريميوم
User: يريد نشر إعلان مع تمييز (highlighted)
System: السعر = 0 ج.م (مجاني في الباقة البريميوم!)
```

---

### مثال 4: مستخدم بدون باقة (No Package)

```python
# In SiteConfiguration:
featured_ad_price = 75
urgent_ad_price = 50
pinned_ad_price = 125
```

**السيناريو:**
```
User: ليس لديه أي باقة نشطة
User: يريد نشر إعلان مع تمييز (highlighted)
System: السعر = 75 ج.م (من إعدادات الموقع)
```

---

## المقارنة | Comparison

### قبل التحديث (Before):

| المستخدم | الباقة | سعر التمييز |
|---------|--------|-------------|
| أحمد | مجانية | 50 ج.م (من الموقع) |
| سارة | قياسية | 50 ج.م (من الموقع) |
| محمد | بريميوم | 50 ج.م (من الموقع) |
| علي | بدون باقة | 50 ج.م (من الموقع) |

**❌ المشكلة:** الجميع يدفع نفس السعر!

### بعد التحديث (After):

| المستخدم | الباقة | سعر التمييز |
|---------|--------|-------------|
| أحمد | مجانية | 100 ج.م (من الباقة) |
| سارة | قياسية | 50 ج.م (من الباقة) |
| محمد | بريميوم | 0 ج.م (مجاني في الباقة!) |
| علي | بدون باقة | 75 ج.م (من الموقع) |

**✅ الحل:** كل باقة لها أسعارها الخاصة!

---

## استراتيجيات التسعير | Pricing Strategies

### 1. Freemium Model

```python
# Free package: Expensive features
free_package.feature_highlighted_price = 100
free_package.feature_urgent_price = 75

# Premium package: Cheap/free features
premium_package.feature_highlighted_price = 0
premium_package.feature_urgent_price = 0
```

**الهدف:** تشجيع المستخدمين على شراء الباقات المدفوعة

---

### 2. Volume Discount

```python
# Small package: High per-feature price
small_package.feature_highlighted_price = 80

# Large package: Low per-feature price
large_package.feature_highlighted_price = 20
```

**الهدف:** مكافأة المستخدمين الذين يشترون باقات أكبر

---

### 3. Bundle Strategy

```python
# Basic package: Pay for each feature
basic_package.feature_highlighted_price = 50
basic_package.feature_urgent_price = 30

# Pro package: Some features free, others discounted
pro_package.feature_highlighted_price = 0   # Free!
pro_package.feature_urgent_price = 10       # Discounted
```

**الهدف:** تحفيز الترقية إلى باقات أعلى

---

## الاختبار | Testing

### Test Case 1: User with Package

```python
def test_feature_pricing_with_package():
    # Create package with custom feature prices
    package = AdPackage.objects.create(
        name="Test Package",
        price=100,
        ad_count=5,
        duration_days=30,
        feature_highlighted_price=25,  # Custom price
        feature_urgent_price=15,
        feature_pinned_price=50,
    )

    # Create user package
    user_package = UserPackage.objects.create(
        user=user,
        package=package,
        ads_remaining=5,
        expiry_date=timezone.now() + timedelta(days=30),
    )

    # Create ad with features
    response = client.post('/classifieds/create/', {
        'title': 'Test Ad',
        'feature_highlighted': 'on',  # Select highlighted
        # ... other fields ...
    })

    # Check that package price is used (25 EGP, not site default 50 EGP)
    assert response.context['features_cost'] == Decimal('25')
```

### Test Case 2: User without Package

```python
def test_feature_pricing_without_package():
    # No active package for user

    # Create ad with features
    response = client.post('/classifieds/create/', {
        'title': 'Test Ad',
        'feature_highlighted': 'on',
        # ... other fields ...
    })

    # Check that site default price is used (from SiteConfiguration)
    site_config = SiteConfiguration.get_solo()
    assert response.context['features_cost'] == site_config.featured_ad_price
```

### Test Case 3: Package with Free Features

```python
def test_free_features_in_premium_package():
    # Create premium package with free features
    premium = AdPackage.objects.create(
        name="Premium",
        price=500,
        ad_count=50,
        duration_days=90,
        feature_highlighted_price=0,  # FREE!
        feature_urgent_price=0,       # FREE!
        feature_pinned_price=0,       # FREE!
    )

    user_package = UserPackage.objects.create(user=user, package=premium, ...)

    # Create ad with ALL features
    response = client.post('/classifieds/create/', {
        'feature_highlighted': 'on',
        'feature_urgent': 'on',
        'feature_pinned': 'on',
        # ...
    })

    # Total features cost should be 0
    assert response.context['features_cost'] == Decimal('0')
```

---

## الفوائد | Benefits

### 1. للمستخدمين (For Users)

✅ **وضوح الأسعار:** كل باقة تعرض أسعارها الخاصة
✅ **خيارات أكثر:** يمكن اختيار الباقة بناءً على أسعار المميزات
✅ **قيمة أفضل:** الباقات الأغلى توفر مميزات أرخص/مجانية

### 2. للمديرين (For Admins)

✅ **مرونة في التسعير:** أسعار مختلفة لكل باقة
✅ **استراتيجيات متنوعة:** Freemium, Volume Discount, Bundle
✅ **سهولة التعديل:** تغيير أسعار باقة واحدة دون التأثير على الباقي

### 3. للمنصة (For Platform)

✅ **زيادة الإيرادات:** تشجيع الترقية إلى باقات أعلى
✅ **ولاء أكبر:** مكافأة المستخدمين المخلصين بأسعار أفضل
✅ **تحليلات أدق:** معرفة أي المميزات والباقات أكثر ربحية

---

## الملخص | Summary

### ما تم تغييره:

1. ✅ **ClassifiedAdCreateView.get_context_data()**: تمرير `feature_prices` حسب الباقة
2. ✅ **ClassifiedAdCreateView.form_valid()**: حساب التكلفة من أسعار الباقة
3. ✅ **ad_form.html Template**: عرض الأسعار من `feature_prices` بدلاً من `site_config`
4. ✅ **JavaScript**: استخدام الأسعار الصحيحة في الحسابات

### النتيجة النهائية:

- **قبل:** أسعار ثابتة من إعدادات الموقع
- **بعد:** أسعار مرتبطة بالباقة + fallback لإعدادات الموقع

### الملفات المعدلة:

- `main/classifieds_views.py` (ClassifiedAdCreateView)
- `templates/classifieds/ad_form.html`

---

**تاريخ التحديث | Update Date:** 2025-12-30
**الإصدار | Version:** 1.0
**الحالة | Status:** ✅ مكتمل | Completed
