# نظام ترقية الإعلانات - Ad Upgrade System

## نظرة عامة - Overview

تم إنشاء نظام شامل لترقية الإعلانات يسمح للمستخدمين بإضافة ميزات مدفوعة لإعلاناتهم لزيادة الظهور والمبيعات.

## الميزات المتاحة - Available Features

### 1. إعلان مميز (Featured Ad) ⭐
- **الوصف**: يظهر الإعلان بلون مميز مع أيقونة نجمة ذهبية
- **المزايا**:
  - ظهور بارز في القوائم
  - أولوية في نتائج البحث
  - زيادة المشاهدات بـ 3-5 أضعاف
- **الأسعار**:
  - 7 أيام: 50 ر.س
  - 14 يوم: 80 ر.س
  - 30 يوم: 100 ر.س (الأكثر شعبية)

### 2. تثبيت في الأعلى (Pinned Ad) 📌
- **الوصف**: يظهر الإعلان في أعلى القائمة دائماً
- **المزايا**:
  - موقع ثابت في الأعلى
  - أيقونة دبوس مميزة
  - مشاهدات أكثر بـ 10 أضعاف
- **الأسعار**:
  - 7 أيام: 75 ر.س
  - 14 يوم: 120 ر.س
  - 30 يوم: 150 ر.س (الأكثر شعبية)

### 3. إعلان عاجل (Urgent Ad) ⚡
- **الوصف**: شارة "عاجل" حمراء بارزة
- **المزايا**:
  - جذب انتباه فوري
  - أولوية في الترشيحات
  - مناسب للبيع السريع
- **الأسعار**:
  - 7 أيام: 30 ر.س
  - 14 يوم: 48 ر.س
  - 30 يوم: 60 ر.س (الأكثر شعبية)

## سير العمل - Workflow

### 1. صفحة النجاح (Success Page)
```
URL: /ar/classifieds/create/success/<ad_id>/
Template: templates/classifieds/ad_create_success.html
```
- يرى المستخدم رسالة نجاح بعد إنشاء الإعلان
- زر "ترقية الإعلان" يوجه للخطوة التالية

### 2. صفحة اختيار الترقيات (Checkout Page)
```
URL: /ar/classifieds/<ad_id>/upgrade/
View: AdUpgradeCheckoutView
Template: templates/classifieds/ad_upgrade_checkout.html
```

**الميزات**:
- عرض معلومات الإعلان
- خيارات الترقية (تمييز، تثبيت، عاجل)
- اختيار المدة لكل ميزة (7، 14، 30 يوم)
- ملخص الطلب التفاعلي
- حساب السعر الإجمالي تلقائياً

**JavaScript Functionality**:
- تفعيل/إلغاء تفعيل الخيارات
- اختيار المدة لكل ميزة
- تحديث الملخص والسعر الإجمالي
- التحقق من صحة البيانات

### 3. معالجة الترقية (Process Upgrade)
```
URL: /ar/classifieds/<ad_id>/upgrade/process/
View: AdUpgradeProcessView (POST)
```

**العملية**:
1. استقبال البيانات من النموذج
2. حساب السعر الإجمالي
3. إنشاء سجل دفع (Payment)
4. حفظ بيانات الترقية في metadata
5. التوجيه لصفحة الدفع

### 4. صفحة الدفع (Payment Page)
```
URL: /ar/payment/upgrade/<payment_id>/
View: payment_page_upgrade
Template: templates/payments/payment_page.html
```

**المحتوى**:
- عرض ملخص الترقيات
- خيارات الدفع (PayPal، Paymob، إلخ)
- معلومات الأمان

## قاعدة البيانات - Database

### جدول Payment
```python
class Payment(models.Model):
    user = ForeignKey(User)
    provider = CharField  # 'paypal', 'paymob', etc.
    amount = DecimalField
    currency = CharField  # 'SAR'
    status = CharField  # 'pending', 'completed', 'failed'
    metadata = JSONField  # {ad_id, upgrades: [{type, duration, price, name}]}
```

