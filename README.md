# 🛍️ إدريسي مارت (Idrissi Mart)

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0-green.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**منصة تجارة إلكترونية حديثة مبنية بإطار Django**

[المميزات](#-المميزات-الرئيسية) •
[التثبيت](#-التثبيت-والإعداد) •
[الاستخدام](#-الاستخدام) •
[المساهمة](#-المساهمة)

</div>

---

## 📋 نظرة عامة

**إدريسي مارت** هو منصة تجارة إلكترونية حديثة ومتكاملة تهدف إلى تمكين المتاجر والبائعين من عرض منتجاتهم بسهولة وبأسلوب عصري. تدعم المنصة اللغة العربية والإنجليزية، مع تصميم متجاوب وأداء عالي وتحسينات أمنية متقدمة.

### ✨ **الإصدار 2.0 - ميزات جديدة**

- 🛒 **سلة التسوق** مع أيقونة متحركة وعداد مباشر
- ❤️ **قائمة المفضلة** مع حفظ تلقائي للمنتجات المحبوبة
- 🌍 **محدد الدولة** مع دعم 8 دول عربية
- 📱 **تذييل محسّن** متجاوب مع نموذج اشتراك بالنشرة البريدية
- ⬆️ **زر العودة للأعلى** يظهر تلقائيًا عند التمرير
- 🎨 **رسوم متحركة متقدمة** باستخدام GSAP
- 🌓 **الوضع الليلي/النهاري** مع حفظ التفضيل

---

## 🌟 المميزات الرئيسية

### 🎨 **واجهة المستخدم**
- ✅ تصميم حديث ومتجاوب باستخدام **Bootstrap 5 RTL**
- ✅ دعم **الوضع الليلي/النهاري** مع حفظ التفضيل تلقائيًا
- ✅ **محول لغات** (عربي / إنجليزي) مع اتجاه ديناميكي RTL/LTR
- ✅ حركات انتقالية ناعمة بـ **60 إطار/ثانية**
- ✅ تأثيرات Parallax على الصفحة الرئيسية
- ✅ أزرار تفاعلية مع تأثير Ripple
- ✅ خط **Cairo** الاحترافي للنصوص العربية

### 🛒 **التجارة الإلكترونية**
- ✅ **سلة تسوق** مع إدارة ذكية للمنتجات
- ✅ **قائمة المفضلة** مع تبديل سريع
- ✅ **عدادات متحركة** للسلة والمفضلة
- ✅ **إشعارات فورية** لجميع العمليات
- ✅ **كروت منتجات** جاهزة للاستخدام
- ✅ **تقييمات النجوم** والمراجعات
- ✅ **شارات الخصومات** المتحركة
- ✅ حفظ البيانات في الجلسة

### 🌍 **دعم متعدد الدول**
- ✅ نموذج Django كامل لإدارة الدول
- ✅ 8 دول عربية افتراضيًا (السعودية، الإمارات، مصر، الكويت، قطر، البحرين، عمان، الأردن)
- ✅ أعلام الدول بـ Emoji
- ✅ أكواد الهواتف والعملات
- ✅ إمكانية إضافة دول جديدة بسهولة
- ✅ حفظ اختيار الدولة في localStorage

### 📱 **التذييل المحسّن**
- ✅ تصميم متجاوب على جميع الأجهزة
- ✅ نموذج **اشتراك بالنشرة البريدية**
- ✅ روابط **وسائل التواصل الاجتماعي** متحركة
- ✅ معلومات الاتصال مع أيقونات
- ✅ روابط سريعة منظمة
- ✅ **زر العودة للأعلى** مع رسوم متحركة

### ⚙️ **الوظائف الأساسية**
- ✅ إدارة البائعين والمنتجات
- ✅ صفحات ديناميكية مع تصنيفات وفلاتر
- ✅ دعم كامل للوسائط المتعددة
- ✅ إعدادات بيئية آمنة باستخدام `.env`
- ✅ نظام إعدادات منفصل (محلي / إنتاج / Docker)
- ✅ معالجات سياق مخصصة (Context Processors)
- ✅ نقاط نهاية API لـ AJAX

### 🔒 **الأمان والجودة**
- ✅ حماية **CSRF** على جميع الطلبات
- ✅ فحص الأمان عبر **Bandit**
- ✅ تحسين جودة الكود باستخدام **Ruff**
- ✅ فحص القوالب عبر **DjLint**
- ✅ جميع المفاتيح تُدار من `.env`
- ✅ منع حقن SQL باستخدام ORM
- ✅ حماية من XSS عبر قوالب Django
- ✅ جلسات آمنة ومشفرة

### 🧑‍💻 **تجربة المطورين**
- ✅ أوامر سريعة عبر **Makefile**
- ✅ إعداد CI/CD عبر GitHub Actions
- ✅ فحوصات Pre-commit تلقائية
- ✅ أدوات اختبار وتصحيح مدمجة
- ✅ توثيق شامل وكامل
- ✅ أمثلة جاهزة للاستخدام

---

## 🗂️ هيكل المشروع الكامل

```
idrissimart/
├── manage.py
├── .env                          # إعدادات البيئة (غير مرفوعة إلى Git)
├── .env.example                  # قالب ملف البيئة
├── pyproject.toml                # إعداد Ruff + Bandit
├── Makefile                      # أوامر مساعدة للمطورين
├── test_all.sh                   # سكربت شامل للفحوصات
├── requirements.txt              # تبعيات Python
├── README.md                     # هذا الملف
│
├── .github/
│   └── workflows/
│       └── django-ci.yml         # إعداد CI/CD
│
├── idrissimart/                  # ملفات الإعدادات الأساسية
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── common.py             # إعدادات مشتركة
│   │   ├── local.py              # إعدادات التطوير المحلي
│   │   ├── production.py         # إعدادات الإنتاج
│   │   └── docker.py             # إعدادات Docker
│   ├── urls.py                   # المسارات الرئيسية
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
│
├── main/                         # التطبيق الأساسي
│   ├── models.py                 # نماذج Django (Country, Product, etc.)
│   ├── views.py                  # Views للسلة والمفضلة
│   ├── urls.py                   # مسارات التطبيق
│   ├── admin.py                  # لوحة تحكم Django Admin
│   ├── signals.py                # إشارات Django
│   ├── decorators.py             # Decorators مخصصة
│   ├── context_processors.py     # معالجات السياق
│   └── management/
│       └── commands/
│           └── populate_countries.py  # أمر تعبئة الدول
│
├── templates/                    # القوالب
│   ├── base.html                 # القالب الأساسي
│   ├── home.html                 # الصفحة الرئيسية
│   ├── partials/
│   │   ├── _header.html          # الترويسة (مع السلة والمفضلة)
│   │   └── _footer.html          # التذييل (محسّن)
│   └── components/
│       └── product_card.html     # كرت المنتج القابل لإعادة الاستخدام
│
├── static/                       # الملفات الثابتة
│   ├── css/
│   │   └── style.css             # ملف CSS محسّن
│   ├── js/
│   │   ├── main.js               # JavaScript الرئيسي
│   │   ├── cart-wishlist.js      # مساعد السلة والمفضلة
│   │   └── test-utils.js         # أدوات الاختبار والتصحيح
│   ├── images/
│   │   └── logos/
│   └── fonts/
│
├── media/                        # ملفات الوسائط المرفوعة
│   ├── products/
│   └── vendors/
│
├── locale/                       # ملفات الترجمة
│   ├── ar/
│   └── en/
│
└── logs/                         # سجلات النظام
    └── debug.log
```

---

## ⚡ التثبيت السريع (15 دقيقة)

### **المتطلبات الأساسية**
- Python 3.11+
- PostgreSQL 13+ (أو SQLite للتطوير)
- Git

### **الخطوة 1: استنساخ المشروع**
```bash
git clone https://github.com/yourusername/idrissimart.git
cd idrissimart
```

### **الخطوة 2: إنشاء بيئة افتراضية**
```bash
python -m venv venv

# على Windows:
venv\Scripts\activate

# على Linux/Mac:
source venv/bin/activate
```

### **الخطوة 3: تثبيت التبعيات**
```bash
pip install -r requirements.txt
```

أو باستخدام Makefile:
```bash
make install
```

### **الخطوة 4: إعداد ملف البيئة**
```bash
cp .env.example .env
```

أنشئ مفتاح أمان جديد:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

عدّل ملف `.env`:
```env
DJANGO_SECRET_KEY=ضع_المفتاح_هنا
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### **الخطوة 5: تهيئة قاعدة البيانات**
```bash
# إنشاء الهجرات
python manage.py makemigrations

# تطبيق الهجرات
python manage.py migrate

# تعبئة الدول الافتراضية
python manage.py populate_countries

# إنشاء مستخدم مدير
python manage.py createsuperuser
```

### **الخطوة 6: جمع الملفات الثابتة**
```bash
python manage.py collectstatic --noinput
```

### **الخطوة 7: تشغيل الخادم**
```bash
python manage.py runserver
```

افتح المتصفح على:
```
http://127.0.0.1:8000/
```

لوحة التحكم:
```
http://127.0.0.1:8000/admin/
```

---

## 🎯 الإعداد الكامل للميزات الجديدة

### **1. إعداد السلة والمفضلة**

أضف إلى `settings/common.py`:
```python
# إعدادات الجلسة
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # أسبوعين
SESSION_SAVE_EVERY_REQUEST = False

# معالجات السياق
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'main.context_processors.countries',
    'main.context_processors.user_preferences',
]

# إعدادات السلة والمفضلة
CART_SESSION_KEY = 'cart'
WISHLIST_SESSION_KEY = 'wishlist'
MAX_CART_ITEMS = 100
MAX_WISHLIST_ITEMS = 50
```

### **2. إعداد نموذج الدول**

نموذج `Country` موجود في `main/models.py`:
```bash
# تطبيق الهجرات
python manage.py makemigrations
python manage.py migrate

# تعبئة الدول
python manage.py populate_countries
```

### **3. إضافة المسارات**

في `main/urls.py`:
```python
urlpatterns = [
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('api/wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('api/set-country/', views.set_country, name='set_country'),
]
```

### **4. تحديث القوالب**

استبدل الملفات التالية:
- ✅ `templates/partials/_header.html` - ترويسة محسّنة
- ✅ `templates/partials/_footer.html` - تذييل محسّن
- ✅ `static/css/style.css` - أنماط جديدة
- ✅ `static/js/main.js` - JavaScript محسّن

أضف:
- ✅ `static/js/cart-wishlist.js` - مساعد السلة والمفضلة
- ✅ `static/js/test-utils.js` - أدوات الاختبار (اختياري)

### **5. تحديث base.html**

أضف قبل `</body>`:
```html
<!-- Cart & Wishlist Helper -->
<script src="{% static 'js/cart-wishlist.js' %}"></script>

<!-- Testing Utilities (للتطوير فقط) -->
{% if DEBUG %}
<script src="{% static 'js/test-utils.js' %}"></script>
{% endif %}
```

---

## 🚀 أوامر Makefile المفيدة

| الأمر | الوصف |
|-------|--------|
| `make help` | عرض جميع الأوامر المتاحة |
| `make install` | تثبيت جميع التبعيات |
| `make setup` | إعداد المشروع بالكامل (migrations + static) |
| `make migrate` | تطبيق هجرات قاعدة البيانات |
| `make migrations` | إنشاء هجرات جديدة |
| `make superuser` | إنشاء مستخدم مدير |
| `make run` | تشغيل الخادم المحلي |
| `make lint` | تشغيل جميع أدوات الفحص |
| `make lint-fix` | إصلاح مشاكل التنسيق تلقائيًا |
| `make test` | تشغيل الاختبارات |
| `make clean` | تنظيف الملفات المؤقتة |
| `make collectstatic` | جمع الملفات الثابتة |
| `make populate-countries` | تعبئة الدول الافتراضية |

---

## 🎨 الاستخدام

### **استخدام السلة والمفضلة**

#### في القوالب:
```html
<!-- زر إضافة للسلة -->
<button class="btn btn-primary-custom"
        data-action="add-to-cart"
        data-item-id="{{ product.id }}"
        data-item-name="{{ product.name }}">
    <i class="fas fa-shopping-cart"></i> إضافة للسلة
</button>

<!-- زر المفضلة -->
<button class="wishlist-btn"
        data-action="toggle-wishlist"
        data-item-id="{{ product.id }}"
        data-item-name="{{ product.name }}">
    <i class="far fa-heart"></i>
</button>
```

#### في JavaScript:
```javascript
// إضافة منتج للسلة
CartWishlist.addToCart('123', 'اسم المنتج');

// إزالة منتج من السلة
CartWishlist.removeFromCart('123', 'اسم المنتج');

// إضافة للمفضلة
CartWishlist.addToWishlist('123', 'اسم المنتج');

// تحديث العداد
CartWishlist.updateBadgeCount('cart', 10);

// إظهار إشعار
CartWishlist.showNotification('تم بنجاح!', 'success');
```

### **استخدام كرت المنتج**

```html
{% for product in products %}
<div class="col-lg-3 col-md-4 col-sm-6">
    {% include 'components/product_card.html' with product=product %}
</div>
{% endfor %}
```

### **إضافة دولة جديدة**

عبر Django Admin:
```
/admin/main/country/add/
```

أو عبر Shell:
```bash
python manage.py shell
```

```python
from main.models import Country

Country.objects.create(
    name='السودان',
    name_en='Sudan',
    code='SD',
    flag_emoji='🇸🇩',
    phone_code='+249',
    currency='SDG',
    order=9,
    is_active=True
)
```

---

## 🧪 الاختبار والتصحيح

### **اختبارات Django**
```bash
# تشغيل جميع الاختبارات
python manage.py test

# اختبار تطبيق معين
python manage.py test main

# اختبار مع التغطية
coverage run --source='.' manage.py test
coverage report
```

### **اختبارات JavaScript (في المتصفح)**

افتح Console ونفذ:
```javascript
// تشغيل جميع الاختبارات
IdrissiTest.runAll()

// اختبار السلة فقط
IdrissiTest.testCart()

// اختبار المفضلة فقط
IdrissiTest.testWishlist()

// اختبار الإشعارات
IdrissiTest.testNotifications()

// فحص الأداء
IdrissiTest.checkPerformance()

// عرض المساعدة
IdrissiTest.help()
```

### **فحوصات الجودة**
```bash
# فحص الكود مع Ruff
ruff check .

# تنسيق الكود
ruff format .

# فحص الأمان مع Bandit
bandit -r . -c pyproject.toml

# فحص القوالب
djlint templates/ --check

# أو استخدم Makefile
make lint
make lint-fix
```

### **الفحص الشامل**
```bash
# تشغيل جميع الفحوصات
./test_all.sh

# أو
make test-all
```

---

## 📱 الاستجابة للأجهزة

المنصة متجاوبة بالكامل مع جميع الأحجام:

| الجهاز | العرض | التخطيط |
|--------|-------|----------|
| 📱 Mobile | < 576px | عمود واحد |
| 📱 Large Mobile | 576px - 768px | عمودين |
| 💻 Tablet | 768px - 992px | 3 أعمدة |
| 💻 Desktop | 992px - 1200px | 4 أعمدة |
| 🖥️ Large Desktop | > 1200px | 4+ أعمدة |

---

## 🌍 اللغات والدعم الدولي

### **اللغات المدعومة**
- 🇸🇦 العربية (افتراضي - RTL)
- 🇬🇧 الإنجليزية (LTR)

### **إدارة الترجمات**
```bash
# إنشاء ملفات الترجمة
python manage.py makemessages -l ar
python manage.py makemessages -l en

# تحديث الترجمات
python manage.py makemessages -a

# تجميع الترجمات
python manage.py compilemessages
```

### **الدول المدعومة افتراضيًا**
- 🇸🇦 السعودية (SA)
- 🇦🇪 الإمارات (AE)
- 🇪🇬 مصر (EG)
- 🇰🇼 الكويت (KW)
- 🇶🇦 قطر (QA)
- 🇧🇭 البحرين (BH)
- 🇴🇲 عُمان (OM)
- 🇯🇴 الأردن (JO)

---

## 🔒 الأمان

### **ممارسات الأمان المطبقة**

- ✅ **CSRF Protection**: جميع النماذج محمية
- ✅ **SQL Injection**: استخدام ORM فقط
- ✅ **XSS Protection**: تنظيف القوالب تلقائيًا
- ✅ **Session Security**: جلسات مشفرة وآمنة
- ✅ **Password Hashing**: تجزئة قوية للكلمات السرية
- ✅ **HTTPS Ready**: جاهز للإنتاج مع SSL
- ✅ **Environment Variables**: جميع الأسرار في `.env`
- ✅ **Rate Limiting**: يمكن تفعيله بسهولة
- ✅ **Input Validation**: تحقق من المدخلات في Backend

### **إعدادات الإنتاج**

في `settings/production.py`:
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 📊 نقاط نهاية API

| النهاية | الطريقة | الوصف | المعاملات |
|---------|---------|-------|------------|
| `/api/cart/add/` | POST | إضافة منتج للسلة | `item_id`, `item_name` |
| `/api/cart/remove/` | POST | إزالة منتج من السلة | `item_id` |
| `/api/wishlist/add/` | POST | إضافة منتج للمفضلة | `item_id`, `item_name` |
| `/api/wishlist/remove/` | POST | إزالة منتج من المفضلة | `item_id` |
| `/api/set-country/` | POST | تغيير الدولة | `country_code` |

### **مثال على الاستخدام**

```javascript
// إضافة منتج للسلة
fetch('/api/cart/add/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: 'item_id=123&item_name=منتج تجريبي'
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('تمت الإضافة بنجاح');
    }
});
```

---

## 🧰 التقنيات المستخدمة

### **الواجهة الأمامية**
| التقنية | الإصدار | الاستخدام |
|---------|---------|-----------|
| Bootstrap 5 RTL | 5.3.2 | إطار العمل الأساسي |
| Font Awesome | 6.4.2 | الأيقونات |
| Swiper.js | 11.0 | العروض المتحركة |
| GSAP | 3.12.2 | الرسوم المتحركة |
| Cairo Font | - | الخط العربي |

### **الواجهة الخلفية**
| التقنية | الإصدار | الاستخدام |
|---------|---------|-----------|
| Django | 5.0+ | إطار العمل الرئيسي |
| Python | 3.11+ | لغة البرمجة |
| PostgreSQL | 13+ | قاعدة البيانات |
| Pillow | - | معالجة الصور |
| python-dotenv | - | إدارة البيئة |

### **الجودة والأمان**
| الأداة | الاستخدام |
|--------|-----------|
| Ruff | فحص وتنسيق الكود |
| Bandit | فحص الأمان |
| DjLint | فحص القوالب |
| pre-commit | فحوصات تلقائية |
| coverage | قياس تغطية الاختبارات |

### **الأتمتة**
| الأداة | الاستخدام |
|--------|-----------|
| Makefile | أوامر سريعة |
| GitHub Actions | CI/CD |
| Docker | containerization |

---

## 📦 قيد التطوير

### **المرحلة التالية (Q1 2025)**
- [ ] 🔐 تسجيل دخول متعدد (Google, Facebook, Twitter)
- [ ] 💳 بوابات دفع متعددة (Stripe, PayPal, Moyasar)
- [ ] 📧 إشعارات البريد الإلكتروني
- [ ] 🔔 إشعارات دفع متصفح
- [ ] 📊 لوحة تحكم تحليلات
- [ ] 🏪 لوحة تحكم البائعين
- [ ] 💬 دردشة مباشرة (WebSocket)
- [ ] 📱 تطبيق موبايل (React Native)

### **المرحلة المتقدمة (Q2-Q3 2025)**
- [ ] 🤖 توصيات ذكية بالذكاء الاصطناعي
- [ ] 📦 تتبع الشحنات
- [ ] ⭐ نظام مراجعات متقدم
- [ ] 🎁 نظام كوبونات وخصومات
- [ ] 🔍 بحث متقدم مع فلاتر
- [ ] 📱 PWA (Progressive Web App)
- [ ] 🌐 API عامة للمطورين
- [ ] 🎨 Theme Builder للتخصيص

---

## 💡 نصائح التطوير

### **Best Practices**

1. **استخدم pre-commit**
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

2. **اكتب اختبارات**
   ```bash
   # لكل feature جديد
   python manage.py test main.tests.test_cart
   ```

3. **استخدم Type Hints**
   ```python
   def add_to_cart(request: HttpRequest) -> JsonResponse:
       pass
   ```

4. **وثّق الكود**
   ```python
   def complex_function():
       """
       شرح مفصل للدالة.

       Args:
           param1: وصف المعامل الأول

       Returns:
           وصف القيمة المرجعة
       """
       pass
   ```

5. **استخدم الإشارات (Signals)**
   ```python
   from django.db.models.signals import post_save
   from django.dispatch import receiver

   @receiver(post_save, sender=Order)
   def send_order_email(sender, instance, created, **kwargs):
       if created:
           # أرسل بريد إلكتروني
           pass
   ```

---

## 🐛 حل المشاكل الشائعة

### **المشكلة: السلة لا تتحدث**
**الحل:**
```python
# تأكد من وجود CSRF token في القالب
{% csrf_token %}

# تأكد من تفعيل Session middleware
'django.contrib.sessions.middleware.SessionMiddleware',
```

### **المشكلة: الرسوم المتحركة بطيئة**
**الحل:**
```javascript
// استخدم GPU acceleration
.my-element {
    transform: translateZ(0);
    will-change: transform;
}
```

### **المشكلة: التذييل مكسور على الموبايل**
**الحل:**
```bash
# امسح الكاش
python manage.py collectstatic --clear --noinput

# تأكد من تحديث CSS
```

### **المشكلة: الدول لا تظهر**
**الحل:**
```bash
# تأكد من تطبيق الهجرات
python manage.py migrate

# عبّئ الدول
python manage.py populate_countries
```

### **المشكلة: 403 Forbidden على POST**
**الحل:**
```html
<!-- أضف CSRF token -->
{% csrf_token %}

<!-- أو في JavaScript -->
headers: {
    'X-CSRFToken': getCookie('csrftoken')
}
```

---

## 🚀 النشر على الإنتاج

### **1. إعداد الخادم**
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install python3-pip python3-venv nginx postgresql
```

### **2. إعداد قاعدة البيانات**
```sql
CREATE DATABASE idrissimart;
CREATE USER idrissimart_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE idrissimart TO idrissimart_user;
```

### **3. إعداد Gunicorn**
```bash
pip install gunicorn

# إنشاء خدمة systemd
sudo nano /etc/systemd/system/idrissimart.service
```

### **4. إعداد Nginx**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **5. إعداد SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### **6. المتغيرات البيئية للإنتاج**
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/idrissimart
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 📚 الموارد والمراجع

### **التوثيق الرسمي**
- [Django Docs](https://docs.djangoproject.com/)
- [Bootstrap RTL Docs](https://getbootstrap.com/)
- [GSAP Docs](https://greensock.com/docs/)
- [Swiper Docs](https://swiperjs.com/)

### **دروس ومقالات**
- [Django Best Practices](https://djangobestpractices.com/)
- [Real Python Django Tutorials](https://realpython.com/tutorials/django/)
- [MDN Web Docs](https://developer.mozilla.org/)

### **المجتمع**
- [Django Forum](https://forum.djangoproject.com/)
- [Stack Overflow - Django](https://stackoverflow.com/questions/tagged/django)
- [Reddit - r/django](https://reddit.com/r/django)

---

## 🤝 المساهمة

نرحب بمساهماتكم! إليك كيفية المساهمة:

### **1. Fork المشروع**
```bash
git clone https://github.com/yourusername/idrissimart.git
cd idrissimart
```

### **2. إنشاء فرع جديد**
```bash
git checkout -b feature/amazing-feature
```

### **3. إجراء التغييرات**
```bash
# اكتب الكود
# اكتب الاختبارات
# حدّث التوثيق
```

### **4. التزام التغييرات**
```bash
git add .
git commit -m "إضافة ميزة رائعة"
```

### **5. رفع التغييرات**
```bash
git push origin feature/amazing-feature
```

### **6. فتح Pull Request**

---

## 📞 الدعم والتواصل

### **للدعم الفني**
- 📧 البريد: support@idrisimart.com
- 💬 Discord: [انضم إلى مجتمعنا](#)
- 📱 واتساب: +966 XX XXX XXXX

### **للاستفسارات التجارية**
- 📧 البريد: business@idrisimart.com
- 🌐 الموقع: https://idrisimart.com

### **وسائل التواصل الاجتماعي**
- 🐦 تويتر: [@idrisimart](#)
- 📘 فيسبوك: [Idrisi Mart](#)
- 📸 انستقرام: [@idrisimart](#)
- 💼 لينكد إن: [Idrisi Mart](#)

---

## 📜 الترخيص

هذا المشروع مرخص تحت **رخصة MIT** - انظر ملف [LICENSE](LICENSE) للتفاصيل.

```
MIT License

Copyright (c) 2025 Idrisi Mart

يُسمح بالاستخدام والنسخ والتعديل والتوزيع مع الحفاظ على حقوق النشر الأصلية.
```

---

## 💬 الشكر والتقدير

### **شكر خاص لـ:**
- 🙏 فريق Django على الإطار الرائع
- 🎨 مجتمع Bootstrap على التصميم
- ✨ GreenSock على GSAP المذهلة
- 💖 جميع المساهمين والداعمين

### **تم البناء باستخدام:**
- ❤️ الحب والشغف
- ☕ الكثير من القهوة
- 🌙 ساعات طويلة من الليل
- 🎯 الاهتمام بأدق التفاصيل

---

## 🌟 شعار إدريسي مارت

<div align="center">

### **"التسوق بسهولة، بثقة، وبأسلوب عصري"**

**إدريسي مارت** - منصتك الموثوقة للتجارة الإلكترونية

---

⭐ **إذا أعجبك المشروع، لا تنسى أن تمنحه نجمة على GitHub!** ⭐

[![Star on GitHub](https://img.shields.io/github/stars/yourusername/idrissimart?style=social)](https://github.com/yourusername/idrissimart)

</div>

---

<div align="center">

**النسخة:** 2.0.0
**آخر تحديث:** 2025
**صُنع بـ ❤️ في المملكة العربية السعودية**

[الرئيسية](#-إدريسي-مارت-idrissi-mart) • [المميزات](#-المميزات-الرئيسية) • [التثبيت](#-التثبيت-السريع-15-دقيقة) • [التوثيق](#-الموارد-والمراجع) • [المساهمة](#-المساهمة)

</div>
