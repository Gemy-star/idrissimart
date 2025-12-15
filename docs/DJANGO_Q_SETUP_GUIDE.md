# Django Q Configuration & Scheduled Tasks

## نظرة عامة - Overview

تم إعداد Django Q لإدارة المهام غير المتزامنة والمهام المجدولة باستخدام Redis كـ message broker.

---

## التكوين - Configuration

### 1. Q_CLUSTER Settings في docker.py

```python
Q_CLUSTER = {
    "name": "idrissimart",
    "workers": 4,                    # عدد الـ workers
    "timeout": 90,                   # مهلة تنفيذ المهمة (ثانية)
    "retry": 120,                    # مهلة إعادة المحاولة
    "redis": {
        "host": "127.0.0.1",         # عنوان Redis
        "port": 6379,                # منفذ Redis
        "db": 0,                     # رقم قاعدة البيانات
        "password": None,            # كلمة مرور Redis (إن وجدت)
    },
    "compress": True,                # ضغط البيانات
    "save_limit": 250,              # حد حفظ النتائج
    "queue_limit": 500,             # حد قائمة الانتظار
    "orm": "default",               # استخدام ORM لحفظ النتائج
}
```

### 2. متغيرات البيئة - Environment Variables

يمكن تخصيص الإعدادات عبر متغيرات البيئة:

```bash
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
```

---

## المهام المجدولة - Scheduled Tasks

### ملف: `main/scheduled_tasks.py`

#### 1. expire_ads_task()
**الوظيفة:** إنهاء صلاحية الإعلانات المنتهية

**الجدول:** يومياً الساعة 2:00 صباحاً

**الوصف:**
- يبحث عن الإعلانات النشطة التي انتهت صلاحيتها
- يحدث حالتها إلى `EXPIRED`
- يسجل النتائج في الـ logs

**العائد:**
```python
{
    "success": True,
    "count": 5,
    "message": "Successfully expired 5 ads"
}
```

---

#### 2. send_expiration_notifications_task(days=3)
**الوظيفة:** إرسال إشعارات قبل انتهاء الإعلانات

**الجدول:**
- يومياً الساعة 10:00 صباحاً (قبل 3 أيام)
- يومياً الساعة 11:00 صباحاً (قبل 7 أيام)

**الوصف:**
- يبحث عن الإعلانات التي ستنتهي خلال X أيام
- يرسل إشعار داخلي (Notification)
- يرسل بريد إلكتروني
- يمنع الإشعارات المكررة (خلال 24 ساعة)

**العائد:**
```python
{
    "success": True,
    "count": 3,
    "notifications_sent": 3,
    "emails_sent": 2,
    "message": "Sent notifications for 3 ads"
}
```

---

#### 3. send_7day_expiration_notifications_task()
**الوظيفة:** إرسال إشعارات قبل 7 أيام من الانتهاء

**الجدول:** يومياً الساعة 11:00 صباحاً

**الوصف:** نفس `send_expiration_notifications_task` لكن مع `days=7`

---

#### 4. cleanup_old_notifications_task()
**الوظيفة:** حذف الإشعارات القديمة المقروءة

**الجدول:** أسبوعياً يوم الأحد الساعة 3:00 صباحاً

**الوصف:**
- يحذف الإشعارات المقروءة الأقدم من 30 يوم
- يحافظ على نظافة قاعدة البيانات

**العائد:**
```python
{
    "success": True,
    "count": 150,
    "message": "Deleted 150 old notifications"
}
```

---

#### 5. check_upgrade_expiry_task()
**الوظيفة:** التحقق من انتهاء صلاحية تمييزات الإعلانات

**الجدول:** كل 6 ساعات

**الوصف:**
- يبحث عن التمييزات النشطة المنتهية
- يقوم بإيقافها تلقائياً

**العائد:**
```python
{
    "success": True,
    "count": 2,
    "message": "Deactivated 2 expired upgrades"
}
```

---

## الإعداد - Setup

### 1. تثبيت المتطلبات

```bash
pip install django-q2
pip install redis
```

### 2. إضافة إلى INSTALLED_APPS

في `settings/common.py`:
```python
INSTALLED_APPS = [
    # ...
    'django_q',
    # ...
]
```

### 3. تشغيل Migrations

```bash
python manage.py migrate django_q
```

### 4. تسجيل المهام المجدولة

```bash
# طريقة سهلة باستخدام management command
python manage.py setup_scheduled_tasks

# إعادة تعيين وإنشاء من جديد
python manage.py setup_scheduled_tasks --reset
```

**أو يدوياً في Django shell:**
```python
python manage.py shell

from main.scheduled_tasks import register_scheduled_tasks
register_scheduled_tasks()
```

---

## التشغيل - Running

### Development (محلي)

```bash
# تشغيل Django Q worker
python manage.py qcluster
```

### Production (Docker)

#### 1. تحديث docker-compose.yml

```yaml
services:
  web:
    # ... existing web service config

  redis:
    image: redis:7-alpine
    container_name: idrissimart_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  qcluster:
    build: .
    container_name: idrissimart_qcluster
    command: python manage.py qcluster
    volumes:
      - .:/app
    depends_on:
      - redis
      - db
    env_file:
      - .env
    restart: unless-stopped
    environment:
      - DJANGO_SETTINGS_MODULE=idrissimart.settings.docker
      - REDIS_HOST=redis
      - REDIS_PORT=6379

volumes:
  redis_data:
```

