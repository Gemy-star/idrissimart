# Management Commands للإعلانات - Ads Management Commands

## نظرة عامة
هذا الملف يوثق الـ management commands المتعلقة بإدارة الإعلانات.

---

## 1. expire_ads

### الوصف
تحديث حالة الإعلانات التي انتهت صلاحيتها إلى `EXPIRED`.

### الاستخدام
```bash
# تطبيق التحديثات
python manage.py expire_ads

# معاينة فقط (بدون تطبيق)
python manage.py expire_ads --dry-run
```

### المعاملات
- `--dry-run`: معاينة النتائج بدون تطبيق التغييرات

### مثال على الناتج
```
⚠️  تم العثور على 5 إعلان منتهي - Found 5 expired ads
  - [123] شقة للبيع في القاهرة (انتهى منذ 2 يوم - expired 2 days ago)
  - [456] سيارة للبيع (انتهى منذ 5 يوم - expired 5 days ago)
  ...

✅ تم تحديث 5 إعلان إلى حالة "منتهي"
✅ Updated 5 ads to EXPIRED status
```

### Cron Job المقترح
```cron
# كل يوم الساعة 2 صباحاً
0 2 * * * cd /var/www/idrissimart && /path/to/python manage.py expire_ads >> /var/log/expire_ads.log 2>&1
```

---

## 2. send_expiration_notifications

### الوصف
إرسال إشعارات للأعضاء بقرب انتهاء إعلاناتهم.

### الاستخدام
```bash
# إرسال إشعارات قبل 3 أيام (افتراضي)
python manage.py send_expiration_notifications

# إرسال إشعارات قبل 7 أيام
python manage.py send_expiration_notifications --days 7

# معاينة فقط
python manage.py send_expiration_notifications --days 3 --dry-run
```

### المعاملات
- `--days N`: عدد الأيام قبل الانتهاء (افتراضي: 3)
- `--dry-run`: معاينة بدون إرسال إشعارات

### مثال على الناتج
```
⚠️  تم العثور على 3 إعلان سينتهي خلال 3 أيام
⚠️  Found 3 ads expiring within 3 days

  - [123] شقة للبيع (باقي 2 يوم - 2 days left) - المالك: ahmed
  - [456] سيارة للبيع (باقي 3 يوم - 3 days left) - المالك: mohamed
  - [789] محل للإيجار (باقي 1 يوم - 1 day left) - المالك: sara

✅ تم إرسال 3 إشعار داخلي و 2 بريد إلكتروني
✅ Sent 3 in-app notifications and 2 emails
```

### Cron Jobs المقترحة
```cron
# إشعار قبل 3 أيام - كل يوم الساعة 10 صباحاً
0 10 * * * cd /var/www/idrissimart && /path/to/python manage.py send_expiration_notifications --days 3 >> /var/log/expiry_notifications.log 2>&1

# إشعار قبل 7 أيام - كل يوم الساعة 11 صباحاً
0 11 * * * cd /var/www/idrissimart && /path/to/python manage.py send_expiration_notifications --days 7 >> /var/log/expiry_notifications.log 2>&1
```

---

## 3. check_saved_search_notifications

### الوصف
فحص حالة إعدادات إشعارات البحث المحفوظ للأعضاء (command موجود مسبقاً).

### الاستخدام
```bash
python manage.py check_saved_search_notifications
```

---

## إعداد Cron Jobs - Production Setup

### 1. فتح crontab
```bash
crontab -e
```

### 2. إضافة الـ commands
```cron
# Ad Expiration Management
# تحديث الإعلانات المنتهية - كل يوم الساعة 2 صباحاً
0 2 * * * cd /var/www/idrissimart && /usr/bin/python3 manage.py expire_ads >> /var/log/django/expire_ads.log 2>&1

# إشعارات قبل 3 أيام - كل يوم الساعة 10 صباحاً
0 10 * * * cd /var/www/idrissimart && /usr/bin/python3 manage.py send_expiration_notifications --days 3 >> /var/log/django/notifications_3days.log 2>&1

# إشعارات قبل 7 أيام - كل يوم الساعة 11 صباحاً
0 11 * * * cd /var/www/idrissimart && /usr/bin/python3 manage.py send_expiration_notifications --days 7 >> /var/log/django/notifications_7days.log 2>&1

# تنظيف الـ logs القديمة - كل أسبوع
0 3 * * 0 find /var/log/django/ -name "*.log" -mtime +30 -delete
```

