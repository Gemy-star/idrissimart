# Theme-Based Logo System Implementation

## Overview
تم إضافة نظام شعارات متعدد يدعم الوضع الفاتح والداكن وشعار مصغر للـ Loader.

## Changes Made

### 1. Model Updates (`content/site_config.py`)

#### New Fields Added:
```python
logo_light = models.ImageField(
    verbose_name="شعار الموقع - الوضع الفاتح",
    help_text="شعار الموقع الذي يظهر في الوضع الفاتح (Light Mode). إذا تُرك فارغاً، سيُستخدم الشعار الافتراضي"
)

logo_dark = models.ImageField(
    verbose_name="شعار الموقع - الوضع الداكن",
    help_text="شعار الموقع الذي يظهر في الوضع الداكن (Dark Mode). إذا تُرك فارغاً، سيُستخدم الشعار الافتراضي"
)

logo_mini = models.ImageField(
    verbose_name="شعار مصغر - Loader",
    help_text="شعار مصغر يظهر في صفحات التحميل (Loader). إذا تُرك فارغاً، سيُستخدم الشعار الافتراضي"
)
```

#### Helper Methods:
```python
def get_logo_for_theme(theme='light'):
    """Get appropriate logo based on theme (light/dark)"""
    
def get_loader_logo():
    """Get logo for loader/spinner"""
    
def get_logo_url(theme='light'):
    """Get logo URL based on theme"""
    
def get_loader_logo_url():
    """Get loader logo URL"""
```

### 2. Admin Updates (`content/admin.py`)

تم إضافة قسم جديد "شعارات الموقع" في صفحة الإدارة يحتوي على:
- الشعار الافتراضي (logo)
- شعار الوضع الفاتح (logo_light)
- شعار الوضع الداكن (logo_dark)
- الشعار المصغر (logo_mini)

### 3. Template Tags (`main/templatetags/idrissimart_tags.py`)

#### New Template Tags:

##### Get Site Logo by Theme:
```django
{% load idrissimart_tags %}

<!-- Get light theme logo -->
{% get_site_logo 'light' %}

<!-- Get dark theme logo -->
{% get_site_logo 'dark' %}

<!-- Get loader logo -->
{% get_site_logo 'loader' %}

<!-- Get default logo -->
{% get_site_logo %}
```

##### Get Loader Logo:
```django
{% load idrissimart_tags %}

<!-- Get loader/mini logo -->
{% get_loader_logo %}
```

### 4. Context Processor Updates (`content/context_processors.py`)

Added helper functions accessible in all templates:
```python
# Available in all templates via context
{{ site_config.get_logo_url }}
{{ site_config.get_loader_logo_url }}
```

## Usage Examples

### Example 1: Logo in Navbar with Theme Support
```django
{% load idrissimart_tags %}

<nav class="navbar">
    <!-- Light theme logo (visible in light mode) -->
    <img src="{% get_site_logo 'light' %}" 
         alt="Logo" 
         class="navbar-logo d-none d-light-block">
    
    <!-- Dark theme logo (visible in dark mode) -->
    <img src="{% get_site_logo 'dark' %}" 
         alt="Logo" 
         class="navbar-logo d-none d-dark-block">
</nav>
```

### Example 2: Loader/Spinner with Mini Logo
```django
{% load idrissimart_tags %}

<div class="loader-container">
    <img src="{% get_loader_logo %}" 
         alt="Loading..." 
         class="spinner-logo">
</div>
```

### Example 3: Using Model Methods Directly
```django
<!-- In template with site_config available -->
<img src="{{ site_config.get_logo_url }}" alt="Default Logo">
<img src="{{ site_config.get_logo_for_theme.light.url }}" alt="Light Logo">
<img src="{{ site_config.get_logo_for_theme.dark.url }}" alt="Dark Logo">
<img src="{{ site_config.get_loader_logo.url }}" alt="Loader Logo">
```

### Example 4: JavaScript Theme Switching
```html
<script>
const lightLogo = "{% get_site_logo 'light' %}";
const darkLogo = "{% get_site_logo 'dark' %}";

function updateLogo(theme) {
    const logoImg = document.querySelector('.navbar-logo');
    logoImg.src = theme === 'dark' ? darkLogo : lightLogo;
}

// Listen to theme changes
document.addEventListener('themeChanged', (e) => {
    updateLogo(e.detail.theme);
});
</script>
```

## CSS for Theme-Based Display

```css
/* Show light logo only in light mode */
[data-theme='light'] .navbar-logo-dark {
    display: none !important;
}

/* Show dark logo only in dark mode */
[data-theme='dark'] .navbar-logo-light {
    display: none !important;
}

/* Loader logo animation */
.spinner-logo {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

## Migration

Migration file created: `content/migrations/0030_add_theme_logos.py`

To apply:
```bash
poetry run python manage.py migrate content
```

## Fallback Behavior

- إذا لم يتم رفع `logo_light` → يستخدم `logo` الافتراضي
- إذا لم يتم رفع `logo_dark` → يستخدم `logo` الافتراضي
- إذا لم يتم رفع `logo_mini` → يستخدم `logo` الافتراضي

## Admin Interface

في صفحة إعدادات الموقع (`/admin/content/siteconfiguration/`):

1. **قسم "شعارات الموقع"** يحتوي على:
   - الشعار الافتراضي
   - شعار الوضع الفاتح
   - شعار الوضع الداكن
   - الشعار المصغر

2. كل حقل له وصف توضيحي يشرح الاستخدام

3. الشعار الافتراضي يُستخدم كـ fallback إذا لم يتم رفع الشعارات الأخرى

## Benefits

✅ **Theme Support**: شعارات منفصلة للوضع الفاتح والداكن
✅ **Performance**: شعار مصغر خاص للـ loaders
✅ **Flexibility**: استخدام الشعار الافتراضي كـ fallback تلقائي
✅ **Easy to Use**: Template tags بسيطة وواضحة
✅ **Backward Compatible**: لا يؤثر على الشعار الموجود حالياً
