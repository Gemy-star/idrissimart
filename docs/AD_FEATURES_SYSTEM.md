# نظام مميزات الإعلانات الجديدة
## New Ad Features System Documentation

## نظرة عامة | Overview

تم إضافة 3 مميزات جديدة للإعلانات المبوبة:
1. **تواصل ليصلك عرض سعر** - ميزة مدفوعة لإخفاء السعر
2. **نشر على فيسبوك** - ميزة مدفوعة مع معالجة يدوية من الإدارة
3. **إضافة فيديو** - ميزة قيد التطوير (غير نشطة حالياً)

Three new features have been added to classified ads:
1. **Contact for Price Quote** - Paid feature to hide price
2. **Share on Facebook** - Paid feature with manual admin handling
3. **Add Video** - Under development feature (inactive)

---

## الميزة 1: تواصل ليصلك عرض سعر | Feature 1: Contact for Price Quote

### الوصف | Description

**عربي:**
- إخفاء السعر الفعلي للإعلان
- عرض رسالة "تواصل ليصلك عرض سعر" بدلاً من السعر
- مثالي للإعلانات القابلة للتفاوض أو الأسعار المتغيرة
- ميزة مدفوعة: 50 ريال

**English:**
- Hide actual ad price
- Display "Contact for price quote" message instead
- Ideal for negotiable or variable pricing ads
- Paid feature: 50 SAR

### الحقول في قاعدة البيانات | Database Fields

```python
# ClassifiedAd model
contact_for_price = models.BooleanField(
    default=False,
    verbose_name=_("تواصل ليصلك عرض سعر - Contact for Price")
)
```

### كيفية العمل | How It Works

1. **التفعيل:**
   - المستخدم يذهب إلى صفحة الإعلان الخاص به
   - يضغط على "ترقية الإعلان"
   - يختار ميزة "تواصل ليصلك عرض سعر"
   - يدفع 50 ريال

2. **التأثير على العرض:**
   - في صفحة تفاصيل الإعلان: يظهر صندوق بنفسجي مع رسالة "تواصل ليصلك عرض سعر"
   - في بطاقة الإعلان (card): يظهر نفس الصندوق بدلاً من السعر
   - زر "تواصل للسعر" يظهر للمستخدمين

3. **الإلغاء:**
   - صاحب الإعلان يمكنه إلغاء التفعيل من نفس الصفحة
   - يعود السعر الأصلي للظهور فوراً

### الملفات المتأثرة | Affected Files

- **Model:** [main/models.py](main/models.py:1431) - `contact_for_price` field
- **Template (Detail):** [templates/classifieds/ad_detail.html](templates/classifieds/ad_detail.html:1384-1409)
- **Template (Card):** [templates/partials/_ad_card_component.html](templates/partials/_ad_card_component.html:199-222)
- **View:** [main/ad_features_views.py](main/ad_features_views.py:20-100)

---

## الميزة 2: نشر على فيسبوك | Feature 2: Share on Facebook

### الوصف | Description

**عربي:**
- نشر الإعلان على صفحة الفيسبوك الرسمية للموقع
- يتم التنفيذ يدوياً من قبل الإدارة خلال 24 ساعة
- يصل الإعلان لجمهور أكبر على فيسبوك
- ميزة مدفوعة: 100 ريال

**English:**
- Publish ad on site's official Facebook page
- Manually executed by admin within 24 hours
- Reaches larger audience on Facebook
- Paid feature: 100 SAR

### الحقول في قاعدة البيانات | Database Fields

```python
# ClassifiedAd model
share_on_facebook = models.BooleanField(default=False)
facebook_share_requested = models.BooleanField(default=False)
facebook_share_completed = models.BooleanField(default=False)
facebook_shared_at = models.DateTimeField(blank=True, null=True)
facebook_post_url = models.URLField(blank=True, null=True)
```

### Model الإضافي | Additional Model

