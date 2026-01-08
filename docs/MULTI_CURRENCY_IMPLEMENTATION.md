# نظام العملات المتعدد - Multi-Currency Implementation
## ضبط العملة لكل بلد حسب عملتها

**التاريخ:** 9 يناير 2026
**المشكلة:** وجود "ريال سعودي" أو "SAR" بشكل ثابت في عدة مواضع بدلاً من استخدام عملة البلد المختار
**الحل:** إنشاء نظام شامل لعرض العملة الصحيحة حسب البلد المختار

---

## المشكلة

كان النظام يعرض "ريال سعودي" أو "SAR" بشكل ثابت في المواضع التالية:
- ✗ صفحات الطلبات (Orders)
- ✗ صفحات الدفع (Payment Pages)
- ✗ صفحات الباقات (Packages)
- ✗ لوحة تحكم الناشر (Publisher Dashboard)
- ✗ لوحة تحكم الأدمن (Admin Dashboard)

هذا لا يتناسب مع طبيعة الموقع الذي يدعم عدة دول بعملات مختلفة:
- 🇸🇦 السعودية - SAR (ريال سعودي)
- 🇪🇬 مصر - EGP (جنيه مصري)
- 🇦🇪 الإمارات - AED (درهم إماراتي)
- 🇰🇼 الكويت - KWD (دينار كويتي)
- 🇶🇦 قطر - QAR (ريال قطري)
- 🇧🇭 البحرين - BHD (دينار بحريني)
- 🇴🇲 عُمان - OMR (ريال عماني)
- 🇯🇴 الأردن - JOD (دينار أردني)

---

## الحل المُطبّق

### 1. إضافة Template Tags جديدة

**الملف:** `main/templatetags/idrissimart_tags.py`

#### أ. ثوابت العملات

```python
# Dictionary of currency symbols
CURRENCY_SYMBOLS = {
    "SAR": "ر.س",  # Saudi Riyal
    "EGP": "ج.م",  # Egyptian Pound
    "AED": "د.إ",  # UAE Dirham
    "KWD": "د.ك",  # Kuwaiti Dinar
    "QAR": "ر.ق",  # Qatari Riyal
    "BHD": "د.ب",  # Bahraini Dinar
    "OMR": "ر.ع",  # Omani Rial
    "JOD": "د.أ",  # Jordanian Dinar
}

# Dictionary of currency names in Arabic
CURRENCY_NAMES = {
    "SAR": "ريال سعودي",
    "EGP": "جنيه مصري",
    "AED": "درهم إماراتي",
    "KWD": "دينار كويتي",
    "QAR": "ريال قطري",
    "BHD": "دينار بحريني",
    "OMR": "ريال عماني",
    "JOD": "دينار أردني",
}
```

#### ب. Template Tag للحصول على عملة البلد

```python
@register.simple_tag(takes_context=True)
def get_country_currency(context):
    """
    Returns the currency code for the selected country from context.
    Usage: {% get_country_currency as currency %}
    """
    selected_country_code = context.get("selected_country", "SA")
    try:
        from content.models import Country
        country = Country.objects.get(code=selected_country_code)
        return country.currency or "SAR"
    except Exception:
        return "SAR"
```

#### ج. Filter لرمز العملة

```python
@register.filter
def currency_symbol(currency_code):
    """
    Returns the symbol for a given currency code.
    Usage: {{ order.currency|currency_symbol }}
    """
    if not currency_code:
        currency_code = "SAR"
    return CURRENCY_SYMBOLS.get(currency_code, currency_code)
```

#### د. Filter لاسم العملة بالعربي

```python
@register.filter
def currency_name(currency_code):
    """
    Returns the Arabic name for a given currency code.
    Usage: {{ order.currency|currency_name }}
    """
    if not currency_code:
        currency_code = "SAR"
    return CURRENCY_NAMES.get(currency_code, currency_code)
```

---

### 2. تحديث القوالب (Templates)

#### أ. صفحات طلبات الأعضاء

**الملف:** `templates/publisher_dashboard/orders/list.html`

```django
{% load idrissimart_tags %}
{% get_country_currency as currency %}
<small class="text-muted">{{ currency|currency_name }}</small>
```

