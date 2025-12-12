"""
مثال على كيفية استخدام نظام التحقق في الـ Views

هذا الملف يوضح كيفية تطبيق متطلبات التحقق على الـ views المختلفة
"""

# مثال 1: استخدام decorator للحماية
from main.decorators import verification_required_for_services
from django.contrib.auth.decorators import login_required


@login_required
@verification_required_for_services
def create_ad_view(request):
    """
    عرض إنشاء إعلان جديد
    سيتم التحقق من المستخدم تلقائياً إذا كان الإعداد مفعل
    """
    # كود إنشاء الإعلان
    pass


# مثال 2: التحقق اليدوي في view
from content.verification_utils import user_can_use_services
from django.contrib import messages
from django.shortcuts import redirect


@login_required
def add_to_cart_view(request, ad_id):
    """
    إضافة منتج للسلة مع التحقق اليدوي
    """
    # التحقق من قدرة المستخدم على استخدام الخدمة
    can_use, message = user_can_use_services(request.user)
    if not can_use:
        messages.warning(request, message)
        return redirect("main:publisher_settings")

    # كود إضافة المنتج للسلة
    pass


# مثال 3: استخدام في Class-Based View
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from content.verification_utils import user_can_use_services


class CreateAdView(LoginRequiredMixin, CreateView):
    """
    عرض إنشاء إعلان باستخدام Class-Based View
    """

    def dispatch(self, request, *args, **kwargs):
        """
        التحقق من المستخدم قبل تنفيذ الطلب
        """
        can_use, message = user_can_use_services(request.user)
        if not can_use:
            messages.warning(request, message)
            return redirect("main:publisher_settings")

        return super().dispatch(request, *args, **kwargs)


# مثال 4: استخدام في AJAX/API View
from django.http import JsonResponse
from content.verification_utils import user_can_use_services


@login_required
def ajax_add_to_wishlist(request):
    """
    إضافة للمفضلة عبر AJAX
    """
    can_use, message = user_can_use_services(request.user)
    if not can_use:
        return JsonResponse(
            {"success": False, "message": message, "requires_verification": True}
        )

    # كود إضافة للمفضلة
    return JsonResponse({"success": True, "message": "تم الإضافة بنجاح"})


# مثال 5: التحقق في Template
"""
في القالب (Template):

{% if verification_requirements.services_require_verification %}
    {% if not user.email_verified and not user.phone_verified %}
        <div class="alert alert-warning">
            {{ verification_requirements.verification_message }}
            <a href="{% url 'main:publisher_settings' %}">تحقق من حسابك</a>
        </div>
    {% endif %}
{% endif %}
"""


# مثال 6: شرط مخصص في view
from content.verification_utils import is_verification_required_for_services


@login_required
def custom_service_view(request):
    """
    عرض مع شرط مخصص
    """
    # التحقق من تفعيل الإعداد
    if is_verification_required_for_services():
        # التحقق من المستخدم
        is_verified = (
            request.user.email_verified
            or request.user.phone_verified
            or request.user.is_staff
        )

        if not is_verified:
            messages.warning(request, "يجب التحقق من حسابك لاستخدام هذه الخدمة")
            return redirect("main:publisher_settings")

    # كود الخدمة
    pass
