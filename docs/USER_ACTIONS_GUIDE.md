# دليل إجراءات المستخدمين في لوحة الأدمن
## User Management Actions Guide

تم إنشاء هذا الدليل في: 2026-01-09

---

## 📋 نظرة عامة

يوفر نظام إدارة المستخدمين مجموعة شاملة من الإجراءات التي يمكن للمشرفين تنفيذها على حسابات المستخدمين. يتضمن هذا الدليل شرحًا تفصيليًا لكل إجراء والفرق بين الإجراءات المتشابهة.

---

## 🔧 الإجراءات المتاحة

### 1. التعليق (Suspend) - `is_suspended`
**إجراء مؤقت وقابل للإلغاء**

#### الوصف:
- تعليق مؤقت لحساب المستخدم
- يمنع المستخدم من تنفيذ بعض الأنشطة
- **قابل للإلغاء** في أي وقت من قبل المشرف
- الحساب يظل نشطًا (`is_active = True`)

#### متى تستخدمه:
- ✅ عند وجود شبهة انتهاك بسيط
- ✅ كتحذير مؤقت للمستخدم
- ✅ أثناء التحقيق في سلوك المستخدم
- ✅ لمنح المستخدم فرصة ثانية

#### التأثير:
```python
user.is_suspended = True
user.suspension_reason = "سبب التعليق"
# user.is_active = True (لا يتغير)
```

#### كيفية الاستخدام:
1. من صفحة تفاصيل المستخدم: `/admin/users/<user_id>/`
2. اضغط على زر "تعليق"
3. تأكيد الإجراء
4. لإلغاء التعليق: اضغط "إلغاء التعليق"

#### الـ Endpoints:
- **URL:** `/admin/users/<user_id>/action/`
- **Method:** POST
- **Body:** `{ "action": "suspend" }`
- **Response:** `{ "success": true, "message": "تم تعليق المستخدم..." }`

---

### 2. الحظر (Ban) - `is_banned`
**إجراء نهائي وصارم**

#### الوصف:
- حظر دائم ونهائي للمستخدم
- **يُعطّل الحساب بالكامل** (`is_active = False`)
- يمنع تسجيل الدخول نهائيًا
- قابل للإلغاء ولكن نادرًا ما يُلغى

#### متى تستخدمه:
- ⛔ انتهاكات جسيمة متكررة
- ⛔ محتوى غير قانوني أو ضار
- ⛔ احتيال أو نصب مثبت
- ⛔ بعد فشل التعليق المتكرر

#### التأثير:
```python
user.is_banned = True
user.is_active = False  # تعطيل كامل للحساب
user.ban_reason = "سبب الحظر النهائي"
```

#### كيفية الاستخدام:
1. من صفحة تفاصيل المستخدم: `/admin/users/<user_id>/`
2. اضغط على زر "حظر المستخدم" (أحمر)
3. تأكيد الإجراء (سيظهر تحذير بأنه نهائي)
4. لإلغاء الحظر (نادر): اضغط "إلغاء الحظر"

#### الـ Endpoints:
- **URL:** `/admin/users/<user_id>/action/`
- **Method:** POST
- **Body:** `{ "action": "ban", "reason": "سبب الحظر" }`
- **Response:** `{ "success": true, "message": "تم حظر المستخدم نهائياً." }`

---

### 3. التوثيق (Verify)
**منح شارة التوثيق الرسمية**

#### الوصف:
- تأكيد هوية المستخدم
- منح شارة "موثق" ✓
- يزيد من مصداقية المستخدم

#### متى تستخدمه:
- ✅ بعد التحقق من الوثائق الرسمية
- ✅ للحسابات الرسمية (شركات، مؤسسات)
- ✅ للناشرين الموثوقين

#### الـ Endpoints:
- **URL:** `/admin/users/<user_id>/action/`
- **Method:** POST
- **Body:** `{ "action": "verify" }`

---

### 4. إرسال الإشعار (Send Notification)
**التواصل المباشر مع المستخدم**

#### الوصف:
- إرسال إشعار مخصص للمستخدم
- يدعم الإرسال عبر البريد الإلكتروني و/أو SMS
- يمكن تخصيص العنوان والنص

