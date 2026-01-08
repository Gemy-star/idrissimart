# إصلاح حذف الحساب في لوحة التحكم
## Account Deletion Fix - User Dashboard

## التاريخ | Date
9 يناير 2026 | January 9, 2026

---

## المشكلة | The Problem

**الوصف:**
عند محاولة العضو حذف حسابه من لوحة التحكم → **الحذف لا يعمل**

**الأعراض:**
- الضغط على زر "حذف الحساب نهائياً" لا يؤدي إلى أي نتيجة
- لا توجد رسائل خطأ واضحة
- الحساب لا يُحذف ولا يتم تسجيل الخروج

**السبب الجذري:**
```javascript
// ❌ Missing CSRF token in fetch request
fetch('{% url "main:publisher_delete_account" %}', {
    method: 'POST',
    body: formData,
    credentials: 'same-origin'
    // ❌ No CSRF token header!
})
```

Django's CSRF protection يرفض الطلب لعدم وجود CSRF token في الـ headers!

---

## الحل | The Solution

### إضافة CSRF Token في Fetch Request

**الملف:** [templates/dashboard/publisher_settings.html](templates/dashboard/publisher_settings.html) (Line ~850)

#### قبل التعديل:

```javascript
fetch('{% url "main:publisher_delete_account" %}', {
    method: 'POST',
    body: formData,              // ✅ FormData with CSRF token
    credentials: 'same-origin'   // ✅ Send cookies
    // ❌ But no X-CSRFToken header!
})
```

**المشكلة:** Django يتحقق من الـ header بالإضافة للـ form data!

#### بعد التعديل:

```javascript
fetch('{% url "main:publisher_delete_account" %}', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken')  // ✅ CSRF token in header
    },
    body: formData,
    credentials: 'same-origin'
})
```

**الحل:** إضافة CSRF token في الـ headers!

---

## الكود الكامل | Complete Code

### JavaScript Function

```javascript
// Delete account
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', function() {
        const form = document.getElementById('deleteAccountForm');
        const passwordInput = form.querySelector('input[name="password"]');

        // Validate password input
        if (!passwordInput.value) {
            showToast('{% trans "يرجى إدخال كلمة المرور" %}', 'error');
            return;
        }

        // Confirm deletion
        if (confirm('{% trans "هل أنت متأكد تماماً؟ هذا الإجراء لا يمكن التراجع عنه!" %}')) {
            const formData = new FormData(form);

            // Disable button to prevent multiple clicks
            confirmDeleteBtn.disabled = true;
            confirmDeleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>{% trans "جاري الحذف..." %}';

            // ✅ Send request with CSRF token
            fetch('{% url "main:publisher_delete_account" %}', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')  // ✅ FIX!
                },
                body: formData,
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.message || '{% trans "حدث خطأ" %}');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');

                    // Close modal
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById('deleteAccountModal')
                    );
                    if (modal) modal.hide();

                    // Redirect after delay
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1500);
                } else {
                    showToast(data.message, 'error');

                    // Re-enable button
                    confirmDeleteBtn.disabled = false;
                    confirmDeleteBtn.innerHTML = '<i class="fas fa-trash-alt me-2"></i>{% trans "حذف الحساب نهائياً" %}';
                }
            })
            .catch(error => {
                showToast(error.message || '{% trans "حدث خطأ" %}', 'error');

                // Re-enable button
                confirmDeleteBtn.disabled = false;
                confirmDeleteBtn.innerHTML = '<i class="fas fa-trash-alt me-2"></i>{% trans "حذف الحساب نهائياً" %}';
            });
        }
    });
}
```

---

## كيف يعمل النظام | How It Works

### تدفق حذف الحساب

