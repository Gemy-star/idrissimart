# نظام طلبات الأعضاء والمدفوعات المحدّث
## User Orders & Payments System - Complete Overhaul

## التاريخ | Date
9 يناير 2026 | January 9, 2026

---

## نظرة عامة | Overview

تم إعادة هيكلة نظام الطلبات والمدفوعات لحل المشاكل التالية:
- عدم ظهور طلبات العضو (مشتريات السلة) في صفحة مخصصة
- الخلط بين طلبات البيع وطلبات الشراء
- عدم وجود حقل العملة في الطلبات

---

## المشاكل المحلولة | Problems Solved

### 1. الفرق بين نوعي الطلبات

**قبل التحديث:**
- صفحة واحدة مربكة تخلط بين:
  - طلبات البيع (Orders containing my ads as a seller)
  - طلبات الشراء (My orders as a buyer)

**بعد التحديث:**
✅ فصل واضح:
- `/publisher/orders/` → طلبات البيع (Orders for items I sell)
- `/my-orders/` → طلباتي (My purchases as a buyer)

### 2. حقل العملة مفقود

**قبل:**
```python
# Order Model - كان يعتمد على افتراض SAR فقط
total_amount = DecimalField(...)
# لا يوجد حقل currency
```

**بعد:**
```python
# Order Model - الآن يدعم عملات متعددة
currency = CharField(max_length=3, default="SAR")
total_amount = DecimalField(...)
```

### 3. عرض الطلبات بغض النظر عن حالة الدفع

**تم إضافة:**
- فلترة حسب حالة الدفع (unpaid, partial, paid)
- عرض جميع الطلبات حتى لو لم يتم الدفع
- عرض المبلغ المدفوع والمتبقي بوضوح

---

## التغييرات في قاعدة البيانات | Database Changes

### 1. Order Model - إضافة حقل العملة

**الملف:** `main/models.py` (Line ~3220)

```python
class Order(models.Model):
    # ... existing fields ...

    # NEW FIELD ✅
    currency = models.CharField(
        max_length=3,
        default="SAR",
        verbose_name=_("العملة - Currency"),
        help_text=_("العملة المستخدمة للطلب"),
    )

    total_amount = models.DecimalField(...)
    paid_amount = models.DecimalField(...)
    remaining_amount = models.DecimalField(...)
```

**Migration:**
- ملف: `main/migrations/0043_add_currency_to_order.py`
- الأمر: `python manage.py migrate`

**فوائد:**
- دعم عملات متعددة (SAR, EGP, USD, EUR, etc.)
- تخزين سعر الصرف وقت الطلب
- عرض صحيح للأسعار حسب الدولة

---

## Views الجديدة | New Views

### 1. my_orders_list (طلباتي - مشترياتي)

**الملف:** `main/user_orders_views.py`

```python
@login_required
def my_orders_list(request):
    """عرض طلبات العضو (مشترياته من السلة)"""
    # Get user's own orders (as a buyer)
    orders = Order.objects.filter(user=request.user)

    # Filters
    - status (pending, processing, shipped, delivered, cancelled)
    - payment_status (unpaid, partial, paid)
    - search by order_number

    # Statistics
    - total_orders
    - pending, processing, delivered counts
    - total_spent
    - unpaid, partially_paid counts
```

**الفرق الجوهري:**
```python
# OLD - Publisher Orders (what I sell)
orders = Order.objects.filter(items__ad__user=request.user)

# NEW - My Orders (what I buy)
orders = Order.objects.filter(user=request.user)
```

### 2. my_order_detail (تفاصيل الطلب)

```python
@login_required
def my_order_detail(request, order_id):
    """عرض تفاصيل طلب معين"""
    order = get_object_or_404(
        Order.objects.filter(user=request.user),
        id=order_id
    )
```

---

## URLs الجديدة | New URLs

### قبل التحديث:
```python
# فقط طلبات البيع
path("publisher/orders/", ...)  # ❌ مربك
```

### بعد التحديث:
```python
# طلبات البيع (ما أبيعه)
path("publisher/orders/",
     admin_orders_views.publisher_orders_list,
     name="publisher_orders_list")

# طلباتي (ما أشتريه) ✅ NEW
path("my-orders/",
     user_orders_views.my_orders_list,
     name="my_orders")

path("my-orders/<int:order_id>/",
     user_orders_views.my_order_detail,
     name="my_order_detail")
```

---

