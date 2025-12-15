# نظام انتهاء وتجديد الإعلانات - Ad Expiration & Renewal System

## نظرة عامة - Overview

تم تنفيذ نظام شامل لإدارة انتهاء صلاحية الإعلانات وتجديدها بشكل تلقائي ويدوي. النظام يضمن:
- ✅ الإعلانات المنتهية لا تظهر في القوائم النشطة
- ✅ إشعارات تلقائية للأعضاء قبل انتهاء إعلاناتهم
- ✅ واجهة سهلة لتجديد الإعلانات (مجاناً أو مدفوع)
- ✅ إدارة متقدمة للإعلانات المنتهية في dashboard العضو

---

## الملفات المعدلة والمضافة - Modified & Added Files

### 1. النموذج - Model Updates
**File:** `main/models.py`

#### Methods المضافة في ClassifiedAd:

```python
def is_expired(self):
    """Check if ad has expired"""

def days_until_expiry(self):
    """Get number of days until expiry (returns 0 if expired)"""

def can_be_renewed(self):
    """Check if ad can be renewed (expired or expiring within 7 days)"""

def get_renewal_options(self):
    """Get available renewal options with prices and durations"""

def renew(self, duration_days=30, is_free=True, renew_upgrades=False):
    """Renew the ad for specified duration"""
```

#### Methods الموجودة مسبقاً في ClassifiedAdManager:

```python
def active(self):
    """Get only active ads that haven't expired - ALREADY WORKING ✅"""

def expired_ads(self, user=None):
    """Get expired ads, optionally filtered by user - ALREADY EXISTS ✅"""

def expiring_soon(self, days=3, user=None):
    """Get ads expiring within specified days - ALREADY EXISTS ✅"""
```

---

### 2. Views للإعلانات المنتهية والتجديد
**File:** `main/publisher_views.py`

#### Views المضافة:

```python
class PublisherExpiredAdsView(ListView):
    """عرض الإعلانات المنتهية أو القريبة من الانتهاء"""

def publisher_renew_ad_options(request, ad_id):
    """عرض خيارات التجديد المختلفة"""

def publisher_process_renewal(request, ad_id):
    """معالجة طلب التجديد (مجاني أو مدفوع)"""
```

---

### 3. Management Commands للمهام التلقائية
**Files:** `main/management/commands/`

#### expire_ads.py
```bash
# تحديث حالة الإعلانات المنتهية تلقائياً
python manage.py expire_ads
python manage.py expire_ads --dry-run  # معاينة فقط
```

**الوظيفة:**
- يبحث عن الإعلانات النشطة التي تجاوزت تاريخ انتهائها
- يحدث حالتها إلى `EXPIRED`
- يسجل التغييرات في الـ logs

**Cron Job المقترح:**
```cron
# كل يوم الساعة 2 صباحاً
0 2 * * * cd /path/to/project && python manage.py expire_ads
```

#### send_expiration_notifications.py
```bash
# إرسال إشعارات قبل انتهاء الإعلانات
python manage.py send_expiration_notifications --days 3
python manage.py send_expiration_notifications --days 7 --dry-run
```

**الوظيفة:**
- يبحث عن الإعلانات التي ستنتهي خلال X أيام
- يرسل إشعار داخلي (Notification)
- يرسل بريد إلكتروني (إذا كان مفعلاً للعضو)
- يمنع الإشعارات المكررة (خلال 24 ساعة)

**Cron Job المقترح:**
```cron
# كل يوم الساعة 10 صباحاً - إشعار قبل 3 أيام
0 10 * * * cd /path/to/project && python manage.py send_expiration_notifications --days 3

# كل يوم الساعة 11 صباحاً - إشعار قبل 7 أيام
0 11 * * * cd /path/to/project && python manage.py send_expiration_notifications --days 7
```

---

### 4. Templates
**Files:** `templates/dashboard/`

#### expired_ads.html
- عرض الإعلانات المنتهية والقريبة من الانتهاء
- إحصائيات (منتهية / ستنتهي قريباً)
- أزرار سريعة للتجديد والتعديل
- تصميم بسيط وواضح

