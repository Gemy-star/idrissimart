# دليل نظام التحقق الكامل - Complete Verification System Guide

## نظرة عامة

تم استكمال وتطوير نظام التحقق من البريد الإلكتروني والموبايل ليكون قابلاً للتحكم بالكامل من لوحة تحكم الأدمن.

## الميزات الرئيسية

### 1. إعدادات قابلة للتحكم من الأدمن

يمكن التحكم في جميع إعدادات التحقق من صفحة Constance Config في لوحة تحكم الأدمن:

#### إعدادات التحقق المتاحة:

1. **REQUIRE_EMAIL_VERIFICATION** (افتراضياً: False)
   - تفعيل/تعطيل التحقق من البريد الإلكتروني أثناء التسجيل
   - عند التفعيل: يتم إرسال رابط تحقق إلى البريد الإلكتروني

2. **REQUIRE_PHONE_VERIFICATION** (افتراضياً: False)
   - تفعيل/تعطيل التحقق من رقم الهاتف أثناء التسجيل
   - عند التفعيل: يتم إرسال OTP عبر SMS

3. **REQUIRE_VERIFICATION_FOR_SERVICES** (افتراضياً: False)
   - تفعيل/تعطيل إلزام التحقق لاستخدام خدمات الموقع
   - عند التفعيل: يجب التحقق من البريد أو الهاتف قبل استخدام الخدمات

4. **VERIFICATION_SERVICES_MESSAGE**
   - الرسالة التي تظهر للمستخدمين غير المتحققين
   - يمكن تخصيصها من لوحة التحكم

### 2. صفحات التحقق

#### صفحة التحقق من البريد الإلكتروني
- المسار: `/email-verification-required/`
- الميزات:
  - تصميم عصري وجذاب
  - زر إعادة إرسال رابط التحقق
  - عداد تنازلي (60 ثانية)
  - تعليمات مساعدة
  - روابط للدعم الفني

#### صفحة التحقق من الموبايل
- المسار: `/phone-verification-required/`
- الميزات:
  - واجهة تفاعلية من 3 خطوات
  - إرسال OTP عبر SMS
  - إدخال الرمز (6 أرقام)
  - تأكيد تلقائي عند إدخال 6 أرقام
  - إمكانية إعادة الإرسال
  - عداد تنازلي

### 3. نظام Decorators للتحكم في الوصول

تم إنشاء ملف `content/verification_decorators.py` يحتوي على:

#### @verification_required()
```python
from content.verification_decorators import verification_required

@verification_required()
def my_service_view(request):
    # يتحقق من حالة التحقق بناءً على الإعدادات
    # يُعيد التوجيه تلقائياً إذا كان التحقق مطلوباً
    pass
```

#### @email_verification_required()
```python
from content.verification_decorators import email_verification_required

@email_verification_required()
def my_email_protected_view(request):
    # يتطلب تحقق البريد الإلكتروني
    pass
```

#### @phone_verification_required()
```python
from content.verification_decorators import phone_verification_required

@phone_verification_required()
def my_phone_protected_view(request):
    # يتطلب تحقق رقم الهاتف
    pass
```

### 4. Context Processor

تم تحديث `content/context_processors.py` لتوفير معلومات التحقق في جميع القوالب:

```django
{% if verification_requirements.services_require_verification %}
    {% if not user_verification_status.is_email_verified and not user_verification_status.is_phone_verified %}
        <div class="alert alert-warning">
            {{ verification_requirements.verification_message }}
        </div>
    {% endif %}
{% endif %}
```

المتغيرات المتاحة في القوالب:
- `verification_requirements.email_required`
- `verification_requirements.phone_required`
- `verification_requirements.services_require_verification`
- `verification_requirements.verification_message`
- `user_verification_status.is_email_verified`
- `user_verification_status.is_phone_verified`
- `user_verification_status.needs_verification`

## كيفية الاستخدام

### للمطورين

#### 1. حماية View بالتحقق

```python
from content.verification_decorators import verification_required
from django.shortcuts import render

@verification_required()
def post_ad_view(request):
    """View محمي - يتطلب التحقق إذا كان مفعلاً في الإعدادات"""
    return render(request, 'ads/post_ad.html')
```

#### 2. التحقق اليدوي في الكود

```python
from content.verification_utils import (
    is_verification_required_for_services,
    user_can_use_services
)

def my_view(request):
    if is_verification_required_for_services():
        can_use, message = user_can_use_services(request.user)
        if not can_use:
            messages.warning(request, message)
            return redirect('main:email_verification_required')

    # المتابعة في الكود
    pass
```

#### 3. في القوالب

```django
{% if verification_requirements.services_require_verification %}
    {% if user_verification_status.needs_verification %}
        <div class="verification-banner">
            <i class="fas fa-exclamation-circle"></i>
            {{ verification_requirements.verification_message }}
            <a href="{% url 'main:email_verification_required' %}" class="btn btn-warning">
                تحقق الآن
            </a>
        </div>
    {% endif %}
{% endif %}
```

### للمسؤولين (Admins)

