# إصلاح مشكلة "نسيت كلمة المرور"
## Password Reset Fix Documentation

## المشكلة | Problem

كانت ميزة "نسيت كلمة المرور" لا تعمل بشكل صحيح بسبب:
1. **مفتاح SendGrid API غير موجود** - مما منع إرسال البريد الإلكتروني
2. **خطأ في اسم URL في قالب البريد** - كان يستخدم `password_reset_confirm` بدلاً من `main:password_reset_confirm`
3. **عدم وجود fallback للتطوير** - عندما لا يكون SendGrid متاحاً

The password reset feature wasn't working due to:
1. **Missing SendGrid API key** - preventing email delivery
2. **Wrong URL name in email template** - using `password_reset_confirm` instead of `main:password_reset_confirm`
3. **No development fallback** - when SendGrid is not available

---

## الحل | Solution

### 1. إصلاح إعدادات البريد الإلكتروني
**File:** `idrissimart/settings/common.py`

تم تحديث الإعدادات لتشمل:
- التحقق من وجود `SENDGRID_API_KEY` قبل استخدام SendGrid
- استخدام `console.EmailBackend` كـ fallback في وضع التطوير
- رسائل تحذيرية واضحة عند عدم توفر SendGrid

Updated settings to include:
- Check for `SENDGRID_API_KEY` before using SendGrid
- Use `console.EmailBackend` as fallback in development
- Clear warning messages when SendGrid is not available

```python
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

try:
    import sendgrid_backend

    if SENDGRID_API_KEY:
        EMAIL_BACKEND = "sendgrid_backend.SendGridBackend"
        SENDGRID_SANDBOX_MODE_IN_DEBUG = True
    else:
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
        import logging
        logging.warning("SendGrid API key not configured. Using console email backend.")
except ImportError:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    import logging
    logging.warning("SendGrid backend not installed. Using console email backend.")
```

### 2. إصلاح دالة استعادة كلمة المرور
**File:** `main/auth_views.py`

التحسينات:
- معالجة أفضل للأخطاء مع رسائل واضحة
- في وضع التطوير (DEBUG): طباعة رابط استعادة كلمة المرور في console
- استخدام `settings.DEFAULT_FROM_EMAIL` بدلاً من hardcoded email
- تسجيل الأخطاء للتشخيص

Improvements:
- Better error handling with clear messages
- In DEBUG mode: print password reset link to console
- Use `settings.DEFAULT_FROM_EMAIL` instead of hardcoded email
- Error logging for diagnostics

**Key Features:**
```python
# In DEBUG mode, log reset link to console
if settings.DEBUG:
    reset_link = f"{context['protocol']}://{context['domain']}/reset/{context['uid']}/{context['token']}/"
    print(f"\n{'='*60}")
    print(f"PASSWORD RESET LINK FOR: {user.email}")
    print(f"Link: {reset_link}")
    print(f"{'='*60}\n")
```

### 3. إصلاح قالب البريد الإلكتروني
**File:** `templates/password/password_reset_email.txt`

تم تصحيح اسم URL من:
```django
{% url 'password_reset_confirm' uidb64=uid token=token %}
```

إلى:
```django
{% url 'main:password_reset_confirm' uidb64=uid token=token %}
```

---

## كيفية الاستخدام | How to Use

### للتطوير | For Development

1. **بدون SendGrid** (Console Backend):
   - لا يلزم تكوين `SENDGRID_API_KEY`
   - سيتم طباعة رابط استعادة كلمة المرور في console
   - يمكن نسخ الرابط واستخدامه مباشرة

Without SendGrid (Console Backend):
- No need to configure `SENDGRID_API_KEY`
- Password reset link will be printed to console
- Copy the link and use it directly

2. **مع SendGrid**:
   - أضف `SENDGRID_API_KEY` إلى ملف `.env`
   - سيتم إرسال البريد الإلكتروني فعلياً

With SendGrid:
- Add `SENDGRID_API_KEY` to `.env` file
- Email will be sent for real

### للإنتاج | For Production

1. **تكوين SendGrid**:
   ```bash
   # في ملف .env
   SENDGRID_API_KEY=your-api-key-here
   DEFAULT_FROM_EMAIL=noreply@idrissimart.com
   ```

2. **التحقق من الإعدادات**:
   ```bash
   python manage.py shell -c "from constance import config; print('SendGrid Enabled:', config.SENDGRID_ENABLED); print('Has API Key:', bool(config.SENDGRID_API_KEY))"
   ```

---

## الاختبار | Testing

### اختبار في وضع التطوير | Test in Development Mode

1. انتقل إلى صفحة "نسيت كلمة المرور": `http://localhost:8000/password-reset-request/`
2. أدخل بريد إلكتروني مسجل
3. انظر في console لرؤية رابط استعادة كلمة المرور
4. انسخ الرابط واستخدمه لإعادة تعيين كلمة المرور

Steps:
1. Go to password reset page: `http://localhost:8000/password-reset-request/`
2. Enter a registered email
3. Check console for password reset link
4. Copy the link and use it to reset password

### مثال على الإخراج | Console Output Example

```
============================================================
PASSWORD RESET LINK FOR: user@example.com
Link: http://localhost:8000/reset/MQ/c3r8a2-e4f5g6h7i8j9k0l1m2n3o4p5/
============================================================
```

---

## ملاحظات مهمة | Important Notes

### الأمان | Security

1. **User Enumeration Prevention**:
   - الرسالة نفسها تظهر سواء كان البريد موجوداً أم لا
   - Same message shown whether email exists or not

2. **Suspended Users**:
   - لا يمكن للمستخدمين المعلقين إعادة تعيين كلمة المرور
   - Suspended users cannot reset their password

3. **Token Expiry**:
   - الرابط صالح لمدة 24 ساعة فقط
   - Link valid for 24 hours only

### استكشاف الأخطاء | Troubleshooting

#### لا يتم إرسال البريد | Email Not Sending

1. تحقق من console للحصول على رسائل الخطأ
2. تأكد من تكوين `SENDGRID_API_KEY` بشكل صحيح
3. في وضع التطوير، انظر في console للحصول على الرابط

Steps:
1. Check console for error messages
2. Verify `SENDGRID_API_KEY` is configured correctly
3. In development, look in console for the link

#### خطأ في URL | URL Error

إذا كان الرابط لا يعمل:
- تأكد من استخدام `main:password_reset_confirm` في القالب
- تحقق من `urls.py` للتأكد من وجود المسار

If link doesn't work:
- Ensure using `main:password_reset_confirm` in template
- Check `urls.py` to verify path exists

---

## الملفات المعدلة | Modified Files

1. ✅ `idrissimart/settings/common.py` - Email backend configuration
2. ✅ `main/auth_views.py` - Password reset view with better error handling
3. ✅ `templates/password/password_reset_email.txt` - Fixed URL name

---

## الخطوات التالية | Next Steps

للإنتاج، يُنصح بـ:
1. تكوين SendGrid API key
2. التحقق من email templates
3. اختبار كامل للميزة في بيئة الإنتاج

For production, recommended to:
1. Configure SendGrid API key
2. Verify email templates
3. Full testing in production environment

---

**تاريخ الإصلاح | Fix Date:** 2025-12-30
**الحالة | Status:** ✅ تم الحل | Resolved
