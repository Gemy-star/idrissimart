# Home Slider Implementation

## Overview
تم استبدال Hero Section الثابت بنظام سلايدر ديناميكي باستخدام Swiper.js

## التغييرات المنفذة

### 1. **نموذج HomeSlider الجديد** (`content/models.py`)

```python
class HomeSlider(models.Model):
    """Model for homepage slider/carousel"""

    # Fields:
    - title / title_ar
    - subtitle / subtitle_ar
    - description / description_ar (CKEditor)
    - image (ImageField)
    - button_text / button_text_ar
    - button_url
    - background_color (hex color)
    - text_color (hex color)
    - is_active (BooleanField)
    - order (IntegerField)
    - created_at / updated_at
```

**المميزات:**
✅ دعم كامل للغتين (عربي/إنجليزي)
✅ صور عالية الدقة (1920x800px recommended)
✅ ألوان خلفية ونصوص قابلة للتخصيص
✅ ترتيب الشرائح
✅ تفعيل/إلغاء تفعيل الشرائح

### 2. **الهجرة التلقائية للبيانات**

**Migration Files:**
- `0008_homeslider.py` - إنشاء النموذج
- `0009_migrate_hero_to_slider.py` - نقل بيانات Hero القديم

**ما تم نقله:**
```python
Hero Section → Slider #1
- hero_title → title
- hero_title_ar → title_ar
- hero_subtitle → subtitle
- hero_subtitle_ar → subtitle_ar
- hero_image → image
- hero_button_text → button_text
- hero_button_text_ar → button_text_ar
- hero_button_url → button_url
```

### 3. **Admin Interface** (`content/admin.py`)

```python
@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title_display', 'is_active', 'order', 'created_at']
    list_editable = ['is_active', 'order']

    Actions:
    - activate_slides
    - deactivate_slides
```

**المميزات:**
✅ معاينة الصور في القائمة
✅ تحرير سريع للحالة والترتيب
✅ إجراءات جماعية
✅ مجموعات حقول منظمة

### 4. **Context Processor** (`content/context_processors.py`)

```python
def home_sliders(request):
    return {
        "home_sliders": HomeSlider.objects.filter(is_active=True).order_by("order")
    }
```

تم إضافته في `settings/common.py`:
```python
"content.context_processors.home_sliders",
```

### 5. **قالب Swiper** (`templates/partials/_home_slider.html`)

**المميزات:**
- ✅ Swiper.js integration
- ✅ تأثير fade crossfade
- ✅ Auto-play (5 seconds)
- ✅ Navigation arrows
- ✅ Pagination dots
- ✅ دعم الثيم الداكن
- ✅ متجاوب بالكامل (Responsive)
- ✅ عناصر زخرفية متحركة
- ✅ تأثيرات AOS للحركة

**Swiper Configuration:**
```javascript
{
    loop: true,
    autoplay: { delay: 5000 },
    speed: 1000,
    effect: 'fade',
    fadeEffect: { crossFade: true },
    pagination: { clickable: true },
    navigation: { nextEl, prevEl }
}
```

## الاستخدام

### في الصفحة الرئيسية:

```django
{% include 'partials/_home_slider.html' %}
```

### إضافة شرائح جديدة:

1. Admin Panel → Content → Home Sliders
2. Click "Add Home Slider"
3. Fill in the data:
   - **Title** (AR/EN)
   - **Subtitle** (AR/EN) - optional
   - **Description** (AR/EN) - optional
   - **Image** (1920x800px recommended)
   - **Button** text and URL - optional
   - **Colors** (background & text)
   - **Order** number
   - **Active** checkbox

### أمثلة على استخدامات الشرائح:

1. **Welcome Slide**
   - Title: "مرحباً بك في إدريسي مارت"
   - Subtitle: "سوقك الموثوق للإعلانات المبوبة"
   - Button: "تصفح الإعلانات" → /classifieds/

2. **Feature Promotion**
   - Title: "أعلن مجاناً"
   - Description: "انشر إعلانك واصل إلى آلاف المشترين"
   - Button: "نشر إعلان" → /classifieds/create/

3. **Special Offer**
   - Title: "عروض خاصة"
   - Description: "باقات مميزة بأسعار تنافسية"
   - Button: "اشترك الآن" → /packages/

## التصميم والألوان

### الألوان الافتراضية:
```css
background_color: #4B315E (purple gradient)
text_color: #FFFFFF (white)
```

### عناصر التصميم:
- Gradient buttons
- Floating animations
- Decorative circles
- Glass-morphism effects
- Smooth transitions

### Responsive Breakpoints:
```css
Desktop: 600px height
Tablet: 550px height
Mobile: 500px height
```

## الملفات المتأثرة

### Created:
1. ✅ `content/models.py` - HomeSlider model
2. ✅ `content/admin.py` - Admin interface
3. ✅ `content/context_processors.py` - Context processor
4. ✅ `content/migrations/0008_homeslider.py`
5. ✅ `content/migrations/0009_migrate_hero_to_slider.py`
6. ✅ `templates/partials/_home_slider.html`

### Modified:
1. ✅ `idrissimart/settings/common.py` - Added context processor

## الخطوات التالية

### لاستبدال Hero Section في الصفحة الرئيسية:

1. فتح `templates/pages/home.html` (أو الملف المناسب)
2. استبدال قسم Hero القديم بـ:
   ```django
   {% include 'partials/_home_slider.html' %}
   ```

### لإزالة حقول Hero من HomePage (اختياري):

يمكن إنشاء migration لإزالة الحقول القديمة:
```python
# Future migration
operations = [
    migrations.RemoveField(model_name='homepage', name='hero_title'),
    migrations.RemoveField(model_name='homepage', name='hero_title_ar'),
    # ... rest of hero fields
]
```

⚠️ **ملاحظة:** يُنصح بالانتظار والتأكد من عمل السلايدر بشكل صحيح قبل إزالة الحقول القديمة.

## المزايا

✅ **ديناميكية:** إضافة/تعديل شرائح بدون كود
✅ **متعددة اللغات:** دعم كامل للعربية والإنجليزية
✅ **سهلة الإدارة:** واجهة admin بسيطة
✅ **احترافية:** تصميم حديث مع Swiper
✅ **متجاوبة:** تعمل على جميع الأجهزة
✅ **قابلة للتخصيص:** ألوان وترتيب مرن
✅ **محسّنة للأداء:** صور محسّنة وأكواد نظيفة

## الخلاصة

تم بنجاح:
1. ✅ إنشاء نموذج HomeSlider
2. ✅ نقل بيانات Hero القديم تلقائياً
3. ✅ إضافة واجهة Admin كاملة
4. ✅ تطبيق Swiper.js للسلايدر
5. ✅ دعم الثيمات (فاتح/داكن)
6. ✅ تصميم متجاوب بالكامل

الآن يمكن للمسؤولين إدارة شرائح الصفحة الرئيسية بسهولة من لوحة التحكم! 🎉

---
**تاريخ التنفيذ:** ديسمبر 2025
