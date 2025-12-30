# تحديثات نظام الحقول المخصصة (Custom Fields System)

## التاريخ: 2024
## الإصدار: 2.0

---

## 📋 ملخص التحديثات

تم تطوير نظام الحقول المخصصة بشكل كامل لإضافة مرونة أكبر في إدارة الحقول وعرضها في مناطق مختلفة من الموقع.

---

## ✨ الميزات الجديدة

### 1. خيار "في الفلاتر" (Show in Filters)
- إضافة حقل جديد `show_in_filters` إلى نموذج `CategoryCustomField`
- يسمح بتحديد ما إذا كان الحقل سيظهر في فلاتر البحث على صفحات الأقسام
- يمكن التحكم به بشكل مستقل عن خيار "على البطاقة"

### 2. إضافة الحقل لأقسام متعددة (Bulk Category Assignment)
- واجهة جديدة لإضافة حقل مخصص لأقسام متعددة دفعة واحدة
- عرض شجري للأقسام مع إمكانية اختيار متعدد
- تحديد خصائص الحقل (مطلوب، على البطاقة، في الفلاتر) لجميع الأقسام المختارة

---

## 🔧 التغييرات التقنية

### قاعدة البيانات

#### Migration: `0037_add_show_in_filters_to_category_custom_field`
```python
# main/models.py - CategoryCustomField
show_in_filters = models.BooleanField(
    default=False,
    verbose_name=_("إظهار في الفلاتر"),
    help_text=_("هل يظهر هذا الحقل في فلاتر البحث؟")
)
```

### Models

**الحقول المتاحة الآن في `CategoryCustomField`:**
- `show_on_card` - عرض الحقل على بطاقة الإعلان
- `show_in_filters` - عرض الحقل في فلاتر البحث
- `is_required` - هل الحقل مطلوب عند إنشاء إعلان
- `is_active` - هل الحقل نشط
- `order` - ترتيب الحقل

### Views

#### AdminCustomFieldAddToCategoriesView (جديد)
```python
# main/views.py
class AdminCustomFieldAddToCategoriesView(SuperadminRequiredMixin, View):
    """
    AJAX view لإضافة حقل مخصص لأقسام متعددة دفعة واحدة

    POST Parameters:
        - field_id: معرف الحقل المخصص
        - category_ids: قائمة معرفات الأقسام
        - is_required: هل الحقل مطلوب
        - show_on_card: هل يظهر على البطاقة
        - show_in_filters: هل يظهر في الفلاتر
    """
```

#### AdminCategoryCustomFieldsView (محدث)
- إضافة معالجة `show_in_filters` في GET و POST
- إرجاع بيانات الحقل مع خيار الفلاتر
- حفظ تحديثات show_in_filters

### Templates

#### categories.html (محدث)
**التغييرات:**
1. إضافة checkbox "في الفلاتر" في `displayCustomFields()`
2. إضافة checkbox "في الفلاتر" في `addCustomField()`
3. تحديث `saveCustomFields()` لإرسال بيانات `show_in_filters`
4. تقليل عرض الأعمدة لاستيعاب الحقل الجديد (col-md-3 → col-md-2 للخيارات)
5. إضافة `g-2` للصفوف لتباعد أفضل

#### custom_fields.html (محدث)
**التغييرات:**
1. إضافة عمود "في الفلاتر" في جدول العرض
2. إضافة زر "إضافة لأقسام أخرى" لكل حقل
3. إضافة modal جديد `addToCategoriesModal` للإضافة الجماعية
4. عرض شجري تفاعلي للأقسام
5. إظهار الأقسام الموجودة بالفعل كـ "معطلة" مع badge "موجود"

### JavaScript Functions

#### openAddToCategoriesModal(fieldId)
```javascript
// فتح نافذة إضافة الحقل لأقسام متعددة
// يجلب بيانات الحقل ويبني شجرة الأقسام
```

#### buildCategoryTree(existingCategoryIds)
```javascript
// بناء شجرة الأقسام بشكل تفاعلي
// تعطيل الأقسام الموجودة بالفعل
// عرض الأقسام الرئيسية والفرعية
```

#### addFieldToCategories()
```javascript
// إرسال طلب AJAX لإضافة الحقل للأقسام المختارة
// معالجة النجاح والأخطاء
```

### URLs