#### متى تستخدمه:
- 📧 إشعارات مهمة للمستخدم
- 📧 تحذيرات قبل اتخاذ إجراء
- 📧 تنبيهات حول نشاط مشبوه

#### كيفية الاستخدام:
##### من صفحة إدارة المستخدمين (`/admin/users/`):
1. اضغط على القائمة المنسدلة للإجراءات
2. اختر "إرسال إشعار"
3. سيتم توجيهك لصفحة تفاصيل المستخدم

##### من صفحة تفاصيل المستخدم (`/admin/users/<user_id>/`):
1. اضغط على زر "إرسال إشعار" (برتقالي)
2. املأ العنوان والنص
3. اختر طريقة الإرسال:
   - ☑️ البريد الإلكتروني
   - ☑️ الرسائل النصية (SMS)
4. اضغط "إرسال"

#### الـ Endpoints:
- **URL:** `/admin/users/<user_id>/send-notification/`
- **Method:** POST
- **Body:**
```json
{
  "title": "عنوان الإشعار",
  "message": "نص الإشعار",
  "send_email": true,
  "send_sms": false
}
```
- **Response:**
```json
{
  "success": true,
  "message": "تم إرسال الإشعار عبر البريد الإلكتروني"
}
```

---

## 📊 مقارنة شاملة

| الميزة | التعليق (Suspend) | الحظر (Ban) |
|--------|-------------------|-------------|
| **الحقل** | `is_suspended` | `is_banned` |
| **الدوام** | مؤقت | نهائي |
| **تعطيل الحساب** | ❌ لا (`is_active = True`) | ✅ نعم (`is_active = False`) |
| **تسجيل الدخول** | ⚠️ محدود | ⛔ ممنوع تمامًا |
| **قابل للإلغاء** | ✅ بسهولة | ⚠️ نادرًا |
| **الاستخدام** | انتهاكات بسيطة | انتهاكات جسيمة |
| **اللون في الواجهة** | 🟠 برتقالي | 🔴 أحمر |
| **الأيقونة** | `pause-circle` | `ban` |
| **حقل السبب** | `suspension_reason` | `ban_reason` |

---

## 🔄 مسار العمل الموصى به

### السيناريو 1: مستخدم ينشر محتوى مخالف لأول مرة
```
1. إرسال إشعار تحذيري
   ↓
2. التعليق المؤقت (3-7 أيام)
   ↓
3. إلغاء التعليق إذا التزم
   ↓
4. المراقبة المستمرة
```

### السيناريو 2: مستخدم متكرر المخالفات
```
1. إرسال إشعار نهائي
   ↓
2. التعليق الطويل (14-30 يوم)
   ↓
3. إذا تكرر → الحظر النهائي
```

### السيناريو 3: محتوى غير قانوني فوري
```
1. الحظر الفوري (Ban) ✋
   ↓
2. حذف المحتوى المخالف
   ↓
3. الإبلاغ للسلطات (إن لزم)
```

---

## 🛠️ التطبيق التقني

### 1. قاعدة البيانات
```python
# main/models.py - User Model
class User(AbstractUser):
    # التعليق المؤقت
    is_suspended = models.BooleanField(
        default=False,
        verbose_name="معلق - Suspended"
    )
    suspension_reason = models.TextField(
        blank=True,
        verbose_name="سبب التعليق"
    )

    # الحظر النهائي
    is_banned = models.BooleanField(
        default=False,
        verbose_name="محظور - Banned"
    )
    ban_reason = models.TextField(
        blank=True,
        verbose_name="سبب الحظر"
    )
```

### 2. View الإجراءات
```python
# main/views.py
@superadmin_required
@require_POST
def admin_user_action(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    data = json.loads(request.body)
    action = data.get("action")

    if action == "suspend":
        user.is_suspended = True
        user.save(update_fields=["is_suspended"])

    elif action == "unsuspend":
        user.is_suspended = False
        user.save(update_fields=["is_suspended"])

    elif action == "ban":
        user.is_banned = True
        user.is_active = False  # تعطيل كامل
        user.ban_reason = data.get("reason", "")
        user.save(update_fields=["is_banned", "is_active", "ban_reason"])

    elif action == "unban":
        user.is_banned = False
        user.is_active = True  # إعادة التفعيل
        user.ban_reason = ""
        user.save(update_fields=["is_banned", "is_active", "ban_reason"])

    return JsonResponse({"success": True, "message": "..."})
```

