# ميزة عرض الحقول المخصصة على بطاقة الإعلان
# Custom Fields Display on Ad Card Feature

## نظرة عامة | Overview

تتيح هذه الميزة للمسؤولين تحديد الحقول المخصصة التي يجب عرضها على بطاقة الإعلان من الخارج (في صفحات القوائم) بدلاً من إظهارها فقط في صفحة التفاصيل.

This feature allows administrators to specify which custom fields should be displayed on the ad card externally (in listing pages) instead of only showing them on the detail page.

---

## التغييرات التقنية | Technical Changes

### 1. Database Schema

**ملف:** `main/models.py`

تم إضافة حقل جديد إلى model `CategoryCustomField`:

```python
show_on_card = models.BooleanField(
    default=False,
    verbose_name=_("إظهار على بطاقة الإعلان"),
    help_text=_("إظهار قيمة هذا الحقل على بطاقة الإعلان من الخارج")
)
```

**Migration:** `0017_add_show_on_card_to_category_custom_field.py`

---

### 2. Model Method

تم إضافة method جديد في `ClassifiedAd` model:

```python
def get_custom_fields_for_card(self):
    """Get custom fields that should be displayed on the ad card"""
    # Returns list of dicts with: label, value, icon
```

هذا الـ method:
- يحصل على جميع الحقول المخصصة للقسم حيث `show_on_card=True`
- يعالج القيم المخزنة في `custom_fields` JSON
- للحقول من نوع select/radio، يحصل على label بدلاً من value
- للحقول من نوع checkbox، يحول القيمة إلى "نعم"/"لا"
- يرجع array من objects تحتوي على: `label`, `value`, `icon`

---

### 3. Template Updates

**ملف:** `templates/partials/_ad_card_component.html`

تم استبدال:
```django-html
{% if ad.custom_fields.condition %}
<span class="feature-tag condition-tag">
    <i class="fas fa-box-open"></i>
    <span>{{ ad.custom_fields.condition }}</span>
</span>
{% endif %}
```

بـ:
```django-html
{% with custom_fields_for_card=ad.get_custom_fields_for_card %}
    {% for field in custom_fields_for_card %}
    <span class="feature-tag custom-field-tag">
        <i class="fas {{ field.icon }}"></i>
        <span>{{ field.label }}: {{ field.value }}</span>
    </span>
    {% endfor %}
{% endwith %}
```

---

### 4. CSS Styling

**ملف:** `static/css/style.css`

تم إضافة styles للـ `.custom-field-tag`:

```css
.custom-field-tag {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e3a8a;
  border-color: #93c5fd;
}

.custom-field-tag:hover {
  background: linear-gradient(135deg, #bfdbfe, #93c5fd);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

[data-theme='dark'] .custom-field-tag {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.15));
  color: #93c5fd;
  border-color: rgba(59, 130, 246, 0.4);
}
```

---

### 5. Admin Interface

#### A. لوحة الحقول المخصصة (Custom Fields Panel)

**ملف:** `templates/admin_dashboard/custom_fields.html`

تم إضافة عمود "على البطاقة" في جدول العرض:
```django-html
<th>{% trans "على البطاقة" %}</th>
...
<td>
    {% if cf.show_on_card %}
        <i class="fas fa-eye text-primary"></i>
    {% else %}
        <i class="fas fa-eye-slash text-muted"></i>
    {% endif %}
</td>
```

#### B. صفحة إدارة الأقسام (Categories Management)

**ملف:** `templates/admin_dashboard/categories.html`

تم تحديث:
1. **`addCustomField()` function:** أضيف checkbox "على البطاقة"
2. **`displayCustomFields()` function:** يعرض حالة show_on_card الحالية
3. **`saveCustomFields()` function:** يرسل قيمة show_on_card للـ backend

```javascript
const showOnCard = item.querySelector('[name="field_show_on_card"]').checked;
```

#### C. Backend API

**ملف:** `main/views.py` - `AdminCategoryCustomFieldsView`

**GET method:** يرجع `show_on_card` في response:
```python
fields_data.append({
    ...
    "show_on_card": cf.show_on_card,
})
```

**POST method:** يحفظ `show_on_card`:
```python
CategoryCustomField.objects.create(
    ...
    show_on_card=field_data.get("show_on_card", False),
)
```

---

## كيفية الاستخدام | Usage Guide

### للمسؤولين | For Administrators

1. **الذهاب إلى صفحة الأقسام:**
   - لوحة التحكم > الأقسام > إدارة الحقول المخصصة

2. **إضافة/تعديل حقل مخصص:**
   - عند إضافة حقل جديد، ستجد checkbox جديد: **"على البطاقة"**
   - إذا فعّلت هذا الخيار، سيظهر الحقل على بطاقة الإعلان في صفحات القوائم