```python
# main/urls.py
path(
    "admin/custom-fields/add-to-categories/",
    views.AdminCustomFieldAddToCategoriesView.as_view(),
    name="admin_custom_field_add_to_categories",
)
```

---

## 📱 واجهة المستخدم

### صفحة إدارة الأقسام (categories.html)

**قبل:**
```
| اسم الحقل | النوع | الخيارات | مطلوب | على البطاقة | حذف |
```

**بعد:**
```
| اسم الحقل | النوع | الخيارات | مطلوب | على البطاقة | في الفلاتر | حذف |
```

### صفحة الحقول المخصصة (custom_fields.html)

**الأعمدة الجديدة:**
1. **في الفلاتر**: أيقونة filter لإظهار حالة الحقل في الفلاتر
2. **إجراءات**: زر أخضر جديد "إضافة لأقسام أخرى" مع أيقونة `plus-circle`

**Modal الإضافة الجماعية:**
- عنوان واضح مع اسم الحقل
- شجرة أقسام قابلة للتمرير (max-height: 400px)
- الأقسام الموجودة تظهر معطلة مع badge "موجود"
- ثلاثة خيارات: مطلوب، على البطاقة، في الفلاتر
- أزرار إلغاء وحفظ

---

## 🎯 حالات الاستخدام

### 1. إضافة حقل "السعر" للفلاتر فقط
```
✓ في الفلاتر
✗ على البطاقة
```
يظهر في فلاتر البحث ولكن ليس على بطاقة الإعلان

### 2. إضافة حقل "الموديل" للبطاقة والفلاتر
```
✓ في الفلاتر
✓ على البطاقة
```
يظهر في كلا المكانين

### 3. إضافة حقل "رقم الهاتف" للبطاقة فقط
```
✗ في الفلاتر
✓ على البطاقة
```
يظهر على البطاقة فقط وليس في الفلاتر

### 4. إضافة حقل لـ 10 أقسام دفعة واحدة
1. اذهب إلى صفحة الحقول المخصصة
2. اضغط زر "إضافة لأقسام أخرى" للحقل المراد
3. اختر الأقسام من الشجرة
4. حدد الخصائص (مطلوب، على البطاقة، في الفلاتر)
5. احفظ - يتم إضافة الحقل لجميع الأقسام بنفس الخصائص

---

## 🔍 مسار البيانات

### عند عرض حقول قسم:
```
AdminCategoryCustomFieldsView (GET)
    ↓
CategoryCustomField.objects.filter(category=category)
    ↓
{
    "id": 1,
    "name": "year",
    "label_ar": "السنة",
    "type": "number",
    "show_on_card": true,
    "show_in_filters": true,  ← الحقل الجديد
    "is_required": false
}
    ↓
displayCustomFields() في JavaScript
    ↓
عرض checkbox للفلاتر
```

### عند حفظ حقول:
```
JavaScript: saveCustomFields()
    ↓
جمع بيانات show_in_filters من checkbox
    ↓
POST إلى AdminCategoryCustomFieldsView
    ↓
CategoryCustomField.objects.update_or_create(
    ...,
    show_in_filters=data.get('show_in_filters')
)
```

### عند إضافة حقل لأقسام متعددة:
```
زر "إضافة لأقسام أخرى"
    ↓
openAddToCategoriesModal(fieldId)
    ↓
جلب بيانات الحقل من API
    ↓
buildCategoryTree() - بناء شجرة الأقسام
    ↓
اختيار الأقسام + تحديد الخصائص
    ↓
addFieldToCategories()
    ↓
POST إلى AdminCustomFieldAddToCategoriesView
    ↓
Loop على الأقسام المختارة:
    CategoryCustomField.objects.update_or_create(...)
    ↓
إرجاع عدد الأقسام المضافة
```

---

## 🧪 اختبار الميزات

### اختبار 1: عرض وحفظ خيار الفلاتر
```python
# في صفحة إدارة قسم
1. افتح قسم
2. اضغط "إدارة الحقول المخصصة"
3. أضف حقل جديد
4. حدد checkbox "في الفلاتر"
5. احفظ
6. تحقق من حفظ القيمة في قاعدة البيانات
```

### اختبار 2: إضافة حقل لأقسام متعددة
```python
# في صفحة الحقول المخصصة
1. اختر حقل موجود
2. اضغط زر "إضافة لأقسام أخرى"
3. اختر 3 أقسام
4. حدد "في الفلاتر" و "على البطاقة"
5. احفظ
6. تحقق من إنشاء 3 سجلات CategoryCustomField
7. تحقق من show_in_filters=True لكل سجل
```