#### 2. تشغيل الـ containers

```bash
# بناء وتشغيل
docker-compose up -d

# التحقق من الـ logs
docker-compose logs -f qcluster

# إعادة تشغيل qcluster فقط
docker-compose restart qcluster
```

---

## المراقبة - Monitoring

### 1. Django Admin

افتح `/admin/django_q/` لرؤية:
- **Successful tasks:** المهام الناجحة
- **Failed tasks:** المهام الفاشلة
- **Scheduled tasks:** المهام المجدولة
- **ORM Queries:** الاستعلامات

### 2. Logs

```bash
# Development
tail -f /path/to/logs/django.log

# Docker
docker-compose logs -f qcluster
```

### 3. Django Shell

```python
python manage.py shell

# عرض المهام المجدولة
from django_q.models import Schedule
for task in Schedule.objects.all():
    print(f"{task.name}: Next run at {task.next_run}")

# عرض آخر 10 مهام
from django_q.models import Success, Failure

# Successful tasks
for task in Success.objects.all()[:10]:
    print(f"{task.name}: {task.result}")

# Failed tasks
for task in Failure.objects.all()[:10]:
    print(f"{task.name}: {task.result}")
```

---

## الاختبار - Testing

### 1. اختبار مهمة يدوياً

```python
python manage.py shell

# اختبار expire_ads_task
from main.scheduled_tasks import expire_ads_task
result = expire_ads_task()
print(result)

# اختبار send_expiration_notifications_task
from main.scheduled_tasks import send_expiration_notifications_task
result = send_expiration_notifications_task(days=3)
print(result)
```

### 2. تشغيل مهمة مجدولة مباشرة

```python
from django_q.tasks import async_task

# تشغيل المهمة asynchronously
task_id = async_task('main.scheduled_tasks.expire_ads_task')
print(f"Task ID: {task_id}")

# التحقق من النتيجة
from django_q.models import Task
task = Task.objects.get(id=task_id)
print(task.result())
```

### 3. اختبار بدون تنفيذ

استخدم management commands الموجودة:
```bash
python manage.py expire_ads --dry-run
python manage.py send_expiration_notifications --days 3 --dry-run
```

---

## استكشاف الأخطاء - Troubleshooting

### المشكلة: Redis connection refused

**الحل:**
```bash
# التحقق من Redis
redis-cli ping
# يجب أن يعود: PONG

# أو في Docker
docker-compose exec redis redis-cli ping
```

### المشكلة: المهام لا تعمل

**الحل:**
```bash
# التحقق من qcluster يعمل
ps aux | grep qcluster

# في Docker
docker-compose ps qcluster

# إعادة تشغيل
python manage.py qcluster
# أو
docker-compose restart qcluster
```

### المشكلة: المهام تفشل

**الحل:**
```python
# فحص الأخطاء في Django admin
# /admin/django_q/failure/

# أو في shell
from django_q.models import Failure
for fail in Failure.objects.all()[:5]:
    print(f"{fail.name}: {fail.result}")
```

---

## الأمان - Security

### 1. تأمين Redis

```bash
# في redis.conf
requirepass your_strong_password
bind 127.0.0.1

# في Q_CLUSTER settings
"redis": {
    "password": "your_strong_password",
}
```

### 2. تحديد الصلاحيات

```python
# في docker-compose.yml
environment:
  - REDIS_PASSWORD=${REDIS_PASSWORD}
```

---

## الأداء - Performance

### 1. تحسين عدد Workers

```python
# للسيرفرات القوية
Q_CLUSTER = {
    "workers": 8,  # زيادة عدد workers
}

# للسيرفرات الضعيفة
Q_CLUSTER = {
    "workers": 2,  # تقليل عدد workers
}
```

### 2. Timeout Settings

```python
Q_CLUSTER = {
    "timeout": 90,    # للمهام العادية
    "timeout": 300,   # للمهام الطويلة (emails, reports)
}
```

### 3. Queue Limits

```python
Q_CLUSTER = {
    "queue_limit": 1000,  # زيادة الحد للمهام الكثيرة
}
```

---

## الأوامر المفيدة - Useful Commands

```bash
# إعداد المهام المجدولة
python manage.py setup_scheduled_tasks

# إعادة تعيين المهام
python manage.py setup_scheduled_tasks --reset

# تشغيل qcluster
python manage.py qcluster

# حذف جميع المهام المكتملة
python manage.py qclean

# عرض إحصائيات
python manage.py qinfo

# اختبار مهمة
python manage.py shell
>>> from django_q.tasks import async_task
>>> async_task('main.scheduled_tasks.expire_ads_task')
```

---

## جدول المهام - Task Schedule Summary

| المهمة | التوقيت | الوظيفة |
|--------|---------|---------|
| `expire_ads_task` | يومياً 2:00 ص | إنهاء صلاحية الإعلانات |
| `send_expiration_notifications_task` | يومياً 10:00 ص | إشعارات قبل 3 أيام |
| `send_7day_expiration_notifications_task` | يومياً 11:00 ص | إشعارات قبل 7 أيام |
| `cleanup_old_notifications_task` | أسبوعياً أحد 3:00 ص | حذف الإشعارات القديمة |
| `check_upgrade_expiry_task` | كل 6 ساعات | فحص انتهاء التمييزات |

---

## المراجع - References

- [Django Q2 Documentation](https://django-q2.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**تاريخ الإنشاء:** 14 ديسمبر 2025
**الإصدار:** 1.0
