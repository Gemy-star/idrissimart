from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
import json
from datetime import datetime, timedelta

from .models import (
    Category,
    ClassifiedAd,
    AdFeaturePrice,
    CartSettings,
    AdTransaction,
    AdPackage,
    UserPackage,
    CustomField,
    AdFeature,
    Order,
)


@login_required
def enhanced_ad_create(request):
    """Enhanced ad creation with custom fields and features"""
    if request.method == "POST":
        try:
            # Get form data
            title = request.POST.get("title")
            description = request.POST.get("description")
            price = request.POST.get("price")
            category_id = request.POST.get("category")

            # Validate required fields
            if not all([title, description, price, category_id]):
                return JsonResponse(
                    {"success": False, "error": _("جميع الحقول مطلوبة")}
                )

            category = get_object_or_404(Category, id=category_id)

            # Create the ad
            ad = ClassifiedAd.objects.create(
                title=title,
                description=description,
                price=Decimal(price),
                category=category,
                user=request.user,
                status="pending",
            )

            # Process custom fields
            custom_fields_data = {}
            for field in CustomField.objects.filter(category=category):
                field_value = request.POST.get(f"custom_field_{field.id}")
                if field_value:
                    custom_fields_data[field.name] = field_value

            ad.custom_fields = custom_fields_data

            # Process selected features
            selected_features = request.POST.getlist("features")
            total_features_price = Decimal("0")

            for feature_id in selected_features:
                try:
                    feature = AdFeature.objects.get(id=feature_id)
                    feature_price = AdFeaturePrice.objects.filter(
                        feature=feature, category=category
                    ).first()

                    if feature_price:
                        total_features_price += feature_price.price
                        # Add feature to ad (you might need a many-to-many relationship)

                except AdFeature.DoesNotExist:
                    continue

            ad.features_price = total_features_price
            ad.save()

            # Cart system is now replaced with Order system
            # Ads are created directly without reservations
            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم إنشاء الإعلان بنجاح"),
                    "ad_id": ad.id,
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # GET request - show form
    categories = Category.objects.filter(parent__isnull=False)  # Only subcategories
    features = AdFeature.objects.filter(is_active=True)
    cart_settings = CartSettings.objects.first()

    context = {
        "categories": categories,
        "features": features,
        "cart_settings": cart_settings,
    }

    return render(request, "classifieds/enhanced_ad_create.html", context)


@login_required
def packages_list(request):
    """
    List available packages for users
    عدم ظهور باقات النشر للاعضاء غير الواقع الحجانية فقط وغيرها تكون مقفله بعد تأكيد الايميل
    """
    # Get user's active packages
    active_packages = []
    if request.user.is_authenticated:
        active_packages = UserPackage.objects.filter(
            user=request.user, is_active=True, expiry_date__gt=timezone.now()
        ).select_related("package")

    # Check if user has verified email
    email_verified = False
    if request.user.is_authenticated:
        email_verified = getattr(request.user, "is_email_verified", False)

    # Get general packages (not category-specific)
    # If email is not verified, show only free packages
    if email_verified or not request.user.is_authenticated:
        general_packages = AdPackage.objects.filter(
            category__isnull=True, is_active=True
        ).order_by("price")
    else:
        # Only show free packages for non-verified users
        general_packages = AdPackage.objects.filter(
            category__isnull=True, is_active=True, price=0
        ).order_by("price")

    # Get category-specific packages grouped by category
    category_packages = {}
    if email_verified or not request.user.is_authenticated:
        categories_with_packages = Category.objects.filter(
            adpackage__isnull=False, adpackage__is_active=True
        ).distinct()

        for category in categories_with_packages:
            packages = AdPackage.objects.filter(
                category=category, is_active=True
            ).order_by("price")
            if packages.exists():
                category_packages[category] = packages

    context = {
        "active_packages": active_packages,
        "general_packages": general_packages,
        "category_packages": category_packages,
        "email_verified": email_verified,
        "show_email_verification_warning": request.user.is_authenticated
        and not email_verified,
    }

    return render(request, "classifieds/packages_list.html", context)