3. **مثال عملي:**
   - حقل: "الماركة" (Brand)
   - نوع: اختيار (Select)
   - خيارات: "سوكيا, تويوتا, نيسان"
   - ✅ **على البطاقة:** مُفعّل

   النتيجة: عند نشر إعلان سيارة ماركة "سوكيا"، ستظهر "الماركة: سوكيا" على البطاقة

### للمستخدمين | For Users

عند تصفح الإعلانات:
- ستظهر قيم الحقول المخصصة المُفعّلة على البطاقات مباشرة
- يمكن رؤية معلومات إضافية دون الحاجة لفتح صفحة التفاصيل
- تحسين تجربة البحث والتصفح

---

## أمثلة الاستخدام | Use Cases

### 1. إعلانات السيارات
- **الماركة** (Brand): سوكيا، تويوتا، نيسان
- **سنة الصنع** (Year): 2020، 2021، 2022
- **الحالة** (Condition): جديد، مستعمل

### 2. إعلانات العقارات
- **نوع العقار** (Property Type): شقة، فيلا، أرض
- **عدد الغرف** (Rooms): 2، 3، 4
- **المساحة** (Area): 150m²، 200m²

### 3. إعلانات الإلكترونيات
- **الماركة** (Brand): Samsung، Apple، Huawei
- **الحالة** (Condition): جديد، مستعمل، معاد تجديده

---

## الأداء والأمثلة | Performance Considerations

### Database Queries

الـ method `get_custom_fields_for_card()` يستخدم:
```python
.select_related('custom_field')  # Join للحد من queries
.order_by('order')                # ترتيب حسب الأولوية
```

### Caching (اختياري للتحسين المستقبلي)

يمكن إضافة caching للحقول المخصصة:
```python
from django.core.cache import cache

def get_custom_fields_for_card(self):
    cache_key = f'ad_fields_card_{self.category_id}'
    fields = cache.get(cache_key)
    if fields is None:
        # ... الكود الحالي ...
        cache.set(cache_key, fields, 3600)  # 1 hour
    return fields
```

---

## الاختبار | Testing

### اختبار يدوي | Manual Testing

1. ✅ إنشاء حقل مخصص جديد مع تفعيل "على البطاقة"
2. ✅ ربط الحقل بقسم معين
3. ✅ نشر إعلان في هذا القسم مع تعبئة الحقل
4. ✅ التحقق من ظهور القيمة على بطاقة الإعلان في صفحة القوائم
5. ✅ إلغاء تفعيل "على البطاقة" والتحقق من عدم الظهور

### اختبار الـ Dark Mode

✅ تم اختبار الـ styles في الوضع الفاتح والداكن

---

## الملفات المتأثرة | Affected Files

```
main/
  ├── models.py                                    [✅ Updated]
  ├── views.py                                     [✅ Updated]
  └── migrations/
      └── 0017_add_show_on_card...py               [✅ New]

templates/
  ├── partials/
  │   └── _ad_card_component.html                 [✅ Updated]
  └── admin_dashboard/
      ├── custom_fields.html                      [✅ Updated]
      └── categories.html                         [✅ Updated]

static/
  └── css/
      └── style.css                               [✅ Updated]

docs/
  └── CUSTOM_FIELDS_CARD_DISPLAY.md               [✅ New]
```

---

## الخلاصة | Summary

✅ **تم بنجاح:**
- إضافة حقل `show_on_card` إلى database
- تحديث admin interface لتمكين/تعطيل الميزة
- إضافة method لاسترجاع الحقول المناسبة
- تحديث template لعرض الحقول ديناميكياً
- إضافة CSS styling كامل (light + dark mode)
- توثيق كامل للميزة

✅ **الفوائد:**
- تحسين تجربة المستخدم في تصفح الإعلانات
- عرض معلومات إضافية دون الحاجة لفتح التفاصيل
- مرونة كاملة للمسؤولين في تحديد الحقول المعروضة
- أداء محسّن باستخدام select_related

---

## الصيانة المستقبلية | Future Maintenance

### إضافات محتملة:
1. **تحديد عدد أقصى للحقول المعروضة** (مثلاً 3 حقول فقط)
2. **ترتيب مخصص للحقول على البطاقة** (منفصل عن ترتيب الإدخال)
3. **أيقونات مخصصة لكل حقل** (حالياً يستخدم icon من CustomField)
4. **عرض مختصر للقيم الطويلة** (truncate بعد عدد معين من الأحرف)

### كود مقترح للتحسينات:
```python
# في CategoryCustomField model
card_display_order = models.PositiveIntegerField(
    default=0,
    verbose_name=_("ترتيب العرض على البطاقة")
)

# في get_custom_fields_for_card method
MAX_FIELDS_ON_CARD = 3
fields_to_display = fields_to_display[:MAX_FIELDS_ON_CARD]
```

---

**تاريخ الإنشاء:** 2024
**الحالة:** ✅ مكتمل ومفعّل
**التوافق:** Django 5.2.7+