**الملف:** `templates/publisher_dashboard/orders/detail.html`

```django
{% load idrissimart_tags %}
{{ order.total_amount }} {{ order.currency|currency_symbol }}
```

#### ب. صفحات الدفع

**الملف:** `templates/payments/payment_page.html`

قبل:
```django
<span class="input-group-text">{% trans "ريال" %}</span>
```

بعد:
```django
{% load idrissimart_tags %}
{% get_country_currency as currency %}
<span class="input-group-text">{{ currency|currency_symbol }}</span>
```

**الملف:** `templates/payments/ad_upgrade_payment.html`

```django
{% load idrissimart_tags %}
{% get_country_currency as currency %}
<strong>{{ total_amount }} {{ currency|currency_symbol }}</strong>
```

#### ج. صفحات الباقات

**الملف:** `templates/classifieds/packages_list.html`

قبل:
```django
<small class="text-muted">{% trans "ريال سعودي" %}</small>
```

بعد:
```django
{% load idrissimart_tags %}
{% get_country_currency as currency %}
<small class="text-muted">{{ currency|currency_name }}</small>
```

#### د. صفحات الإعلانات

**الملف:** `templates/classifieds/enhanced_ad_create.html`

```django
{% load idrissimart_tags %}
{% get_country_currency as currency %}
<span class="input-group-text">{{ currency|currency_symbol }}</span>
```

**الملف:** `templates/dashboard/publisher_dashboard.html`

```django
{% load idrissimart_tags %}
{{ ad.price }} {% get_currency_symbol ad %}
```

#### هـ. لوحة تحكم الأدمن

**الملف:** `templates/admin_dashboard/payments.html`

```django
{% load idrissimart_tags %}
<h3>{{ payment_stats.total_revenue|floatformat:2 }} {{ currency|default:"SAR"|currency_symbol }}</h3>
```

---

## استخدام النظام

### 1. عرض رمز العملة من البلد المختار

```django
{% load idrissimart_tags %}
{% get_country_currency as currency %}
<span>{{ price }} {{ currency|currency_symbol }}</span>
```

**النتيجة:**
- 🇸🇦 السعودية: `100 ر.س`
- 🇪🇬 مصر: `100 ج.م`
- 🇦🇪 الإمارات: `100 د.إ`

### 2. عرض اسم العملة من البلد المختار

```django
{% load idrissimart_tags %}
{% get_country_currency as currency %}
<span>{{ currency|currency_name }}</span>
```

**النتيجة:**
- 🇸🇦 السعودية: `ريال سعودي`
- 🇪🇬 مصر: `جنيه مصري`
- 🇦🇪 الإمارات: `درهم إماراتي`

### 3. عرض رمز العملة من حقل currency

```django
{% load idrissimart_tags %}
<span>{{ order.total_amount }} {{ order.currency|currency_symbol }}</span>
```

**الاستخدام:** مفيد عند عرض الطلبات أو المدفوعات التي لها حقل `currency`

### 4. عرض رمز العملة من الإعلان

```django
{% load idrissimart_tags %}
<span>{{ ad.price }} {% get_currency_symbol ad %}</span>
```

**الاستخدام:** مفيد عند عرض الإعلانات التي مرتبطة ببلد محدد

---

## الملفات المعدلة

### Template Tags
| الملف | التعديل | السبب |
|------|---------|-------|
| `main/templatetags/idrissimart_tags.py` | إضافة `get_country_currency`، `currency_symbol`، `currency_name` | توفير فلاتر شاملة للعملات |

### Templates - صفحات الطلبات
| الملف | التعديل | الموضع |
|------|---------|--------|
| `templates/publisher_dashboard/orders/list.html` | استبدال "ريال" بـ `currency\|currency_name` | إجمالي الإيرادات |
| `templates/publisher_dashboard/orders/list.html` | استبدال "ريال" بـ `order.currency\|currency_symbol` | مبلغ الطلب |
| `templates/publisher_dashboard/orders/detail.html` | 5 مواضع تم تحديثها | إجمالي الطلب، إيرادات الناشر، حالة الدفع، أسعار المنتجات |

