# نظام التحقق - دليل سريع للمطورين

## استخدام سريع

### 1. حماية View

```python
from content.verification_decorators import verification_required

@verification_required()
def my_view(request):
    # هذا الـ view محمي - يتطلب تحقق إذا كان مفعلاً
    pass
```

### 2. في القالب

```django
{% if user_verification_status.needs_verification %}
    <div class="alert alert-warning">
        يرجى التحقق من حسابك
        <a href="{% url 'main:email_verification_required' %}">تحقق الآن</a>
    </div>
{% endif %}
```

### 3. إعدادات التحقق (Constance Config)

- `REQUIRE_EMAIL_VERIFICATION` - تحقق البريد إلزامي عند التسجيل
- `REQUIRE_PHONE_VERIFICATION` - تحقق الموبايل إلزامي عند التسجيل
- `REQUIRE_VERIFICATION_FOR_SERVICES` - التحقق مطلوب للخدمات
- `VERIFICATION_SERVICES_MESSAGE` - رسالة التحقق المخصصة

### URLs الجديدة

- `/email-verification-required/` - صفحة التحقق من البريد
- `/phone-verification-required/` - صفحة التحقق من الموبايل
- `/mark-phone-verified/` - API لتحديث حالة التحقق

### Context Variables

```django
{{ verification_requirements.email_required }}
{{ verification_requirements.phone_required }}
{{ verification_requirements.services_require_verification }}
{{ user_verification_status.is_email_verified }}
{{ user_verification_status.is_phone_verified }}
```

للمزيد: راجع `docs/COMPLETE_VERIFICATION_SYSTEM.md`
