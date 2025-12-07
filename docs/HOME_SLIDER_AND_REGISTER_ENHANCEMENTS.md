# Home Slider & Registration Page Enhancements

## Date: December 7, 2025

## Overview
Enhanced the home slider to properly handle HTML entities and improved the registration page with better UI/UX for account type information and reCAPTCHA verification.

---

## 1. Custom Template Filter for HTML Entity Cleaning

### File: `main/templatetags/string_filters.py`

Added a new `clean_html` filter to properly handle HTML entities and clean content:

```python
@register.filter(name='clean_html')
def clean_html(value):
    """
    Remove HTML tags and decode HTML entities like &nbsp;, &lt;, etc.
    """
    if not value:
        return value

    # First decode HTML entities like &nbsp; &lt; &gt;
    value = html.unescape(value)

    # Remove HTML tags
    value = re.sub(r'<[^>]+>', '', value)

    # Replace multiple spaces with single space
    value = re.sub(r'\s+', ' ', value)

    # Strip leading/trailing whitespace
    return value.strip()
```

**Features:**
- Decodes HTML entities (`&nbsp;`, `&lt;`, `&gt;`, etc.)
- Removes HTML tags
- Normalizes whitespace
- Trims leading/trailing spaces

---

## 2. Home Slider Updates

### File: `templates/partials/_home_slider.html`

**Changes:**
1. Added `string_filters` to template tags: `{% load i18n static string_filters %}`
2. Replaced `striptags|safe` with `clean_html` filter for subtitles:

```django
{% if slide.get_subtitle %}
<p class="hero-subtitle" data-aos="fade-up" data-aos-delay="100">
    {% if LANGUAGE_CODE == 'ar' %}
        {{ slide.subtitle_ar|default:slide.subtitle|clean_html }}
    {% else %}
        {{ slide.subtitle|clean_html }}
    {% endif %}
</p>
{% endif %}
```

**Benefits:**
- Properly displays subtitle text without HTML entities showing
- Removes unwanted HTML tags
- Cleaner text rendering

---

## 3. Registration Page - Account Type Alert Enhancement

### File: `templates/pages/register.html`

**Old Design:**
```html
<div class="alert alert-info mb-4" role="alert">
    <i class="fas fa-info-circle me-2"></i>
    <strong>نوع الحساب:</strong> مستخدم قياسي
    <br>
    <small>يمكنك الترقية إلى حساب ناشر لاحقاً...</small>
</div>
```

**New Design:**
```html
<div class="alert alert-primary mb-4 border-0 shadow-sm" role="alert"
     style="background: linear-gradient(135deg, rgba(13, 110, 253, 0.1) 0%, rgba(13, 110, 253, 0.05) 100%);
            border-right: 4px solid var(--primary-color) !important;">
    <div class="d-flex align-items-start gap-3">
        <div class="flex-shrink-0">
            <div class="rounded-circle bg-primary bg-opacity-10 p-2"
                 style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                <i class="fas fa-user-circle text-primary" style="font-size: 1.2rem;"></i>
            </div>
        </div>
        <div class="flex-grow-1">
            <h6 class="alert-heading mb-2 fw-bold" style="color: var(--primary-color);">
                <i class="fas fa-info-circle me-1"></i>
                نوع الحساب: <span class="badge bg-primary">مستخدم قياسي</span>
            </h6>
            <p class="mb-0 small" style="line-height: 1.6;">
                <i class="fas fa-arrow-up me-1" style="color: var(--primary-color);"></i>
                يمكنك الترقية إلى حساب ناشر لاحقاً...
            </p>
        </div>
    </div>
</div>
```

**Improvements:**
- ✅ Gradient background for modern look
- ✅ Right border accent (4px solid primary color)
- ✅ Circular icon badge with user icon
- ✅ Badge for account type ("مستخدم قياسي")
- ✅ Better visual hierarchy with flex layout
- ✅ Shadow for depth
- ✅ Icon indicators for upgrade path
- ✅ Theme-aware using CSS variables

