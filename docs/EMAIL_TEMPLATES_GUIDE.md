# Email Templates Guide - إدريسي مارت

## 📧 نظرة عامة

تم إنشاء مجموعة من قوالب البريد الإلكتروني الاحترافية لـ **إدريسي مارت** باستخدام ألوان العلامة التجارية من `style.css`:

### 🎨 ألوان العلامة التجارية
- **اللون الأساسي**: `#4b315e` (بنفسجي)
- **اللون الأساسي الداكن**: `#3a2449`
- **اللون الثانوي**: `#ff6001` (برتقالي)
- **لون التمييز البنفسجي**: `#6b4c7a`
- **لون التمييز البرتقالي**: `#ff8534`

## 📁 القوالب المتاحة

### 1. Welcome Email - البريد الترحيبي
**الملف**: `templates/emails/welcome.html`

**الاستخدام**:
```python
from main.services.email_service import EmailService

EmailService.send_welcome_email(
    email="user@example.com",
    user_name="أحمد محمد"
)
```

**المتغيرات**:
- `site_name`: اسم الموقع
- `user_name`: اسم المستخدم
- `site_url`: رابط الموقع

**الميزات**:
- ترحيب حار بالمستخدم الجديد
- قائمة بميزات المنصة
- زر CTA للبدء في التصفح
- تدرج لوني جذاب باستخدام ألوان العلامة التجارية

---

### 2. OTP Verification - التحقق برمز OTP
**الملف**: `templates/emails/otp_verification.html`

**الاستخدام**:
```python
EmailService.send_otp_email(
    email="user@example.com",
    otp_code="742839",
    user_name="فاطمة علي"
)
```

**المتغيرات**:
- `site_name`: اسم الموقع
- `user_name`: اسم المستخدم
- `otp_code`: رمز التحقق (6 أرقام)
- `expiry_minutes`: مدة صلاحية الرمز بالدقائق

**الميزات**:
- عرض رمز OTP بخط كبير واضح
- مربع منقط ملون للرمز
- تحذير أمني
- نصائح أمان للمستخدم
- عداد زمني للصلاحية

---

### 3. Password Reset - إعادة تعيين كلمة المرور
**الملف**: `templates/emails/password_reset.html`

**الاستخدام**:
```python
EmailService.send_password_reset_email(
    email="user@example.com",
    reset_link="http://example.com/reset/token123",
    user_name="خالد السعيد"
)
```

**المتغيرات**:
- `site_name`: اسم الموقع
- `user_name`: اسم المستخدم
- `reset_link`: رابط إعادة تعيين كلمة المرور
- `site_url`: رابط الموقع

**الميزات**:
- زر واضح لإعادة التعيين
- رابط بديل نصي
- معلومات أمنية مهمة
- تنبيه بصلاحية الرابط (24 ساعة)
- نصائح لاختيار كلمة مرور قوية

---

### 4. Ad Approved - الموافقة على الإعلان
**الملف**: `templates/emails/ad_approved.html`

**الاستخدام**:
```python
EmailService.send_ad_approved_email(
    email="user@example.com",
    ad_title="آيفون 14 برو ماكس",
    ad_url="http://example.com/ad/123",
    user_name="سارة أحمد"
)
```

**المتغيرات**:
- `site_name`: اسم الموقع
- `user_name`: اسم المستخدم
- `ad_title`: عنوان الإعلان
- `ad_url`: رابط الإعلان
- `site_url`: رابط الموقع

**الميزات**:
- تصميم احتفالي بألوان خضراء للنجاح
- بطاقة عرض الإعلان
- قائمة بالإجراءات المتاحة
- نصائح لزيادة المبيعات
- زر لعرض الإعلان

---

## 🎨 ميزات التصميم المشتركة

### 1. الهيدر (Header)
- تدرج لوني باستخدام ألوان العلامة التجارية
- أيقونة كبيرة مميزة لكل نوع رسالة
- عنوان واضح ووصف قصير

### 2. المحتوى (Body)
- نص واضح بخط Cairo
- تباعد مريح للعين
- استخدام صناديق ملونة للمعلومات المهمة
- أيقونات إيموجي لإضافة الحيوية

### 3. الأزرار (CTA Buttons)
- تدرج لوني جذاب
- تأثيرات hover
- ظلال ثلاثية الأبعاد
- حواف دائرية

