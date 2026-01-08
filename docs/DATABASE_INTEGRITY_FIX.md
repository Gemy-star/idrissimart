# Database Integrity Fix - Country Foreign Key

## 🔍 المشكلة | Problem

عند تشغيل المايجريشن على السيرفر، يظهر الخطأ التالي:
```
django.db.utils.OperationalError: (1292, "Truncated incorrect INTEGER value: 'SA'")
```

**السبب:** بعض المستخدمين لديهم قيم نصية (مثل `'SA'`) في عمود `country_id` الذي يجب أن يحتوي على أرقام صحيحة (Foreign Key).

---

## ✅ الحل | Solution

تم إنشاء سكريبت `fix_db_integrity.py` الذي:
1. ✅ يستخدم Django ORM (يعمل مع SQLite و MySQL)
2. ✅ يجد جميع المستخدمين ذوي `country_id` غير صحيحة
3. ✅ يحدثهم ليستخدموا دولة افتراضية صالحة
4. ✅ يتحقق من نجاح العملية

---

## 🚀 الاستخدام | Usage

### على السيرفر (Production) - MySQL/MariaDB

```bash
# 1. انتقل إلى مجلد المشروع
cd /srv/idrissimart

# 2. قم بتشغيل السكريبت مع إعدادات Docker
poetry run python fix_db_integrity.py

# أو إذا كنت تستخدم إعدادات Docker محددة
DJANGO_SETTINGS_MODULE=idrissimart.settings.docker poetry run python fix_db_integrity.py
```

### محلياً (Development) - SQLite

```bash
# على Windows
poetry run python fix_db_integrity.py

# على Linux/Mac
python3 fix_db_integrity.py
```

---

## 📝 المخرجات | Output

عند تشغيل السكريبت بنجاح:

```
============================================================
🔧 Database Integrity Fix - Country Foreign Key
============================================================
📊 Database: idrissimart
🔌 Engine: django.db.backends.mysql

✓ Found 8 active countries
  Valid IDs: [1, 2, 3, 4, 5]...

❌ Found 43 users with invalid country_id:
   - User ID 1: country_id = 'SA'
   - User ID 2: country_id = ''
   - User ID 3: country_id = 'None'
   ... and 40 more

✓ Default country selected:
  ID: 2
  Name: السعودية / Saudi Arabia

🔄 Updating 43 users to country ID 2...
✅ Successfully updated 43 users!

🔍 Verifying fix...
✅ All users now have valid country references!

============================================================
✅ Database integrity fix completed successfully!
============================================================
```

---

## ⚙️ كيف يعمل السكريبت | How It Works

### 1. الكشف عن المشكلة
```sql
SELECT id, country_id
FROM users
WHERE country_id IS NULL
   OR country_id = ''
   OR country_id NOT IN (
       SELECT id FROM content_country WHERE is_active = 1
   )
```

### 2. التحديث
```sql
UPDATE users
SET country_id = <default_country_id>
WHERE id = <user_id>
```

### 3. التحقق
يتحقق السكريبت من أن جميع المستخدمين لديهم `country_id` صحيح بعد التحديث.

---

## 🔧 الإعدادات | Configuration

السكريبت يدعم الإعدادات التالية:

### 1. استخدام إعدادات Django الحالية
```bash
# يستخدم DJANGO_SETTINGS_MODULE من البيئة
poetry run python fix_db_integrity.py
```

### 2. تحديد إعدادات معينة
```bash
# للإنتاج (Production)
DJANGO_SETTINGS_MODULE=idrissimart.settings.docker poetry run python fix_db_integrity.py

# للتطوير (Development)
DJANGO_SETTINGS_MODULE=idrissimart.settings.local poetry run python fix_db_integrity.py
```

---

## ⚠️ ملاحظات مهمة | Important Notes

### قبل تشغيل السكريبت:

1. **عمل نسخة احتياطية من القاعدة**
   ```bash
   # MySQL/MariaDB
   mysqldump -u username -p database_name > backup.sql

   # SQLite
   cp db.sqlite3 db.sqlite3.backup
   ```

2. **التأكد من وجود دول نشطة**
   - يجب أن يكون هناك دولة واحدة على الأقل في جدول `content_country` مع `is_active=True`

3. **صلاحيات قاعدة البيانات**
   - يجب أن يكون للمستخدم صلاحيات `UPDATE` على جدول `users`

### بعد تشغيل السكريبت:

4. **تشغيل المايجريشن**
   ```bash
   poetry run python manage.py migrate
   ```

5. **التحقق من النظام**
   ```bash
   poetry run python manage.py check
   ```

---

## 🐛 استكشاف الأخطاء | Troubleshooting

### خطأ: "No active countries found"
```bash
# الحل: أضف دولة واحدة على الأقل
poetry run python manage.py shell
>>> from content.models import Country
>>> Country.objects.create(
...     code='SA',
...     name='Saudi Arabia',
...     name_ar='السعودية',
...     name_en='Saudi Arabia',
...     is_active=True
... )
```

### خطأ: "ModuleNotFoundError: No module named 'idrissimart'"
```bash
# الحل: قم بتشغيل السكريبت من مجلد المشروع الرئيسي
cd /srv/idrissimart  # أو مسار مشروعك
poetry run python fix_db_integrity.py
```

### خطأ: "Database is locked" (SQLite)
```bash
# الحل: أغلق أي اتصالات مفتوحة بالقاعدة
# ثم أعد تشغيل السكريبت
```

---

## 📊 الحالات التي يتعامل معها السكريبت

| الحالة | القيمة الحالية | القيمة الجديدة |
|--------|----------------|----------------|
| قيمة NULL | `NULL` | ID صالح |
| سلسلة فارغة | `''` | ID صالح |
| كود دولة نصي | `'SA'`, `'EG'` | ID صالح |
| رقم غير موجود | `999` | ID صالح |
| قيمة 'None' نصية | `'None'` | ID صالح |

---

## 🔄 التكامل مع CI/CD

يمكنك إضافة السكريبت إلى خط الإنتاج:

```yaml
# .github/workflows/deploy.yml
- name: Fix Database Integrity
  run: poetry run python fix_db_integrity.py

- name: Run Migrations
  run: poetry run python manage.py migrate
```

---

## 📚 ملفات ذات صلة | Related Files

- **السكريبت الرئيسي:** `fix_db_integrity.py`
- **الموديل:** `content/models.py` (Country model)
- **المايجريشن:** `main/migrations/0044_alter_user_city_alter_user_country.py`
- **إعدادات السيرفر:** `idrissimart/settings/docker.py`

---

## ✅ التحقق من النجاح | Success Verification

بعد تشغيل السكريبت والمايجريشن:

```bash
# 1. تحقق من عدم وجود أخطاء
poetry run python manage.py check

# 2. تحقق من المستخدمين
poetry run python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(country_id__isnull=True).count()
0  # يجب أن يكون صفر

>>> User.objects.filter(country_id='').count()
0  # يجب أن يكون صفر
```

---

**آخر تحديث:** 2026-01-09
**الإصدار:** 2.0
**الحالة:** ✅ جاهز للاستخدام على الإنتاج