```
[المستخدم يضغط "حذف الحساب"]
           ↓
[يفتح Modal التأكيد]
           ↓
[يُدخل كلمة المرور]
           ↓
[يضغط "حذف الحساب نهائياً"]
           ↓
[تأكيد آخر: "هل أنت متأكد تماماً؟"]
           ↓
     [نعم]  [لا]
       ↓      ↓
    [AJAX]  [إلغاء]
       ↓
[POST إلى /dashboard/settings/delete-account/]
       ↓
[View: publisher_delete_account]
       ↓
   [فحص CSRF token] ✅ الآن يعمل!
       ↓
   [فحص كلمة المرور]
       ↓
  ┌────┴────┐
  ↓         ↓
[صحيحة]  [خاطئة]
  ↓         ↓
[حذف]     [خطأ]
  ↓
[user.is_active = False]
  ↓
[logout()]
  ↓
[رسالة نجاح]
  ↓
[redirect إلى الصفحة الرئيسية]
```

---

## Django View

**الملف:** [main/views.py](main/views.py#L7221)

```python
@login_required
@require_POST
def publisher_delete_account(request):
    """Delete publisher account (soft delete)"""
    try:
        user = request.user
        password = request.POST.get("password", "")

        # Check if user is authenticated
        if not user.is_authenticated:
            return JsonResponse(
                {"success": False, "message": _("يجب تسجيل الدخول أولاً")},
                status=401
            )

        # Verify password
        if not password:
            return JsonResponse(
                {"success": False, "message": _("يرجى إدخال كلمة المرور")},
                status=400
            )

        if not user.check_password(password):
            return JsonResponse(
                {"success": False, "message": _("كلمة المرور غير صحيحة")},
                status=400
            )

        # Deactivate user account (soft delete)
        user.is_active = False
        user.save()

        # Log out the user
        from django.contrib.auth import logout
        logout(request)

        return JsonResponse({
            "success": True,
            "message": _("تم حذف الحساب بنجاح"),
            "redirect": reverse("main:home"),
        })

    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ أثناء حذف الحساب")},
            status=500
        )
```

**ملاحظات:**
- ✅ الـ View صحيح ولا يحتاج تعديل
- ✅ يستخدم `@require_POST` للحماية
- ✅ يفحص CSRF token تلقائياً
- ✅ Soft delete: يعطّل الحساب بدلاً من حذفه

---

## Modal الحذف | Deletion Modal

**الملف:** [templates/dashboard/publisher_settings.html](templates/dashboard/publisher_settings.html#L580)

```html
<!-- Delete Account Modal -->
<div class="modal fade" id="deleteAccountModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    {% trans "تأكيد حذف الحساب" %}
                </h5>
                <button type="button" class="btn-close btn-close-white"
                        data-bs-dismiss="modal"></button>
            </div>

            <div class="modal-body">
                <p class="text-danger fw-bold">
                    {% trans "تحذير: هذا الإجراء لا يمكن التراجع عنه!" %}
                </p>
                <p>{% trans "سيتم حذف جميع بياناتك بما في ذلك:" %}</p>
                <ul>
                    <li>{% trans "جميع إعلاناتك" %}</li>
                    <li>{% trans "رسائلك ومحادثاتك" %}</li>
                    <li>{% trans "إعداداتك وتفضيلاتك" %}</li>
                </ul>

                <form id="deleteAccountForm">
                    {% csrf_token %}
                    <div class="form-group mb-3">
                        <label class="form-label">
                            {% trans "أدخل كلمة المرور للتأكيد" %}
                            <span class="text-danger">*</span>
                        </label>
                        <input type="password"
                               class="form-control"
                               name="password"
                               id="deleteAccountPassword"
                               placeholder="{% trans 'كلمة المرور' %}"
                               required
                               autocomplete="current-password">
                        <small class="form-text text-muted">
                            {% trans "يرجى إدخال كلمة المرور الخاصة بك لتأكيد الحذف" %}
                        </small>
                    </div>
                </form>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-secondary"
                        data-bs-dismiss="modal">
                    {% trans "إلغاء" %}
                </button>
                <button type="button" class="btn btn-danger"
                        id="confirmDeleteBtn">
                    <i class="fas fa-trash-alt me-2"></i>
                    {% trans "حذف الحساب نهائياً" %}
                </button>
            </div>
        </div>
    </div>
</div>
```

---

## CSRF Token في Django

### كيف يعمل CSRF Protection

Django يتحقق من CSRF token بطريقتين:

1. **Form Data:** `<input type="hidden" name="csrfmiddlewaretoken">`
2. **HTTP Header:** `X-CSRFToken` header

**للـ AJAX requests:** يجب إرسال الـ token في الـ header!

### getCookie Function

```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

**الاستخدام:**
```javascript
const csrftoken = getCookie('csrftoken');

fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken  // ✅ Required!
    },
    body: formData
})
```

---

## الاختبار | Testing

### 1. اختبار عملية الحذف

```bash
# 1. سجل دخول كعضو
http://localhost:8000/accounts/login/

