# خطوات إصلاح Slugs العربية في الإنتاج (Production)

## 📋 نظرة عامة
هذا الدليل يشرح خطوات تطبيق إصلاحات الـ slugs العربية في بيئة الإنتاج بشكل آمن.

---

## ⚠️ قبل البدء - احتياطات مهمة

### 1. النسخ الاحتياطي
```bash
# عمل نسخة احتياطية من قاعدة البيانات
# PostgreSQL
pg_dump -U username -d database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# أو MySQL
mysqldump -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# أو SQLite
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. وضع الصيانة (اختياري)
```bash
# إذا كنت تستخدم nginx
sudo systemctl stop nginx
# أو عرض صفحة صيانة
```

---

## 🚀 الخطوات التفصيلية

### الخطوة 1: رفع الملفات المحدثة

```bash
# على جهازك المحلي - Commit التغييرات
cd /path/to/idrissimart
git add main/views.py
git add main/management/commands/fix_arabic_slugs.py
git commit -m "Fix: Add Arabic slug support and URL decoding for categories"
git push origin main

# على السيرفر - Pull التغييرات
cd /path/to/production/idrissimart
git pull origin main
```

---

### الخطوة 2: تفعيل البيئة الافتراضية

```bash
# إذا كنت تستخدم virtualenv
source venv/bin/activate

# أو Poetry
poetry shell

# أو pipenv
pipenv shell
```

---

### الخطوة 3: تحديث Dependencies (إذا لزم الأمر)

```bash
# Poetry
poetry install --no-dev

# أو pip
pip install -r requirements.txt
```

---

### الخطوة 4: تجربة Dry Run أولاً (موصى به بشدة!)

```bash
# معاينة التغييرات على الفئات فقط
python manage.py fix_arabic_slugs --categories-only --dry-run

# التحقق من النتائج
# إذا كانت النتائج صحيحة، تابع إلى الخطوة التالية
```

**مثال على النتيجة المتوقعة:**
```
Found 80 categories to process
✓ الوظائف المساندة
  Old: support-jobs → New: الوظائف-المساندة
📊 Category Results: 78 fixed, 2 already correct
```

---

### الخطوة 5: تطبيق الإصلاح على الفئات

```bash
# تطبيق الإصلاح فعلياً
python manage.py fix_arabic_slugs --categories-only

# انتظر حتى يكتمل (قد يستغرق 30 ثانية - دقيقتين)
```

**نتيجة متوقعة:**
```
✅ All slugs have been fixed successfully!
📊 Category Results: 80 fixed, 0 already correct
```

---

### الخطوة 6: إصلاح Slugs الإعلانات (اختياري)

```bash
# معاينة أولاً
python manage.py fix_arabic_slugs --ads-only --dry-run

# إذا كانت النتائج مرضية، طبق
python manage.py fix_arabic_slugs --ads-only
```

**⚠️ ملاحظة:** قد يستغرق هذا وقتاً أطول إذا كان لديك آلاف الإعلانات (5-10 دقائق لـ 10,000 إعلان).

---

### الخطوة 7: جمع الملفات الثابتة (Static Files)

```bash
# إذا كان هناك تغييرات في CSS/JS
python manage.py collectstatic --noinput
```

---

### الخطوة 8: إعادة تشغيل الخدمات

#### إذا كنت تستخدم Gunicorn + Systemd:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

#### إذا كنت تستخدم uWSGI:
```bash
sudo systemctl restart uwsgi
sudo systemctl restart nginx
```

#### إذا كنت تستخدم Supervisor:
```bash
sudo supervisorctl restart idrissimart
```

#### إذا كنت تستخدم Docker:
```bash
docker-compose restart web
```

---

### الخطوة 9: التحقق من عمل الموقع

```bash
# اختبار الموقع
curl -I https://yourdomain.com

# يجب أن ترى: HTTP/2 200
```

**اختبارات يدوية:**
1. افتح الموقع في المتصفح
2. انقر على أيقونة فئة في الهيدر
3. تحقق من أن الرابط يحتوي على slug عربي: `?category=الوظائف-المساندة`
4. تحقق من ظهور الإعلانات في الصفحة
5. جرب فئات مختلفة

---

### الخطوة 10: مراقبة السجلات (Logs)

```bash
# راقب سجلات Gunicorn
tail -f /path/to/gunicorn/error.log

# أو سجلات Nginx
tail -f /var/log/nginx/error.log

# ابحث عن أي أخطاء متعلقة بـ:
# - Category.DoesNotExist
# - UnicodeDecodeError
# - 404 errors
```

---

## 🔍 التحقق من النجاح

### 1. التحقق من قاعدة البيانات

```bash
# افتح Django shell
python manage.py shell

