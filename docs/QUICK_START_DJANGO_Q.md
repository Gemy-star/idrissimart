# Quick Start Guide - Django Q Setup

## 🚀 البداية السريعة

### 1. تثبيت المتطلبات

```bash
pip install django-q2 redis hiredis
```

### 2. التحقق من Redis يعمل

```bash
# محلياً
redis-cli ping
# يجب أن يعود: PONG

# في Docker
docker-compose up -d redis
docker-compose exec redis redis-cli ping
```

### 3. تشغيل Migrations

```bash
python manage.py migrate django_q
```

### 4. إعداد المهام المجدولة

```bash
python manage.py setup_scheduled_tasks
```

### 5. تشغيل Django Q Worker

**محلياً:**
```bash
python manage.py qcluster
```

**في Docker:**
```bash
docker-compose up -d qcluster
docker-compose logs -f qcluster
```

---

## ✅ التحقق من التشغيل

### اختبار سريع

```python
python manage.py shell

# اختبار مهمة
from main.scheduled_tasks import expire_ads_task
result = expire_ads_task()
print(result)
```

### عرض المهام المجدولة

```bash
# في Django Admin
# افتح: http://localhost:8000/admin/django_q/schedule/

# أو في shell
python manage.py shell
from django_q.models import Schedule
for task in Schedule.objects.all():
    print(f"{task.name}: Next run at {task.next_run}")
```

---

## 📋 المهام المجدولة

| المهمة | التوقيت | الوصف |
|--------|---------|-------|
| Expire Ads | يومياً 2:00 ص | إنهاء صلاحية الإعلانات المنتهية |
| 3-Day Notifications | يومياً 10:00 ص | إشعارات قبل 3 أيام من الانتهاء |
| 7-Day Notifications | يومياً 11:00 ص | إشعارات قبل 7 أيام من الانتهاء |
| Cleanup Notifications | أسبوعياً 3:00 ص | حذف الإشعارات القديمة |
| Check Upgrades | كل 6 ساعات | فحص انتهاء التمييزات |

---

## 🔧 الأوامر المهمة

```bash
# إعداد المهام
python manage.py setup_scheduled_tasks

# إعادة تعيين المهام
python manage.py setup_scheduled_tasks --reset

# تشغيل worker
python manage.py qcluster

# حذف المهام المكتملة
python manage.py qclean

# عرض معلومات
python manage.py qinfo

# اختبار مهمة يدوياً
python manage.py expire_ads --dry-run
python manage.py send_expiration_notifications --days 3 --dry-run
```

---

## 🐳 Docker Commands

```bash
# بناء وتشغيل
docker-compose up -d

# عرض logs
docker-compose logs -f qcluster

# إعادة تشغيل
docker-compose restart qcluster

# تنفيذ أمر
docker-compose exec qcluster python manage.py setup_scheduled_tasks

# إيقاف
docker-compose down
```

---

## 🔍 استكشاف الأخطاء

### Redis لا يعمل
```bash
# محلياً
sudo systemctl start redis
sudo systemctl status redis

# Docker
docker-compose up -d redis
docker-compose logs redis
```

### qcluster لا يعمل
```bash
# محلياً
ps aux | grep qcluster
python manage.py qcluster

# Docker
docker-compose ps qcluster
docker-compose restart qcluster
docker-compose logs -f qcluster
```

### المهام لا تنفذ
```bash
# التحقق من المهام المجدولة
python manage.py shell
from django_q.models import Schedule
print(Schedule.objects.count())

# التحقق من الأخطاء
from django_q.models import Failure
for f in Failure.objects.all()[:5]:
    print(f.name, f.result)
```

---

## 📚 المزيد من المعلومات

- [DJANGO_Q_SETUP_GUIDE.md](DJANGO_Q_SETUP_GUIDE.md) - دليل شامل
- [AD_EXPIRATION_RENEWAL_SYSTEM.md](AD_EXPIRATION_RENEWAL_SYSTEM.md) - نظام التجديد
- [MANAGEMENT_COMMANDS_GUIDE.md](MANAGEMENT_COMMANDS_GUIDE.md) - دليل الأوامر

---

## ⚠️ ملاحظات مهمة

1. تأكد من تشغيل Redis قبل qcluster
2. استخدم `--reset` بحذر (يحذف جميع المهام)
3. راقب الـ logs بانتظام
4. استخدم `--dry-run` للاختبار أولاً
5. قم بعمل backup للبيانات قبل التحديثات الكبيرة

---

**تم بحمد الله! 🎉**
