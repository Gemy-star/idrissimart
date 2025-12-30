# نظام توثيق العضوية
## User Verification System Documentation

## نظرة عامة | Overview

تم إنشاء نظام توثيق شامل للمستخدمين يسمح لهم بتقديم طلبات للحصول على علامة التوثيق الزرقاء (Verified Badge) على حساباتهم.

A comprehensive user verification system has been created allowing users to submit requests to get a verified badge on their accounts.

---

## المزايا | Features

### للمستخدمين | For Users

1. **✅ طلب التوثيق** - إمكانية تقديم طلب توثيق مع رفع وثائق رسمية
2. **✅ متابعة الحالة** - متابعة حالة الطلب (قيد المراجعة، موافق، مرفوض)
3. **✅ علامة التوثيق** - الحصول على علامة زرقاء بجانب الاسم
4. **✅ أولوية الظهور** - إعلانات الحسابات الموثقة تظهر بشكل أفضل
5. **✅ زيادة الثقة** - المستخدمون يفضلون التعامل مع الحسابات الموثقة

### للإدارة | For Admins

1. **✅ مراجعة الطلبات** - مراجعة طلبات التوثيق من لوحة الإدارة
2. **✅ الموافقة/الرفض** - اتخاذ قرار بشأن كل طلب
3. **✅ إضافة ملاحظات** - إضافة ملاحظات للمستخدم في حالة الرفض
4. **✅ تتبع المراجعين** - معرفة من راجع كل طلب

---

## الملفات المضافة | New Files

### 1. Forms
**File:** [main/verification_forms.py](c:\WORK\idrissimart\main\verification_forms.py)

```python
class UserVerificationRequestForm(forms.ModelForm):
    """Form for users to request account verification"""
    - Validates document type
    - Validates file size (max 5MB)
    - Validates file types (JPG, PNG, PDF)
```

### 2. Views
**File:** [main/verification_views.py](c:\WORK\idrissimart\main\verification_views.py)

**Views:**
- `verification_request()` - صفحة تقديم طلب التوثيق
- `verification_pending()` - صفحة عرض حالة الطلب المعلق
- `verification_status()` - صفحة عرض جميع الطلبات

### 3. Templates

#### [templates/verification/verification_request.html](c:\WORK\idrissimart\templates\verification\verification_request.html)
- صفحة تقديم طلب التوثيق
- عرض مزايا التوثيق
- نموذج رفع الوثائق
- التحقق من صحة الملفات

#### [templates/verification/verification_pending.html](c:\WORK\idrissimart\templates\verification\verification_pending.html)
- صفحة حالة الطلب المعلق
- Timeline لمراحل المراجعة
- تفاصيل الطلب
- معلومات مهمة

#### [templates/verification/verification_status.html](c:\WORK\idrissimart\templates\verification\verification_status.html)
- عرض جميع طلبات التوثيق
- حالة كل طلب
- ملاحظات الإدارة
- تاريخ المراجعة

---

## الملفات المعدلة | Modified Files

### 1. URLs
**File:** [main/urls.py](c:\WORK\idrissimart\main\urls.py:560-575)

```python
# Verification URLs
path("verification/request/", verification_views.verification_request, name="verification_request"),
path("verification/pending/", verification_views.verification_pending, name="verification_pending"),
path("verification/status/", verification_views.verification_status, name="verification_status"),
```

### 2. Header Navigation
**File:** [templates/partials/_header.html](c:\WORK\idrissimart\templates\partials\_header.html:164-172)

تم إضافة رابط التوثيق في قائمة المستخدم:
```html
<li>
    <a class="dropdown-item" href="{% url "main:verification_request" %}">
        {% if request.user.is_verified %}
            <i class="fas fa-shield-check me-2 text-success"></i>حساب موثق
        {% else %}
            <i class="fas fa-shield-alt me-2 text-warning"></i>توثيق الحساب
        {% endif %}
    </a>
</li>
```

---

## كيفية الاستخدام | How to Use

### للمستخدمين | For Users

#### 1. الوصول لصفحة التوثيق
```
الطريقة 1: من قائمة المستخدم في الهيدر
👤 (أيقونة المستخدم) → 🛡️ توثيق الحساب

الطريقة 2: الرابط المباشر
http://localhost:8000/verification/request/
```

#### 2. تقديم طلب التوثيق

