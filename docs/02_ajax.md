# 🔌 دليل تطبيق AJAX الكامل

## 📋 نظرة عامة

تم تحديث جميع الميزات لتستخدم **AJAX** للتواصل مع الخادم بدون إعادة تحميل الصفحة.

---

## ✨ الميزات المحدثة

### 1. **محدد الدولة** 🌍
- ✅ إرسال AJAX إلى `/api/set-country/`
- ✅ حفظ الاختيار في Session وLocalStorage
- ✅ حالة تحميل أثناء الطلب
- ✅ إشعارات نجاح/خطأ

### 2. **سلة التسوق** 🛒
- ✅ إضافة منتج: `/api/cart/add/`
- ✅ إزالة منتج: `/api/cart/remove/`
- ✅ تحديث العداد تلقائياً
- ✅ رسوم متحركة عند الإضافة/الإزالة

### 3. **قائمة المفضلة** ❤️
- ✅ إضافة/إزالة: `/api/wishlist/add/` و `/api/wishlist/remove/`
- ✅ تبديل الأيقونة (♡ ↔ ♥)
- ✅ تحديث العداد تلقائياً
- ✅ حفظ الحالة

---

## 🔧 البنية التحتية

### **الملفات المطلوبة**

```
static/js/
├── main.js              # JavaScript الرئيسي (محدث)
└── cart-wishlist.js     # مساعد السلة والمفضلة (محدث)
```

### **نقاط النهاية API المطلوبة**

| النهاية | الطريقة | الوصف |
|---------|---------|-------|
| `/api/set-country/` | POST | تغيير الدولة |
| `/api/cart/add/` | POST | إضافة للسلة |
| `/api/cart/remove/` | POST | إزالة من السلة |
| `/api/wishlist/add/` | POST | إضافة للمفضلة |
| `/api/wishlist/remove/` | POST | إزالة من المفضلة |

---

## 📝 كيفية التطبيق

### **الخطوة 1: تحديث views.py**

تأكد من وجود جميع الـ Views:

```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Country

@require_POST
def set_country(request):
    """AJAX endpoint to set user's country"""
    country_code = request.POST.get('country_code')

    if country_code and Country.objects.filter(code=country_code, is_active=True).exists():
        request.session['selected_country'] = country_code
        return JsonResponse({
            'success': True,
            'message': 'تم تغيير الدولة بنجاح'
        })

    return JsonResponse({
        'success': False,
        'message': 'كود دولة غير صالح'
    }, status=400)

@require_POST
def add_to_cart(request):
    """Add item to cart"""
    item_id = request.POST.get('item_id')

    if not item_id:
        return JsonResponse({'success': False, 'message': 'معرف المنتج مطلوب'}, status=400)

    cart = request.session.get('cart', [])

    if item_id not in cart:
        cart.append(item_id)
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': 'تمت الإضافة بنجاح',
            'cart_count': len(cart)
        })

    return JsonResponse({
        'success': False,
        'message': 'المنتج موجود بالفعل في السلة'
    })

@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    item_id = request.POST.get('item_id')
    cart = request.session.get('cart', [])

    if item_id in cart:
        cart.remove(item_id)
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': 'تمت الإزالة بنجاح',
            'cart_count': len(cart)
        })

    return JsonResponse({
        'success': False,
        'message': 'المنتج غير موجود في السلة'
    })

@require_POST
def add_to_wishlist(request):
    """Add item to wishlist"""
    item_id = request.POST.get('item_id')

    if not item_id:
        return JsonResponse({'success': False, 'message': 'معرف المنتج مطلوب'}, status=400)

    wishlist = request.session.get('wishlist', [])

    if item_id not in wishlist:
        wishlist.append(item_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': 'تمت الإضافة للمفضلة',
            'wishlist_count': len(wishlist)
        })

    return JsonResponse({
        'success': False,
        'message': 'المنتج موجود بالفعل في المفضلة'
    })

@require_POST
def remove_from_wishlist(request):
    """Remove item from wishlist"""
    item_id = request.POST.get('item_id')
    wishlist = request.session.get('wishlist', [])

    if item_id in wishlist:
        wishlist.remove(item_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': 'تمت الإزالة من المفضلة',
            'wishlist_count': len(wishlist)
        })

    return JsonResponse({
        'success': False,
        'message': 'المنتج غير موجود في المفضلة'
    })
```

