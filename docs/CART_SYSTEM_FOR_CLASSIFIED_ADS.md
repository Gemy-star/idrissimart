# نظام السلة للإعلانات المبوبة - Cart System for Classified Ads

## التاريخ: 30 ديسمبر 2025

---

## 📋 ملخص النظام

تم إضافة نظام شامل للسلة في الإعلانات المبوبة مع تحكم كامل من الأدمن، يسمح للناشرين بتفعيل خيار السلة لإعلاناتهم مع دفع رسوم خدمة عند البيع عبر المنصة.

---

## ✨ الميزات الرئيسية

### 1. **التحكم من مستوى القسم (Category Level)**
- الأدمن يحدد الأقسام التي تدعم السلة (مثل المنتجات)
- الأقسام التي لا تدعم السلة (مثل الوظائف) لا تظهر بها هذه الميزة
- نص إرشادي مخصص لكل قسم يشرح شروط استخدام السلة

### 2. **التحكم من مستوى الإعلان (Ad Level)**
- الناشر يختار تفعيل السلة عند إنشاء الإعلان
- حقل `publisher_cart_enabled`: يشير لطلب الناشر
- حقل `cart_enabled_by_admin`: يتم تفعيله من الأدمن بعد استلام المنتج

### 3. **رسوم الخدمة (Service Fees)**
- رسوم ثابتة أو نسبة مئوية من سعر المنتج
- يتم خصمها من الناشر عند البيع الفعلي
- منفصلة تماماً عن نسبة الحجز من المشتري

### 4. **تنبيهات وإرشادات**
- تنبيه للناشر بضرورة جعل السعر شاملاً للرسوم والتوصيل
- شرح واضح لآلية عمل النظام
- تعليمات قابلة للتخصيص من الأدمن

---

## 🔧 التغييرات التقنية

### Models

#### 1. Category Model
```python
# main/models.py

allow_cart = models.BooleanField(
    default=False,
    verbose_name=_("السماح بالسلة"),
    help_text=_("تفعيل نظام السلة لهذا القسم"),
)

cart_instructions = models.TextField(
    blank=True,
    verbose_name=_("إرشادات السلة"),
    help_text=_("نص إرشادي يظهر للناشر عند تفعيل السلة"),
    default="عند تفعيل السلة، يجب أن يكون السعر شاملاً رسوم الخدمة والتوصيل. سيتم خصم رسوم الخدمة منك عند البيع عبر المنصة.",
)
```

#### 2. ClassifiedAd Model
```python
# main/models.py

publisher_cart_enabled = models.BooleanField(
    default=False,
    verbose_name=_("الناشر فعّل السلة"),
    help_text=_("الناشر طلب تفعيل السلة لهذا الإعلان"),
)

cart_enabled_by_admin = models.BooleanField(
    default=False,
    verbose_name=_("السلة مفعلة من الإدارة"),
    help_text=_("يتم تفعيلها بعد استلام المنتج"),
)
```

#### 3. SiteConfiguration Model
```python
# content/site_config.py

cart_service_fee_type = models.CharField(
    max_length=20,
    choices=[
        ('fixed', _('رسوم ثابتة')),
        ('percentage', _('نسبة مئوية'))
    ],
    default='percentage',
    verbose_name=_("نوع رسوم خدمة السلة"),
)

cart_service_fixed_fee = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0,
    verbose_name=_("رسوم خدمة السلة الثابتة"),
)

cart_service_percentage = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=5,
    verbose_name=_("نسبة رسوم خدمة السلة"),
    validators=[MinValueValidator(0), MaxValueValidator(100)]
)

cart_service_instructions = models.TextField(
    blank=True,
    verbose_name=_("تعليمات خدمة السلة للناشر"),
    default="عند تفعيل السلة، سيتم خصم رسوم خدمة من ثمن المنتج عند البيع. يجب أن يكون السعر شاملاً لهذه الرسوم ورسوم التوصيل.",
)
```

---

### Admin Interface

#### 1. CategoryAdmin
```python
# main/admin.py

fieldsets = (
    ...
    (
        _("إعدادات السلة والحجز - Cart & Reservation"),
        {
            "fields": (
                "allow_cart",
                "cart_instructions",  # <- جديد
                "default_reservation_percentage",
                "min_reservation_amount",
                "max_reservation_amount",
                "require_admin_approval",
            ),
            "classes": ("collapse",),
        },
    ),
    ...
)
```