### بيانات الترقية في Metadata
```json
{
  "ad_id": 26,
  "upgrades": [
    {
      "type": "featured",
      "duration": 30,
      "price": "100.00",
      "name": "إعلان مميز"
    },
    {
      "type": "pinned",
      "duration": 14,
      "price": "120.00",
      "name": "تثبيت في الأعلى"
    }
  ]
}
```

## الإعدادات - Constance Settings

### الأسعار القابلة للتخصيص
يمكن تغيير الأسعار من لوحة التحكم `/admin/constance/config/`:

**7 أيام**:
- `FEATURED_AD_PRICE_7DAYS`: 50.00 ر.س
- `PINNED_AD_PRICE_7DAYS`: 75.00 ر.س
- `URGENT_AD_PRICE_7DAYS`: 30.00 ر.س

**14 يوم**:
- `FEATURED_AD_PRICE_14DAYS`: 80.00 ر.س
- `PINNED_AD_PRICE_14DAYS`: 120.00 ر.س
- `URGENT_AD_PRICE_14DAYS`: 48.00 ر.س

**30 يوم**:
- `FEATURED_AD_PRICE_30DAYS`: 100.00 ر.س
- `PINNED_AD_PRICE_30DAYS`: 150.00 ر.س
- `URGENT_AD_PRICE_30DAYS`: 60.00 ر.س

## الفرق بين Subscription و AdPackage

### UserSubscription (اشتراك شهري/سنوي)
```python
class UserSubscription(models.Model):
    plan = CharField  # 'monthly', 'yearly'
    price = DecimalField
    start_date = DateField
    end_date = DateField
    auto_renew = BooleanField
```

**الاستخدام**:
- اشتراك متكرر (شهري/سنوي)
- ميزات عضوية مميزة (Premium Membership)
- تجديد تلقائي
- مثال: اشتراك شهري بـ 99 ر.س للحصول على ميزات إضافية

### AdPackage (باقات الإعلانات)
```python
class AdPackage(models.Model):
    ad_count = PositiveIntegerField  # عدد الإعلانات
    ad_duration_days = PositiveIntegerField  # مدة كل إعلان
    duration_days = PositiveIntegerField  # صلاحية الباقة
    feature_pinned_price = DecimalField
    feature_urgent_price = DecimalField
    feature_highlighted_price = DecimalField
```

**الاستخدام**:
- شراء عدد محدد من الإعلانات
- كل إعلان له مدة ظهور محددة
- أسعار إضافية للميزات (تمييز، تثبيت، عاجل)
- مثال: باقة 10 إعلانات لمدة 30 يوم بـ 200 ر.س

### UserPackage (الباقات المشتراة)
```python
class UserPackage(models.Model):
    user = ForeignKey(User)
    package = ForeignKey(AdPackage)
    payment = ForeignKey(Payment)
    expiry_date = DateTimeField
    ads_remaining = PositiveIntegerField
```

**الاستخدام**:
- تتبع الباقات المشتراة
- عدد الإعلانات المتبقية
- تاريخ انتهاء الصلاحية

## ملاحظات التطوير

### TODO: تنفيذ الميزات بعد الدفع
بعد نجاح الدفع، يجب:

1. **تحديث جدول ClassifiedAd**:
```python
ad = ClassifiedAd.objects.get(pk=ad_id)

# تفعيل الميزات حسب الترقيات
for upgrade in upgrades:
    if upgrade['type'] == 'featured':
        ad.is_highlighted = True
        # Create AdFeature record
        AdFeature.objects.create(
            ad=ad,
            feature_type='highlighted',
            end_date=now() + timedelta(days=upgrade['duration'])
        )

    elif upgrade['type'] == 'pinned':
        ad.is_pinned = True
        AdFeature.objects.create(
            ad=ad,
            feature_type='pinned',
            end_date=now() + timedelta(days=upgrade['duration'])
        )

    elif upgrade['type'] == 'urgent':
        ad.is_urgent = True
        AdFeature.objects.create(
            ad=ad,
            feature_type='urgent',
            end_date=now() + timedelta(days=upgrade['duration'])
        )

ad.save()
```