**الخطوات:**
1. اختر نوع الوثيقة (بطاقة هوية، جواز سفر، سجل تجاري، إلخ)
2. ارفع صورة واضحة للوثيقة (JPG, PNG, PDF - حجم أقصى 5MB)
3. أضف أي ملاحظات إضافية (اختياري)
4. اضغط "إرسال طلب التوثيق"

#### 3. متابعة الحالة

بعد تقديم الطلب:
- ستتلقى رسالة تأكيد
- سيتم تحويلك لصفحة "قيد المراجعة"
- يمكنك متابعة جميع طلباتك من: `/verification/status/`

### للإدارة | For Admins

#### مراجعة الطلبات من Django Admin

```python
# الوصول للطلبات
/admin/main/userverificationrequest/

# لكل طلب يمكن:
1. مراجعة الوثيقة المرفوعة
2. تغيير الحالة (pending, verified, rejected)
3. إضافة ملاحظات للمستخدم
4. حفظ التغييرات
```

---

## حالات الطلب | Request States

| الحالة | Status | الوصف | Description |
|--------|--------|-------|-------------|
| قيد المراجعة | `pending` | الطلب تحت المراجعة | Request under review |
| موثق | `verified` | تم الموافقة على الطلب | Request approved |
| مرفوض | `rejected` | تم رفض الطلب | Request rejected |
| غير موثق | `unverified` | لم يتم تقديم طلب | No request submitted |

---

## أنواع الوثائق المقبولة | Accepted Document Types

1. **بطاقة الهوية** (`national_id`)
   - بطاقة الهوية الوطنية
   - National ID Card

2. **جواز السفر** (`passport`)
   - جواز سفر ساري المفعول
   - Valid Passport

3. **السجل التجاري** (`commercial_register`)
   - للشركات والأنشطة التجارية
   - For businesses

4. **شهادة ضريبية** (`tax_certificate`)
   - البطاقة الضريبية
   - Tax ID

5. **رخصة مهنية** (`professional_license`)
   - للمهنيين (أطباء، مهندسين، إلخ)
   - For professionals

6. **أخرى** (`other`)
   - وثائق أخرى
   - Other documents

---

## قواعد التحقق | Validation Rules

### حجم الملف | File Size
```python
max_size = 5MB (5 * 1024 * 1024 bytes)
```

### أنواع الملفات المقبولة | Accepted File Types
```python
allowed_types = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "application/pdf"
]
```

### الحقول المطلوبة | Required Fields
- ✅ نوع الوثيقة (Document Type)
- ✅ ملف الوثيقة (Document File)
- ⭕ ملاحظات (Optional)

---

## تكامل مع النظام | System Integration

### Model: UserVerificationRequest

```python
class UserVerificationRequest(models.Model):
    user = ForeignKey(User)
    document_type = CharField(choices=DocumentType.choices)
    document_file = FileField(upload_to="verification_documents/")
    additional_documents = JSONField(default=list)
    notes = TextField(blank=True)
    status = CharField(choices=VerificationStatus.choices)
    admin_notes = TextField(blank=True)
    reviewed_by = ForeignKey(User, null=True)
    reviewed_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### User.is_verified Property

```python
@property
def is_verified(self):
    """Check if user is verified"""
    return self.verification_status == self.VerificationStatus.VERIFIED
```

---

## واجهة المستخدم | User Interface

### صفحة طلب التوثيق

```
┌─────────────────────────────────────────┐
│        🛡️  توثيق الحساب                │
│                                         │
│  ⭐ مزايا توثيق الحساب                │
│  ✓ علامة التوثيق الزرقاء               │
│  ✓ زيادة الثقة                        │
│  ✓ أولوية في الظهور                   │
│  ✓ زيادة المبيعات                     │
│                                         │
│  📄 نموذج التقديم                     │
│  └─ نوع الوثيقة: [▼]                  │
│  └─ رفع الوثيقة: [📤 اختر ملف]       │
│  └─ ملاحظات: [________]               │
│                                         │
│  [✉️ إرسال طلب التوثيق]               │
└─────────────────────────────────────────┘
```

### صفحة الطلب المعلق

```
┌─────────────────────────────────────────┐
│      ⏳ طلبك قيد المراجعة              │
│                                         │
│  Timeline:                              │
│  ✅ تم استلام الطلب                   │
│  🔄 قيد المراجعة (حالياً)             │
│  ⏸️  الموافقة النهائية                │
│                                         │
│  💡 معلومات مهمة:                      │
│  • ستصلك رسالة عند المراجعة           │
│  • المراجعة تستغرق 2-3 أيام            │
│  • تحقق من بريدك بانتظام              │
└─────────────────────────────────────────┘
```

---

## الأمان | Security

### 1. Authentication Required
```python
@login_required
def verification_request(request):
    # Only authenticated users can request verification
