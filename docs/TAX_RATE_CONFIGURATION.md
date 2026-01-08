# إعدادات الضريبة (VAT/Tax Configuration)

## 📋 نظرة عامة | Overview

تم إضافة إعداد قابل للتعديل من داش بورد الأدمن لضبط نسبة الضريبة (VAT) على جميع المعاملات المالية في الموقع.

---

## 🎯 المشكلة السابقة | Previous Issue

**كانت نسبة الضريبة مكتوبة بشكل ثابت (hardcoded) في الكود:**
- `15%` في ملف `main/pricing_views.py`
- `0.15` في JavaScript في `templates/classifieds/ad_features_upgrade.html`

**❌ لم يكن ممكناً تعديلها بدون تعديل الكود يدوياً**

---

## ✅ الحل | Solution

### 1. إضافة إعداد في Django Constance

تم إضافة إعداد `TAX_RATE` في ملف الإعدادات:

**الملف:** `idrissimart/settings/constance_config.py`

```python
"TAX_RATE": (
    15.0,
    _("نسبة الضريبة (%) - Tax Rate"),
    float,
),
```

**المجموعة:** `"Payment General Settings"`

---

## 🔧 التعديلات التقنية | Technical Changes

### الملفات المعدّلة | Modified Files

#### 1. **idrissimart/settings/constance_config.py**
- ✅ إضافة `TAX_RATE` config
- ✅ إضافته إلى `CONSTANCE_CONFIG_FIELDSETS`

#### 2. **main/pricing_views.py**
**قبل:**
```python
"tax_rate": Decimal("0.15"),  # 15% tax
```

**بعد:**
```python
from constance import config

# Get tax rate from Constance config (default 15%)
tax_rate_percentage = getattr(config, 'TAX_RATE', 15.0)
tax_rate_decimal = Decimal(str(tax_rate_percentage)) / Decimal("100")

pricing_details = {
    "tax_rate": tax_rate_decimal,
    "tax_rate_percentage": tax_rate_percentage,  # For display
}
```

#### 3. **main/ad_features_views.py**
**قبل:**
```python
# لا يوجد tax rate في الـ context
```

**بعد:**
```python
from constance import config

# Get tax rate from Constance config
tax_rate_percentage = getattr(config, 'TAX_RATE', 15.0)

context = {
    "tax_rate": tax_rate_percentage / 100.0,  # 0.15
    "tax_rate_percentage": tax_rate_percentage,  # 15
}
```

#### 4. **templates/classifieds/ad_pricing.html**
**قبل:**
```django
<span>{% trans "الضريبة" %} ({{ pricing_details.tax_rate|floatformat:"0" }}%)</span>
```

**بعد:**
```django
<span>{% trans "الضريبة" %} ({{ pricing_details.tax_rate_percentage|floatformat:"0" }}%)</span>
```

#### 5. **templates/classifieds/ad_features_upgrade.html**
**قبل:**
```javascript
const tax = subtotal * 0.15;
```
```html
<span>{% trans "الضريبة (15%):" %}</span>
```

**بعد:**
```javascript
const tax = subtotal * {{ tax_rate|default:"0.15" }};
```
```html
<span>{% trans "الضريبة" %} ({{ tax_rate_percentage|floatformat:"0" }}%):</span>
```

---

## 📍 أين يتم تطبيق الضريبة؟ | Where Tax is Applied

### ✅ الأماكن المحدثة (Updated)

1. **نشر الإعلانات** (`main/pricing_views.py`)
   - رسوم نشر الإعلان الأساسية
   - يتم عرض السعر الأساسي + الضريبة + المجموع الكلي

2. **ترقية مميزات الإعلان** (`main/ad_features_views.py`)
   - Contact for Price
   - Facebook Share
   - Video Upload (قريباً)
   - يتم حساب الضريبة على مجموع المميزات المختارة

### 🔍 أماكن أخرى قد تحتاج لمراجعة (Pending Review)

3. **ترقية الإعلانات** (Featured, Pinned, Urgent)
   - `main/classifieds_views.py` → `AdUpgradeCheckoutView`
   - `main/classifieds_views.py` → `AdUpgradeProcessView`

4. **شراء الباقات** (Packages)
   - `main/payment_views.py` → `package_checkout`
   - قد تحتاج لإضافة الضريبة على أسعار الباقات

