# نظام عرض الأسعار والباقات
## Ad Pricing & Packages Display System

## نظرة عامة | Overview

تم إنشاء نظام جديد لعرض الأسعار والباقات عندما يحاول المستخدم نشر إعلان جديد بدون رصيد مجاني متبقي.

A new system has been created to display pricing and packages when a user tries to post a new ad without free ads remaining.

---

## سير العمل | Workflow

### السيناريو الأساسي | Basic Scenario

```
المستخدم يضغط "نشر إعلان جديد"
        ↓
هل لديه باقة نشطة مع رصيد متبقي؟
        ↓
     لا ← يتم تحويله لصفحة الأسعار
        ↓
يرى:
  1. سعر النشر للقسم المحدد (أو السعر الافتراضي)
  2. جميع الباقات المتوفرة
  3. مقارنة بين الدفع لكل إعلان والباقات
        ↓
يختار:
  - "نشر إعلان الآن" (دفع لإعلان واحد)
  - أو شراء باقة
```

```
User clicks "Post New Ad"
        ↓
Does user have active package with remaining ads?
        ↓
     No → Redirect to pricing page
        ↓
User sees:
  1. Category-specific pricing (or default)
  2. All available packages
  3. Comparison between pay-per-ad and packages
        ↓
User chooses:
  - "Post Ad Now" (pay for one ad)
  - Or buy a package
```

---

## الملفات الجديدة | New Files

### 1. Views

**File:** [main/pricing_views.py](c:\WORK\idrissimart\main\pricing_views.py)

```python
@login_required
def ad_pricing_view(request):
    """
    Show pricing for posting an ad when user has no free ads remaining.
    Display:
    1. Category-specific pricing (if category_id in session/GET)
    2. Available packages
    3. Option to pay per ad
    """
```

**Features:**
- ✅ Check if user has active package
- ✅ Redirect to ad_create if user has free ads
- ✅ Get category-specific pricing (if available)
- ✅ Calculate pricing with tax (15%)
- ✅ Display all active packages

### 2. Template

**File:** [templates/classifieds/ad_pricing.html](c:\WORK\idrissimart\templates\classifieds\ad_pricing.html)

**Sections:**

#### Page Header
```
┌──────────────────────────────────┐
│   📋 أسعار نشر الإعلانات          │
│                                  │
│   اختر الطريقة المناسبة لك       │
└──────────────────────────────────┘
```

#### Pricing Options (2 Cards)

**Card 1: Pay Per Ad**
```
┌──────────────────────────┐
│   📄 الدفع لكل إعلان     │
│                          │
│   [Price]                │
│   السعر الأساسي           │
│   + الضريبة 15%          │
│   = المجموع              │
│                          │
│   ✓ Features list        │
│                          │
│   [نشر إعلان الآن]       │
└──────────────────────────┘
```

**Card 2: Best Package (Recommended)**
```
┌──────────────────────────┐
│  ⭐ موصى به              │
│   👑 [Package Name]      │
│                          │
│   [Price]                │
│   صالحة لـ X يوم         │
│                          │
│   ⭐ X إعلان مجاني       │
│   ✓ Features list        │
│                          │
│   [اشترِ الباقة]         │
└──────────────────────────┘
```

#### All Packages Section

Grid of all available packages with:
- Package name and description
- Price
- Number of ads
- Validity period
- Features
- "Best Value" badge for popular packages

---

## الملفات المعدلة | Modified Files

### 1. ClassifiedAdCreateView

**File:** [main/classifieds_views.py](c:\WORK\idrissimart\main\classifieds_views.py:224-268)

**Changes in `dispatch` method:**

```python
def dispatch(self, request, *args, **kwargs):
    # Check if user has active package
    active_package = UserPackage.objects.filter(
        user=user,
        expiry_date__gte=timezone.now(),
        ads_remaining__gt=0,
    ).first()

    # Check if coming from pricing page
    pay_per_ad = request.GET.get("pay_per_ad") == "true"

    # If no package and not paying per ad → redirect to pricing
    if not active_package and not pay_per_ad:
        category_id = request.GET.get("category")
        if category_id:
            return redirect(f"{reverse('main:ad_pricing')}?category={category_id}")
        return redirect("main:ad_pricing")

    # Continue with ad creation...
```

**Logic:**
1. ✅ Check if user is authenticated
2. ✅ Check if user has active package with remaining ads
3. ✅ Check if user explicitly wants to pay per ad (`?pay_per_ad=true`)
4. ✅ If no package and not paying per ad → redirect to pricing page
5. ✅ Pass category ID if available for category-specific pricing

### 2. URLs

**File:** [main/urls.py](c:\WORK\idrissimart\main\urls.py:125-129)