@login_required
@staff_member_required
def reservation_management(request):
    """Redirect to new Order management system"""
    messages.info(request, _("نظام الحجوزات تم دمجه مع نظام الطلبات الجديد"))
    return redirect("main:admin_orders_list")


# AJAX Views


@require_http_methods(["GET"])
def get_custom_fields(request):
    """Get custom fields for a category"""
    category_id = request.GET.get("category_id")

    if not category_id:
        return JsonResponse({"success": False, "error": _("معرف القسم مطلوب")})

    try:
        category = Category.objects.get(id=category_id)
        fields = CustomField.objects.filter(category=category, is_active=True)

        fields_data = []
        for field in fields:
            field_data = {
                "id": field.id,
                "name": field.name,
                "field_type": field.field_type,
                "is_required": field.is_required,
                "help_text": field.help_text,
                "options": field.options.split(",") if field.options else [],
            }
            fields_data.append(field_data)

        return JsonResponse({"success": True, "fields": fields_data})

    except Category.DoesNotExist:
        return JsonResponse({"success": False, "error": _("القسم غير موجود")})


@require_http_methods(["GET"])
def get_features(request):
    """Get available features for a category"""
    category_id = request.GET.get("category_id")

    if not category_id:
        return JsonResponse({"success": False, "error": _("معرف القسم مطلوب")})

    try:
        category = Category.objects.get(id=category_id)
        features = AdFeature.objects.filter(is_active=True)

        features_data = []
        for feature in features:
            feature_price = AdFeaturePrice.objects.filter(
                feature=feature, category=category
            ).first()

            feature_data = {
                "id": feature.id,
                "name": feature.name,
                "description": feature.description,
                "icon": feature.icon,
                "price": str(feature_price.price) if feature_price else "0",
                "duration_days": feature_price.duration_days if feature_price else None,
            }
            features_data.append(feature_data)

        return JsonResponse({"success": True, "features": features_data})

    except Category.DoesNotExist:
        return JsonResponse({"success": False, "error": _("القسم غير موجود")})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_features_price(request):
    """Calculate total price for selected features"""
    try:
        data = json.loads(request.body)
        category_id = data.get("category_id")
        feature_ids = data.get("feature_ids", [])

        if not category_id:
            return JsonResponse({"success": False, "error": _("معرف القسم مطلوب")})

        category = Category.objects.get(id=category_id)
        total_price = Decimal("0")

        for feature_id in feature_ids:
            feature_price = AdFeaturePrice.objects.filter(
                feature_id=feature_id, category=category
            ).first()

            if feature_price:
                total_price += feature_price.price

        return JsonResponse({"success": True, "total_price": str(total_price)})

    except (json.JSONDecodeError, Category.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_reservation(request):
    """Create a new reservation"""
    try:
        data = json.loads(request.body)
        ad_id = data.get("ad_id")
        quantity = int(data.get("quantity", 1))

        if not ad_id:
            return JsonResponse({"success": False, "error": _("معرف الإعلان مطلوب")})

        ad = ClassifiedAd.objects.get(id=ad_id)

        # Check if cart is enabled
        cart_settings = CartSettings.objects.first()
        if not cart_settings or not cart_settings.enable_cart:
            return JsonResponse({"success": False, "error": _("سلة الحجز غير مفعلة")})

        # Calculate total amount
        total_amount = ad.price * quantity

        # Create reservation
        reservation = AdReservation.objects.create(
            user=request.user,
            ad=ad,
            quantity=quantity,
            total_amount=total_amount,
            expires_at=timezone.now()
            + timedelta(hours=cart_settings.reservation_duration),
        )

        return JsonResponse(
            {
                "success": True,
                "message": _("تم حجز الإعلان بنجاح"),
                "reservation_id": reservation.id,
            }
        )

    except (json.JSONDecodeError, ClassifiedAd.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def activate_package(request):
    """Activate a free package"""
    try:
        data = json.loads(request.body)
        package_id = data.get("package_id")

        if not package_id:
            return JsonResponse({"success": False, "error": _("معرف الباقة مطلوب")})

        package = AdPackage.objects.get(id=package_id)

        # Check if package is free
        if package.price > 0:
            return JsonResponse({"success": False, "error": _("هذه الباقة غير مجانية")})

        # Check if user already activated this free package before (even if expired)
        already_activated = UserPackage.objects.filter(
            user=request.user, package=package
        ).exists()

        if already_activated:
            return JsonResponse(
                {
                    "success": False,
                    "error": _(
                        "لقد قمت بتفعيل هذه الباقة المجانية من قبل. الباقات المجانية يمكن تفعيلها مرة واحدة فقط."
                    ),
                }
            )

        # Create user package
        user_package = UserPackage.objects.create(
            user=request.user,
            package=package,
            ads_remaining=package.ad_count,
            expiry_date=timezone.now() + timedelta(days=package.duration_days),
            is_active=True,
        )

        return JsonResponse({"success": True, "message": _("تم تفعيل الباقة بنجاح")})

    except (json.JSONDecodeError, AdPackage.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["GET"])
@staff_member_required
def reservation_details(request, reservation_id):
    """Deprecated - Redirect to new Order system"""
    return JsonResponse(
        {"success": False, "error": _("نظام الحجوزات تم استبداله بنظام الطلبات الجديد")}
    )


@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def update_reservation_status(request):
    """Deprecated - Redirect to new Order system"""
    return JsonResponse(
        {"success": False, "error": _("نظام الحجوزات تم استبداله بنظام الطلبات الجديد")}
    )


@csrf_exempt
@require_http_methods(["DELETE"])
@staff_member_required
def delete_reservation(request):
    """Deprecated - Redirect to new Order system"""
    return JsonResponse(
        {"success": False, "error": _("نظام الحجوزات تم استبداله بنظام الطلبات الجديد")}
    )


@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def send_reservation_notification(request):
    """Deprecated - Redirect to new Order system"""
    return JsonResponse(
        {"success": False, "error": _("نظام الحجوزات تم استبداله بنظام الطلبات الجديد")}
    )


@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def add_reservation(request):
    """Deprecated - Redirect to new Order system"""
    return JsonResponse(
        {"success": False, "error": _("نظام الحجوزات تم استبداله بنظام الطلبات الجديد")}
    )


@require_http_methods(["GET"])
@staff_member_required
def get_users(request):
    """Get list of users for dropdown"""
    users = User.objects.filter(is_active=True).values("id", "username", "email")[:100]

    return JsonResponse({"success": True, "users": list(users)})


@require_http_methods(["GET"])
@staff_member_required
def get_ads(request):
    """Get list of ads for dropdown"""
    ads = ClassifiedAd.objects.filter(status="approved").values("id", "title", "price")[
        :100
    ]

    return JsonResponse({"success": True, "ads": list(ads)})


@staff_member_required
def admin_site_content(request):
    """Admin page to manage site content using django-solo models"""
    from content.site_config import (
        SiteConfiguration,
        AboutPage,
        ContactPage,
        HomePage,
        TermsPage,
        PrivacyPage,
    )

    context = {
        "active_nav": "site_content",
        "site_config": SiteConfiguration.get_solo(),
        "about_page": AboutPage.get_solo(),
        "contact_page": ContactPage.get_solo(),
        "home_page": HomePage.get_solo(),
        "terms_page": TermsPage.get_solo(),
        "privacy_page": PrivacyPage.get_solo(),
    }

    return render(request, "admin_dashboard/site_content.html", context)


@staff_member_required
def admin_edit_homepage(request):
    """Edit HomePage content"""
    from content.site_config import HomePage
    from django import forms
    from django_ckeditor_5.widgets import CKEditor5Widget

    class HomePageForm(forms.ModelForm):
        class Meta:
            model = HomePage
            fields = [
                "hero_title",
                "hero_title_ar",
                "hero_subtitle",
                "hero_subtitle_ar",
                "hero_image",
                "hero_button_text",
                "hero_button_text_ar",
                "hero_button_url",
                "show_modal",
                "modal_title",
                "modal_title_ar",
                "modal_content",
                "modal_content_ar",
                "modal_image",
                "modal_button_text",
                "modal_button_text_ar",
                "modal_button_url",
                "show_featured_categories",
                "show_featured_ads",
            ]
            widgets = {
                "hero_subtitle": CKEditor5Widget(config_name="default"),
                "hero_subtitle_ar": CKEditor5Widget(config_name="default"),
                "modal_content": CKEditor5Widget(config_name="default"),
                "modal_content_ar": CKEditor5Widget(config_name="default"),
            }

    home_page = HomePage.get_solo()

    if request.method == "POST":
        form = HomePageForm(request.POST, request.FILES, instance=home_page)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث محتوى الصفحة الرئيسية بنجاح"))
            return redirect("main:admin_site_content")
    else:
        form = HomePageForm(instance=home_page)

    context = {
        "active_nav": "site_content",
        "form": form,
        "page_title": _("تحرير الصفحة الرئيسية"),
    }

    return render(request, "admin_dashboard/edit_homepage.html", context)


@staff_member_required
def admin_edit_aboutpage(request):
    """Edit AboutPage content"""
    from content.site_config import AboutPage
    from django import forms
    from django_ckeditor_5.widgets import CKEditor5Widget

    class AboutPageForm(forms.ModelForm):
        class Meta:
            model = AboutPage
            fields = [
                "title",
                "title_ar",
                "content",
                "content_ar",
                "mission",
                "mission_ar",
                "vision",
                "vision_ar",
                "values",
                "values_ar",
                "featured_image",
            ]
            widgets = {
                "content": CKEditor5Widget(config_name="default"),
                "content_ar": CKEditor5Widget(config_name="default"),
                "mission": CKEditor5Widget(config_name="default"),
                "mission_ar": CKEditor5Widget(config_name="default"),
                "vision": CKEditor5Widget(config_name="default"),
                "vision_ar": CKEditor5Widget(config_name="default"),
                "values": CKEditor5Widget(config_name="default"),
                "values_ar": CKEditor5Widget(config_name="default"),
            }

    about_page = AboutPage.get_solo()

    if request.method == "POST":
        form = AboutPageForm(request.POST, request.FILES, instance=about_page)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث صفحة من نحن بنجاح"))
            return redirect("main:admin_site_content")
    else:
        form = AboutPageForm(instance=about_page)

    context = {
        "active_nav": "site_content",
        "form": form,
        "page_title": _("تحرير صفحة من نحن"),
    }

    return render(request, "admin_dashboard/edit_aboutpage.html", context)


@staff_member_required
def admin_edit_contactpage(request):
    """Edit ContactPage content"""
    from content.site_config import ContactPage
    from django import forms
    from django_ckeditor_5.widgets import CKEditor5Widget

    class ContactPageForm(forms.ModelForm):
        class Meta:
            model = ContactPage
            fields = [
                "title",
                "title_ar",
                "description",
                "description_ar",
                "enable_contact_form",
                "notification_email",
                "office_hours",
                "office_hours_ar",
                "map_embed_code",
            ]
            widgets = {
                "description": CKEditor5Widget(config_name="default"),
                "description_ar": CKEditor5Widget(config_name="default"),
                "office_hours": CKEditor5Widget(config_name="default"),
                "office_hours_ar": CKEditor5Widget(config_name="default"),
                "map_embed_code": CKEditor5Widget(config_name="default"),
            }

    contact_page = ContactPage.get_solo()

    if request.method == "POST":
        form = ContactPageForm(request.POST, instance=contact_page)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث صفحة اتصل بنا بنجاح"))
            return redirect("main:admin_site_content")
    else:
        form = ContactPageForm(instance=contact_page)

    context = {
        "active_nav": "site_content",
        "form": form,
        "page_title": _("تحرير صفحة اتصل بنا"),
    }

    return render(request, "admin_dashboard/edit_contactpage.html", context)


@staff_member_required
def admin_edit_siteconfig(request):
    """Edit SiteConfiguration"""
    from content.site_config import SiteConfiguration
    from django import forms
    from django_ckeditor_5.widgets import CKEditor5Widget

    class SiteConfigForm(forms.ModelForm):
        class Meta:
            model = SiteConfiguration
            fields = [
                "meta_keywords",
                "meta_keywords_ar",
                "footer_text",
                "footer_text_ar",
                "copyright_text",
            ]
            widgets = {
                "footer_text": CKEditor5Widget(config_name="default"),
                "footer_text_ar": CKEditor5Widget(config_name="default"),
            }

    site_config = SiteConfiguration.get_solo()

    if request.method == "POST":
        form = SiteConfigForm(request.POST, instance=site_config)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث إعدادات الموقع بنجاح"))
            return redirect("main:admin_site_content")
    else:
        form = SiteConfigForm(instance=site_config)

    context = {
        "active_nav": "site_content",
        "form": form,
        "page_title": _("تحرير إعدادات الموقع"),
    }

    return render(request, "admin_dashboard/edit_siteconfig.html", context)


@staff_member_required
def admin_edit_termspage(request):
    """Edit TermsPage content"""
    from content.site_config import TermsPage
    from django import forms
    from django_ckeditor_5.widgets import CKEditor5Widget

    class TermsPageForm(forms.ModelForm):
        class Meta:
            model = TermsPage
            fields = [
                "title",
                "title_ar",
                "content",
                "content_ar",
            ]
            widgets = {
                "content": CKEditor5Widget(config_name="default"),
                "content_ar": CKEditor5Widget(config_name="default"),
            }

    terms_page = TermsPage.get_solo()

    if request.method == "POST":
        form = TermsPageForm(request.POST, instance=terms_page)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث صفحة الشروط والأحكام بنجاح"))
            return redirect("main:admin_site_content")
    else:
        form = TermsPageForm(instance=terms_page)

    context = {
        "active_nav": "site_content",
        "form": form,
        "terms_page": terms_page,
        "page_title": _("تحرير الشروط والأحكام"),
    }

    return render(request, "admin_dashboard/edit_termspage.html", context)


@staff_member_required
def admin_edit_privacypage(request):
    """Edit PrivacyPage content"""
    from content.site_config import PrivacyPage
    from django import forms
    from django_ckeditor_5.widgets import CKEditor5Widget

    class PrivacyPageForm(forms.ModelForm):
        class Meta:
            model = PrivacyPage
            fields = [
                "title",
                "title_ar",
                "content",
                "content_ar",
            ]
            widgets = {
                "content": CKEditor5Widget(config_name="default"),
                "content_ar": CKEditor5Widget(config_name="default"),
            }

    privacy_page = PrivacyPage.get_solo()

    if request.method == "POST":
        form = PrivacyPageForm(request.POST, instance=privacy_page)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث صفحة سياسة الخصوصية بنجاح"))
            return redirect("main:admin_site_content")
    else:
        form = PrivacyPageForm(instance=privacy_page)

    context = {
        "active_nav": "site_content",
        "form": form,
        "privacy_page": privacy_page,
        "page_title": _("تحرير سياسة الخصوصية"),
    }

    return render(request, "admin_dashboard/edit_privacypage.html", context)