```python
class FacebookShareRequest(models.Model):
    """Model to track Facebook share requests for admin review"""

    class Status(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار - Pending")
        IN_PROGRESS = "in_progress", _("جاري التنفيذ - In Progress")
        COMPLETED = "completed", _("تم التنفيذ - Completed")
        REJECTED = "rejected", _("مرفوض - Rejected")

    ad = ForeignKey("ClassifiedAd")
    user = ForeignKey("User")
    status = CharField(max_length=20, choices=Status.choices)
    requested_at = DateTimeField(auto_now_add=True)
    processed_at = DateTimeField(null=True, blank=True)
    processed_by = ForeignKey("User", null=True)
    facebook_post_url = URLField(null=True, blank=True)
    admin_notes = TextField(blank=True)
    payment_confirmed = BooleanField(default=False)
    payment_amount = DecimalField(max_digits=10, decimal_places=2)
```

### سير العمل | Workflow

#### للمستخدم | For User:

1. **طلب الميزة:**
   - المستخدم يذهب لصفحة "ترقية الإعلان"
   - يختار "نشر على فيسبوك"
   - يدفع 100 ريال
   - يتم إنشاء طلب FacebookShareRequest بحالة "pending"

2. **متابعة الحالة:**
   - في صفحة الإعلان، يظهر badge "قيد المراجعة"
   - يتلقى المستخدم إشعار عند الموافقة أو الرفض

3. **بعد النشر:**
   - badge يتحول إلى "تم النشر"
   - يظهر زر "عرض المنشور" يوجه لرابط فيسبوك

#### للإدارة | For Admin:

1. **استلام الطلب:**
   - يظهر في Django Admin تحت "Facebook Share Requests"
   - الطلبات مرتبة حسب التاريخ (الأحدث أولاً)

2. **مراجعة الطلب:**
   ```
   /admin/main/facebooksharerequest/
   ```
   - مراجعة تفاصيل الإعلان
   - التحقق من الدفع
   - تغيير الحالة إلى "in_progress"

3. **النشر على فيسبوك:**
   - نشر الإعلان يدوياً على صفحة فيسبوك
   - نسخ رابط المنشور
   - في Django Admin:
     - تغيير الحالة إلى "completed"
     - لصق رابط المنشور في `facebook_post_url`
     - الحفظ

4. **أو الرفض:**
   - تغيير الحالة إلى "rejected"
   - كتابة سبب الرفض في `admin_notes`
   - الحفظ

### الملفات | Files

- **Model:** [main/models.py](main/models.py:1437-1478) - Facebook fields
- **Request Model:** [main/models.py](main/models.py:3731-3840) - FacebookShareRequest
- **Admin:** [main/admin.py](main/admin.py:2023-2167) - FacebookShareRequestAdmin
- **View:** [main/ad_features_views.py](main/ad_features_views.py:20-145)
- **URL:** [main/urls.py](main/urls.py:200-203)

### Admin Dashboard

**List Display:**
- ID الطلب
- عنوان الإعلان (مع رابط)
- المستخدم (مع رابط)
- الحالة (ملون)
- تأكيد الدفع
- تاريخ الطلب
- تاريخ المعالجة
- المعالج

**Actions:**
- تحديث إلى "جاري التنفيذ"
- تحديد كمكتمل
- رفض الطلب
- تأكيد الدفع

---

## الميزة 3: إضافة فيديو | Feature 3: Add Video

### الوصف | Description

**عربي:**
- إضافة فيديو لل إعلان (YouTube, Vimeo, أو رفع مباشر)
- **حالياً: قيد التطوير**
- غير نشطة، تظهر رسالة "قيد التطوير"
- السعر المخطط: 75 ريال

**English:**
- Add video to ad (YouTube, Vimeo, or direct upload)
- **Currently: Under Development**
- Inactive, shows "under development" message
- Planned price: 75 SAR

### الحقول في قاعدة البيانات | Database Fields