```python
path(
    "classifieds/pricing/",
    pricing_views.ad_pricing_view,
    name="ad_pricing",
),
```

**Imports:**
```python
from . import pricing_views
```

---

## Routes & URLs

### Main Route

```
/classifieds/pricing/
```

**URL Name:** `main:ad_pricing`

**Query Parameters:**
- `category` (optional) - Category ID for category-specific pricing

**Examples:**
```
/classifieds/pricing/
/classifieds/pricing/?category=5
```

### Usage from Other Pages

**From Ad Create Button:**
```html
<a href="{% url 'main:ad_create' %}">نشر إعلان</a>
```
→ Auto-redirects to pricing if no free ads

**With Category:**
```html
<a href="{% url 'main:ad_create' %}?category=5">نشر في هذا القسم</a>
```
→ Auto-redirects to `pricing/?category=5`

**Direct Pay Per Ad:**
```html
<a href="{% url 'main:ad_create' %}?pay_per_ad=true">دفع لإعلان واحد</a>
```
→ Skips pricing page, goes directly to form

---

## Pricing Calculation

### Default Pricing

```python
# From SiteConfiguration
base_price = site_config.ad_base_fee  # Default: 50 SAR
tax_rate = 0.15  # 15%
tax_amount = base_price * tax_rate
total_price = base_price + tax_amount
```

### Category-Specific Pricing

```python
# If category has custom pricing
if category.ad_base_fee:
    base_price = category.ad_base_fee
else:
    base_price = site_config.ad_base_fee
```

**Example:**
```
Base Price: 50 SAR
Tax (15%):   7.50 SAR
────────────────────
Total:      57.50 SAR
```

---

## الباقات | Packages

### Package Display

Each package card shows:

1. **Package Name** - من Model: `package.name`
2. **Description** - من Model: `package.description`
3. **Price** - من Model: `package.price`
4. **Validity** - من Model: `package.validity_days`
5. **Features:**
   - Number of ads: `package.ad_limit`
   - Photos allowed: `package.max_photos`
   - Featured ads: `package.allow_featured`
   - Priority support: `package.priority_support`

### Badges

**"موصى به" (Recommended):**
- First package in list
- Highlighted with gold border
- Scale 1.05 transform
- Gold star badge

**"الأكثر مبيعاً" (Best Seller):**
- If `package.is_popular == True`
- Orange badge
- Fire icon

---

## UI/UX Features

### Responsive Design

```css
Desktop (> 768px):  2 cards per row
Tablet (≤ 768px):   1 card per row
Mobile (≤ 576px):   Full width cards
```

### Dark Mode Support

```css
[data-theme="dark"] .pricing-card {
    background: #2a1a3a;
}

[data-theme="dark"] .package-card {
    background: #2a1a3a;
}
```

### Interactive Elements

**Hover Effects:**
- Cards lift up (`translateY(-10px)`)
- Shadow increases
- Border color changes

**Recommended Card:**
- Always scaled 1.05
- Gold border
- "⭐ موصى به" badge

---

## سيناريوهات الاستخدام | Use Cases

### Scenario 1: مستخدم جديد بدون باقة

```
1. User: يضغط "نشر إعلان"
2. System: يتحقق من الرصيد → لا يوجد
3. System: Redirect to /classifieds/pricing/
4. User: يرى الأسعار والباقات
5. User: يختار "نشر إعلان الآن" (50 ريال)
6. System: Redirect to /classifieds/create/?pay_per_ad=true
7. User: يملأ النموذج
8. System: يحسب التكلفة = 50 + ضريبة
9. User: يدفع
10. System: ينشر الإعلان
```

### Scenario 2: مستخدم يريد النشر في قسم محدد

```
1. User: في صفحة القسم، يضغط "نشر إعلان هنا"
2. System: Redirect to /classifieds/pricing/?category=5
3. User: يرى سعر القسم المحدد (إذا كان مخصص)
4. User: يختار باقة
5. System: Redirect to /packages/?select=3
6. User: يشتري الباقة
7. User: Redirect to /classifieds/create/?category=5
8. System: يستخدم من رصيد الباقة
```

### Scenario 3: مستخدم لديه باقة مع رصيد

```
1. User: يضغط "نشر إعلان"
2. System: يتحقق من الرصيد → يوجد 3 إعلانات متبقية
3. System: يتخطى صفحة الأسعار
4. System: Redirect مباشرة to /classifieds/create/
5. User: يملأ النموذج
6. System: ينشر مجاناً (يخصم من الرصيد)
```

---

## التكامل | Integration

### مع نظام الباقات | With Packages System

```python
# Button in pricing page
<a href="{% url 'main:packages' %}?highlight={{ package.id }}">
    اشترِ الباقة
</a>
```

