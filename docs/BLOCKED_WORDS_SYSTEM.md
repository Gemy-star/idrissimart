# نظام حظر الكلمات في أسماء المستخدمين

## نظرة عامة

تم إضافة نظام شامل لحظر الكلمات غير المسموحة في أسماء المستخدمين لحماية الموقع من:
1. استخدام كلمات محجوزة للنظام (admin, moderator, إلخ)
2. استخدام اسم الموقع أو علامته التجارية
3. استخدام كلمات مسيئة أو غير لائقة
4. استخدام محتوى إباحي أو جنسي

## الكلمات المحظورة

### 1. الكلمات المحجوزة (Reserved Words)
- **متعلقة بالإدارة**: admin, ادمن, أدمن, مدير, مشرف, administrator, moderator
- **اسم الموقع**: idrissimart, إدريسي مارت, ادريسي مارت, إدريسيمارت, idrissi, إدريسي
- **أدوار النظام**: root, superuser, system, staff, support, دعم, webmaster, owner, مالك
- **اختلافات بالأرقام**: adm1n, adm!n, @dmin, 4dmin

### 2. الكلمات المسيئة (Offensive Words)
- كلمات عربية مسيئة
- كلمات إنجليزية مسيئة
- محتوى جنسي/إباحي (عربي وإنجليزي)
- خطاب الكراهية
- كلمات متعلقة بالاحتيال والقمار

## آلية العمل

### 1. التحقق في نموذج التسجيل
```python
# في main/forms.py - RegistrationForm
def clean_username(self):
    from main.blocked_words import is_username_allowed

    username = self.cleaned_data.get("username").lower()

    # التحقق من الكلمات المحظورة
    is_allowed, error_message = is_username_allowed(username)
    if not is_allowed:
        raise ValidationError(error_message)

    # التحقق من التكرار
    if User.objects.filter(username=username).exists():
        raise ValidationError(_("اسم المستخدم مستخدم من قبل"))

    return username
```

### 2. التحقق في نموذج المستخدم (Model Level)
```python
# في main/models.py - User Model
def clean(self):
    from django.core.exceptions import ValidationError
    from main.blocked_words import is_username_allowed

    super().clean()

    if self.username:
        is_allowed, error_message = is_username_allowed(self.username)
        if not is_allowed:
            raise ValidationError({'username': error_message})

def save(self, *args, **kwargs):
    self.full_clean()  # يستدعي clean() تلقائياً
    super().save(*args, **kwargs)
```

### 3. التطبيع (Normalization)
النظام يقوم بتطبيع النص قبل الفحص:
- تحويل الأحرف للصغيرة (lowercase)
- إزالة المسافات
- إزالة الشرطات السفلية (_)
- إزالة الشرطات (-)
- إزالة النقاط (.)

هذا يضمن اكتشاف المحاولات الملتوية مثل:
- `ad_min` → `admin`
- `ad-min` → `admin`
- `ad.min` → `admin`
- `A D M I N` → `admin`

## الدوال المتاحة

### 1. `is_username_allowed(username)`
التحقق من السماح باسم المستخدم

**المعاملات:**
- `username` (str): اسم المستخدم المراد فحصه

**الإرجاع:**
- `tuple`: (is_allowed: bool, error_message: str)

**مثال:**
```python
from main.blocked_words import is_username_allowed

is_allowed, message = is_username_allowed("admin123")
if not is_allowed:
    print(message)  # "الاسم يحتوي على كلمة محجوزة: admin"
```

### 2. `contains_blocked_word(text, check_offensive=True, check_reserved=True)`
فحص نص لوجود كلمات محظورة

**المعاملات:**
- `text` (str): النص المراد فحصه
- `check_offensive` (bool): فحص الكلمات المسيئة
- `check_reserved` (bool): فحص الكلمات المحجوزة

**الإرجاع:**
- `tuple`: (is_blocked: bool, reason: str)

**مثال:**
```python
from main.blocked_words import contains_blocked_word

is_blocked, reason = contains_blocked_word(
    "myusername_admin",
    check_offensive=True,
    check_reserved=True
)
```