# ثم قم بالتالي:
from main.models import Category
cat = Category.objects.filter(parent__isnull=True).first()
print(f"Slug: {cat.slug}")
# يجب أن ترى slug عربي مثل: "الوظائف-المساندة"
```

### 2. التحقق من الروابط في المتصفح

افتح Chrome DevTools → Network Tab:
- انقر على فئة
- تحقق من الـ Request URL
- يجب أن تحتوي على الـ slug العربي

---

## 🐛 استكشاف الأخطاء

### المشكلة 1: لا تظهر إعلانات بعد النقر على فئة

**الحل:**
```bash
# تحقق من أن الفئات نشطة
python manage.py shell

from main.models import Category
cats = Category.objects.filter(slug__contains='الوظائف')
for cat in cats:
    print(f"{cat.name_ar}: is_active={cat.is_active}")
```

### المشكلة 2: أخطاء 404 أو UnicodeError

**الحل:**
```bash
# تحقق من إعدادات Django
# في settings.py:
# DEFAULT_CHARSET = 'utf-8'
# وتأكد من:
# DATABASES['default']['OPTIONS'] = {'charset': 'utf8mb4'}  # For MySQL
```

### المشكلة 3: Slugs لا تزال بالإنجليزية

**الحل:**
```bash
# أعد تشغيل الأمر
python manage.py fix_arabic_slugs --categories-only

# تحقق من السجلات
# إذا رأيت "already correct"، معناها تم التحديث مسبقاً
```

### المشكلة 4: بطء في التحميل

**الحل:**
```bash
# أعد بناء الفهارس
python manage.py sqlsequencereset main | python manage.py dbshell

# أو PostgreSQL:
# VACUUM ANALYZE main_category;
# REINDEX TABLE main_category;
```

---

## 📊 الأداء المتوقع

| العملية | عدد العناصر | الوقت المتوقع |
|---------|-------------|----------------|
| إصلاح الفئات | 100 فئة | ~30 ثانية |
| إصلاح الإعلانات | 1,000 إعلان | ~2 دقيقة |
| إصلاح الإعلانات | 10,000 إعلان | ~10 دقائق |

---

## 🔄 التراجع (Rollback) في حالة المشاكل

### إذا حدثت مشاكل:

```bash
# 1. أوقف الخدمات
sudo systemctl stop gunicorn nginx

# 2. استعد النسخة الاحتياطية
# PostgreSQL
psql -U username -d database_name < backup_YYYYMMDD_HHMMSS.sql

# MySQL
mysql -u username -p database_name < backup_YYYYMMDD_HHMMSS.sql

# SQLite
cp db.sqlite3.backup_YYYYMMDD_HHMMSS db.sqlite3

# 3. ارجع للكود القديم
git reset --hard HEAD~1

# 4. أعد تشغيل الخدمات
sudo systemctl start gunicorn nginx
```

---

## ✅ Checklist النهائي

قبل إنهاء الصيانة، تأكد من:

- [ ] تم تطبيق الإصلاح بنجاح (رأيت رسالة "All slugs have been fixed successfully!")
- [ ] تم إعادة تشغيل جميع الخدمات
- [ ] الموقع يعمل ويفتح بشكل طبيعي
- [ ] روابط الفئات في الهيدر تحتوي على slugs عربية
- [ ] النقر على الفئات يعرض الإعلانات الصحيحة
- [ ] لا توجد أخطاء في السجلات
- [ ] تم اختبار فئات متعددة
- [ ] الأداء طبيعي (لا بطء ملحوظ)

---

## 📝 ملاحظات إضافية

### 1. الصيانة الدورية
يمكنك تشغيل هذا الأمر دورياً إذا كنت تضيف فئات جديدة:
```bash
# إضافة إلى cron job
0 2 * * 0 cd /path/to/project && python manage.py fix_arabic_slugs --categories-only
```

### 2. مراقبة الأداء
```bash
# راقب استخدام CPU والذاكرة أثناء التنفيذ
htop

# أو
top
```

### 3. إشعار المستخدمين (اختياري)
إذا كان لديك نظام إشعارات، أعلم المستخدمين بالتحديث:
```python
from django.contrib.messages import info
info(request, "تم تحديث النظام لدعم الروابط العربية بشكل أفضل!")
```

---

## 🆘 الحصول على المساعدة

إذا واجهت مشاكل:
1. راجع السجلات: `tail -f /var/log/gunicorn/error.log`
2. تحقق من Django logs
3. راجع قاعدة البيانات
4. استعد النسخة الاحتياطية إذا لزم الأمر

---

## 📅 تاريخ التحديث
- **تاريخ الإنشاء**: 29 يناير 2026
- **الإصدار**: 1.0.0
- **آخر تحديث**: 29 يناير 2026

---

## 🎯 الخلاصة

باتباع هذه الخطوات بعناية، ستتمكن من تحديث نظامك في الإنتاج بشكل آمن وبدون توقف خدمة أو فقدان بيانات. تذكر دائماً:

1. **النسخ الاحتياطي أولاً**
2. **Dry Run قبل التطبيق الفعلي**
3. **المراقبة بعد التطبيق**
4. **الاختبار الشامل**

🚀 حظاً موفقاً!