---

### **الخطوة 2: تحديث urls.py**

```python
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),

    # API endpoints
    path('api/set-country/', views.set_country, name='set_country'),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('api/wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
```

---

### **الخطوة 3: تحديث الملفات الثابتة**

استبدل الملفات التالية بالإصدارات المحدثة:

1. ✅ `static/js/main.js` - يحتوي على AJAX لمحدد الدولة
2. ✅ `static/js/cart-wishlist.js` - يحتوي على AJAX للسلة والمفضلة

---

### **الخطوة 4: تحديث base.html**

تأكد من تضمين الملفات بالترتيب الصحيح:

```html
{% load static %}

<!-- قبل </body> -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

<!-- JavaScript مخصص -->
<script src="{% static 'js/main.js' %}"></script>
<script src="{% static 'js/cart-wishlist.js' %}"></script>

{% if DEBUG %}
<script src="{% static 'js/test-utils.js' %}"></script>
{% endif %}
```

---

## 🎯 الاستخدام

### **في القوالب HTML**

#### **1. زر إضافة للسلة**
```html
<button class="btn btn-primary-custom"
        data-action="add-to-cart"
        data-item-id="{{ product.id }}"
        data-item-name="{{ product.name }}">
    <i class="fas fa-shopping-cart"></i> إضافة للسلة
</button>
```

#### **2. زر المفضلة**
```html
<button class="wishlist-btn"
        data-action="toggle-wishlist"
        data-item-id="{{ product.id }}"
        data-item-name="{{ product.name }}">
    <i class="far fa-heart"></i>
</button>
```

#### **3. محدد الدولة**
الكود موجود بالفعل في `_header.html` - لا حاجة للتغيير

---

### **في JavaScript**

#### **استدعاء مباشر:**
```javascript
// إضافة للسلة
CartWishlist.addToCart('123', 'اسم المنتج');

// إزالة من السلة
CartWishlist.removeFromCart('123', 'اسم المنتج');

// إضافة للمفضلة
CartWishlist.addToWishlist('456', 'اسم المنتج');

// تحديث العداد يدوياً
CartWishlist.updateBadgeCount('cart', 10);

// إظهار إشعار
CartWishlist.showNotification('رسالة نجاح', 'success');
CartWishlist.showNotification('رسالة خطأ', 'error');
```

---

## 🔍 الاختبار

### **1. اختبار محدد الدولة**

افتح Console وجرّب:
```javascript
// تغيير الدولة إلى مصر
localStorage.setItem('selectedCountry', 'EG');
location.reload();

// التحقق من الدولة المحفوظة
console.log(localStorage.getItem('selectedCountry'));
```

### **2. اختبار السلة**

```javascript
// إضافة منتج تجريبي
CartWishlist.addToCart('test-123', 'منتج تجريبي');

// التحقق من الاستجابة
// يجب أن ترى إشعار نجاح وتحديث العداد
```

### **3. اختبار المفضلة**

```javascript
// إضافة للمفضلة
CartWishlist.addToWishlist('test-456', 'منتج مفضل');

// إزالة من المفضلة
CartWishlist.removeFromWishlist('test-456', 'منتج مفضل');
```

### **4. اختبار شامل**

```javascript
// إذا قمت بإضافة test-utils.js
IdrissiTest.runAll();
```

---

## 🐛 حل المشاكل

### **المشكلة 1: خطأ 403 Forbidden**

**السبب:** CSRF token مفقود