---

## 4. Google reCAPTCHA Enhancements

### File: `main/forms.py`

**Updated Error Messages:**

```python
captcha = ReCaptchaField(
    widget=ReCaptchaV2Checkbox(
        attrs={
            "data-theme": "light",
            "data-size": "normal",
        }
    ),
    label="",
    error_messages={
        "required": _("⚠️ يرجى إكمال التحقق من reCAPTCHA للتأكد من أنك لست روبوت"),
        "invalid": _("❌ فشل التحقق من reCAPTCHA. يرجى المحاولة مرة أخرى أو تحديث الصفحة"),
    },
)
```

**Changes:**
- Added emoji icons (⚠️ for required, ❌ for invalid)
- Clearer, more professional Arabic messages
- Removed confusing debug text
- Added empty label to avoid duplication

### File: `templates/pages/register.html`

**Enhanced reCAPTCHA Section:**

```html
<div class="form-group">
    <div class="d-flex align-items-center gap-2 mb-2">
        <i class="fas fa-shield-alt text-success"></i>
        <label class="form-label mb-0 fw-bold">التحقق الأمني</label>
    </div>
    <div class="p-3 bg-light rounded-3 d-inline-block"
         style="border: 2px solid var(--border-color);">
        {{ form.captcha }}
    </div>
    {% if form.captcha.errors %}
        <div class="alert alert-danger mt-2 mb-0" role="alert">
            <i class="fas fa-exclamation-triangle me-1"></i>
            {{ form.captcha.errors.0 }}
        </div>
    {% endif %}
    <small class="text-muted d-block mt-2">
        <i class="fas fa-info-circle me-1"></i>
        يرجى تحديد المربع أعلاه للتحقق من أنك إنسان وليس روبوت
    </small>
</div>
```

**Improvements:**
- ✅ Shield icon with "التحقق الأمني" label
- ✅ Light background box with border for reCAPTCHA widget
- ✅ Better error display with alert styling
- ✅ Helpful instruction text below
- ✅ Icons for visual cues
- ✅ Responsive design

---

## Testing Checklist

### Home Slider
- [ ] HTML entities (like `&nbsp;`) no longer visible in subtitles
- [ ] Arabic and English subtitles display correctly
- [ ] Text is clean without HTML tags
- [ ] Border radius removed from slider

### Registration Page - Account Type Alert
- [ ] Alert displays with gradient background
- [ ] Icon badge visible on the right
- [ ] Badge shows "مستخدم قياسي"
- [ ] Right border accent (4px) visible
- [ ] Responsive on mobile devices
- [ ] Dark theme compatible

### reCAPTCHA
- [ ] "التحقق الأمني" label displays with shield icon
- [ ] reCAPTCHA widget in bordered light box
- [ ] Help text visible below widget
- [ ] Error messages show with alert styling
- [ ] Error messages clear and professional
- [ ] Emoji icons display correctly
- [ ] Form validation works properly

---

## Files Modified

1. ✅ `main/templatetags/string_filters.py` - Added `clean_html` filter
2. ✅ `templates/partials/_home_slider.html` - Applied filter, loaded templatetag
3. ✅ `templates/pages/register.html` - Enhanced alert and reCAPTCHA UI
4. ✅ `main/forms.py` - Improved reCAPTCHA error messages

---

## Browser Compatibility

All enhancements use standard Bootstrap 5 classes and modern CSS that is compatible with:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

---

## Future Enhancements

1. Consider adding animation to the account type alert (fade-in on page load)
2. Add success animation when reCAPTCHA is completed
3. Add tooltip explaining publisher account benefits
4. Consider adding a "Learn More" link in the account type alert

---

## Notes

- The `clean_html` filter can be reused in other templates where HTML entity cleaning is needed
- All UI enhancements use CSS variables for theme compatibility
- RTL (Arabic) layout fully supported
- No JavaScript changes required - all backend/template improvements
