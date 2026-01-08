# دليل إعداد تسجيل الدخول عبر السوشيال ميديا (Google & Facebook)

## نظرة عامة

تم إضافة دعم كامل لتسجيل الدخول عبر Google و Facebook باستخدام django-allauth. جميع الإعدادات قابلة للتحكم من لوحة تحكم الأدمن دون الحاجة لتعديل الكود.

## الخطوات المطلوبة

### 1. تثبيت المكتبات

قم بتثبيت المكتبة المطلوبة:

```bash
pip install django-allauth==70.0.0
```

أو ببساطة:

```bash
pip install -r requirements.txt
```

### 2. تشغيل Migrations

```bash
python manage.py migrate
```

سيتم إنشاء جداول django-allauth تلقائياً.

### 3. إعداد Google OAuth

#### أ. إنشاء مشروع في Google Cloud Console

1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروع جديد أو اختر مشروع موجود
3. من القائمة، اذهب إلى **APIs & Services** → **Credentials**
4. انقر على **Create Credentials** → **OAuth client ID**
5. اختر **Web application**
6. أضف **Authorized redirect URIs**:
   ```
   http://localhost:8000/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   ```
7. احفظ **Client ID** و **Client secret**

#### ب. تفعيل Google+ API

1. من القائمة، اذهب إلى **APIs & Services** → **Library**
2. ابحث عن "Google+ API"
3. انقر على **Enable**

#### ج. إضافة الإعدادات في لوحة تحكم Django

1. سجل دخول إلى لوحة تحكم الأدمن
2. اذهب إلى **Constance** → **Config**
3. ابحث عن قسم **"Social Authentication"**
4. فعّل **SOCIAL_AUTH_ENABLED** = `True`
5. أضف **GOOGLE_OAUTH_CLIENT_ID** = `your-client-id`
6. أضف **GOOGLE_OAUTH_SECRET** = `your-client-secret`
7. احفظ التغييرات

### 4. إعداد Facebook Login

#### أ. إنشاء تطبيق Facebook

1. اذهب إلى [Facebook Developers](https://developers.facebook.com/)
2. انقر على **My Apps** → **Create App**
3. اختر **Consumer** كنوع التطبيق
4. أكمل البيانات المطلوبة
5. من لوحة التطبيق، اذهب إلى **Settings** → **Basic**
6. احفظ **App ID** و **App Secret**

#### ب. إعداد Facebook Login

1. من القائمة الجانبية، اذهب إلى **Facebook Login** → **Settings**
2. أضف **Valid OAuth Redirect URIs**:
   ```
   http://localhost:8000/accounts/facebook/login/callback/
   https://yourdomain.com/accounts/facebook/login/callback/
   ```
3. احفظ التغييرات

#### ج. إضافة الإعدادات في لوحة تحكم Django

1. سجل دخول إلى لوحة تحكم الأدمن
2. اذهب إلى **Constance** → **Config**
3. ابحث عن قسم **"Social Authentication"**
4. فعّل **SOCIAL_AUTH_ENABLED** = `True`
5. أضف **FACEBOOK_APP_ID** = `your-app-id`
6. أضف **FACEBOOK_APP_SECRET** = `your-app-secret`
7. احفظ التغييرات

### 5. إعداد متغيرات البيئة (اختياري)

للأمان، يُفضل وضع المفاتيح في ملف `.env`:

```env
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_SECRET=your-google-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

الإعدادات في Constance ستقرأ من المتغيرات البيئية تلقائياً.

### 6. إضافة Social Applications في Django Admin

1. اذهب إلى **Django Admin** → **Sites** → **Social applications**
2. انقر على **Add social application**

#### للـ Google:
- **Provider**: Google
- **Name**: Google OAuth
- **Client id**: your-google-client-id
- **Secret key**: your-google-secret
- **Sites**: اختر موقعك (example.com)

#### للـ Facebook:
- **Provider**: Facebook
- **Name**: Facebook Login
- **Client id**: your-facebook-app-id
- **Secret key**: your-facebook-app-secret
- **Sites**: اختر موقعك (example.com)

## التحقق من التثبيت

### اختبار محلي

1. شغّل السيرفر:
   ```bash
   python manage.py runserver
   ```

2. اذهب إلى صفحة تسجيل الدخول: `http://localhost:8000/login/`

3. يجب أن ترى أزرار Google و Facebook مفعّلة

4. انقر على أي زر وتأكد من إعادة التوجيه إلى صفحة المزود

### التحقق من الإعدادات

```python
# في Django shell
python manage.py shell

from content.social_auth_config import (
    is_social_auth_enabled,
    is_google_auth_configured,
    is_facebook_auth_configured
)

print(f"Social Auth Enabled: {is_social_auth_enabled()}")
print(f"Google Configured: {is_google_auth_configured()}")
print(f"Facebook Configured: {is_facebook_auth_configured()}")
```

## المشاكل الشائعة وحلولها

### المشكلة 1: أزرار Social Login معطلة

**الحل:**
- تأكد من أن `SOCIAL_AUTH_ENABLED = True` في Constance
- تأكد من إدخال Client ID و Secret بشكل صحيح
- أعد تشغيل السيرفر بعد تغيير الإعدادات

### المشكلة 2: redirect_uri_mismatch

**الحل:**
- تأكد من أن Redirect URI في Google/Facebook يطابق تماماً:
  ```
  http://localhost:8000/accounts/google/login/callback/
  ```
- لاحظ `/` في النهاية مهم!

### المشكلة 3: SocialApp matching query does not exist

**الحل:**
- تأكد من إضافة Social Application في Django Admin
- تأكد من اختيار الموقع الصحيح (Site)

### المشكلة 4: Access blocked: Authorization Error

**الحل:**
- تأكد من تفعيل Google+ API في Google Cloud Console
- تأكد من أن البريد الإلكتروني للاختبار مضاف في OAuth consent screen

## URLs المتاحة

بعد التثبيت، ستكون URLs التالية متاحة:

- `/accounts/google/login/` - تسجيل دخول Google
- `/accounts/facebook/login/` - تسجيل دخول Facebook
- `/accounts/google/login/callback/` - Callback لـ Google
- `/accounts/facebook/login/callback/` - Callback لـ Facebook
- `/accounts/logout/` - تسجيل خروج

## الإعدادات المتقدمة

### تخصيص البيانات المطلوبة

يمكن تعديل البيانات المطلوبة من Google/Facebook في `content/social_auth_config.py`:

```python
# مثال: إضافة scope جديد لـ Google
"SCOPE": [
    "profile",
    "email",
    "https://www.googleapis.com/auth/user.birthday.read",
],
```

### ربط حسابات متعددة

django-allauth يدعم ربط حسابات اجتماعية متعددة لنفس المستخدم تلقائياً.

## الأمان

- ✅ جميع Client IDs و Secrets مخزنة بشكل آمن
- ✅ يمكن استخدام متغيرات البيئة للحماية الإضافية
- ✅ CSRF protection مفعّل تلقائياً
- ✅ دعم HTTPS في الإنتاج

## الإنتاج (Production)

في الإنتاج، تأكد من:

1. استخدام HTTPS:
   ```python
   ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
   ```

2. تحديث Redirect URIs:
   ```
   https://yourdomain.com/accounts/google/login/callback/
   https://yourdomain.com/accounts/facebook/login/callback/
   ```

3. إزالة localhost من Authorized domains

## الدعم

للمشاكل أو الاستفسارات، راجع:
- [django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login/)

---

تم التحديث: يناير 2026