```

### 2. File Validation
```python
# Check file size
if file.size > 5 * 1024 * 1024:
    raise ValidationError("حجم الملف كبير جداً")

# Check file type
if file.content_type not in allowed_types:
    raise ValidationError("نوع الملف غير مدعوم")
```

### 3. Prevent Multiple Pending Requests
```python
pending_request = UserVerificationRequest.objects.filter(
    user=user,
    status=User.VerificationStatus.PENDING
).first()

if pending_request:
    # Redirect to pending page
```

---

## إشعارات | Notifications

### للمستخدم | For User

**عند تقديم الطلب:**
```
✅ تم إرسال طلب التوثيق بنجاح!
سنقوم بمراجعة طلبك خلال 2-3 أيام عمل.
```

**عند الموافقة:** (يمكن إضافته لاحقاً)
```
🎉 تهانينا! تم توثيق حسابك بنجاح!
```

**عند الرفض:** (يمكن إضافته لاحقاً)
```
❌ تم رفض طلب التوثيق
السبب: [ملاحظات الإدارة]
```

---

## تحسينات مستقبلية | Future Improvements

### المقترحات:

1. **إشعارات البريد الإلكتروني**
   - إرسال بريد عند تغيير حالة الطلب
   - Email notifications on status change

2. **إشعارات داخل الموقع**
   - In-app notifications

3. **رفع وثائق متعددة**
   - Support for multiple documents
   - Additional documents field

4. **التحقق التلقائي**
   - AI-powered document verification
   - OCR for ID verification

5. **مستويات التوثيق**
   - Basic verification
   - Business verification
   - Premium verification

6. **صفحة للإدارة مخصصة**
   - Custom admin page for reviewing requests
   - Batch approval

---

## الاختبار | Testing

### خطوات الاختبار:

#### 1. اختبار تقديم الطلب

```bash
# ابدأ الخادم
python manage.py runserver

# سجل دخول كمستخدم عادي
http://localhost:8000/login/

# اذهب لصفحة التوثيق
http://localhost:8000/verification/request/

# قدم طلب توثيق:
1. اختر نوع الوثيقة
2. ارفع صورة أو PDF
3. أضف ملاحظات (اختياري)
4. اضغط "إرسال"
```

#### 2. اختبار المراجعة

```bash
# سجل دخول كـ admin
http://localhost:8000/admin/

# اذهب لطلبات التوثيق
/admin/main/userverificationrequest/

# راجع الطلب:
1. افتح الطلب
2. اطلع على الوثيقة
3. غير الحالة
4. أضف ملاحظات
5. احفظ
```

#### 3. اختبار العرض

```bash
# تحقق من ظهور الرابط في القائمة
✓ قائمة المستخدم → توثيق الحساب

# تحقق من صفحة الحالة
http://localhost:8000/verification/status/

# تحقق من علامة التوثيق
✓ يظهر "حساب موثق" بدلاً من "توثيق الحساب"
```

---

## الأخطاء الشائعة | Common Issues

### 1. "حجم الملف كبير جداً"
**الحل:** الملف يجب أن يكون أقل من 5MB

### 2. "نوع الملف غير مدعوم"
**الحل:** استخدم JPG, PNG, GIF, أو PDF فقط

### 3. "لديك طلب قيد المراجعة"
**الحل:** انتظر حتى يتم مراجعة الطلب الحالي

### 4. "حسابك موثق بالفعل"
**الحل:** لا حاجة لطلب توثيق جديد

---

## الخلاصة | Summary

تم إنشاء نظام توثيق كامل يتضمن:

- ✅ 3 صفحات (طلب، معلق، حالة)
- ✅ نموذج مع التحقق الكامل
- ✅ تكامل مع قائمة المستخدم
- ✅ واجهة مستخدم جذابة
- ✅ دعم RTL/LTR
- ✅ دعم الوضع الداكن
- ✅ Responsive للموبايل

A complete verification system including:

- ✅ 3 pages (request, pending, status)
- ✅ Form with full validation
- ✅ Integration with user menu
- ✅ Attractive UI
- ✅ RTL/LTR support
- ✅ Dark mode support
- ✅ Mobile responsive

---

**تاريخ الإنشاء | Creation Date:** 2025-12-30
**الإصدار | Version:** 1.0
**الحالة | Status:** ✅ مكتمل | Completed