## Templates الجديدة | New Templates

### 1. my_orders_list.html

**الموقع:** `templates/dashboard/my_orders_list.html`

**المميزات:**
- بطاقات إحصائية جذابة (Total, Delivered, Processing, Total Spent)
- جدول تفاعلي يعرض:
  - رقم الطلب
  - التاريخ
  - عدد المنتجات
  - المبلغ الإجمالي
  - المبلغ المدفوع
  - المبلغ المتبقي
  - حالة الدفع (Badges ملونة)
  - حالة الطلب (Badges ملونة)
  - زر "عرض التفاصيل"

**نظام الألوان:**
```html
<!-- حالات الدفع -->
<span class="badge bg-success">مدفوع</span>      <!-- Paid -->
<span class="badge bg-warning">جزئي</span>       <!-- Partial -->
<span class="badge bg-danger">غير مدفوع</span>   <!-- Unpaid -->

<!-- حالات الطلب -->
<span class="badge bg-success">تم التسليم</span>  <!-- Delivered -->
<span class="badge bg-info">تم الشحن</span>       <!-- Shipped -->
<span class="badge bg-primary">قيد المعالجة</span><!-- Processing -->
<span class="badge bg-warning">قيد الانتظار</span> <!-- Pending -->
<span class="badge bg-danger">ملغي</span>         <!-- Cancelled -->
```

**فلاتر متقدمة:**
```html
<!-- فلتر الحالة -->
<select name="status">
    <option value="">جميع الحالات</option>
    <option value="pending">قيد الانتظار</option>
    <option value="processing">قيد المعالجة</option>
    <option value="shipped">تم الشحن</option>
    <option value="delivered">تم التسليم</option>
    <option value="cancelled">ملغي</option>
</select>

<!-- فلتر حالة الدفع -->
<select name="payment_status">
    <option value="">جميع حالات الدفع</option>
    <option value="unpaid">غير مدفوع</option>
    <option value="partial">دفع جزئي</option>
    <option value="paid">مدفوع بالكامل</option>
</select>

<!-- بحث -->
<input type="text" name="search" placeholder="رقم الطلب">
```

**Pagination:** ✅ مدمج بالكامل

**Dark Mode:** ✅ مدعوم

---

## الروابط في القوائم | Menu Links

### قائمة المستخدم (Desktop)

**الموقع:** `templates/partials/_header.html`

```html
<ul class="dropdown-menu dropdown-menu-end">
    <li><h6 class="dropdown-header">
        <i class="fas fa-tachometer-alt"></i> لوحة التحكم
    </h6></li>

    <li><a class="dropdown-item" href="{% url 'main:my_ads' %}">
        <i class="fas fa-tachometer-alt me-2 text-primary"></i>
        لوحة التحكم
    </a></li>

    <li><a class="dropdown-item" href="{% url 'main:my_ads' %}">
        <i class="fas fa-bullhorn me-2 text-info"></i>
        إعلاناتي
    </a></li>

    <!-- NEW LINK ✅ -->
    <li><a class="dropdown-item" href="{% url 'main:my_orders' %}">
        <i class="fas fa-shopping-cart me-2 text-success"></i>
        طلباتي
    </a></li>

    <li><a class="dropdown-item" href="{% url 'main:publisher_chats' %}">
        <i class="fas fa-comments me-2 text-primary"></i>
        رسائلي
    </a></li>

    <!-- ... verification & settings ... -->
</ul>
```

### القائمة المحمولة (Mobile)

```html
<li><a href="{% url 'main:my_ads' %}" class="mobile-nav-link">
    <i class="fas fa-tachometer-alt text-primary"></i>
    <span>لوحة التحكم</span>
</a></li>

<li><a href="{% url 'main:my_ads' %}" class="mobile-nav-link">
    <i class="fas fa-bullhorn text-info"></i>
    <span>إعلاناتي</span>
</a></li>

<!-- NEW LINK ✅ -->
<li><a href="{% url 'main:my_orders' %}" class="mobile-nav-link">
    <i class="fas fa-shopping-cart text-success"></i>
    <span>طلباتي</span>
</a></li>

<li><a href="{% url 'main:publisher_chats' %}" class="mobile-nav-link">
    <i class="fas fa-comments text-success"></i>
    <span>رسائلي</span>
</a></li>
```

---

## مقارنة شاملة | Complete Comparison

### قبل التحديث | Before

