# لوحة تحكم الأعضاء ونظام توثيق العضوية
## Member Dashboard & Account Verification System

## نظرة عامة | Overview

تم إضافة نظام متكامل للوحة تحكم الأعضاء مع نظام توثيق العضوية لمنح المستخدمين المزيد من المصداقية والثقة.

---

## لوحة تحكم الأعضاء | Member Dashboard

### الصفحات المتاحة

#### 1. لوحة التحكم الرئيسية (My Ads)
- **URL**: `/classifieds/my-ads/`
- **View**: `MyClassifiedAdsView`
- **Template**: `templates/classifieds/my_ads_list.html`

**المميزات:**
- عرض جميع إعلانات المستخدم
- إحصائيات سريعة (إجمالي الإعلانات، النشطة، المعلقة، المنتهية)
- عرض معلومات الباقة النشطة (إذا كانت موجودة)
- معلومات تفصيلية عن مميزات الباقة وأسعار الخدمات

#### 2. صفحة الإحصائيات (Reports)
- **URL**: `/publisher/reports/`
- **View**: `PublisherReportsView`
- **Template**: `templates/classifieds/publisher_reports.html`

**المميزات:**
- إحصائيات شاملة لأداء الإعلانات
- عدد المشاهدات والتفاعلات
- الإعلانات الأكثر أداءً
- إحصائيات حسب القسم والحالة

#### 3. صفحة الإعدادات (Settings)
- **URL**: `/publisher/settings/`
- **View**: `PublisherSettingsView`
- **Template**: `templates/dashboard/publisher_settings.html`

**المميزات:**
- تعديل الملف الشخصي
- إعدادات الإشعارات
- إعدادات الأمان
- إدارة الحساب

---

## نظام توثيق العضوية | Account Verification System

### نموذج البيانات | Data Model

#### UserVerificationRequest Model
```python
class UserVerificationRequest(models.Model):
    user = ForeignKey(User)
    document_type = CharField(max_length=30, choices=DocumentType.choices)
    document_file = FileField(upload_to="verification_documents/")
    additional_documents = JSONField(default=list)
    notes = TextField(blank=True)
    status = CharField(choices=VerificationStatus.choices)
    admin_notes = TextField(blank=True)
    reviewed_by = ForeignKey(User, null=True)
    reviewed_at = DateTimeField(null=True)
```

### أنواع المستندات المقبولة | Accepted Document Types

1. **بطاقة الهوية** - National ID
2. **جواز السفر** - Passport
3. **السجل التجاري** - Commercial Register
4. **شهادة ضريبية** - Tax Certificate
5. **رخصة مهنية** - Professional License
6. **أخرى** - Other

### حالات التوثيق | Verification Statuses

```python
class VerificationStatus(models.TextChoices):
    UNVERIFIED = "unverified", "غير موثق"
    PENDING = "pending", "قيد المراجعة"
    VERIFIED = "verified", "موثق"
    REJECTED = "rejected", "مرفوض"
```

---

## الروابط في القوائم | Menu Links

### قائمة المستخدم الرئيسية (Desktop)
تظهر عند النقر على أيقونة المستخدم في الهيدر:

```
┌─ لوحة التحكم ─────────────────┐
│ • لوحة التحكم                  │
│ • إعلاناتي                     │
│ • رسائلي                       │
├─────────────────────────────────┤
│ • توثيق الحساب / حساب موثق    │
│ • الإعدادات                    │
├─────────────────────────────────┤
│ • تسجيل الخروج                 │
└─────────────────────────────────┘
```

### القائمة المحمولة (Mobile)
تظهر في القائمة الجانبية على الأجهزة المحمولة:

```
- الرئيسية
- الأقسام
- المدونة
─────────────────
- لوحة التحكم
- إعلاناتي
- رسائلي
─────────────────
- توثيق الحساب
- الإعدادات
- عمليات البحث المحفوظة
─────────────────
- تسجيل الخروج
```

---

## صفحة توثيق العضوية | Verification Request Page

### URL
- `/verification/request/`
- Route Name: `main:verification_request`

### المميزات | Features

#### 1. عرض فوائد التوثيق
```
✓ شارة "موثق" على جميع إعلاناتك
✓ زيادة الثقة مع المشترين
✓ أولوية في نتائج البحث
✓ إمكانية الوصول لمميزات حصرية
```

#### 2. نموذج تقديم الطلب
- اختيار نوع المستند
- رفع صورة المستند
- إضافة ملاحظات (اختياري)

#### 3. تتبع حالة الطلب
- إذا كان الطلب قيد المراجعة → عرض صفحة الانتظار
- إذا كان موثقاً → التوجيه للإعدادات
- إذا كان مرفوضاً → إمكانية تقديم طلب جديد

---

## مسار توثيق العضوية | Verification Workflow

```
[مستخدم غير موثق]
        ↓
[تقديم طلب التوثيق]
        ↓
[رفع المستندات المطلوبة]
        ↓
[الحالة: قيد المراجعة]
        ↓
    ┌───────┐
    │ الإدارة │
    └───────┘
        ↓
   ┌────┴────┐
   ↓         ↓
[قبول]   [رفض]
   ↓         ↓
[موثق]  [إشعار الرفض]
```

---

## إشعارات التوثيق | Verification Notifications

### عند تقديم الطلب
```
تم إرسال طلب التوثيق بنجاح!
سنقوم بمراجعة طلبك خلال 2-3 أيام عمل.
```

