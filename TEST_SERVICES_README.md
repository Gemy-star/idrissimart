# 🧪 اختبار خدمات الإنتاج | Production Services Testing

## 🚀 البدء السريع | Quick Start

### 1️⃣ التحقق من الإعدادات
```bash
# Linux/Mac
make check-services

# Windows
check_services.bat

# أو مباشرة
poetry run python check_services.py
```

### 2️⃣ اختبار جميع الخدمات
```bash
# Linux/Mac
make test-services

# Windows
test_services.bat all

# أو مباشرة
poetry run python test_production_services.py --all
```

## 📋 الأوامر المتاحة

### ✅ التحقق السريع
```bash
poetry run python check_services.py
```
يتحقق من وجود الإعدادات فقط (سريع - بدون اتصال)

### 🧪 اختبار شامل
```bash
# اختبار الكل
poetry run python test_production_services.py --all

# اختبار Paymob فقط
poetry run python test_production_services.py --paymob

# اختبار PayPal فقط
poetry run python test_production_services.py --paypal

# اختبار Twilio فقط
poetry run python test_production_services.py --twilio

# اختبار إرسال SMS
poetry run python test_production_services.py --sms +201234567890
```

## 📦 تثبيت المكتبات المطلوبة

```bash
# باستخدام Poetry (مفضل)
poetry install

# أو إضافة المكتبات يدوياً
poetry add colorama paypalrestsdk requests twilio
```

## 🔧 الإعدادات المطلوبة

تأكد من وجود هذه المتغيرات في `.env`:

```env
# Paymob
PAYMOB_API_KEY=your_key
PAYMOB_SECRET_KEY=your_secret
PAYMOB_PUBLIC_KEY=your_public_key

# PayPal
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_secret
PAYPAL_MODE=sandbox

# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

## 📖 التوثيق الكامل

راجع [TEST_SERVICES_GUIDE.md](TEST_SERVICES_GUIDE.md) للحصول على:
- شرح مفصل لكل خدمة
- استكشاف الأخطاء وحلها
- أمثلة المخرجات
- ملاحظات الأمان

## 🎯 أمثلة سريعة

### مثال 1: فحص الإعدادات
```bash
$ poetry run python check_services.py

━━━ PAYMOB ━━━
✓ API Key: **********BXXil
✓ Secret Key: **********7ea4
✓ Public Key: **********0srZ
✓ Integration ID: Optional

━━━ PAYPAL ━━━
✓ Client ID: **********1foq
✓ Client Secret: **********wYYr
✓ Mode: sandbox
```

### مثال 2: اختبار شامل
```bash
$ poetry run python test_production_services.py --paymob

======================================================================
                  TESTING PAYMOB PAYMENT GATEWAY
======================================================================
ℹ Checking Paymob configuration...
✓ Configuration keys are present
✓ Paymob service is ENABLED
✓ Authentication successful!
✓ Test payment created successfully!
```

## ⚠️ ملاحظات مهمة

- 🔴 **لا تستخدم بيانات حقيقية** في الاختبارات
- 🟡 تأكد من وضع **Sandbox** في PayPal أثناء التطوير
- 🟢 رسائل Twilio قد تكلف حتى في التطوير

## 🐛 استكشاف الأخطاء

| الخطأ | الحل |
|-------|------|
| `API Key is not configured` | أضف المفاتيح في `.env` |
| `Authentication failed` | تحقق من صحة المفاتيح |
| `Service is DISABLED` | فعّل الخدمة في django-constance |
| `SMS failed` | تحقق من صيغة رقم الهاتف |

## 📞 الدعم

- 📚 [Paymob Docs](https://docs.paymob.com/)
- 📚 [PayPal Developer](https://developer.paypal.com/)
- 📚 [Twilio Docs](https://www.twilio.com/docs)