### 3. `clean_text_content(text)`
فحص محتوى نصي (للإعلانات، التعليقات، إلخ)

**المعاملات:**
- `text` (str): المحتوى المراد فحصه

**الإرجاع:**
- `tuple`: (is_clean: bool, issues: list)

**مثال:**
```python
from main.blocked_words import clean_text_content

is_clean, issues = clean_text_content("محتوى الإعلان هنا")
if not is_clean:
    for issue in issues:
        print(issue)
```

## أمثلة الاستخدام

### مثال 1: التحقق قبل إنشاء حساب
```python
username = request.POST.get('username')
is_allowed, message = is_username_allowed(username)

if not is_allowed:
    messages.error(request, message)
    return redirect('register')
```

### مثال 2: التحقق من محتوى الإعلان
```python
ad_content = form.cleaned_data['description']
is_clean, issues = clean_text_content(ad_content)

if not is_clean:
    for issue in issues:
        form.add_error('description', issue)
```

### مثال 3: التحقق في API
```python
from rest_framework.decorators import api_view
from main.blocked_words import is_username_allowed

@api_view(['POST'])
def register_api(request):
    username = request.data.get('username')
    is_allowed, message = is_username_allowed(username)

    if not is_allowed:
        return Response({
            'error': message
        }, status=400)
```

## إضافة كلمات محظورة جديدة

لإضافة كلمات محظورة جديدة، قم بتحرير `main/blocked_words.py`:

```python
# في RESERVED_WORDS لإضافة كلمات محجوزة
RESERVED_WORDS = [
    # ... الكلمات الموجودة
    'newword',  # إضافة كلمة جديدة
    'كلمة_جديدة',
]

# في OFFENSIVE_WORDS لإضافة كلمات مسيئة
OFFENSIVE_WORDS = [
    # ... الكلمات الموجودة
    'badword',
    'كلمة_سيئة',
]
```

## الاختبار

تم توفير ملف اختبار: `test_blocked_words.py`

**تشغيل الاختبار:**
```bash
python manage.py shell < test_blocked_words.py
```

أو:
```bash
python test_blocked_words.py
```

## الحماية المتعددة الطبقات

النظام يوفر حماية على 3 مستويات:

1. **Form Level** (`main/forms.py`):
   - يتم الفحص عند إدخال البيانات في النموذج
   - رسائل خطأ واضحة للمستخدم

2. **Model Level** (`main/models.py`):
   - يتم الفحص قبل الحفظ في قاعدة البيانات
   - حماية ضد التعديلات المباشرة

3. **Validation Utils** (`main/blocked_words.py`):
   - دوال قابلة لإعادة الاستخدام
   - يمكن استخدامها في أي مكان بالمشروع

## ملاحظات مهمة

1. **حساسية الأحرف**: النظام غير حساس لحالة الأحرف (case-insensitive)
2. **التطبيع التلقائي**: يتم إزالة المسافات والرموز قبل الفحص
3. **القوائم قابلة للتوسع**: يمكن إضافة كلمات جديدة بسهولة
4. **الأداء**: الفحص سريع ولا يؤثر على أداء التطبيق
5. **متعدد اللغات**: يدعم العربية والإنجليزية

## التحديثات المستقبلية

يمكن إضافة:
- قاعدة بيانات للكلمات المحظورة (بدلاً من القوائم الثابتة)
- واجهة إدارية لإضافة/حذف الكلمات
- تصنيفات مختلفة للكلمات المحظورة
- تقارير عن محاولات استخدام كلمات محظورة
- نظام تعلم آلي لاكتشاف كلمات جديدة

## الملفات المعدلة

1. ✅ `main/blocked_words.py` - قوائم الكلمات ودوال الفحص (جديد)
2. ✅ `main/forms.py` - التحقق في نموذج التسجيل
3. ✅ `main/models.py` - التحقق على مستوى النموذج
4. ✅ `test_blocked_words.py` - اختبارات التحقق (جديد)
5. ✅ `docs/BLOCKED_WORDS_SYSTEM.md` - هذا الملف (جديد)