```python
# ClassifiedAd model
video_url = models.URLField(
    blank=True,
    null=True,
    verbose_name=_("رابط الفيديو - Video URL"),
    help_text=_("رابط فيديو YouTube أو Vimeo (ميزة قيد التطوير)")
)
video_file = models.FileField(
    blank=True,
    null=True,
    upload_to="ad_videos/",
    verbose_name=_("ملف الفيديو - Video File")
)
```

### العرض الحالي | Current Display

في صفحة تفاصيل الإعلان، إذا كان `video_url` أو `video_file` موجود:

```html
<div class="modern-card card ad-content-card mb-4">
    <div class="card-header">
        <h4><i class="fas fa-video"></i> فيديو الإعلان</h4>
    </div>
    <div class="card-body">
        <div class="alert alert-info">
            <i class="fas fa-tools"></i>
            <h5>ميزة قيد التطوير</h5>
            <p>نعمل حالياً على تطوير ميزة إضافة الفيديو للإعلانات.
               سيتم إطلاق هذه الخدمة قريباً!</p>
        </div>
    </div>
</div>
```

### في صفحة الترقية | On Upgrade Page

```html
<div class="feature-card coming-soon">
    <span class="badge coming-soon">
        <i class="fas fa-tools"></i> قريباً
    </span>
    <div class="feature-icon">
        <i class="fas fa-video"></i>
    </div>
    <h3>إضافة فيديو</h3>
    <p>أضف فيديو لإعلانك لجذب المزيد من المشترين...</p>
    <div class="feature-price">75.00 ريال</div>
    <button disabled class="btn-coming-soon">
        <i class="fas fa-hourglass-half"></i> قيد التطوير
    </button>
</div>
```

---

## صفحة ترقية الإعلان | Ad Features Upgrade Page

### المسار | Route

```
/classifieds/<ad_id>/features/
```

**URL Name:** `main:ad_features_upgrade`

### المميزات | Features

1. **عرض جميع المميزات:**
   - Contact for Price (نشط)
   - Facebook Share (نشط)
   - Video (قيد التطوير)

2. **معلومات الإعلان:**
   - عنوان الإعلان
   - التصنيف
   - تاريخ النشر

3. **الحالة الحالية:**
   - Badge "مفعّل" للمميزات النشطة
   - Badge "قيد المراجعة" لطلبات فيسبوك المعلقة
   - Badge "تم النشر" لطلبات فيسبوك المكتملة

4. **حساب السعر:**
   - المجموع الفرعي (مجموع المميزات المختارة)
   - الضريبة 15%
   - المجموع الكلي
   - تحديث تلقائي عند اختيار/إلغاء المميزات

5. **زر الدفع:**
   - غير نشط إذا لم يتم اختيار أي ميزة جديدة
   - نشط عند اختيار ميزة واحدة على الأقل

### الملفات | Files

- **Template:** [templates/classifieds/ad_features_upgrade.html](templates/classifieds/ad_features_upgrade.html)
- **View:** [main/ad_features_views.py](main/ad_features_views.py:14-77)
- **URL:** [main/urls.py](main/urls.py:189-193)

---

## بطاقة المميزات في صفحة الإعلان | Features Card in Ad Detail Page

### الموقع | Location

في الشريط الجانبي (sidebar) لصفحة تفاصيل الإعلان:
- بعد بطاقة السعر
- قبل بطاقة معلومات البائع
- **تظهر فقط لصاحب الإعلان**

In the sidebar of ad detail page:
- After price card
- Before seller info card
- **Only visible to ad owner**

### المحتوى | Content

```
┌─────────────────────────────────┐
│     ⭐ مميزات الإعلان           │
├─────────────────────────────────┤
│ 💰 تواصل ليصلك عرض سعر          │
│    [badge: مفعّل / غير مفعّل]    │
│                                 │
│ 📘 نشر على فيسبوك               │
│    [badge: حالة]                │
│                                 │
│ 🎥 إضافة فيديو                 │
│    [badge: قريباً]              │
│                                 │
│  [🚀 ترقية الإعلان]            │
└─────────────────────────────────┘
```