**الحل:**
```html
<!-- تأكد من وجود CSRF token في base.html -->
{% csrf_token %}
```

### **المشكلة 2: العداد لا يتحدث**

**السبب:** Badge classes غير موجودة

**الحل:**
```html
<!-- تأكد من وجود الأيقونات في _header.html -->
<span class="badge-count cart-count">0</span>
<span class="badge-count wishlist-count">0</span>
```

### **المشكلة 3: الإشعارات لا تظهر**

**السبب:** GSAP غير محمّل

**الحل:**
```html
<!-- تأكد من تحميل GSAP قبل main.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
```

### **المشكلة 4: الدولة لا تُحفظ**

**السبب:** Session middleware غير مفعل

**الحل:**
```python
# في settings.py
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... باقي middleware
]
```

---

## 📊 تدفق البيانات

### **محدد الدولة:**
```
المستخدم ينقر على دولة
    ↓
JavaScript يرسل AJAX POST
    ↓
Django يحفظ في Session
    ↓
JSON Response
    ↓
تحديث الواجهة + إشعار
```

### **السلة/المفضلة:**
```
المستخدم ينقر على زر
    ↓
JavaScript يرسل AJAX POST
    ↓
Django يضيف/يزيل من Session
    ↓
JSON Response مع العدد الجديد
    ↓
تحديث Badge + إشعار + Custom Event
```

---

## 🎨 التخصيص

### **تغيير ألوان الإشعارات:**

في `cart-wishlist.js`:
```javascript
const colors = {
    success: 'linear-gradient(135deg, #your-color-1, #your-color-2)',
    error: 'linear-gradient(135deg, #your-color-1, #your-color-2)',
    info: 'linear-gradient(135deg, #your-color-1, #your-color-2)'
};
```

### **تغيير مدة الإشعار:**

```javascript
setTimeout(() => {
    // ... animate out
}, 3000);  // غيّر 3000 إلى المدة المطلوبة بالميلي ثانية
```

### **تغيير رسوم التحميل:**

```javascript
this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> النص المخصص';
```

---

## 🔐 أمان AJAX

### **الحماية المطبقة:**

1. ✅ **CSRF Token** على جميع طلبات POST
2. ✅ **Session Security** - البيانات محفوظة في Session
3. ✅ **Input Validation** - التحقق من المدخلات في Backend
4. ✅ **Error Handling** - معالجة الأخطاء في try/catch

### **نصائح إضافية:**

```python
# في views.py - أضف rate limiting
from django.views.decorators.cache import cache_page

@cache_page(60)
@require_POST
def add_to_cart(request):
    # ...
```

---

## 📈 الأداء

### **التحسينات المطبقة:**

- ✅ **Debouncing** على scroll events
- ✅ **Lazy Loading** للصور
- ✅ **GPU Acceleration** للرسوم المتحركة
- ✅ **Async/Await** لطلبات AJAX
- ✅ **Event Delegation** حيث ممكن

### **قياس الأداء:**

```javascript
// في Console
IdrissiTest.checkPerformance();
```

---

## ✅ قائمة التحقق

قبل النشر، تأكد من:

- [ ] جميع نقاط النهاية API تعمل
- [ ] CSRF token موجود
- [ ] Session middleware مفعل
- [ ] الإشعارات تظهر بشكل صحيح
- [ ] العدادات تتحدث
- [ ] الرسوم المتحركة سلسة
- [ ] لا توجد أخطاء في Console
- [ ] التجربة جيدة على Mobile
- [ ] جميع المتصفحات مدعومة

---

## 🎉 النتيجة

الآن لديك نظام AJAX كامل يعمل بدون إعادة تحميل الصفحة!

**الميزات:**
- ⚡ سرعة فائقة
- 🎨 رسوم متحركة سلسة
- 💬 إشعارات فورية
- 📱 متجاوب بالكامل
- 🔒 آمن ومحمي

---

**تم بناؤه بـ ❤️ لمنصة إدريسي مارت**
