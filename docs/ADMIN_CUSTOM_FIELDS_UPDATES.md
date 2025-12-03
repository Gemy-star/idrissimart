# تحديثات نظام الحقول المخصصة في صفحات الإدارة
## Admin Custom Fields System Updates

تاريخ التحديث: 2 ديسمبر 2025

## ✅ الملفات المحدثة / Updated Files

### 1. `main/views.py`

#### AdminCategoryCustomFieldsView (الحقول المخصصة للقسم)

**تم التحديث:**
- ✅ `GET` method - الآن يستخدم `CategoryCustomField` بدلاً من `CustomField.objects.filter(category=...)`
- ✅ `POST` method - ينشئ علاقات `CategoryCustomField` ويدعم `CustomFieldOption`
- ✅ يدعم الخيارات من جدول منفصل بدلاً من النص المفصول بفواصل

**التغييرات الرئيسية:**
```python
# قديم (Old):
fields = CustomField.objects.filter(category=category).order_by("order")

# جديد (New):
category_fields = CategoryCustomField.objects.filter(
    category=category
).select_related("custom_field").prefetch_related(
    "custom_field__field_options"
).order_by("order")
```

#### AdminCustomFieldsView (قائمة الحقول)

**تم التحديث:**
- ✅ `get_queryset()` - يستخدم `prefetch_related('categories')` بدلاً من `select_related('category')`
- ✅ `get_context_data()` - يستخدم `category_fields` لعرض العلاقات بين الأقسام والحقول
- ✅ يدعم البحث عبر أقسام متعددة

**التغييرات الرئيسية:**
```python
# قديم (Old):
queryset = CustomField.objects.select_related("category").order_by("category__name", "order")

# جديد (New):
queryset = CustomField.objects.prefetch_related("categories", "field_options").order_by("name")
```

#### AdminCustomFieldGetView (جلب بيانات حقل)

**تم التحديث:**
- ✅ يجلب الخيارات من `CustomFieldOption` بدلاً من حقل `options`
- ✅ يعيد `category_ids` (متعددة) بدلاً من `category_id` (واحد)
- ✅ يدعم الحقول المشتركة بين عدة أقسام

#### AdminCustomFieldSaveView (حفظ حقل)

**تم التحديث:**
- ✅ لا يتطلب قسم إلزامياً (الحقل يمكن أن يكون عام)
- ✅ ينشئ/يحدث `CategoryCustomField` عند تحديد قسم
- ✅ ينشئ `CustomFieldOption` للخيارات في جدول منفصل
- ✅ يدعم الفواصل المؤقتة للتوافق مع الواجهة الحالية

**التغييرات الرئيسية:**
```python
# قديم (Old):
field.category = get_object_or_404(Category, pk=category_id)
field.options = request.POST.get("options", field.options)

# جديد (New):
CategoryCustomField.objects.update_or_create(
    category=category,
    custom_field=field,
    defaults={"is_required": field.is_required, "order": order}
)
CustomFieldOption.objects.create(
    custom_field=field,
    label_ar=option_value,
    value=option_value,
    order=index
)
```

#### ClassifiedAdDetailView (عرض الإعلان)

**تم التحديث:**
- ✅ يستخدم `CategoryCustomField` بدلاً من `custom_field_schema`
- ✅ يجلب تسميات الحقول من `CustomField.label_ar`
- ✅ يعرض الحقول المخصصة المحفوظة في الإعلان

---

### 2. `main/forms.py`

#### ClassifiedAdForm

**تم التحديث:**
- ✅ `add_custom_fields()` - يستخدم `CategoryCustomField` بدلاً من `custom_field_schema`
- ✅ يجلب الخيارات من `CustomFieldOption` بدلاً من قائمة بسيطة
- ✅ `save()` - يحفظ القيم مع البادئة `custom_` لاسم الحقل
- ✅ يدعم جميع أنواع الحقول (select, radio, checkbox, date, number, textarea, text)

**التغييرات الرئيسية:**
```python
# قديم (Old):
schema = category.custom_field_schema or []
for field_schema in schema:
    field_name = field_schema.get("name")
    options = field_schema.get("options", [])

# جديد (New):
category_fields = CategoryCustomField.objects.filter(
    category=category, is_active=True
).select_related('custom_field').prefetch_related('custom_field__field_options')

for cf in category_fields:
    field = cf.custom_field
    field_name = f"custom_{field.name}"
    options = field.field_options.filter(is_active=True).order_by('order')
```