#### renew_ad_options.html
- عرض خيارات التجديد المختلفة (مجاني / مدفوع)
- معاينة الإعلان المراد تجديده
- خيار تجديد التمييزات (Upgrades) مع الإعلان
- معالجة AJAX للتجديد المجاني
- توجيه للدفع للخيارات المدفوعة

---

### 5. URLs
**File:** `main/urls.py`

```python
# Expired Ads List
path('publisher/expired-ads/', PublisherExpiredAdsView.as_view(), name='publisher_expired_ads')

# Renewal Options
path('publisher/ads/<int:ad_id>/renew-options/', publisher_renew_ad_options, name='publisher_renew_ad_options')

# Process Renewal
path('publisher/ads/<int:ad_id>/process-renewal/', publisher_process_renewal, name='publisher_process_renewal')
```

---

### 6. Navigation
**File:** `templates/dashboard/partials/_publisher_nav.html`

تم إضافة رابط جديد في قائمة dashboard:
```html
<a href="{% url 'main:publisher_expired_ads' %}">
    <i class="fas fa-clock"></i>
    <span>إعلانات منتهية</span>
</a>
```

---

## خيارات التجديد - Renewal Options

### 1. تجديد مجاني - Free Renewal
- **المدة:** 30 يوم
- **السعر:** مجاناً
- **الوصف:** تجديد الإعلان لمدة 30 يوم بدون رسوم

### 2. تجديد 60 يوم
- **المدة:** 60 يوم
- **السعر:** 50 ج.م
- **الوصف:** تجديد الإعلان لمدة شهرين

### 3. تجديد 90 يوم
- **المدة:** 90 يوم
- **السعر:** 100 ج.م
- **الوصف:** تجديد الإعلان لمدة 3 أشهر

### 4. تجديد مميز 30 يوم
- **المدة:** 30 يوم
- **السعر:** 150 ج.م
- **الوصف:** تجديد مع تمييز الإعلان
- **المميزات الإضافية:**
  - تمييز الإعلان (Highlighted)
  - ظهور بالأولوية في القوائم
  - مشاهدات أعلى

> **ملاحظة:** يمكن تعديل الأسعار والمدد من `main/models.py` في method `get_renewal_options()`

---

## سير العمل - Workflow

### 1. انتهاء الإعلان التلقائي
```
1. Cron Job يشغل `expire_ads` يومياً
2. البحث عن الإعلانات التي expires_at <= now
3. تحديث status إلى EXPIRED
4. الإعلان لا يظهر في القوائم النشطة (active() method)
```

### 2. الإشعارات قبل الانتهاء
```
1. Cron Job يشغل `send_expiration_notifications` يومياً
2. البحث عن الإعلانات التي ستنتهي خلال 3-7 أيام
3. إنشاء Notification داخلية
4. إرسال بريد إلكتروني (إذا مفعل)
5. تسجيل الإشعار لتجنب التكرار
```

### 3. عملية التجديد
```
1. العضو يدخل على "إعلانات منتهية"
2. يضغط "تجديد الآن"
3. يعرض خيارات التجديد
4. يختار خطة ويضغط "تجديد"
5. إذا مجاني: تجديد فوري + إشعار
6. إذا مدفوع: توجيه لصفحة الدفع
```

---

## الشروط والقيود - Conditions & Restrictions

### متى يمكن تجديد الإعلان؟
✅ يمكن التجديد إذا:
- الإعلان منتهي (status = EXPIRED)
- الإعلان سينتهي خلال 7 أيام
- الإعلان ليس مرفوضاً (REJECTED)
- الإعلان ليس مباعاً (SOLD)

❌ لا يمكن التجديد إذا:
- الإعلان مرفوض أو مباع
- الإعلان لديه أكثر من 7 أيام متبقية

---

## اختبار النظام - Testing

### 1. اختبار انتهاء الإعلانات
```bash
# معاينة الإعلانات التي ستنتهي
python manage.py expire_ads --dry-run

# تطبيق التحديثات
python manage.py expire_ads
```