### 3. Frontend (JavaScript)
```javascript
// templates/admin_dashboard/user_detail.html
function handleUserAction(action, userId) {
    const msgMap = {
        suspend: 'تعليق مؤقت - قابل للإلغاء',
        ban: 'حظر نهائي - سيتم تعطيل الحساب بالكامل',
        unsuspend: 'إلغاء التعليق',
        unban: 'إلغاء الحظر وإعادة تفعيل الحساب'
    };

    // عرض modal التأكيد
    showConfirmModal(msgMap[action], () => {
        fetch(`/admin/users/${userId}/action/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action })
        });
    });
}
```

---

## 📁 الملفات المتأثرة

### النماذج (Models):
- `main/models.py` - User model (fields: `is_suspended`, `is_banned`, `suspension_reason`, `ban_reason`)

### الـ Views:
- `main/views.py` - `admin_user_action()` (دعم suspend, unsuspend, ban, unban, verify)
- `main/views.py` - `admin_send_user_notification()` (إرسال الإشعارات)

### القوالب (Templates):
- `templates/admin_dashboard/user_detail.html` - صفحة تفاصيل المستخدم مع جميع الأزرار
- `templates/admin_dashboard/users_management.html` - قائمة المستخدمين مع القائمة المنسدلة

### الـ URLs:
- `/admin/users/<user_id>/action/` - تنفيذ الإجراءات
- `/admin/users/<user_id>/send-notification/` - إرسال الإشعارات

### الـ Migrations:
- `main/migrations/0046_add_user_ban_fields.py` - إضافة حقول `is_banned` و `ban_reason`

---

## 🔐 الصلاحيات

جميع الإجراءات تتطلب:
- `@superadmin_required` decorator
- المستخدم يجب أن يكون `is_superuser = True`
- لا يمكن للمشرف تنفيذ إجراءات على:
  - نفسه
  - مشرفين آخرين (حماية)

---

## ✅ الاختبار

### اختبار التعليق:
```bash
# 1. تعليق مستخدم
curl -X POST http://localhost:8000/ar/admin/users/5/action/ \
  -H "Content-Type: application/json" \
  -d '{"action": "suspend"}'

# 2. التحقق من الحالة
# user.is_suspended = True
# user.is_active = True

# 3. إلغاء التعليق
curl -X POST http://localhost:8000/ar/admin/users/5/action/ \
  -d '{"action": "unsuspend"}'
```

### اختبار الحظر:
```bash
# 1. حظر مستخدم
curl -X POST http://localhost:8000/ar/admin/users/5/action/ \
  -d '{"action": "ban", "reason": "انتهاكات متكررة"}'

# 2. التحقق من الحالة
# user.is_banned = True
# user.is_active = False ✓

# 3. إلغاء الحظر (نادر)
curl -X POST http://localhost:8000/ar/admin/users/5/action/ \
  -d '{"action": "unban"}'
```

---

## 📞 الدعم

للمزيد من المعلومات أو الإبلاغ عن مشاكل:
- راجع ملف: `docs/USER_MANAGEMENT_ENHANCEMENTS_EN.md`
- راجع ملف: `docs/ADMIN_DASHBOARD_UPDATES.md`

---

## 📝 ملاحظات مهمة

1. **التعليق مؤقت، الحظر نهائي** - اختر بحكمة
2. **يُفضل إرسال إشعار قبل أي إجراء** - لإعطاء المستخدم فرصة
3. **وثّق سبب الإجراء** - لحفظ السجلات
4. **الحظر لا يُلغى إلا في حالات استثنائية** - قرار نهائي

---

**آخر تحديث:** 2026-01-09
**الإصدار:** 1.0
**المطور:** Admin Dashboard Team