---

## 🔄 التوافق مع الواجهة الحالية / Backward Compatibility

**معالجة الخيارات:**
- الواجهة الحالية ترسل الخيارات مفصولة بفواصل: `"جديد,مستعمل,للإيجار"`
- الكود الجديد يقبل هذا التنسيق ويحوله تلقائياً إلى سجلات `CustomFieldOption`
- عند الجلب، يتم دمج الخيارات بفواصل للتوافق

**أسماء الحقول:**
- في النماذج: يتم إضافة بادئة `custom_` لجميع الحقول المخصصة
- مثال: `condition` → `custom_condition`
- هذا لتجنب التعارض مع حقول النموذج الأساسية

---

## 📝 ملاحظات للمطورين / Developer Notes

### استعلامات محسنة / Optimized Queries

استخدم دائماً:
```python
# للحصول على حقول قسم
CategoryCustomField.objects.filter(category=category, is_active=True)\
    .select_related('custom_field')\
    .prefetch_related('custom_field__field_options')\
    .order_by('order')
```

### عرض الخيارات / Display Options

```python
# في القوالب
{% for cf in category_fields %}
    <label>{{ cf.custom_field.label }}</label>
    {% if cf.custom_field.field_type == 'select' %}
        <select name="custom_{{ cf.custom_field.name }}">
            {% for option in cf.custom_field.field_options.all %}
                <option value="{{ option.value }}">{{ option.label }}</option>
            {% endfor %}
        </select>
    {% endif %}
{% endfor %}
```

### حفظ القيم / Save Values

```python
# الحقول المخصصة تُحفظ في JSONField
ad.custom_fields = {
    'custom_condition': 'new',
    'custom_year': '2024',
    'custom_color': 'blue'
}
ad.save()
```

---

## ⚠️ تحذيرات هامة / Important Warnings

1. **لا تستخدم `custom_field_schema` بعد الآن:**
   - هذا الحقل قديم وقد يتم حذفه في المستقبل
   - استخدم `CategoryCustomField` بدلاً منه

2. **الحقول لها أسماء فريدة عالمياً:**
   - `CustomField.name` يجب أن يكون فريد في النظام بأكمله
   - لا يمكن إنشاء حقلين بنفس الاسم حتى لو في أقسام مختلفة

3. **الخيارات في جدول منفصل:**
   - لا تحفظ الخيارات في حقل `options` نصي
   - استخدم `CustomFieldOption` دائماً

4. **العلاقات M2M:**
   - الحقل يمكن أن يكون في عدة أقسام
   - استخدم `CategoryCustomField` للربط

---

## ✅ قائمة التحقق / Checklist

- [x] تحديث `AdminCategoryCustomFieldsView.get()`
- [x] تحديث `AdminCategoryCustomFieldsView.post()`
- [x] تحديث `AdminCustomFieldsView.get_queryset()`
- [x] تحديث `AdminCustomFieldsView.get_context_data()`
- [x] تحديث `AdminCustomFieldGetView.get()`
- [x] تحديث `AdminCustomFieldSaveView.post()`
- [x] تحديث `ClassifiedAdForm.add_custom_fields()`
- [x] تحديث `ClassifiedAdForm.save()`
- [x] تحديث `ClassifiedAdDetailView` (عرض الحقول)
- [x] اختبار النظام بدون أخطاء: `python manage.py check` ✅
- [ ] اختبار إنشاء حقل مخصص جديد في الإدارة
- [ ] اختبار إضافة إعلان مع حقول مخصصة
- [ ] اختبار عرض الإعلان مع الحقول المخصصة
- [ ] تحديث قوالب HTML إذا لزم الأمر

---

## 🎯 الخطوات التالية / Next Steps

1. **اختبار واجهة الإدارة:**
   - افتح `/admin/custom-fields/`
   - جرب إنشاء حقل جديد
   - تأكد من ظهور الخيارات بشكل صحيح

2. **اختبار إضافة إعلان:**
   - اختر قسم له حقول مخصصة
   - تأكد من ظهور الحقول
   - املأ البيانات واحفظ

3. **مراجعة القوالب:**
   - تحقق من `admin_dashboard/custom_fields.html`
   - قد تحتاج تحديثات للواجهة

4. **التوثيق:**
   - راجع `docs/CUSTOM_FIELDS_REDESIGN_GUIDE.md`
   - أضف أمثلة إضافية إذا لزم

---

تم بنجاح ✅