#### 2. SiteConfigurationAdmin
```python
# content/admin.py

fieldsets = (
    ...
    (
        "إعدادات رسوم خدمة السلة",
        {
            "fields": (
                "cart_service_fee_type",
                "cart_service_fixed_fee",
                "cart_service_percentage",
                "cart_service_instructions",
            ),
            "description": "إعدادات رسوم الخدمة التي يتم خصمها من الناشر عند البيع عبر المنصة",
        },
    ),
    ...
)
```

---

### Templates

#### ad_form.html (صفحة إنشاء الإعلان)

**إضافة قسم خيار السلة:**
```html
<!-- Cart/Shopping Cart Option -->
<div class="mb-4" id="cart-option-section" style="display: none;">
    <h4 class="mb-3">
        <i class="fas fa-shopping-cart me-2 text-primary"></i>
        {% trans "تفعيل خدمة السلة (اختياري)" %}
    </h4>
    <div class="card border-primary">
        <div class="card-body">
            <div class="form-check form-switch mb-3">
                <input class="form-check-input" type="checkbox"
                       id="publisher_cart_enabled" name="publisher_cart_enabled">
                <label class="form-check-label fw-bold" for="publisher_cart_enabled">
                    <i class="fas fa-cart-plus me-2 text-success"></i>
                    {% trans "أرغب في تفعيل السلة لهذا الإعلان" %}
                </label>
            </div>
            <div class="alert alert-warning" id="cart-instructions">
                <i class="fas fa-info-circle me-2"></i>
                <strong>{% trans "تنبيه هام:" %}</strong>
                <div id="cart-instructions-text" class="mt-2"></div>
            </div>
            <div class="alert alert-info">
                <ul class="mb-0 small">
                    <li>{% trans "سيتم تفعيل السلة بعد موافقة الإدارة واستلام المنتج" %}</li>
                    <li>{% trans "سيتم خصم رسوم خدمة من ثمن المنتج عند البيع عبر المنصة" %}</li>
                    <li>{% trans "يجب أن يكون السعر شاملاً لرسوم الخدمة والتوصيل" %}</li>
                    <li>{% trans "هذه الرسوم منفصلة عن نسبة الحجز من المشتري" %}</li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

**JavaScript للتحكم في عرض القسم:**
```javascript
// ========== Cart Option Handler ==========
function updateCartOption(categoryData) {
    const cartSection = document.getElementById('cart-option-section');
    const cartInstructionsText = document.getElementById('cart-instructions-text');

    if (categoryData && categoryData.allow_cart) {
        cartSection.style.display = 'block';
        if (categoryData.cart_instructions) {
            cartInstructionsText.textContent = categoryData.cart_instructions;
        } else {
            cartInstructionsText.textContent = '{{ site_config.cart_service_instructions }}';
        }
    } else {
        cartSection.style.display = 'none';
    }
}
```

---

### Views

#### classifieds_views.py - CreateClassifiedAdView

```python
def form_valid(self, form):
    # ... existing code ...

    # Get cart selection from POST
    publisher_cart_enabled = self.request.POST.get("publisher_cart_enabled") == "on"

    # Set cart flags
    if publisher_cart_enabled:
        form.instance.publisher_cart_enabled = True
        # Check if category allows cart
        if form.instance.category and form.instance.category.allow_cart:
            form.instance.allow_cart = False  # Will be enabled by admin
        else:
            form.instance.publisher_cart_enabled = False  # Reset if not supported

    # ... rest of the code ...
```

---

## 🎯 سير العمل (Workflow)

### 1. إعداد الأدمن

```
الأدمن Dashboard
    ↓
إعدادات الموقع (SiteConfiguration)
    ↓
إعدادات رسوم خدمة السلة:
    - نوع الرسوم: ثابتة أو نسبة مئوية
    - المبلغ الثابت: مثلاً 50 ج.م
    - أو النسبة: مثلاً 5%
    - التعليمات: نص مخصص للناشرين
```

```
الأدمن Dashboard
    ↓
إدارة الأقسام (Categories)
    ↓
تعديل قسم (مثل: منتجات إلكترونية)
    ↓
إعدادات السلة والحجز:
    ✓ السماح بالسلة: نعم
    - إرشادات السلة: (نص مخصص)
```

### 2. الناشر ينشئ إعلان

```
الناشر يفتح "إنشاء إعلان"
    ↓
يختار القسم (مثلاً: منتجات إلكترونية)
    ↓
يظهر قسم "تفعيل خدمة السلة"
    ↓
يضع ✓ على "أرغب في تفعيل السلة"
    ↓