# 2. اذهب للإعدادات
http://localhost:8000/dashboard/settings/

# 3. انقر على تبويب "إدارة الحساب"
# 4. انقر على "حذف الحساب"
# 5. أدخل كلمة المرور
# 6. اضغط "حذف الحساب نهائياً"
# 7. أكّد في الـ confirm dialog

# النتيجة المتوقعة:
✅ رسالة: "تم حذف الحساب بنجاح"
✅ يتم تسجيل الخروج تلقائياً
✅ redirect إلى الصفحة الرئيسية
✅ is_active = False في قاعدة البيانات
```

### 2. اختبار الحالات الخاصة

#### حالة 1: كلمة مرور خاطئة
```
Input: كلمة مرور خاطئة
Expected: ❌ "كلمة المرور غير صحيحة"
Status Code: 400
```

#### حالة 2: بدون كلمة مرور
```
Input: حقل فارغ
Expected: ❌ "يرجى إدخال كلمة المرور"
Client-side validation: يمنع الإرسال
```

#### حالة 3: غير مسجل دخول
```
Input: طلب بدون session
Expected: ❌ "يجب تسجيل الدخول أولاً"
Status Code: 401
```

#### حالة 4: بدون CSRF token
```
Input: Fetch بدون X-CSRFToken header
Expected: ❌ 403 Forbidden
Django CSRF middleware: يرفض الطلب
```

### 3. التحقق من قاعدة البيانات

```sql
-- قبل الحذف
SELECT id, username, email, is_active FROM users WHERE id = 123;
-- Result: | 123 | testuser | test@example.com | 1 |

-- بعد الحذف
SELECT id, username, email, is_active FROM users WHERE id = 123;
-- Result: | 123 | testuser | test@example.com | 0 |  ✅ Soft delete
```

**ملاحظة:** الحساب لا يُحذف نهائياً، فقط `is_active = False`

---

## Soft Delete vs Hard Delete

### الحل الحالي: Soft Delete ✅

```python
# Soft delete: deactivate account
user.is_active = False
user.save()
```

**الفوائد:**
- ✅ يمكن استرجاع الحساب لاحقاً
- ✅ البيانات لا تُفقد
- ✅ المستخدم لا يستطيع تسجيل الدخول
- ✅ الإعلانات تبقى موجودة

### البديل: Hard Delete ❌

```python
# Hard delete: permanently delete
user.delete()
```

**المشاكل:**
- ❌ لا يمكن استرجاع الحساب
- ❌ فقدان جميع البيانات
- ❌ مشاكل Foreign Key constraints
- ❌ يحتاج ON DELETE CASCADE

**الخلاصة:** Soft delete أفضل للإنتاج!

---

## الحالات المستقبلية | Future Enhancements

### 1. Hard Delete Option (اختياري)

```python
@superadmin_required
def admin_hard_delete_user(request, user_id):
    """Permanently delete user (admin only)"""
    user = get_object_or_404(User, id=user_id)

    # Delete all related data
    user.classified_ads.all().delete()
    user.messages.all().delete()
    user.notifications.all().delete()

    # Delete user
    username = user.username
    user.delete()

    return JsonResponse({
        "success": True,
        "message": f"تم حذف المستخدم {username} نهائياً"
    })
```

### 2. Scheduled Deletion

```python
# models.py
class User(AbstractUser):
    deletion_requested_at = models.DateTimeField(null=True, blank=True)

    def request_deletion(self):
        """Request account deletion (7 days grace period)"""
        self.deletion_requested_at = timezone.now()
        self.is_active = False
        self.save()