### عند الموافقة
```
تهانينا! تم توثيق حسابك بنجاح ✓
الآن يمكنك الاستفادة من جميع مميزات الحسابات الموثقة.
```

### عند الرفض
```
تم رفض طلب التوثيق.
الرجاء التواصل مع الدعم الفني أو تقديم طلب جديد.
```

---

## العرض في واجهة المستخدم | UI Display

### أيقونات التوثيق | Verification Icons

```django-html
{% if request.user.is_verified %}
    <i class="fas fa-shield-check text-success"></i>
    {% trans "حساب موثق" %}
{% else %}
    <i class="fas fa-shield-alt text-warning"></i>
    {% trans "توثيق الحساب" %}
{% endif %}
```

### شارة الحساب الموثق | Verified Badge

```html
<span class="badge-verified">
    <i class="fas fa-check-circle me-1"></i>
    موثق
</span>
```

---

## الصلاحيات والقيود | Permissions & Restrictions

### المستخدمين الموثقين | Verified Users

المزايا:
- شارة "موثق" على الإعلانات
- أولوية في نتائج البحث
- إمكانية الوصول لمميزات متقدمة
- زيادة حد الإعلانات اليومي

### المستخدمين غير الموثقين | Unverified Users

القيود:
- لا توجد شارة توثيق
- أولوية أقل في البحث
- قد تكون بعض المميزات محدودة

---

## الملفات المعدلة | Modified Files

### Templates
1. `templates/partials/_header.html`
   - إضافة رابط لوحة التحكم في القائمة الرئيسية
   - إضافة رابط التوثيق في القائمة الرئيسية
   - إضافة نفس الروابط في القائمة المحمولة

2. `templates/classifieds/my_ads_list.html`
   - تحديث كارت عرض معلومات الباقة
   - إصلاح عرض مميزات الباقة باستخدام الحقول الصحيحة

3. `templates/verification/verification_request.html`
   - صفحة تقديم طلب التوثيق

4. `templates/verification/verification_pending.html`
   - صفحة عرض حالة الطلب أثناء المراجعة

### Views
1. `main/verification_views.py`
   - `verification_request()` - معالجة طلبات التوثيق
   - `verification_pending()` - عرض حالة الطلب

### Models
1. `main/models.py`
   - `UserVerificationRequest` - نموذج طلبات التوثيق
   - `User.is_verified` - خاصية للتحقق من حالة التوثيق

---

## اختبار النظام | Testing

### اختبار توثيق العضوية

```python
# 1. تسجيل الدخول كعضو عادي
user = User.objects.get(username='testuser')
assert user.verification_status == 'unverified'

# 2. الذهاب لصفحة التوثيق
response = client.get(reverse('main:verification_request'))
assert response.status_code == 200

# 3. تقديم طلب التوثيق
response = client.post(reverse('main:verification_request'), {
    'document_type': 'national_id',
    'document_file': test_file,
    'notes': 'طلب توثيق'
})
assert response.status_code == 302  # Redirect to pending

# 4. التحقق من إنشاء الطلب
verification_request = UserVerificationRequest.objects.filter(user=user).first()
assert verification_request.status == 'pending'

# 5. موافقة الإدارة على الطلب
user.verification_status = 'verified'
user.save()
assert user.is_verified == True
```

---

## الأسئلة الشائعة | FAQ

### س: كم يستغرق توثيق الحساب؟
ج: عادةً 2-3 أيام عمل من تاريخ تقديم الطلب.

### س: ما المستندات المطلوبة؟
ج: يمكنك رفع بطاقة الهوية، جواز السفر، السجل التجاري، أو أي مستند رسمي يثبت هويتك.

### س: هل يمكنني تقديم طلب جديد بعد الرفض؟
ج: نعم، يمكنك تقديم طلب جديد في أي وقت.

### س: هل التوثيق مجاني؟
ج: نعم، خدمة توثيق الحساب مجانية بالكامل.

---

## الملاحظات الفنية | Technical Notes

### Security Considerations
1. يتم تخزين المستندات في مجلد آمن: `media/verification_documents/`
2. يمكن للمستخدم فقط رؤية طلباته الخاصة
3. الإدارة فقط يمكنها الموافقة/رفض الطلبات
4. يتم حفظ سجل كامل لجميع الطلبات

### Performance
- استعلامات محسّنة باستخدام `select_related()` و `prefetch_related()`
- فهرسة مناسبة على حقل `verification_status`
- Cache للحسابات الموثقة

### Accessibility
- استخدام ARIA labels مناسبة
- دعم القراءة من اليمين لليسار (RTL)
- دعم الوضع المظلم (Dark Mode)
- استجابة كاملة للأجهزة المحمولة

---

## الخلاصة | Summary

تم تنفيذ نظام متكامل لـ:
✅ لوحة تحكم الأعضاء مع إحصائيات شاملة
✅ نظام توثيق العضوية بالمستندات
✅ روابط في القائمة الرئيسية والمحمولة
✅ كارت عرض معلومات الباقة في صفحة "إعلاناتي"
✅ تتبع حالة طلبات التوثيق
✅ إشعارات للمستخدمين

النظام جاهز للاستخدام ويمكن للمستخدمين الآن:
- الوصول للوحة التحكم من القائمة
- تقديم طلبات توثيق الحساب
- متابعة حالة الطلب
- رؤية مميزات باقتهم النشطة
