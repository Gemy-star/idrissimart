# تفعيل تسجيل الدخول عبر Google/Facebook - دليل سريع

## ✅ تم التثبيت بنجاح!

تم تثبيت `django-allauth==70.0.0` وإضافة جميع الإعدادات المطلوبة.

## الخطوات التالية:

### 1. تشغيل Migrations
```bash
python manage.py migrate
```

### 2. تفعيل من لوحة الأدمن

اذهب إلى: **Admin Panel** → **Constance** → **Config** → **Social Authentication**

فعّل:
- ✅ `SOCIAL_AUTH_ENABLED` = True
- أضف `GOOGLE_OAUTH_CLIENT_ID` و `GOOGLE_OAUTH_SECRET`
- أضف `FACEBOOK_APP_ID` و `FACEBOOK_APP_SECRET`

### 3. إضافة Social Applications

اذهب إلى: **Django Admin** → **Sites** → **Social applications**

أضف:
- Google (Provider: Google)
- Facebook (Provider: Facebook)

## كيفية الحصول على المفاتيح:

### Google:
1. [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth Client ID
3. Add redirect: `http://localhost:8000/accounts/google/login/callback/`

### Facebook:
1. [Facebook Developers](https://developers.facebook.com/)
2. Create App
3. Add redirect: `http://localhost:8000/accounts/facebook/login/callback/`

## الملفات المعدلة:
- ✅ `requirements.txt` - أضيف django-allauth
- ✅ `settings/common.py` - إعدادات allauth
- ✅ `settings/constance_config.py` - إعدادات OAuth
- ✅ `main/urls.py` - URLs الخاصة بـ allauth
- ✅ `templates/pages/login.html` - أزرار Social Login
- ✅ `content/social_auth_config.py` - إدارة إعدادات ديناميكية
- ✅ `content/verification_utils.py` - دعم social_auth_enabled
- ✅ `content/apps.py` - تحميل الإعدادات عند البدء

## المزيد من التفاصيل:
راجع: `docs/SOCIAL_AUTH_SETUP.md`
