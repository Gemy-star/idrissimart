# Google reCAPTCHA Setup Guide

## الحصول على مفاتيح Google reCAPTCHA

### 1. إنشاء حساب reCAPTCHA
1. اذهب إلى [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
2. سجل الدخول بحساب Google الخاص بك

### 2. تسجيل موقع جديد
1. اضغط على زر "+ إنشاء" أو "Create"
2. املأ النموذج:
   - **Label**: اسم المشروع (مثال: Idrissi Mart)
   - **reCAPTCHA type**: اختر **reCAPTCHA v2** ثم "I'm not a robot" Checkbox
   - **Domains**: أضف النطاقات الخاصة بك:
     ```
     localhost
     127.0.0.1
     idrissimart.com
     www.idrissimart.com
     ```
   - **Owners**: بريدك الإلكتروني (اختياري)
   - قبول شروط الخدمة

3. اضغط على "Submit"

### 3. نسخ المفاتيح
بعد التسجيل، ستحصل على:
- **Site Key** (المفتاح العام): يُستخدم في HTML
- **Secret Key** (المفتاح السري): يُستخدم في Backend

### 4. إضافة المفاتيح إلى المشروع

#### في ملف `.env`:
```env
RECAPTCHA_SITE_KEY=your_site_key_here
RECAPTCHA_SECRET_KEY=your_secret_key_here
```

#### مثال:
```env
RECAPTCHA_SITE_KEY=6LdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_SECRET_KEY=6LdYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

## التحقق من التكامل

### 1. اختبار محلي (Local Testing)
- تأكد من إضافة `localhost` و `127.0.0.1` في قائمة النطاقات
- قم بتشغيل السيرفر المحلي
- افتح صفحة التسجيل وتحقق من ظهور reCAPTCHA

### 2. اختبار الإنتاج (Production)
- أضف نطاقك الفعلي في Google reCAPTCHA Admin
- انشر التحديثات
- اختبر صفحة التسجيل

## استكشاف الأخطاء

### رسالة خطأ: "ERROR for site owner: Invalid domain for site key"
- **السبب**: النطاق الحالي غير مسجل في Google reCAPTCHA
- **الحل**: أضف النطاق في [reCAPTCHA Admin](https://www.google.com/recaptcha/admin)

### reCAPTCHA لا تظهر
- **تحقق من**:
  1. تحميل سكريبت Google: `https://www.google.com/recaptcha/api.js`
  2. Site Key صحيح في `.env`
  3. لا توجد أخطاء JavaScript في Console

### فشل التحقق (Verification Failed)
- **تحقق من**:
  1. Secret Key صحيح في `.env`
  2. الاتصال بالإنترنت يعمل
  3. مكتبة `requests` مثبتة: `pip install requests`

## روابط مفيدة

- [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
- [reCAPTCHA Documentation](https://developers.google.com/recaptcha/docs/display)
- [reCAPTCHA FAQ](https://developers.google.com/recaptcha/docs/faq)

## ملاحظات مهمة

1. **للتطوير المحلي**: أضف `localhost` و `127.0.0.1` دائماً
2. **للإنتاج**: استخدم نطاقك الفعلي فقط
3. **الأمان**: لا تشارك Secret Key أبداً
4. **النسخ الاحتياطي**: احفظ المفاتيح في مكان آمن

## مثال على الاستخدام في Template

```html
<!-- في صفحة التسجيل -->
<form method="post">
    {% csrf_token %}

    <!-- الحقول الأخرى -->

    <!-- Google reCAPTCHA -->
    <div class="g-recaptcha" data-sitekey="{{ RECAPTCHA_SITE_KEY }}"></div>

    <button type="submit">تسجيل</button>
</form>

<!-- سكريبت Google reCAPTCHA -->
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
```

## مثال على التحقق في Django View

```python
import requests
from django.conf import settings

def register(request):
    if request.method == 'POST':
        # التحقق من reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')

        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }

        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result.get('success'):
            # التحقق نجح - تابع التسجيل
            pass
        else:
            # التحقق فشل
            messages.error(request, 'فشل التحقق من reCAPTCHA')
```
