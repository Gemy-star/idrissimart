# إصلاح محاذاة كارت المدونات حسب اللغة

## المشكلة
كارت المدونات في الصفحة الرئيسية لم تكن تتبع اتجاه اللغة بشكل صحيح. في اللغة العربية (RTL) يجب أن تكون المحاذاة لليمين، وفي الإنجليزية (LTR) لليسار.

## الحل
تم إضافة دعم كامل لـ RTL/LTR في:
1. إعدادات Swiper Slider
2. CSS للـ wrapper والكاردات
3. محاذاة المحتوى داخل الكاردات (عناوين، نصوص، أيقونات)

## الملفات المعدلة

### 1. templates/pages/home.html

#### تحديث إعدادات Swiper
```javascript
// السطر ~379-417
const isRTL = document.documentElement.dir === 'rtl' || document.body.dir === 'rtl';

new Swiper('.home-blogs-swiper', {
    slidesPerView: 2,
    spaceBetween: 15,
    loop: hasEnoughSlides,
    rtl: isRTL, // Enable RTL support
    autoplay: hasEnoughSlides ? {
        delay: 5000,
        disableOnInteraction: false,
        pauseOnMouseEnter: true,
    } : false,
    speed: 800,
    breakpoints: {
        // ... breakpoints
    }
});
```

**التغييرات:**
- إضافة اكتشاف تلقائي لاتجاه الصفحة (RTL/LTR)
- تمرير خاصية `rtl` إلى Swiper
- Log message يوضح حالة RTL

### 2. static/css/style.css

#### A. Swiper Container RTL Support (السطر ~9787-9807)
```css
.home-blogs-swiper {
  padding-bottom: 50px;
  direction: inherit; /* Inherit direction from parent */
}

/* RTL Support for Blog Cards Alignment */
[dir="rtl"] .home-blogs-swiper .swiper-wrapper {
  direction: rtl;
  text-align: right;
}

[dir="ltr"] .home-blogs-swiper .swiper-wrapper {
  direction: ltr;
  text-align: left;
}

/* Ensure blog cards content follows language direction */
.home-blogs-swiper .blog-post-card {
  direction: inherit;
  text-align: inherit;
}
```

#### B. Blog Footer Info Structure (السطر ~3910-3927)
```css
.blog-post-card .blog-footer-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.blog-post-card .blog-stats {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.blog-post-card .blog-stats small {
    display: flex;
    align-items: center;
    gap: 0.35rem;
}
```

#### C. Card Content RTL/LTR Alignment (السطر ~4051-4093)
```css
/* RTL/LTR Support for Blog Card Content Alignment */
[dir="rtl"] .blog-post-card .card-body,
[dir="rtl"] .blog-post-card .card-footer {
    text-align: right;
}

[dir="ltr"] .blog-post-card .card-body,
[dir="ltr"] .blog-post-card .card-footer {
    text-align: left;
}

/* Blog Tags Alignment */
[dir="rtl"] .blog-post-card .blog-tags {
    justify-content: flex-start;
    flex-wrap: wrap;
}

[dir="ltr"] .blog-post-card .blog-tags {
    justify-content: flex-start;
    flex-wrap: wrap;
}

/* Blog Footer Info Alignment */
[dir="rtl"] .blog-post-card .blog-footer-info {
    direction: rtl;
}

[dir="ltr"] .blog-post-card .blog-footer-info {
    direction: ltr;
}

/* Icon Spacing based on direction */
[dir="rtl"] .blog-post-card .blog-author-details small i {
    margin-left: 0.25rem;
    margin-right: 0;
}

[dir="ltr"] .blog-post-card .blog-author-details small i {
    margin-right: 0.25rem;
    margin-left: 0;
}
```

## كيفية عمل الحل

### 1. اكتشاف اتجاه اللغة
```javascript
const isRTL = document.documentElement.dir === 'rtl' || document.body.dir === 'rtl';
```
يتحقق من attribute `dir` في HTML أو Body element

### 2. تطبيق RTL على Swiper
```javascript
rtl: isRTL
```
Swiper يعكس اتجاه السلايدات تلقائياً عند تفعيل RTL

### 3. CSS Selectors بناءً على Direction
```css
[dir="rtl"] .element { /* RTL styles */ }
[dir="ltr"] .element { /* LTR styles */ }
```

## العناصر المحاذاة

### ✅ Swiper Container
- اتجاه السلايدات (يمين → يسار في RTL)
- زر التالي والسابق (يتبدل تلقائياً)

### ✅ Blog Card Body
- العنوان
- النص الوصفي
- Tags

### ✅ Blog Card Footer
- معلومات الكاتب (author + date)
- الإحصائيات (views + likes)
- الأيقونات والمسافات

### ✅ Icons Spacing
```
RTL: [Icon] نص    (الأيقونة على اليمين)
LTR: [Icon] Text  (الأيقونة على اليسار)
```

## النتيجة

### 🇸🇦 في اللغة العربية (RTL)
```
←←←                     [كارد 4] [كارد 3] [كارد 2] [كارد 1]
محاذاة لليمين
```

### 🇺🇸 في اللغة الإنجليزية (LTR)
```
[Card 1] [Card 2] [Card 3] [Card 4]                     →→→
Left aligned
```

## اختبار التحديثات

1. **التبديل بين اللغات:**
   ```
   - افتح الصفحة الرئيسية باللغة العربية
   - تحقق من محاذاة الكاردات لليمين
   - بدّل إلى الإنجليزية
   - تحقق من محاذاة الكاردات لليسار
   ```

2. **التحقق من المحتوى الداخلي:**
   ```
   - العناوين محاذاة حسب اللغة
   - الأيقونات في الموضع الصحيح
   - النصوص واضحة ومقروءة
   - Stats footer محاذاة صحيحة
   ```

3. **Responsive Testing:**
   ```
   - Desktop (4 cards)
   - Tablet (3 cards)
   - Mobile (2 cards)
   ```

## ملاحظات تقنية

### Swiper RTL Mode
عند تفعيل `rtl: true`:
- السلايدات تبدأ من اليمين
- Navigation buttons تتبدل تلقائياً
- Pagination يظهر من اليمين لليسار
- Transform values معكوسة

### CSS Direction Inheritance
```css
direction: inherit;
text-align: inherit;
```
يضمن أن العناصر الفرعية ترث الاتجاه من الـ parent

### Flexbox في RTL
```css
justify-content: space-between;
```
يعمل بشكل صحيح في كلا الاتجاهين دون تعديل

## التوافقية
✅ جميع المتصفحات الحديثة
✅ Mobile Safari
✅ Chrome/Edge
✅ Firefox
✅ Samsung Internet

---
**تاريخ التحديث**: 9 يناير 2026
**المطور**: AI Assistant
**رقم المراجعة**: 1.0
