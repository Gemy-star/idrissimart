# دليل اختبار خدمات الإنتاج
# Production Services Testing Guide

## نظرة عامة | Overview

هذا السكريبت يختبر الخدمات الخارجية المستخدمة في الموقع للتأكد من عملها بشكل صحيح في بيئة الإنتاج.

This script tests external services used in the website to ensure they work correctly in production.

## الخدمات المدعومة | Supported Services

### 1. Paymob (بوابة الدفع المصرية)
- اختبار المصادقة مع Paymob API
- اختبار إنشاء معاملة دفع تجريبية
- التحقق من المفاتيح والإعدادات

### 2. PayPal (بوابة الدفع العالمية)
- اختبار الاتصال بـ PayPal API
- اختبار إنشاء دفعة تجريبية
- التحقق من الوضع (Sandbox/Live)

### 3. Twilio SMS (خدمة الرسائل النصية)
- اختبار الاتصال بـ Twilio API
- اختبار إرسال رسالة نصية (اختياري)
- التحقق من حالة الحساب

## المتطلبات | Requirements

```bash
# تثبيت المكتبات المطلوبة
poetry install

# أو باستخدام pip
pip install colorama twilio paypalrestsdk requests
```

## الإعدادات | Configuration

تأكد من وجود المتغيرات التالية في ملف `.env`:

### Paymob Configuration
```env
PAYMOB_API_KEY=your_api_key_here
PAYMOB_SECRET_KEY=your_secret_key_here
PAYMOB_PUBLIC_KEY=your_public_key_here
PAYMOB_INTEGRATION_ID=your_integration_id_here
PAYMOB_IFRAME_ID=your_iframe_id_here
PAYMOB_HMAC_SECRET=your_hmac_secret_here
```

### PayPal Configuration
```env
PAYPAL_MODE=sandbox  # أو live للإنتاج
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
```

### Twilio Configuration
```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

## طريقة الاستخدام | Usage

### اختبار جميع الخدمات | Test All Services
```bash
poetry run python test_production_services.py --all
```

### اختبار خدمة معينة | Test Specific Service

#### اختبار Paymob فقط
```bash
poetry run python test_production_services.py --paymob
```

#### اختبار PayPal فقط
```bash
poetry run python test_production_services.py --paypal
```

#### اختبار Twilio فقط
```bash
poetry run python test_production_services.py --twilio
```

### اختبار إرسال SMS | Test SMS Sending
```bash
# اختبار إرسال رسالة نصية لرقم معين
poetry run python test_production_services.py --sms +201234567890

# أو مع اختبار جميع الخدمات
poetry run python test_production_services.py --all --sms +201234567890
```

## مخرجات السكريبت | Script Output

السكريبت يعرض المعلومات التالية لكل خدمة:

### ✓ علامات النجاح (باللون الأخضر)
- تم التحقق من الإعدادات بنجاح
- الاتصال بالـ API نجح
- العملية التجريبية تمت بنجاح

### ✗ علامات الفشل (باللون الأحمر)
- إعدادات مفقودة أو غير صحيحة
- فشل الاتصال بالـ API
- فشل العملية التجريبية

### ℹ معلومات إضافية (باللون الأصفر)
- معلومات عن الإعدادات الحالية
- تحذيرات (مثل وضع Live في PayPal)
- معلومات عن الخطوات التي يتم تنفيذها

## أمثلة على المخرجات | Output Examples

```
======================================================================
                  TESTING PAYMOB PAYMENT GATEWAY
======================================================================
ℹ Checking Paymob configuration...
✓ Configuration keys are present
API Key: ZXlKaGJHY2lPaUpJVXpV...
Secret Key: egy_sk_test_f0fc353...
Public Key: egy_pk_test_n3iBXXi...
✓ Paymob service is ENABLED

ℹ Testing Paymob authentication...
✓ Authentication successful! Token: eyJ0eXAiOiJKV1QiLCJhbGc...

ℹ Testing payment creation (test transaction)...
✓ Test payment created successfully!
Payment URL: https://accept.paymob.com/...
```

## استكشاف الأخطاء | Troubleshooting

### خطأ: "API Key is not configured"
- تأكد من وجود المفاتيح في ملف `.env`
- تأكد من تحميل ملف `.env` بشكل صحيح
- تأكد من عدم وجود مسافات زائدة في القيم

### خطأ: "Authentication failed"
- تحقق من صحة المفاتيح (API Key, Secret Key)
- تأكد من أن المفاتيح لم تنتهي صلاحيتها
- تحقق من اتصالك بالإنترنت

### خطأ: "Service is DISABLED"
- افحص إعدادات django-constance في لوحة الإدارة
- تأكد من تفعيل الخدمة المطلوبة

### خطأ في إرسال SMS
- تحقق من صيغة رقم الهاتف (+countrycode...)
- تأكد من أن الرقم مسجل في حسابك (في وضع Trial)
- تحقق من رصيد حساب Twilio

## ملاحظات مهمة | Important Notes

### 🔴 بيئة الإنتاج | Production Environment
- عند الاختبار في الإنتاج، استخدم أرقام اختبار فقط
- لا تستخدم بيانات بطاقات حقيقية في الاختبار
- تأكد من أن PayPal في وضع Sandbox أثناء التطوير

### 🔐 الأمان | Security
- لا تشارك مخرجات السكريبت التي تحتوي على Tokens
- احفظ ملف `.env` بعيداً عن Git
- استخدم متغيرات البيئة في الإنتاج

### 💰 التكاليف | Costs
- اختبار Paymob في Test Mode مجاني
- اختبار PayPal في Sandbox Mode مجاني
- رسائل Twilio SMS قد تكلف (حتى في التطوير)

## الدعم | Support

إذا واجهت مشاكل:
1. راجع وثائق الخدمة الرسمية:
   - [Paymob Docs](https://docs.paymob.com/)
   - [PayPal Developer](https://developer.paypal.com/)
   - [Twilio Docs](https://www.twilio.com/docs)

2. تحقق من logs Django في:
   ```
   /var/log/django/idrissimart.log
   ```

3. استخدم وضع Debug للحصول على معلومات أكثر تفصيلاً

## تحديثات مستقبلية | Future Updates

- [ ] إضافة اختبار Stripe
- [ ] إضافة اختبار Moyasar
- [ ] إضافة تقرير مفصل بصيغة HTML
- [ ] إضافة جدولة تلقائية للاختبارات