5. **نظام السلة** (Cart System)
   - `main/cart_wishlist_views.py` → `checkout_view`
   - حسب السياسة: هل الضريبة على المشتري أم البائع؟

6. **التوثيق** (Verification Services)
   - إذا كانت هناك رسوم على التوثيق

---

## 🎛️ كيفية التعديل من داش بورد الأدمن | How to Configure

### الطريقة 1: عبر Django Admin

1. انتقل إلى: **Admin Dashboard → Constance → Config**
2. ابحث عن قسم: **"Payment General Settings"**
3. ابحث عن: **"نسبة الضريبة (%) - Tax Rate"**
4. قم بتعديل القيمة (مثال: `15.0` لـ 15%)
5. احفظ التغييرات

### الطريقة 2: عبر داش بورد الأدمن المخصص

1. انتقل إلى: **داش بورد الأدمن → الإعدادات**
2. سيظهر في قسم: **"إعدادات الدفع العامة"**
3. عدّل نسبة الضريبة
4. احفظ

---

## 🧪 اختبار التغييرات | Testing

### 1. اختبار صفحة تسعير الإعلانات
```
URL: /classifieds/pricing/
```
- ✅ تحقق من عرض النسبة الصحيحة
- ✅ تحقق من حساب المبلغ الصحيح

### 2. اختبار صفحة ترقية المميزات
```
URL: /classifieds/{ad_id}/features/
```
- ✅ تحقق من عرض النسبة في واجهة المستخدم
- ✅ تحقق من حساب الضريبة في JavaScript

### 3. تعديل النسبة في Admin
- ✅ غيّر النسبة من 15% إلى 10%
- ✅ تحقق من تحديث الصفحات فوراً
- ✅ أعد النسبة إلى 15%

---

## ⚙️ القيمة الافتراضية | Default Value

- **القيمة الافتراضية:** `15.0` (15%)
- **في حالة عدم تعيين قيمة:** يستخدم النظام `15.0` كاحتياطي (fallback)

```python
tax_rate = getattr(config, 'TAX_RATE', 15.0)  # Fallback to 15%
```

---

## 📊 أمثلة حسابية | Calculation Examples

### مثال 1: نشر إعلان عادي
```
السعر الأساسي: 50 ر.س
الضريبة (15%): 7.50 ر.س
──────────────────────
المجموع: 57.50 ر.س
```

### مثال 2: ترقية مميزات
```
Contact for Price: 0 ر.س
Facebook Share: 100 ر.س
──────────────────────
المجموع الفرعي: 100 ر.س
الضريبة (15%): 15 ر.س
──────────────────────
المجموع الكلي: 115 ر.س
```

### مثال 3: بعد تعديل النسبة لـ 5%
```
المجموع الفرعي: 100 ر.س
الضريبة (5%): 5 ر.س
──────────────────────
المجموع الكلي: 105 ر.س
```

---

## ✅ ملاحظات مهمة | Important Notes

1. **التطبيق الفوري:** التغييرات تُطبق فوراً بدون الحاجة لإعادة تشغيل السيرفر
2. **الأمان:** القيمة محفوظة في قاعدة البيانات وليست في environment variables
3. **الأنواع:** يتم قبول القيم العشرية (float) مثل `15.0` أو `15.5`
4. **العملة:** جميع الأسعار بالريال السعودي (SAR)

---

## 📝 TODO - مهام مستقبلية

- [ ] مراجعة وتحديث `AdUpgradeCheckoutView` لاستخدام الضريبة الديناميكية
- [ ] مراجعة وتحديث `package_checkout` لاستخدام الضريبة الديناميكية
- [ ] مراجعة نظام السلة وتحديد سياسة الضريبة (على المشتري/البائع)
- [ ] إضافة الضريبة إلى تقارير الإحصاءات
- [ ] إضافة log للتغييرات في نسبة الضريبة

---

## 📚 مراجع | References

- [Django Constance Documentation](https://django-constance.readthedocs.io/)
- [Site Configuration Models](../content/site_config.py)
- [Pricing Views](../main/pricing_views.py)
- [Ad Features Views](../main/ad_features_views.py)

---

**تاريخ التحديث:** 2026-01-09
**الإصدار:** 1.0
**الحالة:** ✅ مفعّل ويعمل