#### الوصول إلى الإعدادات:
1. سجل الدخول إلى لوحة تحكم الأدمن
2. اذهب إلى **Constance** → **Config**
3. ابحث عن قسم **Verification Settings**

#### السيناريوهات الشائعة:

##### السيناريو 1: تفعيل التحقق من البريد أثناء التسجيل فقط
```
REQUIRE_EMAIL_VERIFICATION = True
REQUIRE_PHONE_VERIFICATION = False
REQUIRE_VERIFICATION_FOR_SERVICES = False
```
النتيجة: المستخدمون يحتاجون للتحقق من البريد أثناء التسجيل، لكن يمكنهم استخدام الخدمات بدون تحقق

##### السيناريو 2: تفعيل التحقق الكامل (البريد + الموبايل + الخدمات)
```
REQUIRE_EMAIL_VERIFICATION = True
REQUIRE_PHONE_VERIFICATION = True
REQUIRE_VERIFICATION_FOR_SERVICES = True
```
النتيجة: المستخدمون يحتاجون للتحقق من البريد والموبايل، ولا يمكنهم استخدام الخدمات بدون تحقق واحد على الأقل

##### السيناريو 3: تعطيل جميع عمليات التحقق
```
REQUIRE_EMAIL_VERIFICATION = False
REQUIRE_PHONE_VERIFICATION = False
REQUIRE_VERIFICATION_FOR_SERVICES = False
```
النتيجة: لا توجد قيود تحقق - التسجيل والخدمات متاحة بدون تحقق

## التكامل مع الأنظمة الأخرى

### 1. نظام الباقات (Packages)
يمكن ربط منح الباقة المجانية بحالة التحقق:

```python
from content.site_config import SiteConfiguration

site_config = SiteConfiguration.get_solo()
if site_config.require_verification_for_free_package:
    if not (user.is_email_verified and user.is_mobile_verified):
        # لا تمنح الباقة المجانية
        pass
```

### 2. نظام السلة والطلبات
```python
from content.verification_decorators import verification_required

@verification_required()
def add_to_cart_view(request, ad_id):
    # إضافة إلى السلة - محمي بالتحقق
    pass
```

### 3. نظام نشر الإعلانات
```python
from content.verification_decorators import verification_required

@verification_required()
def post_classified_ad(request):
    # نشر إعلان - محمي بالتحقق
    pass
```

## الملفات المعدلة/المضافة

### ملفات جديدة:
1. `content/verification_decorators.py` - Decorators للتحكم في الوصول
2. `templates/pages/email_verification_required.html` - صفحة التحقق من البريد
3. `templates/pages/phone_verification_required.html` - صفحة التحقق من الموبايل
4. `docs/COMPLETE_VERIFICATION_SYSTEM.md` - هذا الملف

### ملفات معدلة:
1. `idrissimart/settings/constance_config.py` - إضافة إعدادات التحقق
2. `content/verification_utils.py` - تحديث للاستخدام من constance
3. `content/context_processors.py` - إضافة حالة التحقق للمستخدم
4. `main/auth_views.py` - إضافة views جديدة
5. `main/urls.py` - إضافة URLs جديدة

## الاختبار

### اختبار التحقق من البريد:
1. فعّل `REQUIRE_EMAIL_VERIFICATION = True`
2. سجل حساب جديد
3. تحقق من إرسال البريد
4. انقر على رابط التحقق
5. تأكد من تحديث حالة `is_email_verified`

### اختبار التحقق من الموبايل:
1. فعّل `REQUIRE_PHONE_VERIFICATION = True`
2. تأكد من إعدادات Twilio صحيحة
3. سجل حساب جديد
4. أدخل رقم هاتف صحيح
5. اطلب OTP
6. أدخل الرمز المستلم
7. تأكد من تحديث حالة `is_mobile_verified`

### اختبار حماية الخدمات:
1. فعّل `REQUIRE_VERIFICATION_FOR_SERVICES = True`
2. سجل حساب جديد بدون تحقق
3. حاول الوصول لخدمة محمية بـ `@verification_required()`
4. تأكد من إعادة التوجيه لصفحة التحقق

## الأمان

- جميع OTP تنتهي صلاحيتها بعد 10 دقائق
- محاولات التحقق محدودة (5 محاولات)
- Tokens التحقق من البريد تنتهي بعد 24 ساعة
- جميع الـ endpoints محمية بـ CSRF tokens
- Session-based verification للأمان

## الدعم والصيانة

للمشاكل أو الاستفسارات:
1. تحقق من logs السيرفر
2. تأكد من إعدادات SMTP/Twilio
3. راجع ملف `content/verification_utils.py`
4. اختبر في وضع development أولاً

## التحديثات المستقبلية المقترحة

- [ ] إضافة تحقق بالوقتين (2FA)
- [ ] دعم تحقق WhatsApp
- [ ] لوحة تحكم للمسؤولين لإدارة حالات التحقق
- [ ] إحصائيات حول معدلات التحقق
- [ ] تذكيرات تلقائية للمستخدمين غير المتحققين

---

تم التحديث: يناير 2026
الإصدار: 2.0