| الجانب | المشكلة |
|--------|---------|
| **الطلبات** | لا توجد صفحة مخصصة لطلبات العضو |
| **العملة** | SAR فقط، لا دعم لعملات أخرى |
| **الفلاتر** | محدودة، لا تفصل بين حالة الطلب والدفع |
| **القوائم** | لا يوجد رابط واضح للطلبات |
| **المبالغ** | عرض غير واضح للمدفوع/المتبقي |

### بعد التحديث | After

| الجانب | الحل ✅ |
|--------|--------|
| **الطلبات** | صفحة مخصصة `/my-orders/` |
| **العملة** | دعم كامل لجميع العملات |
| **الفلاتر** | فصل واضح: status + payment_status |
| **القوائم** | رابط "طلباتي" في جميع القوائم |
| **المبالغ** | عرض دقيق: إجمالي/مدفوع/متبقي + نسبة |

---

## أمثلة الاستخدام | Use Cases

### 1. عرض جميع طلبات العضو

```python
# View: my_orders_list
orders = Order.objects.filter(user=request.user)

# مع الفلاتر
if status_filter:
    orders = orders.filter(status=status_filter)

if payment_status_filter:
    orders = orders.filter(payment_status=payment_status_filter)
```

**النتيجة:**
- عرض جميع الطلبات بغض النظر عن حالة الدفع
- إمكانية فلترة حسب unpaid/partial/paid
- إحصائيات دقيقة لكل حالة

### 2. عرض الطلبات غير المدفوعة فقط

```
GET /my-orders/?payment_status=unpaid
```

**النتيجة:**
```
╔════════════════════════════════════════════╗
║ طلباتي - الطلبات غير المدفوعة            ║
╠════════════════════════════════════════════╣
║ ORD-20260109-A1B2  │ 500 SAR  │ غير مدفوع  ║
║ ORD-20260108-C3D4  │ 350 EGP  │ غير مدفوع  ║
╚════════════════════════════════════════════╝
```

### 3. عرض الطلبات المكتملة (مدفوعة ومسلّمة)

```
GET /my-orders/?status=delivered&payment_status=paid
```

### 4. بحث عن طلب برقمه

```
GET /my-orders/?search=ORD-20260109
```

---

## الإحصائيات المتاحة | Available Statistics

```python
stats = {
    "total_orders": 25,           # إجمالي الطلبات
    "pending": 3,                 # قيد الانتظار
    "processing": 5,              # قيد المعالجة
    "shipped": 4,                 # تم الشحن
    "delivered": 10,              # تم التسليم
    "cancelled": 3,               # ملغي
    "total_spent": 5000.00,       # إجمالي المشتريات
    "unpaid": 2,                  # غير مدفوع
    "partially_paid": 3,          # دفع جزئي
}
```

**العرض:**
```
╔══════════════════════════════════════╗
║ 25           │ 10          │ 5      ║
║ إجمالي       │ تم التسليم  │ معالجة ║
║                                      ║
║ 5000 ريال                           ║
║ إجمالي المشتريات                   ║
╚══════════════════════════════════════╝
```

---

## دعم العملات | Currency Support

### استخدام حقل العملة

```python
# عند إنشاء الطلب
from main.utils import get_selected_country_from_request
from content.models import Country

selected_country_code = get_selected_country_from_request(request)
country = Country.objects.get(code=selected_country_code)

order = Order.objects.create(
    user=request.user,
    currency=country.currency or "SAR",  # ✅ استخدام عملة الدولة
    total_amount=500.00,
    # ...
)
```

### عرض الأسعار بالعملة الصحيحة

```django
<!-- Template -->
<td>
    <strong>{{ order.total_amount }} {{ order.currency }}</strong>
</td>

<!-- Examples -->
500.00 SAR  (السعودية)
350.00 EGP  (مصر)
120.00 USD  (دولي)
```

### خريطة رموز العملات

```python
CURRENCY_SYMBOLS = {
    "SAR": "ر.س",   # ريال سعودي
    "EGP": "ج.م",   # جنيه مصري
    "AED": "د.إ",   # درهم إماراتي
    "KWD": "د.ك",   # دينار كويتي
    "QAR": "ر.ق",   # ريال قطري
    "BHD": "د.ب",   # دينار بحريني
    "OMR": "ر.ع",   # ريال عماني
    "USD": "$",     # دولار
    "EUR": "€",     # يورو
}
```

---