2. **إنشاء سجلات AdFeature**:
```python
from datetime import timedelta
from django.utils import timezone

for upgrade in payment.metadata['upgrades']:
    AdFeature.objects.create(
        ad_id=payment.metadata['ad_id'],
        feature_type=upgrade['type'],  # 'highlighted', 'pinned', 'urgent'
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=upgrade['duration']),
        is_active=True
    )
```

3. **إرسال إشعار للمستخدم**:
```python
Notification.objects.create(
    user=request.user,
    title=_('تم ترقية إعلانك بنجاح'),
    message=_('تم تفعيل الميزات المدفوعة لإعلانك'),
    notification_type='ad_upgrade'
)
```

### مهام Cron المطلوبة

**تعطيل الميزات المنتهية**:
```python
# في management/commands/deactivate_expired_features.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import AdFeature, ClassifiedAd

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get expired features
        expired = AdFeature.objects.filter(
            end_date__lt=timezone.now(),
            is_active=True
        )

        for feature in expired:
            feature.is_active = False
            feature.save()

            # Update ad
            ad = feature.ad
            if feature.feature_type == 'highlighted':
                ad.is_highlighted = False
            elif feature.feature_type == 'pinned':
                ad.is_pinned = False
            elif feature.feature_type == 'urgent':
                ad.is_urgent = False
            ad.save()
```

## التصميم - Design

### الألوان
- **Primary**: `#6b4c7a` (بنفسجي)
- **Featured**: `#ffc107` (ذهبي)
- **Pinned**: `#17a2b8` (أزرق)
- **Urgent**: `#dc3545` (أحمر)
- **Success**: `#28a745` (أخضر)

### الأيقونات
- Featured: `fas fa-star` ⭐
- Pinned: `fas fa-thumbtack` 📌
- Urgent: `fas fa-bolt` ⚡
- Checkout: `fas fa-shopping-cart` 🛒
- Payment: `fas fa-lock` 🔒

### المميزات
- ✅ دعم كامل للوضع الليلي (Dark Mode)
- ✅ تصميم متجاوب (Responsive)
- ✅ رسوم متحركة سلسة
- ✅ تحديث تفاعلي للأسعار
- ✅ واجهة عربية كاملة

## الاختبار - Testing

### سيناريو الاختبار الكامل:
1. إنشاء إعلان جديد
2. الانتقال لصفحة النجاح
3. النقر على "ترقية الإعلان"
4. اختيار ميزة واحدة أو أكثر
5. اختيار المدة لكل ميزة
6. مراجعة الملخص والسعر
7. المتابعة للدفع
8. إتمام عملية الدفع
9. التحقق من تفعيل الميزات
10. التحقق من انتهاء الميزات بعد المدة

## الملفات المعدلة/المضافة

### Templates
- ✅ `templates/classifieds/ad_create_success.html` - Updated
- ✅ `templates/classifieds/ad_upgrade_checkout.html` - New

### Views
- ✅ `main/classifieds_views.py` - Added AdUpgradeCheckoutView, AdUpgradeProcessView
- ✅ `main/payment_views.py` - Added payment_page_upgrade

### URLs
- ✅ `main/urls.py` - Added upgrade routes

### Settings
- ✅ `idrissimart/settings/constance_config.py` - Added pricing settings

### Documentation
- ✅ `docs/AD_UPGRADE_SYSTEM.md` - This file

## الخطوات التالية - Next Steps

1. ✅ إنشاء صفحة الدفع (Payment Gateway Integration)
2. ⏳ تنفيذ callback بعد الدفع الناجح
3. ⏳ تفعيل الميزات على الإعلان
4. ⏳ إضافة مهمة cron لتعطيل الميزات المنتهية
5. ⏳ إضافة صفحة عرض الإعلانات المميزة/المثبتة
6. ⏳ إضافة فلاتر للإعلانات المميزة في البحث
7. ⏳ إضافة إحصائيات للمستخدم عن الترقيات