يرى التنبيهات:
    - سيتم خصم رسوم خدمة
    - السعر يجب أن يكون شاملاً
    - التوصيل على حسابك
    ↓
ينشر الإعلان
    ↓
يتم حفظ: publisher_cart_enabled = True
```

### 3. الأدمن يراجع ويفعل

```
الأدمن Dashboard
    ↓
إدارة الإعلانات
    ↓
يرى الإعلان مع علامة "الناشر طلب السلة"
    ↓
يراجع المنتج
    ↓
يستلم المنتج فعلياً من الناشر
    ↓
يفعل: cart_enabled_by_admin = True
    ↓
الآن المشترون يمكنهم إضافة المنتج للسلة
```

### 4. البيع والخصم

```
مشتري يضيف للسلة
    ↓
يدفع (نسبة الحجز للمنصة)
    ↓
استلام المنتج مؤكد
    ↓
النظام يحسب رسوم الخدمة:
    - نوع ثابت: 50 ج.م
    - أو نسبة: 5% من السعر
    ↓
خصم الرسوم من مستحقات الناشر
    ↓
تحويل الباقي للناشر
```

---

## 📊 أمثلة عملية

### مثال 1: رسوم ثابتة

**الإعدادات:**
- نوع الرسوم: ثابتة
- المبلغ: 50 ج.م

**السيناريو:**
- سعر المنتج: 1000 ج.م
- المشتري يدفع: 1000 ج.م
- نسبة الحجز للمنصة: 100 ج.م (10%)
- رسوم الخدمة من الناشر: 50 ج.م
- الناشر يستلم: 1000 - 50 = **950 ج.م**

### مثال 2: نسبة مئوية

**الإعدادات:**
- نوع الرسوم: نسبة مئوية
- النسبة: 5%

**السيناريو:**
- سعر المنتج: 1000 ج.م
- المشتري يدفع: 1000 ج.م
- نسبة الحجز للمنصة: 100 ج.م (10%)
- رسوم الخدمة من الناشر: 1000 × 5% = 50 ج.م
- الناشر يستلم: 1000 - 50 = **950 ج.م**

---

## 🔒 Validation والتحققات

### في النموذج (Form Validation)

```python
# الناشر لا يمكنه تفعيل السلة إذا القسم لا يدعمها
if publisher_cart_enabled:
    if not form.instance.category.allow_cart:
        form.add_error(None, "هذا القسم لا يدعم السلة")
```

### في الأدمن (Admin Validation)

```python
# الأدمن يجب أن يستلم المنتج قبل التفعيل
if cart_enabled_by_admin and not product_received:
    raise ValidationError("يجب استلام المنتج أولاً")