### 2. اختبار الإشعارات
```bash
# معاينة الإشعارات التي سترسل
python manage.py send_expiration_notifications --days 3 --dry-run

# إرسال الإشعارات
python manage.py send_expiration_notifications --days 3
```

### 3. اختبار التجديد يدوياً
1. افتح Django Shell: `python manage.py shell`
```python
from main.models import ClassifiedAd

# الحصول على إعلان
ad = ClassifiedAd.objects.first()

# التحقق من الانتهاء
print(f"Expired: {ad.is_expired()}")
print(f"Days left: {ad.days_until_expiry()}")
print(f"Can renew: {ad.can_be_renewed()}")

# الحصول على خيارات التجديد
options = ad.get_renewal_options()
for opt in options:
    print(f"{opt['name']}: {opt['price']} EGP - {opt['duration_days']} days")

# تجديد الإعلان
success = ad.renew(duration_days=30, is_free=True)
print(f"Renewal success: {success}")
print(f"New expiry: {ad.expires_at}")
```

---

## الروابط المهمة - Important URLs

| الصفحة | URL | الوصف |
|--------|-----|-------|
| الإعلانات المنتهية | `/publisher/expired-ads/` | قائمة الإعلانات المنتهية |
| خيارات التجديد | `/publisher/ads/{id}/renew-options/` | اختيار خطة التجديد |
| معالجة التجديد | `/publisher/ads/{id}/process-renewal/` | AJAX endpoint للتجديد |

---

## الأداء والتحسينات - Performance & Optimization

### Indexing المطلوب
```sql
-- Index على expires_at و status للسرعة
CREATE INDEX idx_ads_expiry ON classified_ads(expires_at, status);

-- Index على created_at للترتيب
CREATE INDEX idx_ads_created ON classified_ads(created_at DESC);
```

### Caching المقترح
```python
# في settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# في views.py
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def publisher_expired_ads(request):
    ...
```

---

## الأمان - Security

### CSRF Protection
✅ جميع POST requests محمية بـ CSRF token

### Authorization
✅ @publisher_required decorator على جميع الـ views
✅ get_object_or_404 مع user check: `ad.user == request.user`

### Input Validation
✅ التحقق من renewal_type في الـ options المتاحة
✅ التحقق من can_be_renewed() قبل التجديد

---

## الصيانة - Maintenance

### Tasks يومية
1. تشغيل `expire_ads` للتحديث التلقائي
2. تشغيل `send_expiration_notifications` للإشعارات

### Tasks أسبوعية
1. مراجعة الـ logs للأخطاء
2. التحقق من عدد الإعلانات المنتهية
3. مراجعة إحصائيات التجديد

### Tasks شهرية
1. تحليل معدلات التجديد
2. تحسين الأسعار والعروض
3. تحديث النصوص والترجمات

---

## المستقبل - Future Enhancements

### مقترحات للتطوير
- [ ] دفع تلقائي للتجديدات
- [ ] خصومات للتجديدات المتعددة
- [ ] تجديد تلقائي بموافقة العضو
- [ ] تقارير تحليلية للإعلانات المنتهية
- [ ] واجهة API للتجديد من التطبيقات
- [ ] إشعارات SMS للإعلانات الهامة
- [ ] نظام نقاط ومكافآت للتجديدات

---

## الخلاصة - Summary

✅ **تم تنفيذ:**
1. Methods للتحقق من الانتهاء والتجديد في Model
2. Views كاملة للإعلانات المنتهية وخيارات التجديد
3. Management commands للمهام التلقائية
4. Templates جميلة وسهلة الاستخدام
5. Integration كامل مع dashboard العضو
6. نظام إشعارات شامل (داخلي + بريد)

✅ **النتيجة:**
- الإعلانات المنتهية لا تظهر في القوائم النشطة
- الأعضاء يحصلون على إشعارات قبل الانتهاء
- واجهة سهلة للتجديد بخيارات متعددة
- نظام مؤتمت بالكامل يعمل في الخلفية

---

**تاريخ الإنشاء:** 14 ديسمبر 2025
**الإصدار:** 1.0
**المطور:** GitHub Copilot