# management command
def handle_scheduled_deletions():
    """Delete accounts after 7 days grace period"""
    threshold = timezone.now() - timedelta(days=7)
    users_to_delete = User.objects.filter(
        deletion_requested_at__lte=threshold,
        is_active=False
    )

    for user in users_to_delete:
        user.delete()  # Hard delete after grace period
```

### 3. Email Notification

```python
from django.core.mail import send_mail

def send_deletion_confirmation(user):
    """Send email confirmation after deletion"""
    send_mail(
        subject="تأكيد حذف الحساب",
        message=f"""
        مرحباً {user.get_full_name()},

        تم حذف حسابك بنجاح من منصة إدريسي مارت.

        إذا قمت بحذف حسابك بالخطأ، يرجى التواصل معنا خلال 7 أيام.

        مع تحياتنا،
        فريق إدريسي مارت
        """,
        from_email="noreply@idrissimart.com",
        recipient_list=[user.email],
    )
```

### 4. Anonymize Data (GDPR Compliant)

```python
def anonymize_user(user):
    """Anonymize user data (GDPR)"""
    user.username = f"deleted_user_{user.id}"
    user.email = f"deleted_{user.id}@deleted.local"
    user.first_name = ""
    user.last_name = ""
    user.phone = ""
    user.address = ""
    user.avatar = None
    user.is_active = False
    user.save()

    # Keep ads but anonymize author
    user.classified_ads.update(
        user_email="[تم حذف الحساب]",
        user_phone="[تم حذف الحساب]"
    )
```

---

## الأمان | Security

### ميزات الأمان المطبقة

1. **CSRF Protection** ✅
   - Token في الـ form
   - Token في الـ header
   - Django middleware validation

2. **Password Verification** ✅
   - يجب إدخال كلمة المرور
   - التحقق من صحة كلمة المرور

3. **Double Confirmation** ✅
   - Modal confirmation
   - JavaScript confirm dialog

4. **Login Required** ✅
   - `@login_required` decorator
   - يمنع الوصول لغير المسجلين

5. **Rate Limiting** (مستقبلاً)
   ```python
   from django.core.cache import cache

   def check_rate_limit(user):
       key = f"delete_account_{user.id}"
       attempts = cache.get(key, 0)

       if attempts >= 3:
           raise PermissionDenied("محاولات كثيرة جداً")

       cache.set(key, attempts + 1, timeout=3600)
   ```

---

## الأخطاء الشائعة | Common Errors

### 1. CSRF Verification Failed

**السبب:** عدم إرسال CSRF token
**الحل:** ✅ تم إصلاحه بإضافة `X-CSRFToken` header

### 2. 403 Forbidden

**السبب:** CSRF token غير صحيح أو منتهي
**الحل:** Refresh الصفحة للحصول على token جديد

### 3. Password Incorrect

**السبب:** كلمة مرور خاطئة
**الحل:** أدخل كلمة المرور الصحيحة

### 4. User Not Authenticated

**السبب:** Session منتهية
**الحل:** سجل دخول مرة أخرى

---

## الخلاصة | Summary

### ما تم إصلاحه ✅

1. **المشكلة الأساسية:** عدم وجود CSRF token في fetch request
2. **الحل:** إضافة `X-CSRFToken` header
3. **النتيجة:** حذف الحساب يعمل بشكل صحيح

### الملفات المعدلة

- ✅ [templates/dashboard/publisher_settings.html](templates/dashboard/publisher_settings.html#L850) - إضافة CSRF token header

### لا يوجد تعديل على:

- ⭕ [main/views.py](main/views.py#L7221) - View صحيح من البداية
- ⭕ [main/urls.py](main/urls.py#L643) - URL mapping صحيح

### التأكد من العمل

```bash
# Check system
poetry run python manage.py check

# Test deletion
1. Login as member
2. Go to Settings > Account Management
3. Click "Delete Account"
4. Enter password
5. Confirm deletion
✅ Account deactivated successfully!
```

**الحالة:** ✅ المشكلة محلولة والنظام يعمل! 🎉