### 4. الفوتر (Footer)
- معلومات الموقع
- روابط سريعة
- حقوق النشر
- تنويه البريد الآلي

### 5. Responsive Design
- تصميم متجاوب مع جميع الأجهزة
- يعمل بشكل مثالي على الهاتف المحمول
- تحسين الأحجام للشاشات الصغيرة

---

## 🧪 اختبار القوالب

### استخدام السكريبت الجاهز
```bash
# تأكد من تشغيل smtp4dev
docker compose up -d smtp4dev

# قم بتشغيل السكريبت
python test_email.py
```

### الاختبار اليدوي من Django Shell
```python
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# تجهيز السياق
context = {
    "site_name": "إدريسي مارت",
    "user_name": "اسم المستخدم",
    # ... المتغيرات الأخرى
}

# رندر القالب
html_content = render_to_string("emails/welcome.html", context)

# إرسال البريد
email = EmailMultiAlternatives(
    subject="الموضوع",
    body="نص بديل",
    from_email="noreply@idrissimart.local",
    to=["user@example.com"],
)
email.attach_alternative(html_content, "text/html")
email.send()
```

### عرض البريد في المتصفح
افتح: **http://localhost:3100**

---

## 📊 بنية ملف القالب

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>العنوان</title>
    <style>
        /* الأنماط المدمجة (inline styles) */
        /* تستخدم ألوان العلامة التجارية */
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="email-container">
            <!-- الهيدر -->
            <div class="email-header">...</div>

            <!-- المحتوى -->
            <div class="email-body">...</div>

            <!-- الفوتر -->
            <div class="email-footer">...</div>
        </div>
    </div>
</body>
</html>
```

---

## 🔧 التخصيص

### تغيير الألوان
ابحث عن هذه القيم في القوالب:
```css
#4b315e  /* اللون الأساسي البنفسجي */
#3a2449  /* البنفسجي الداكن */
#ff6001  /* البرتقالي */
#6b4c7a  /* بنفسجي فاتح */
#ff8534  /* برتقالي فاتح */
```

### إضافة قسم جديد
```html
<div class="custom-box">
    <div class="custom-title">العنوان</div>
    <div class="custom-content">المحتوى</div>
</div>
```

### إضافة زر جديد
```html
<div class="button-wrapper">
    <a href="{{your_link}}" class="cta-button">
        نص الزر
    </a>
</div>
```

---

## 📋 قائمة التحقق

عند إنشاء قالب جديد:

- [ ] استخدام اللغة العربية (rtl)
- [ ] Responsive design (media queries)
- [ ] ألوان العلامة التجارية
- [ ] خط Cairo
- [ ] أيقونات مناسبة
- [ ] زر CTA واضح
- [ ] معلومات التواصل في الفوتر
- [ ] نص بديل (fallback text)
- [ ] اختبار على smtp4dev
- [ ] اختبار على الهاتف المحمول

---

## 🚀 أفضل الممارسات

### 1. Inline CSS
استخدم Inline CSS لضمان التوافق مع جميع عملاء البريد:
```html
<div style="color: #4b315e; font-size: 16px;">
    النص
</div>
```

### 2. Tables للتخطيط (اختياري)
بعض عملاء البريد القديمة تفضل tables:
```html
<table width="100%" cellpadding="0" cellspacing="0">
    <tr>
        <td>المحتوى</td>
    </tr>
</table>
```

### 3. Alt Text للصور
```html
<img src="logo.png" alt="شعار إدريسي مارت" />
```

### 4. Fallback Fonts
```css
font-family: 'Cairo', 'Segoe UI', Tahoma, Arial, sans-serif;
```

### 5. اختبار متعدد العملاء
- Gmail
- Outlook
- Apple Mail
- Yahoo Mail
- Thunderbird

---

## 🌐 الموارد الإضافية

- **Email on Acid**: اختبار التوافق
- **Litmus**: معاينة عبر العملاء المختلفة
- **Can I Email**: دعم ميزات CSS في البريد
- **MJML**: إطار عمل لتطوير البريد الإلكتروني

---

## 📞 الدعم

للمساعدة في تخصيص القوالب:
1. راجع الكود في `templates/emails/`
2. اختبر على smtp4dev أولاً
3. تحقق من `main/services/email_service.py`

---

**تم إنشاؤه بواسطة GitHub Copilot** 🤖
**© 2026 إدريسي مارت. جميع الحقوق محفوظة.**