### 3. التحقق من Cron Jobs
```bash
# عرض الـ cron jobs الحالية
crontab -l

# فحص سجلات cron
sudo tail -f /var/log/syslog | grep CRON
```

---

## مراقبة الأداء - Monitoring

### عرض الـ Logs
```bash
# آخر 50 سطر
tail -50 /var/log/django/expire_ads.log

# متابعة الـ logs مباشرة
tail -f /var/log/django/expire_ads.log

# البحث عن أخطاء
grep -i "error" /var/log/django/*.log
```

### إحصائيات
```bash
# عدد الإعلانات المنتهية
python manage.py shell -c "from main.models import ClassifiedAd; print(ClassifiedAd.objects.filter(status='expired').count())"

# عدد الإعلانات التي ستنتهي خلال 3 أيام
python manage.py shell -c "from main.models import ClassifiedAd; print(ClassifiedAd.objects.expiring_soon(days=3).count())"
```

---

## استكشاف الأخطاء - Troubleshooting

### المشكلة: Cron لا يعمل
```bash
# التحقق من خدمة cron
sudo systemctl status cron

# إعادة تشغيل cron
sudo systemctl restart cron

# التحقق من الصلاحيات
ls -la /var/www/idrissimart/manage.py
```

### المشكلة: أخطاء في Python path
```bash
# استخدام المسار الكامل لـ Python
which python3
# ثم استخدم المسار الكامل في crontab
```

### المشكلة: أخطاء في البريد الإلكتروني
```python
# في settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # للتطوير
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'     # للإنتاج

# تحقق من إعدادات SMTP
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

---

## الاختبار - Testing

### اختبار يدوي
```bash
# تشغيل في وضع التجربة
python manage.py expire_ads --dry-run
python manage.py send_expiration_notifications --days 3 --dry-run

# تشغيل فعلي
python manage.py expire_ads
python manage.py send_expiration_notifications --days 3
```

### اختبار مع بيانات تجريبية
```python
# Django shell
python manage.py shell

from main.models import ClassifiedAd
from django.utils import timezone
from datetime import timedelta

# إنشاء إعلان منتهي للاختبار
ad = ClassifiedAd.objects.first()
ad.expires_at = timezone.now() - timedelta(days=2)
ad.save()

# تشغيل الـ command
exit()
python manage.py expire_ads

# التحقق
python manage.py shell
from main.models import ClassifiedAd
ClassifiedAd.objects.filter(status='expired').count()
```

---

## الأمان - Security

### حماية Logs
```bash
# إنشاء مجلد logs مع صلاحيات محدودة
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django
sudo chmod 750 /var/log/django
```

### Environment Variables
```bash
# لا تضع sensitive data في crontab
# استخدم .env file بدلاً من ذلك

# في crontab
0 2 * * * cd /var/www/idrissimart && source .env && python manage.py expire_ads
```

---

## نصائح الأداء - Performance Tips

1. **استخدم Database Indexes:**
```sql
CREATE INDEX idx_ads_expiry ON classified_ads(expires_at, status);
```

2. **Batch Processing:**
- استخدم `bulk_update()` للتحديثات الكبيرة
- استخدم `select_related()` و `prefetch_related()`

3. **Async Tasks (مستقبلاً):**
```bash
# استخدم Celery للمهام الكبيرة
pip install celery redis
```

---

## الخلاصة

✅ **Commands المتاحة:**
1. `expire_ads` - تحديث الإعلانات المنتهية
2. `send_expiration_notifications` - إرسال الإشعارات

✅ **Automation:**
- Cron jobs للتشغيل التلقائي
- Logs للمراقبة
- Dry-run للاختبار

✅ **Best Practices:**
- تشغيل يومي في أوقات منخفضة الحمل
- مراقبة الـ logs بانتظام
- اختبار في staging قبل production