### اختبار 3: الأقسام الموجودة
```python
# في modal الإضافة الجماعية
1. اختر حقل مرتبط بـ 2 أقسام
2. افتح modal الإضافة
3. تحقق من تعطيل checkbox الأقسام الموجودة
4. تحقق من ظهور badge "موجود"
5. لا يمكن إلغاء تحديدها
```

---

## 📊 قاعدة البيانات

### مثال على السجلات:

**قبل التحديث:**
```sql
CategoryCustomField:
id | category_id | custom_field_id | is_required | show_on_card
1  | 5          | 10             | False       | True
```

**بعد التحديث:**
```sql
CategoryCustomField:
id | category_id | custom_field_id | is_required | show_on_card | show_in_filters
1  | 5          | 10             | False       | True         | False
2  | 6          | 10             | False       | False        | True
3  | 7          | 10             | False       | True         | True
```

---

## 🚀 الخطوات التالية (مستقبلاً)

1. **استخدام show_in_filters في الفلاتر الفعلية**
   - تحديث صفحات عرض الأقسام لعرض فقط الحقول التي show_in_filters=True
   - بناء فلاتر ديناميكية من الحقول

2. **API لجلب حقول الفلاتر**
   ```python
   def get_filter_fields_for_category(category_id):
       return CategoryCustomField.objects.filter(
           category_id=category_id,
           show_in_filters=True,
           is_active=True
       )
   ```

3. **تحسينات UI**
   - إضافة drag-and-drop لترتيب الحقول
   - معاينة فورية لكيفية ظهور الحقل
   - نسخ إعدادات حقل من قسم لآخر

4. **Validation**
   - التحقق من عدم تكرار نفس الحقل في نفس القسم
   - تحذير عند إضافة حقل موجود
   - حد أقصى لعدد الحقول لكل قسم

---

## 📝 ملاحظات للمطورين

### هام:
1. ✅ Migration تم تطبيقه بنجاح (0037)
2. ✅ جميع الاختبارات النحوية نجحت (python manage.py check)
3. ✅ المسارات (URLs) محدثة ومسجلة
4. ✅ JavaScript يستخدم Django template tags للـ URLs

### نقاط الانتباه:
- عند حذف حقل مخصص، سيتم حذف جميع ارتباطاته بالأقسام (CASCADE)
- عند حذف قسم، سيتم حذف جميع حقوله المخصصة (CASCADE)
- الحقول معطلة (is_active=False) لا تظهر للمستخدمين النهائيين

---

## 👥 الأدوار والصلاحيات

**من يمكنه استخدام هذه الميزات؟**
- ✅ Superadmin فقط
- ❌ Admin عادي
- ❌ Publisher
- ❌ User

جميع الـ views محمية بـ `@superadmin_required` أو `SuperadminRequiredMixin`

---

## 🐛 المشاكل المحتملة والحلول

### مشكلة: modal الإضافة الجماعية لا يفتح
**الحل:**
- تحقق من Bootstrap 5 محمل بشكل صحيح
- تحقق من console للأخطاء JavaScript
- تحقق من CATEGORIES_HIERARCHY متاح في الصفحة

### مشكلة: لا يتم حفظ show_in_filters
**الحل:**
- تحقق من اسم الـ checkbox في JavaScript: `name="field_show_in_filters"`
- تحقق من saveCustomFields() يجمع القيمة بشكل صحيح
- تحقق من Migration تم تطبيقه

### مشكلة: CSRF token error
**الحل:**
- تحقق من getCookie('csrftoken') يعمل
- تحقق من header Content-Type صحيح
- تحقق من Django CSRF middleware مفعل

---

## 📞 الدعم

للأسئلة أو المشاكل المتعلقة بنظام الحقول المخصصة:
1. راجع هذا الملف أولاً
2. تحقق من console.log في المتصفح
3. تحقق من Django debug toolbar
4. راجع الكود في:
   - `main/models.py` (CategoryCustomField)
   - `main/views.py` (AdminCustomFieldAddToCategoriesView)
   - `templates/admin_dashboard/categories.html`
   - `templates/admin_dashboard/custom_fields.html`

---

**تم التحديث بنجاح! ✨**