### الأيقونات والألوان | Icons & Colors

- **Contact for Price:**
  - Icon: `fa-file-invoice-dollar`
  - Color: أخضر (#4caf50) إذا مفعّل، رمادي (#9e9e9e) إذا لا

- **Facebook Share:**
  - Icon: `fab fa-facebook`
  - Color: أزرق فيسبوك (#1877f2) إذا مفعّل
  - Badges:
    - "تم النشر" - أخضر
    - "قيد المراجعة" - أصفر
    - "مفعّل" - أزرق
    - "غير مفعّل" - رمادي

- **Video:**
  - Icon: `fa-video`
  - Color: رمادي (#9e9e9e)
  - Opacity: 0.6
  - Badge: "قريباً" - رمادي

---

## URLs & Routes

### Main Routes

```python
# Ad Features URLs
path(
    "classifieds/<int:ad_id>/features/",
    ad_features_views.ad_features_upgrade,
    name="ad_features_upgrade",
),
path(
    "classifieds/<int:ad_id>/toggle-contact-price/",
    ad_features_views.toggle_contact_for_price,
    name="toggle_contact_for_price",
),
path(
    "classifieds/<int:ad_id>/request-facebook-share/",
    ad_features_views.request_facebook_share,
    name="request_facebook_share",
),
```

---

## API Endpoints (للمستقبل | Future)

حالياً لا توجد API endpoints. يمكن إضافتها لاحقاً:

Currently no API endpoints. Can be added later:

```python
# Suggested endpoints
GET    /api/v1/ads/<id>/features/          # Get ad features status
POST   /api/v1/ads/<id>/features/upgrade/  # Upgrade features
GET    /api/v1/facebook-requests/          # List requests (admin)
PATCH  /api/v1/facebook-requests/<id>/     # Update request status
```

---

## الأمان | Security

### 1. التحقق من الملكية | Ownership Verification

```python
@login_required
def ad_features_upgrade(request, ad_id):
    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)
    # Only owner can upgrade their ad
```

### 2. منع الطلبات المكررة | Prevent Duplicate Requests

```python
if ad.facebook_share_requested:
    messages.warning(request, "لديك طلب قيد المراجعة بالفعل")
    return redirect("main:ad_detail", ad_id=ad.id)
```

### 3. تأكيد الدفع | Payment Confirmation

```python
FacebookShareRequest.objects.create(
    ...
    payment_confirmed=True,  # Should be from payment gateway
    payment_amount=Decimal("100.00"),
)
```

---

## التكامل مع نظام الدفع | Payment Integration

**ملاحظة هامة:** حالياً `payment_confirmed=True` يتم تعيينه مباشرة. يجب التكامل مع:

**Important Note:** Currently `payment_confirmed=True` is set directly. Should integrate with:

1. **بوابة الدفع | Payment Gateway**
   - Paymob
   - PayTabs
   - Stripe
   - أخرى

2. **سير العمل المقترح | Suggested Workflow**
   ```
   User selects features
   → Redirects to payment
   → Payment success callback
   → Create FacebookShareRequest
   → Update ad features
   ```

---

## إحصائيات | Statistics

### للمستخدم | For User

يمكن عرض في لوحة التحكم:
- عدد الإعلانات مع contact_for_price
- عدد طلبات Facebook المعلقة/المكتملة
- إجمالي الإنفاق على المميزات

Can be displayed in dashboard:
- Number of ads with contact_for_price
- Number of pending/completed Facebook requests
- Total spending on features

### للإدارة | For Admin

```python
# Admin dashboard metrics
total_facebook_requests = FacebookShareRequest.objects.count()
pending_requests = FacebookShareRequest.objects.filter(status='pending').count()
completed_requests = FacebookShareRequest.objects.filter(status='completed').count()
total_revenue = FacebookShareRequest.objects.filter(
    payment_confirmed=True
).aggregate(Sum('payment_amount'))
```

---

## التحسينات المستقبلية | Future Improvements

### 1. إشعارات | Notifications

**للمستخدم:**
- عند قبول طلب Facebook
- عند رفض طلب Facebook
- عند نشر الإعلان على Facebook

**للإدارة:**
- عند استلام طلب Facebook جديد
- تذكير بالطلبات المعلقة أكثر من 24 ساعة

### 2. تقارير | Reports

- تقرير المبيعات حسب الميزة
- تقرير الطلبات حسب الحالة
- تقرير أداء الإعلانات المشتركة على Facebook

### 3. نظام القوالب | Templates System

لنشر فيسبوك أوتوماتيكي:
- قوالب جاهزة للمنشورات
- تخصيص حسب التصنيف
- جدولة النشر

### 4. ميزة الفيديو | Video Feature

عند إطلاقها:
- دعم YouTube embed
- دعم Vimeo embed
- رفع ملفات فيديو مباشر (مع ضغط)
- معاينة الفيديو في بطاقة الإعلان
- Gallery مع الصور والفيديو

### 5. حزم المميزات | Feature Packages

```python
# Example
BASIC_PACKAGE = {
    'contact_for_price': True,
    'price': 50
}

PREMIUM_PACKAGE = {
    'contact_for_price': True,
    'facebook_share': True,
    'video': True,
    'price': 200,  # Discount from 225
}
```

---

## Migrations

### Created Migrations

1. **0038_category_cart_instructions_and_more.py**
   - Added Facebook fields to ClassifiedAd
   - Updated AdFeature.FeatureType enum
   - Updated video fields

2. **0039_facebooksharerequest.py**
   - Created FacebookShareRequest model
   - Indexes on status and ad

---

## الاختبار | Testing

### خطوات الاختبار | Test Steps

#### 1. اختبار Contact for Price

```bash
# كمستخدم عادي
1. سجل دخول
2. انتقل لإعلانك
3. اضغط "ترقية الإعلان"
4. اختر "تواصل ليصلك عرض سعر"
5. تحقق من إخفاء السعر في صفحة الإعلان
6. تحقق من ظهور الرسالة في البطاقة
```

#### 2. اختبار Facebook Share

```bash
# كمستخدم
1. اختر "نشر على فيسبوك"
2. تحقق من ظهور "قيد المراجعة"

# كإدارة
3. افتح /admin/main/facebooksharerequest/
4. راجع الطلب
5. غير الحالة إلى "completed"
6. أضف رابط المنشور
7. احفظ

# كمستخدم
8. تحقق من تحديث الحالة إلى "تم النشر"
9. اضغط "عرض المنشور"
10. تحقق من فتح رابط Facebook
```

#### 3. اختبار Video (قيد التطوير)

```bash
1. في صفحة الترقية، تحقق من ظهور "قريباً"
2. تحقق من عدم القدرة على التفعيل
3. إذا تم رفع فيديو يدوياً في DB، تحقق من ظهور رسالة "قيد التطوير"
```

---

## الخلاصة | Summary

تم إضافة نظام مميزات شامل للإعلانات يشمل:

✅ **3 مميزات جديدة:**
- Contact for Price (نشط)
- Facebook Share (نشط مع معالجة يدوية)
- Video (قيد التطوير)

✅ **صفحة ترقية كاملة:**
- عرض المميزات
- حساب السعر تلقائياً
- دعم الضريبة 15%

✅ **لوحة تحكم للإدارة:**
- مراجعة طلبات Facebook
- تتبع الحالات
- Bulk actions

✅ **واجهة مستخدم جذابة:**
- بطاقة المميزات في صفحة الإعلان
- Badges ملونة
- Responsive design
- Dark mode support

✅ **أمان:**
- التحقق من الملكية
- منع الطلبات المكررة
- تأكيد الدفع

---

**تاريخ الإنشاء | Creation Date:** 2025-12-30
**الإصدار | Version:** 1.0
**الحالة | Status:** ✅ مكتمل | Completed
