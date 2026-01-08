"""
أمثلة عملية لاستخدام نظام التحقق
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from content.verification_decorators import (
    verification_required,
    email_verification_required,
    phone_verification_required,
)
from content.verification_utils import (
    is_verification_required_for_services,
    user_can_use_services,
)


# ========================================
# مثال 1: حماية view ببساطة
# ========================================
@verification_required()
def post_classified_ad(request):
    """
    View لنشر إعلان - محمي بنظام التحقق
    سيتم التحقق تلقائياً بناءً على الإعدادات
    """
    if request.method == "POST":
        # معالجة نشر الإعلان
        pass

    return render(request, "ads/post_ad.html")


# ========================================
# مثال 2: تحقق يدوي مخصص
# ========================================
def add_to_cart(request, ad_id):
    """
    إضافة إلى السلة مع تحقق مخصص
    """
    # تحقق يدوي من متطلبات التحقق
    if is_verification_required_for_services():
        can_use, message = user_can_use_services(request.user)
        if not can_use:
            messages.warning(request, message)

            # توجيه ذكي بناءً على حالة المستخدم
            if not request.user.is_authenticated:
                return redirect("main:login")
            elif not request.user.is_email_verified:
                return redirect("main:email_verification_required")
            elif not request.user.is_mobile_verified:
                return redirect("main:phone_verification_required")

    # المتابعة في الإضافة للسلة
    # ...
    return redirect("cart:view_cart")


# ========================================
# مثال 3: تحقق محدد من البريد فقط
# ========================================
@email_verification_required()
def subscribe_to_newsletter(request):
    """
    الاشتراك في النشرة البريدية
    يتطلب تحقق البريد الإلكتروني فقط
    """
    if request.method == "POST":
        # معالجة الاشتراك
        pass

    return render(request, "newsletter/subscribe.html")


# ========================================
# مثال 4: تحقق محدد من الموبايل فقط
# ========================================
@phone_verification_required()
def enable_sms_notifications(request):
    """
    تفعيل إشعارات SMS
    يتطلب تحقق رقم الهاتف فقط
    """
    if request.method == "POST":
        # تفعيل الإشعارات
        pass

    return render(request, "settings/sms_notifications.html")


# ========================================
# مثال 5: عرض معلومات التحقق في Dashboard
# ========================================
def user_dashboard(request):
    """
    لوحة تحكم المستخدم مع معلومات التحقق
    """
    context = {
        "user": request.user,
        # هذه المعلومات متاحة تلقائياً من context_processor
        # لكن يمكن استخدامها في الكود أيضاً
    }

    # تحقق من حالة التحقق
    if request.user.is_authenticated:
        if not request.user.is_email_verified:
            messages.info(
                request,
                _(
                    "يرجى التحقق من بريدك الإلكتروني للحصول على جميع المزايا. "
                    '<a href="/email-verification-required/">تحقق الآن</a>'
                ),
            )

        if not request.user.is_mobile_verified:
            messages.info(
                request,
                _(
                    "يرجى التحقق من رقم هاتفك للحصول على إشعارات SMS. "
                    '<a href="/phone-verification-required/">تحقق الآن</a>'
                ),
            )

    return render(request, "dashboard/user_dashboard.html", context)


# ========================================
# مثال 6: API Endpoint مع تحقق
# ========================================
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def api_create_ad(request):
    """
    API لإنشاء إعلان - مع تحقق يدوي
    """
    # تحقق من المصادقة
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "يجب تسجيل الدخول أولاً"}, status=401
        )

    # تحقق من متطلبات التحقق
    if is_verification_required_for_services():
        can_use, message = user_can_use_services(request.user)
        if not can_use:
            return JsonResponse(
                {
                    "success": False,
                    "message": message,
                    "requires_verification": True,
                    "email_verified": request.user.is_email_verified,
                    "phone_verified": request.user.is_mobile_verified,
                },
                status=403,
            )

    # معالجة إنشاء الإعلان
    # ...

    return JsonResponse({"success": True, "message": "تم إنشاء الإعلان بنجاح"})


# ========================================
# مثال 7: Class-Based View مع تحقق
# ========================================
from django.views import View
from django.utils.decorators import method_decorator


@method_decorator(verification_required(), name="dispatch")
class PostAdView(View):
    """
    Class-based view لنشر إعلان
    محمي بنظام التحقق
    """

    def get(self, request):
        return render(request, "ads/post_ad.html")

    def post(self, request):
        # معالجة نشر الإعلان
        pass


# ========================================
# مثال 8: استخدام في القالب (Template)
# ========================================
"""
في القالب (مثال: base.html أو dashboard):

{% if verification_requirements.services_require_verification %}
    {% if user_verification_status.needs_verification %}
        <div class="verification-alert">
            <div class="alert alert-warning" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>تنبيه:</strong>
                {{ verification_requirements.verification_message }}

                <div class="mt-2">
                    {% if not user_verification_status.is_email_verified %}
                        <a href="{% url 'main:email_verification_required' %}"
                           class="btn btn-sm btn-warning me-2">
                            <i class="fas fa-envelope me-1"></i>
                            تحقق من البريد
                        </a>
                    {% endif %}

                    {% if not user_verification_status.is_phone_verified %}
                        <a href="{% url 'main:phone_verification_required' %}"
                           class="btn btn-sm btn-info">
                            <i class="fas fa-mobile-alt me-1"></i>
                            تحقق من الموبايل
                        </a>
                    {% endif %}
                </div>
            </div>
        </div>
    {% endif %}
{% endif %}

---

في صفحة نشر إعلان:

<form method="post" action="{% url 'ads:post_ad' %}">
    {% csrf_token %}

    {% if user_verification_status.needs_verification %}
        <div class="alert alert-danger">
            <i class="fas fa-lock me-2"></i>
            يجب التحقق من حسابك قبل نشر الإعلانات
        </div>
    {% endif %}

    <!-- باقي الفورم -->
</form>
"""