```

---

## 📱 واجهة المستخدم

### للناشر (Publisher)

**في صفحة الإنشاء:**
```
┌─────────────────────────────────────────┐
│ 🛒 تفعيل خدمة السلة (اختياري)          │
├─────────────────────────────────────────┤
│ ☑ أرغب في تفعيل السلة لهذا الإعلان     │
│                                         │
│ ⚠ تنبيه هام:                           │
│ عند تفعيل السلة، سيتم خصم رسوم         │
│ خدمة من ثمن المنتج عند البيع.          │
│ يجب أن يكون السعر شاملاً لهذه          │
│ الرسوم ورسوم التوصيل.                  │
│                                         │
│ ℹ معلومات:                              │
│ • سيتم التفعيل بعد موافقة الإدارة      │
│ • سيتم خصم رسوم خدمة عند البيع         │
│ • السعر يجب أن يكون شاملاً              │
│ • الرسوم منفصلة عن نسبة الحجز          │
└─────────────────────────────────────────┘
```

### للأدمن (Admin)

**في قائمة الإعلانات:**
```
┌────────────────────────────────────────────────┐
│ الإعلان: آيفون 15 برو                         │
├────────────────────────────────────────────────┤
│ الناشر: أحمد محمد                             │
│ السعر: 25,000 ج.م                             │
│                                                │
│ 🛒 الناشر طلب تفعيل السلة                     │
│ ⏳ في انتظار استلام المنتج                    │
│                                                │
│ [✓ تم استلام المنتج]                          │
│ [تفعيل السلة]                                 │
└────────────────────────────────────────────────┘
```

---

## 🎨 الأقسام التي تدعم السلة

**يُنصح بتفعيل السلة في:**
- ✅ منتجات إلكترونية
- ✅ أجهزة منزلية
- ✅ أثاث
- ✅ ملابس وإكسسوارات
- ✅ كتب ومجلات
- ✅ ألعاب وهوايات

**لا يُنصح بتفعيل السلة في:**
- ❌ وظائف
- ❌ خدمات
- ❌ عقارات
- ❌ سيارات (تحتاج معاملة خاصة)
- ❌ دورات تدريبية

---

## 🧪 اختبار النظام

### خطوات الاختبار الكاملة

1. **إعداد الأدمن:**
   ```
   - افتح: /admin/content/siteconfiguration/
   - اضبط نوع الرسوم على "نسبة مئوية"
   - اضبط النسبة على 5
   - احفظ
   ```

2. **تفعيل قسم:**
   ```
   - افتح: /admin/main/category/
   - اختر قسم (مثل: منتجات إلكترونية)
   - ضع ✓ على "السماح بالسلة"
   - اكتب إرشادات مخصصة
   - احفظ
   ```

3. **إنشاء إعلان كناشر:**
   ```
   - سجل دخول كناشر
   - افتح: /create-ad/
   - اختر القسم المفعل
   - يجب أن يظهر قسم السلة
   - ضع ✓ على تفعيل السلة
   - أكمل الإعلان واحفظ
   ```

4. **تحقق من قاعدة البيانات:**
   ```sql
   SELECT id, title, publisher_cart_enabled, cart_enabled_by_admin
   FROM classified_ads
   WHERE id = <ad_id>;

   -- النتيجة المتوقعة:
   -- publisher_cart_enabled = TRUE
   -- cart_enabled_by_admin = FALSE
   ```

5. **تفعيل من الأدمن:**
   ```
   - افتح: /admin/main/classifiedad/
   - اختر الإعلان
   - ضع ✓ على "السلة مفعلة من الإدارة"
   - احفظ
   ```

6. **تحقق نهائي:**
   ```
   - افتح صفحة الإعلان كمشتري
   - يجب أن يظهر زر "أضف للسلة"
   - اضغط الزر
   - تحقق من السلة
   ```

---

## 🐛 استكشاف الأخطاء

### المشكلة: لا يظهر قسم السلة للناشر

**الحل:**
```
1. تحقق من allow_cart في القسم:
   Category.objects.get(id=X).allow_cart == True

2. تحقق من JavaScript في المتصفح:
   - افتح Developer Tools
   - ابحث عن updateCartOption
   - تحقق من console.log

3. تحقق من بيانات القسم في HTML:
   - ابحث عن data-allow-cart في select option
```

### المشكلة: الناشر فعّل السلة لكن لا تظهر للمشترين

**الحل:**
```
تحقق من:
1. publisher_cart_enabled = True (من الناشر) ✓
2. cart_enabled_by_admin = True (من الأدمن) ✗

الأدمن يجب أن يفعل cart_enabled_by_admin بعد استلام المنتج
```

### المشكلة: رسوم الخدمة لا تُخصم

**الحل:**
```
1. تحقق من إعدادات SiteConfiguration:
   - cart_service_fee_type محدد؟
   - cart_service_fixed_fee أو cart_service_percentage له قيمة؟

2. تحقق من كود حساب الرسوم في Order processing:
   - يجب أن يحسب الرسوم عند تأكيد البيع
```

---

## 📞 الدعم والتطوير المستقبلي

### ميزات مستقبلية مقترحة:

1. **إحصائيات السلة:**
   - عدد المنتجات المباعة عبر السلة
   - إجمالي الرسوم المحصلة
   - أكثر الناشرين استخداماً للسلة

2. **تقارير مالية:**
   - تقرير شهري بالرسوم المستحقة على كل ناشر
   - تصدير CSV/Excel

3. **إشعارات:**
   - إشعار للناشر عند تفعيل السلة من الأدمن
   - إشعار عند البيع وخصم الرسوم

4. **رسوم متدرجة:**
   - رسوم مختلفة حسب الأقسام
   - خصومات للناشرين النشطين

5. **تكامل مع الشحن:**
   - حساب تكلفة الشحن تلقائياً
   - تكامل مع شركات الشحن

---

## ✅ الخلاصة

تم تطبيق نظام سلة متكامل يوفر:

1. ✅ تحكم كامل من الأدمن (الأقسام، الرسوم، التفعيل)
2. ✅ خيار اختياري للناشر عند الإنشاء
3. ✅ إرشادات وتنبيهات واضحة
4. ✅ رسوم مرنة (ثابتة أو نسبية)
5. ✅ فصل بين نسبة الحجز ورسوم الخدمة
6. ✅ Validation شامل للتأكد من الاستخدام الصحيح

النظام جاهز للاستخدام الفوري! 🎉