### مع نظام الدفع | With Payment System

```python
# Pay per ad button
<a href="{% url 'main:ad_create' %}?pay_per_ad=true&category={{ category.id }}">
    نشر إعلان الآن
</a>

# In ClassifiedAdCreateView.form_valid:
if not active_package:
    base_fee = Decimal(str(site_config.ad_base_fee))
    # User will be redirected to payment
```

---

## الأمان | Security

### 1. Authentication Required

```python
@login_required
def ad_pricing_view(request):
    # Only authenticated users can see pricing
```

### 2. Package Validation

```python
# Only show active packages
packages = AdPackage.objects.filter(is_active=True)
```

### 3. Prevent Bypass

```python
# In ClassifiedAdCreateView:
if not active_package and not pay_per_ad:
    return redirect("main:ad_pricing")
# User cannot bypass pricing page without permission
```

---

## الإحصائيات | Analytics

### متتبعات مقترحة | Suggested Tracking

```python
# Track pricing page views
pricing_page_views = count(visits to /classifieds/pricing/)

# Track conversion rate
conversion_rate = (
    users_who_bought_package_from_pricing_page /
    total_pricing_page_views
)

# Track which option users choose
pay_per_ad_clicks = count("نشر إعلان الآن" clicks)
buy_package_clicks = count("اشترِ الباقة" clicks)
```

---

## التحسينات المستقبلية | Future Improvements

### 1. A/B Testing

```python
# Test different pricing displays
variant_a = "Show packages first"
variant_b = "Show pay-per-ad first"
```

### 2. Personalization

```python
# Recommend package based on user history
if user.total_ads_posted > 10:
    recommend = "Premium Package"
elif user.total_ads_posted > 3:
    recommend = "Standard Package"
else:
    recommend = "Basic Package"
```

### 3. Dynamic Pricing

```python
# Category-specific pricing
category.ad_base_fee = 75  # For Premium categories
category.ad_base_fee = 50  # For Standard categories
category.ad_base_fee = 25  # For Basic categories
```

### 4. Discounts & Promotions

```python
# Seasonal discounts
if is_promotion_active:
    discount = 0.20  # 20% off
    final_price = base_price * (1 - discount)
```

### 5. Package Comparison Table

```html
<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>Pay Per Ad</th>
      <th>Basic</th>
      <th>Standard</th>
      <th>Premium</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Number of Ads</td>
      <td>1</td>
      <td>5</td>
      <td>15</td>
      <td>50</td>
    </tr>
    ...
  </tbody>
</table>
```

---

## الاختبار | Testing

### Test Cases

#### 1. User Without Package

```bash
# كمستخدم بدون باقة
1. سجل دخول كمستخدم جديد
2. اذهب إلى /classifieds/create/
3. تحقق من التحويل إلى /classifieds/pricing/
4. تحقق من ظهور السعر الافتراضي
5. تحقق من ظهور جميع الباقات
```

#### 2. User With Package

```bash
# كمستخدم لديه باقة
1. سجل دخول كمستخدم لديه باقة نشطة
2. اذهب إلى /classifieds/create/
3. تحقق من عدم التحويل (يبقى في نفس الصفحة)
4. تحقق من عرض النموذج مباشرة
```

#### 3. Category-Specific Pricing

```bash
# لقسم محدد
1. اذهب إلى /classifieds/pricing/?category=5
2. تحقق من ظهور اسم القسم في العنوان
3. تحقق من عرض السعر المخصص (إذا كان موجود)
```

#### 4. Pay Per Ad

```bash
# الدفع لإعلان واحد
1. من صفحة الأسعار، اضغط "نشر إعلان الآن"
2. تحقق من التحويل إلى /classifieds/create/?pay_per_ad=true
3. املأ النموذج
4. تحقق من حساب التكلفة الصحيح
```

---

## الخلاصة | Summary

تم إنشاء نظام شامل لعرض الأسعار والباقات:

✅ **صفحة تسعير احترافية:**
- عرض السعر الافتراضي أو حسب القسم
- عرض جميع الباقات المتوفرة
- مقارنة بين الخيارات

✅ **تحويل تلقائي:**
- المستخدم بدون رصيد → صفحة الأسعار
- المستخدم مع رصيد → نموذج الإعلان مباشرة

✅ **واجهة جذابة:**
- بطاقات مميزة
- Badges للتوصيات
- Responsive design
- Dark mode support

✅ **تكامل كامل:**
- مع نظام الباقات
- مع نظام الدفع
- مع نظام الإعلانات

---

**تاريخ الإنشاء | Creation Date:** 2025-12-30
**الإصدار | Version:** 1.0
**الحالة | Status:** ✅ مكتمل | Completed