## مسار تدفق الطلبات | Order Flow

```
[إضافة منتج للسلة]
        ↓
[الذهاب للدفع - Checkout]
        ↓
[إنشاء Order + OrderItems]
   status = "pending"
   payment_status = "unpaid"
        ↓
   ┌────┴────┐
   ↓         ↓
[COD]    [Online]
   ↓         ↓
[تأكيد]   [دفع]
   ↓         ↓
status = "processing"
payment_status = "paid"
        ↓
[شحن الطلب]
status = "shipped"
        ↓
[تسليم الطلب]
status = "delivered"
```

**يمكن رؤية الطلب في جميع المراحل ✅**

---

## الاختبار | Testing

### 1. اختبار عرض الطلبات

```python
# Login as a user
user = User.objects.get(username='testuser')
client.force_login(user)

# Create test orders
order1 = Order.objects.create(
    user=user,
    order_number="ORD-TEST-001",
    currency="SAR",
    total_amount=500,
    paid_amount=0,
    payment_status="unpaid",
    status="pending"
)

# Visit my orders page
response = client.get(reverse('main:my_orders'))
assert response.status_code == 200
assert 'ORD-TEST-001' in response.content.decode()
```

### 2. اختبار الفلاتر

```python
# Filter by payment status
response = client.get(reverse('main:my_orders') + '?payment_status=unpaid')
assert order1 in response.context['orders']

# Filter by status
response = client.get(reverse('main:my_orders') + '?status=pending')
assert order1 in response.context['orders']
```

### 3. اختبار العملات

```python
order_egp = Order.objects.create(
    user=user,
    currency="EGP",  # ✅ Egyptian Pound
    total_amount=1000
)

response = client.get(reverse('main:my_orders'))
assert 'EGP' in response.content.decode()
```

---

## الأسئلة الشائعة | FAQ

### س: ما الفرق بين "طلباتي" و "publisher/orders"؟
**ج:**
- **طلباتي** `/my-orders/` → طلباتي كمشتري (what I bought)
- **publisher/orders** `/publisher/orders/` → طلبات بيع إعلاناتي (orders for my ads)

### س: هل تظهر الطلبات غير المدفوعة؟
**ج:** نعم! جميع الطلبات تظهر بغض النظر عن حالة الدفع. يمكنك فلترتها.

### س: كيف أعرف المبلغ المتبقي؟
**ج:** في جدول الطلبات:
- **المبلغ الإجمالي**: total_amount
- **المدفوع**: paid_amount (أخضر)
- **المتبقي**: remaining_amount (أحمر)

### س: هل يدعم النظام عملات متعددة؟
**ج:** نعم! الآن يوجد حقل `currency` في كل طلب.

### س: كيف يتم حساب remaining_amount؟
**ج:** تلقائياً في `Order.save()`:
```python
self.remaining_amount = self.total_amount - self.paid_amount
```

---

## الخلاصة | Summary

### ما تم إنجازه ✅

1. **إضافة حقل العملة** للطلبات
2. **إنشاء صفحة "طلباتي"** المخصصة
3. **فصل واضح** بين طلبات البيع والشراء
4. **فلاتر متقدمة** (status + payment_status)
5. **عرض شامل** للمبالغ (إجمالي/مدفوع/متبقي)
6. **إحصائيات دقيقة** لجميع الحالات
7. **روابط واضحة** في جميع القوائم
8. **دعم Dark Mode** كامل
9. **Pagination** للأداء الأفضل
10. **Templates احترافية** مع تصميم جذاب

### الملفات المعدلة

1. ✅ `main/models.py` - إضافة currency
2. ✅ `main/user_orders_views.py` - Views جديدة
3. ✅ `main/urls.py` - URLs جديدة
4. ✅ `templates/dashboard/my_orders_list.html` - Template جديد
5. ✅ `templates/partials/_header.html` - روابط محدثة
6. ✅ `main/migrations/0043_add_currency_to_order.py` - Migration

### النتيجة النهائية

الآن العضو يمكنه:
- ✅ رؤية جميع طلباته (مشترياته)
- ✅ معرفة حالة كل طلب بوضوح
- ✅ معرفة المبالغ المدفوعة والمتبقية
- ✅ فلترة الطلبات بسهولة
- ✅ البحث عن طلب برقمه
- ✅ الوصول السريع من القائمة

**النظام الآن متكامل وجاهز للإنتاج! 🎉**