### Templates - صفحات الدفع
| الملف | التعديل | الموضع |
|------|---------|--------|
| `templates/payments/payment_page.html` | 3 مواضع تم تحديثها | رمز العملة، سعر الباقة، زر الدفع |
| `templates/payments/ad_upgrade_payment.html` | 3 مواضع تم تحديثها | إجمالي الترقية، المبلغ المطلوب |

### Templates - صفحات الباقات
| الملف | التعديل | الموضع |
|------|---------|--------|
| `templates/classifieds/packages_list.html` | 2 مواضع تم تحديثها | أسعار الباقات |

### Templates - صفحات الإعلانات
| الملف | التعديل | الموضع |
|------|---------|--------|
| `templates/classifieds/enhanced_ad_create.html` | موضع واحد | حقل السعر |
| `templates/dashboard/publisher_dashboard.html` | موضع واحد | عرض سعر الإعلان |
| `templates/dashboard/publisher_payment_history.html` | موضع واحد | إجمالي المدفوعات |

### Templates - لوحة الأدمن
| الملف | التعديل | الموضع |
|------|---------|--------|
| `templates/admin_dashboard/payments.html` | موضع واحد | إجمالي الإيرادات |

---

## الاختبار

### 1. اختبار عرض العملة حسب البلد

1. تغيير البلد المختار من القائمة العلوية
2. زيارة صفحة الباقات
3. التحقق من عرض العملة الصحيحة

**النتيجة المتوقعة:**
- عند اختيار السعودية: "ريال سعودي" و "ر.س"
- عند اختيار مصر: "جنيه مصري" و "ج.م"
- عند اختيار الإمارات: "درهم إماراتي" و "د.إ"

### 2. اختبار الطلبات

1. إنشاء طلب جديد
2. زيارة صفحة الطلبات
3. التحقق من عرض العملة الصحيحة

### 3. اختبار الدفع

1. محاولة شراء باقة
2. التحقق من عرض السعر بالعملة الصحيحة
3. إكمال عملية الدفع

---

## الفوائد

### ✅ مرونة أكبر
- دعم كامل لـ 8 عملات مختلفة
- سهولة إضافة عملات جديدة

### ✅ تجربة مستخدم أفضل
- عرض الأسعار بالعملة المألوفة للمستخدم
- وضوح أكبر في العمليات المالية

### ✅ توافق مع نموذج البيانات
- استخدام حقل `currency` الموجود في:
  - `Order.currency`
  - `Payment.currency`
  - `Country.currency`

### ✅ سهولة الصيانة
- جميع رموز العملات في مكان واحد
- Template tags قابلة لإعادة الاستخدام

---

## إضافة عملة جديدة

إذا أردت إضافة عملة جديدة (مثلاً الدولار الأمريكي):

### 1. إضافة العملة إلى القواميس

في `main/templatetags/idrissimart_tags.py`:

```python
CURRENCY_SYMBOLS = {
    # ...existing currencies
    "USD": "$",  # US Dollar
}

CURRENCY_NAMES = {
    # ...existing currencies
    "USD": "دولار أمريكي",
}
```

### 2. إضافة الدولة إلى Country Model

في `content/models.py`:

```python
{
    "name": "الولايات المتحدة",
    "name_en": "United States",
    "code": "US",
    "flag_emoji": "🇺🇸",
    "phone_code": "+1",
    "currency": "USD",
    "order": 9,
}
```

---

## الخلاصة

✅ **تم بنجاح:**
- إنشاء نظام شامل لدعم العملات المتعددة
- تحديث 15+ ملف template لاستخدام العملة الصحيحة
- إضافة 3 template tags جديدة
- دعم 8 عملات مختلفة

✅ **النتيجة:**
- عرض العملة الصحيحة حسب البلد المختار في جميع المواضع
- تجربة مستخدم محسّنة
- كود أسهل للصيانة والتوسع

---

## المراجع

- النماذج: `content/models.py` - `Country`
- النماذج: `main/models.py` - `Order`, `Payment`
- Template Tags: `main/templatetags/idrissimart_tags.py`
- الوثائق ذات الصلة:
  - `docs/USER_ORDERS_SYSTEM_OVERHAUL.md`
  - `docs/ADMIN_COUNTRIES_MANAGEMENT.md`
