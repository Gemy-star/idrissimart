# دليل تجديد الإعلانات - Ad Renewal Guide

## 📋 المحتويات - Table of Contents

1. [المشكلة والحل - Problem & Solution](#المشكلة-والحل)
2. [Management Command](#management-command)
3. [Admin Actions](#admin-actions)
4. [أمثلة الاستخدام - Usage Examples](#أمثلة-الاستخدام)
5. [إعداد Cron Job](#إعداد-cron-job)

---

## المشكلة والحل

### 🔴 المشكلة - The Problem
الإعلانات التي تصل إلى تاريخ انتهائها (`expires_at`) لا تظهر في الصفحة الرئيسية حتى لو كانت محددة كـ `status='active'` في قاعدة البيانات.

**السبب**:
- الـ `active()` method في Manager يفلتر الإعلانات التي انتهى تاريخها
- الإعلانات تختفي تلقائياً بعد انتهاء صلاحيتها

### ✅ الحل - The Solution
تم إنشاء نظام متكامل لتجديد الإعلانات:

1. **Management Command**: أمر يمكن تشغيله يدوياً أو تلقائياً عبر Cron
2. **Admin Actions**: إجراءات في لوحة الإدارة لتجديد الإعلانات بنقرة واحدة
3. **خيارات متعددة**: تجديد لمدة 30، 60، أو 90 يوم

---

## Management Command

### الأمر الأساسي
```bash
python manage.py renew_expired_ads
```

### الخيارات المتاحة

#### 1. تحديد عدد الأيام
```bash
# تجديد لمدة 30 يوم (افتراضي)
python manage.py renew_expired_ads --days 30

# تجديد لمدة 60 يوم
python manage.py renew_expired_ads --days 60

# تجديد لمدة 90 يوم
python manage.py renew_expired_ads --days 90
```

#### 2. تحديد حالة الإعلانات
```bash
# تجديد الإعلانات النشطة لكن منتهية (افتراضي)
python manage.py renew_expired_ads --status active

# تجديد الإعلانات المحددة كـ منتهية
python manage.py renew_expired_ads --status expired

# تجديد جميع الإعلانات المنتهية
python manage.py renew_expired_ads --status all
```

#### 3. Dry Run (معاينة بدون تنفيذ)
```bash
# معاينة ما سيتم تجديده بدون تحديث قاعدة البيانات
python manage.py renew_expired_ads --dry-run
```

### أمثلة مركبة
```bash
# تجديد جميع الإعلانات المنتهية لمدة 90 يوم مع معاينة
python manage.py renew_expired_ads --status all --days 90 --dry-run

# تجديد الإعلانات النشطة لمدة 60 يوم
python manage.py renew_expired_ads --status active --days 60
```

### المخرجات - Output
```
Checking for ads to renew as of 2025-12-14 20:45...
Found 20 ad(s) to renew:
  - Ad #24: أرض للبيع في القاهرة (expires: 2025-12-09, status: active)
  - Ad #23: شقة للإيجار في الإسكندرية (expires: 2025-12-09, status: active)
  ... and 18 more ads

Successfully renewed 20 ad(s) with new expiration date: 2026-01-13 20:45
```

---

## Admin Actions

### الإجراءات المتاحة في لوحة الإدارة

تم إضافة 3 إجراءات جديدة في Admin Panel:

1. **تجديد الإعلانات لمدة 30 يوم** - Renew for 30 days
2. **تجديد الإعلانات لمدة 60 يوم** - Renew for 60 days
3. **تجديد الإعلانات لمدة 90 يوم** - Renew for 90 days

### كيفية الاستخدام

1. انتقل إلى **Django Admin** → **Classified Ads**
2. حدد الإعلانات التي تريد تجديدها (✓)
3. اختر الإجراء من القائمة المنسدلة **Action**
4. اضغط **Go**

### ماذا يحدث؟

عند تنفيذ الإجراء:
- ✅ يتم تحديث `expires_at` إلى تاريخ جديد
- ✅ يتم تعيين `status` إلى `ACTIVE` (حتى للإعلانات المنتهية)
- ✅ يظهر الإعلان مباشرة في الصفحة الرئيسية
- ✅ رسالة تأكيد بعدد الإعلانات المجددة والتاريخ الجديد

**مثال على الرسالة**:
```
20 إعلان تم تجديده لمدة 30 يوم (تنتهي في 2026-01-13)
```

---

## أمثلة الاستخدام

### السيناريو 1: تجديد يومي تلقائي للإعلانات النشطة
```bash
# في Cron Job (يومياً الساعة 3 صباحاً)
0 3 * * * cd /path/to/idrissimart && python manage.py renew_expired_ads --status active --days 30
```

### السيناريو 2: تجديد الإعلانات المنتهية مرة واحدة
```bash
# تجديد جميع الإعلانات المنتهية لمدة 60 يوم
python manage.py renew_expired_ads --status all --days 60
```

### السيناريو 3: معاينة قبل التنفيذ
```bash
# خطوة 1: معاينة
python manage.py renew_expired_ads --status all --days 90 --dry-run

# خطوة 2: تنفيذ بعد التأكد
python manage.py renew_expired_ads --status all --days 90
```

### السيناريو 4: استخدام Admin Actions
1. افتح `/admin/main/classifiedad/`
2. فلتر الإعلانات حسب **Status: Expired** أو **Expires at: < Today**
3. حدد جميع الإعلانات
4. اختر **تجديد الإعلانات لمدة 30 يوم**
5. اضغط **Go**

---

## إعداد Cron Job

### Linux / macOS

#### فتح Crontab
```bash
crontab -e
```

#### إضافة المهام

```bash
# تجديد الإعلانات النشطة يومياً الساعة 3 صباحاً
0 3 * * * cd /var/www/idrissimart && /usr/bin/python3 manage.py renew_expired_ads --status active --days 30

# تجديد جميع الإعلانات أسبوعياً يوم الأحد الساعة 2 صباحاً
0 2 * * 0 cd /var/www/idrissimart && /usr/bin/python3 manage.py renew_expired_ads --status all --days 60
```

### Windows Task Scheduler

#### إنشاء مهمة جديدة

1. افتح **Task Scheduler**
2. اختر **Create Basic Task**
3. اسم المهمة: `Renew Expired Ads`
4. Trigger: **Daily** الساعة **3:00 AM**
5. Action: **Start a program**
   - Program: `C:\Python311\python.exe`
   - Arguments: `manage.py renew_expired_ads --status active --days 30`
   - Start in: `C:\WORK\idrissimart`

#### باستخدام Command Line
```cmd
# إنشاء مهمة يومية
schtasks /create /tn "RenewExpiredAds" /tr "C:\Python311\python.exe C:\WORK\idrissimart\manage.py renew_expired_ads --status active --days 30" /sc daily /st 03:00
```

### Docker / Django-Crontab

إذا كنت تستخدم Django-Crontab:

#### 1. تثبيت الحزمة
```bash
pip install django-crontab
```

#### 2. إضافة إلى INSTALLED_APPS
```python
INSTALLED_APPS = [
    ...
    'django_crontab',
]
```

#### 3. إضافة CRONJOBS في settings.py
```python
CRONJOBS = [
    # تجديد الإعلانات النشطة يومياً الساعة 3 صباحاً
    ('0 3 * * *', 'django.core.management.call_command', ['renew_expired_ads', '--status', 'active', '--days', '30']),

    # تجديد جميع الإعلانات أسبوعياً
    ('0 2 * * 0', 'django.core.management.call_command', ['renew_expired_ads', '--status', 'all', '--days', '60']),
]
```

#### 4. تفعيل Cron Jobs
```bash
python manage.py crontab add
python manage.py crontab show  # للتحقق
```

---

## ⚙️ الإعدادات المتقدمة

### تخصيص فترة التجديد الافتراضية

يمكنك إضافة إعداد في `settings.py`:

```python
# settings.py
AD_RENEWAL_DEFAULT_DAYS = 30  # افتراضي
AD_RENEWAL_OPTIONS = [30, 60, 90, 180, 365]  # الخيارات المتاحة
```

### Logging

لتسجيل عمليات التجديد:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/path/to/logs/ad_renewal.log',
        },
    },
    'loggers': {
        'django.management.commands.renew_expired_ads': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## 📊 الإحصائيات والمراقبة

### التحقق من الإعلانات المنتهية

```bash
# عرض عدد الإعلانات المنتهية
python manage.py shell -c "from main.models import ClassifiedAd; from django.utils import timezone; print('Expired:', ClassifiedAd.objects.filter(status='active', expires_at__lt=timezone.now()).count())"
```

### مراقبة عمليات التجديد

```bash
# تشغيل مع معاينة أولاً
python manage.py renew_expired_ads --dry-run

# ثم التنفيذ الفعلي
python manage.py renew_expired_ads
```

---

## 🔒 الأمان والاعتبارات

### احتياطات مهمة

1. **استخدم Dry Run أولاً**: دائماً استخدم `--dry-run` قبل التنفيذ الفعلي
2. **النسخ الاحتياطي**: احتفظ بنسخة احتياطية من قاعدة البيانات قبل التجديد الجماعي
3. **الفلترة الدقيقة**: استخدم الفلاتر المناسبة (`--status`) لتجنب تجديد إعلانات غير مرغوبة
4. **المراقبة**: راقب عمليات التجديد التلقائية عبر Logs

### الصلاحيات

- **Management Command**: يحتاج صلاحية تشغيل Django commands
- **Admin Actions**: متاح فقط للـ Staff Users في Admin Panel

---

## 🆘 استكشاف الأخطاء

### المشكلة: لا توجد إعلانات للتجديد

**السبب المحتمل**: جميع الإعلانات لها `expires_at` في المستقبل أو NULL

**الحل**:
```bash
# تحقق من الإعلانات المنتهية
python manage.py shell -c "from main.models import ClassifiedAd; from django.utils import timezone; print(ClassifiedAd.objects.filter(expires_at__lt=timezone.now()).count())"
```

### المشكلة: الإعلانات لا تظهر بعد التجديد

**السبب المحتمل**: قد يكون Cache

**الحل**:
```bash
# مسح Cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### المشكلة: Cron Job لا يعمل

**الحل**:
1. تحقق من الصلاحيات: `chmod +x manage.py`
2. تحقق من المسار الكامل: `/usr/bin/python3`
3. تحقق من Logs: `/var/log/cron` أو `/var/log/syslog`

---

## 📝 ملاحظات ختامية

### الميزات الرئيسية
✅ تجديد تلقائي للإعلانات
✅ خيارات مرنة (30/60/90 يوم)
✅ Dry Run للمعاينة
✅ Admin Actions سهلة الاستخدام
✅ دعم Cron Jobs
✅ إعادة تفعيل الإعلانات المنتهية

### التطويرات المستقبلية المقترحة
- [ ] إضافة إشعارات بالبريد الإلكتروني عند التجديد
- [ ] Dashboard لعرض إحصائيات التجديد
- [ ] API Endpoint لتجديد الإعلانات
- [ ] تجديد تلقائي بناءً على الباقات المدفوعة

---

## 📧 الدعم

للمساعدة أو الاستفسارات:
- راجع الـ Admin Panel في `/admin/`
- استخدم `--help` مع الأمر للحصول على المساعدة

```bash
python manage.py renew_expired_ads --help
```

---

**تاريخ الإنشاء**: 2025-12-14
**الإصدار**: 1.0
**المطور**: Claude Code Assistant
