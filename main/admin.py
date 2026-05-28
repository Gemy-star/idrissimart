from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from allauth.account.models import EmailAddress
admin.site.unregister(EmailAddress)
from django.utils.html import format_html, mark_safe
from django.db import models
from django import forms
from mptt.admin import MPTTModelAdmin
from django_ckeditor_5.widgets import CKEditor5Widget

# Admin site configuration
admin.site.site_header = _("إدارة المنصة")
admin.site.site_title = _("لوحة تحكم المنصة")
admin.site.index_title = _("مرحباً بك في لوحة التحكم")

# Import chatbot admin configurations
from .chatbot_admin import *

# Import chat admin configurations
from .chat_admin import *

from .models import (
    AdFeature,
    AdFeaturePrice,
    AdImage,
    AdPackage,
    AdReport,
    AdReview,
    AdSenseSlot,
    AdTransaction,
    AdUpgradeHistory,
    AdvertisingConfig,
    BannerPricing,
    Cart,
    CartItem,
    CartSettings,
    Category,
    CategoryCustomField,
    ClassifiedAd,
    ContactMessage,
    Coupon,
    CustomField,
    CustomFieldOption,
    CustomPage,
    EmailTemplate,
    FAQ,
    FAQCategory,
    FacebookShareRequest,
    NewsletterSubscriber,
    Notification,
    Order,
    OrderItem,
    BannerSlot,
    PaidBanner,
    Payment,
    SafetyTip,
    SMSTemplate,
    User,
    UserPackage,
    UserVerificationRequest,
    Visitor,
    Wishlist,
    WishlistItem,
)


class AdFeaturePriceInline(admin.TabularInline):
    model = AdFeaturePrice
    extra = 0
    fields = ("feature_type", "price", "duration_days", "is_active")
    verbose_name = _("سعر ميزة الإعلان")
    verbose_name_plural = _("أسعار ميزات الإعلان")


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = (
        "name",
        "name_ar",
        "slug",
        "slug_ar",
        "parent",
        "country",
        "is_active",
        "custom_fields_count",
        "created_at",
    )
    list_filter = ("is_active", "country", "parent", "section_type", "created_at")
    search_fields = ("name", "name_ar", "slug", "slug_ar", "description")
    prepopulated_fields = {"slug": ("name",), "slug_ar": ("name_ar",)}
    list_editable = ("is_active",)
    autocomplete_fields = []  # Enable autocomplete for this model

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "name_ar",
                    "slug",
                    "slug_ar",
                    "parent",
                    "section_type",
                    "country",
                )
            },
        ),
        ("Details", {"fields": ("description", "icon", "image")}),
        ("Advanced", {"fields": ("custom_field_schema",)}),
        (
            _("إعدادات السلة والحجز - Cart & Reservation"),
            {
                "fields": (
                    "allow_cart",
                    "cart_instructions",
                    "default_reservation_percentage",
                    "min_reservation_amount",
                    "max_reservation_amount",
                    "require_admin_approval",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("إعدادات التسعير - Pricing"),
            {
                "fields": (
                    "ad_creation_price",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Settings", {"fields": ("order", "is_active")}),
    )
    inlines = [AdFeaturePriceInline]
    ordering = ("country", "name")
    actions = ["activate_categories", "deactivate_categories", "export_categories_csv"]

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} قسم تم تفعيله").format(updated))

    activate_categories.short_description = _("✓ تفعيل الأقسام المحددة")

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("{} قسم تم إلغاء تفعيله").format(updated))

    deactivate_categories.short_description = _("✗ إلغاء تفعيل الأقسام المحددة")

    def export_categories_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="categories_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow([_("الاسم"), _("الاسم بالعربي"), _("الرابط"), _("القسم الأب"), _("الدولة"), _("نشط")])
        for cat in queryset:
            writer.writerow([
                cat.name, cat.name_ar, cat.slug,
                cat.parent.name if cat.parent else "",
                str(cat.country) if cat.country else "",
                "نعم" if cat.is_active else "لا",
            ])
        self.message_user(request, _("تم تصدير {} قسم").format(queryset.count()))
        return response

    export_categories_csv.short_description = _("📥 تصدير إلى CSV")

    def custom_fields_count(self, obj):
        """Display count of custom fields linked to this category"""
        count = obj.custom_fields.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
                count,
            )
        return format_html('<span style="color: #999;">-</span>')

    custom_fields_count.short_description = _("الحقول المخصصة")

    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.prefetch_related("custom_fields")


# --- Classified Ads Admin ---


class AdImageInline(admin.TabularInline):
    model = AdImage
    extra = 1
    ordering = ["order"]
    fields = ("image", "order")


class AdFeatureInline(admin.TabularInline):
    model = AdFeature
    extra = 1
    fields = ("feature_type", "end_date", "is_active")


class AdUpgradeHistoryInline(admin.TabularInline):
    """Inline for viewing ad upgrade history"""

    model = AdUpgradeHistory
    extra = 0
    can_delete = False
    readonly_fields = (
        "upgrade_type",
        "price_paid",
        "duration_days",
        "start_date",
        "end_date",
        "is_active",
    )
    fields = (
        "upgrade_type",
        "price_paid",
        "duration_days",
        "start_date",
        "end_date",
        "is_active",
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ClassifiedAd)
class ClassifiedAdAdmin(admin.ModelAdmin):
    def view_on_site(self, obj):
        """Return the ad URL directly (bypasses the Sites framework redirect)."""
        from django.utils import translation

        with translation.override("ar"):
            return obj.get_absolute_url()

    list_display = (
        "title",
        "user",
        "category",
        "price",
        "status",
        "is_paid",
        "is_resubmitted",
        "is_highlighted",
        "is_urgent",
        "is_pinned",
        "contact_for_price",
        "auto_refresh",
        "is_hidden",
        "cart_enabled_by_admin",
        "created_at",
        "expires_at",
    )
    list_filter = (
        "status",
        "is_paid",
        "is_resubmitted",
        "category",
        "is_hidden",
        "visibility_type",
        "allow_cart",
        "cart_enabled_by_admin",
        "is_cart_enabled",
        "is_delivery_available",
        "is_urgent",
        "is_highlighted",
        "is_pinned",
        "contact_for_price",
        "auto_refresh",
        "hide_price",
        "price_on_request",
    )
    search_fields = ("title", "description", "user__username")
    readonly_fields = (
        "created_at", "updated_at", "views_count", "reviewed_at",
        "custom_fields_display", "price_display_mode",
    )
    inlines = [AdImageInline, AdFeatureInline, AdUpgradeHistoryInline]
    list_editable = ("status", "is_hidden")
    actions = [
        "approve_ads",
        "reject_ads",
        "mark_as_pending",
        "mark_as_paid",
        "mark_as_unpaid",
        "activate_upgrades_action",
        "renew_ads_30_days",
        "renew_ads_60_days",
        "renew_ads_90_days",
        "hide_prices",
        "show_prices",
        "set_price_on_request",
        "set_contact_for_price",
        "show_regular_price",
        "enable_cart_for_ads",
        "disable_cart_for_ads",
    ]

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }

    class Media:
        js = ("admin/js/category_cascade.js",)

    def approve_ads(self, request, queryset):
        """Approve selected ads and notify owners"""
        from django.utils import timezone
        from .models import Notification

        count = 0
        for ad in queryset.select_related("user"):
            ad.status = ClassifiedAd.AdStatus.ACTIVE
            ad.reviewed_by = request.user
            ad.reviewed_at = timezone.now()
            ad.is_resubmitted = False
            ad.save(update_fields=["status", "reviewed_by", "reviewed_at", "is_resubmitted"])
            Notification.objects.create(
                user=ad.user,
                notification_type=Notification.NotificationType.AD_APPROVED,
                title=_("تم قبول إعلانك"),
                message=_("تمت مراجعة إعلانك '{}' وقبوله. يمكنك الآن مشاهدته منشوراً.").format(ad.title),
                link=ad.get_absolute_url(),
            )
            count += 1
        self.message_user(request, _("{} إعلان تم قبوله بنجاح").format(count))

    approve_ads.short_description = _("قبول الإعلانات المحددة")

    def reject_ads(self, request, queryset):
        """Reject selected ads and notify owners"""
        from django.utils import timezone
        from .models import Notification

        count = 0
        for ad in queryset.select_related("user"):
            ad.status = ClassifiedAd.AdStatus.REJECTED
            ad.reviewed_by = request.user
            ad.reviewed_at = timezone.now()
            ad.save(update_fields=["status", "reviewed_by", "reviewed_at"])
            Notification.objects.create(
                user=ad.user,
                notification_type=Notification.NotificationType.AD_REJECTED,
                title=_("تم رفض إعلانك"),
                message=_("تمت مراجعة إعلانك '{}' ورفضه. يرجى التواصل مع الإدارة لمعرفة السبب.").format(ad.title),
                link=ad.get_absolute_url(),
            )
            count += 1
        self.message_user(request, _("{} إعلان تم رفضه").format(count))

    reject_ads.short_description = _("رفض الإعلانات المحددة")

    def mark_as_pending(self, request, queryset):
        """Mark selected ads as pending review"""
        updated = queryset.update(status=ClassifiedAd.AdStatus.PENDING)
        self.message_user(request, _("{} إعلان في انتظار المراجعة").format(updated))

    mark_as_pending.short_description = _("تعيين كـ قيد المراجعة")

    def mark_as_paid(self, request, queryset):
        """Mark selected ads as paid"""
        updated = queryset.update(is_paid=True)
        self.message_user(request, _("{} إعلان تم تحديده كمدفوع").format(updated))

    mark_as_paid.short_description = _("تحديد كمدفوع")

    def mark_as_unpaid(self, request, queryset):
        """Mark selected ads as unpaid"""
        updated = queryset.update(is_paid=False)
        self.message_user(request, _("{} إعلان تم تحديده كغير مدفوع").format(updated))

    mark_as_unpaid.short_description = _("تحديد كغير مدفوع")

    def activate_upgrades_action(self, request, queryset):
        """Check and expire old upgrades for selected ads"""
        count = 0
        for ad in queryset:
            expired = ad.check_and_expire_upgrades()
            count += expired
        self.message_user(request, _(f"تم فحص الإعلانات وإلغاء {count} ترقية منتهية"))

    activate_upgrades_action.short_description = _("فحص وتحديث الترقيات")

    # ── Price display mode bulk actions ───────────────────────────────────────

    def hide_prices(self, request, queryset):
        updated = queryset.update(hide_price=True, price_on_request=False, contact_for_price=False)
        self.message_user(request, _("{} إعلان: تم تفعيل «إخفاء السعر / اطلب عرض سعر»").format(updated))

    hide_prices.short_description = _("💰 إخفاء السعر — «اطلب عرض سعر»")

    def show_prices(self, request, queryset):
        updated = queryset.update(hide_price=False, price_on_request=False, contact_for_price=False)
        self.message_user(request, _("{} إعلان: تم إظهار السعر الفعلي").format(updated))

    show_prices.short_description = _("💵 إظهار السعر الفعلي")

    def set_price_on_request(self, request, queryset):
        updated = queryset.update(price_on_request=True, hide_price=False, contact_for_price=False)
        self.message_user(request, _("{} إعلان: تم تفعيل «السعر عند الطلب»").format(updated))

    set_price_on_request.short_description = _("📋 السعر عند الطلب")

    def set_contact_for_price(self, request, queryset):
        updated = queryset.update(contact_for_price=True, hide_price=False, price_on_request=False)
        self.message_user(request, _("{} إعلان: تم تفعيل «تواصل ليصلك عرض سعر» (مدفوع)").format(updated))

    set_contact_for_price.short_description = _("⭐ تواصل ليصلك عرض سعر (مدفوع)")

    def show_regular_price(self, request, queryset):
        updated = queryset.update(hide_price=False, price_on_request=False, contact_for_price=False)
        self.message_user(request, _("{} إعلان: تم إلغاء جميع أوضاع إخفاء السعر وإظهار السعر الفعلي").format(updated))

    show_regular_price.short_description = _("🔄 إعادة تعيين — إظهار السعر الفعلي")

    def renew_ads_30_days(self, request, queryset):
        """Renew selected ads for 30 days"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        future_date = now + timedelta(days=30)

        # Update expiration date and ensure status is active
        updated = queryset.update(
            expires_at=future_date, status=ClassifiedAd.AdStatus.ACTIVE
        )

        self.message_user(
            request,
            _("{} إعلان تم تجديده لمدة 30 يوم (تنتهي في {})").format(
                updated, future_date.strftime("%Y-%m-%d")
            ),
        )

    renew_ads_30_days.short_description = _("تجديد الإعلانات لمدة 30 يوم")

    def renew_ads_60_days(self, request, queryset):
        """Renew selected ads for 60 days"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        future_date = now + timedelta(days=60)

        updated = queryset.update(
            expires_at=future_date, status=ClassifiedAd.AdStatus.ACTIVE
        )

        self.message_user(
            request,
            _("{} إعلان تم تجديده لمدة 60 يوم (تنتهي في {})").format(
                updated, future_date.strftime("%Y-%m-%d")
            ),
        )

    renew_ads_60_days.short_description = _("تجديد الإعلانات لمدة 60 يوم")

    def renew_ads_90_days(self, request, queryset):
        """Renew selected ads for 90 days"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        future_date = now + timedelta(days=90)

        updated = queryset.update(
            expires_at=future_date, status=ClassifiedAd.AdStatus.ACTIVE
        )

        self.message_user(
            request,
            _("{} إعلان تم تجديده لمدة 90 يوم (تنتهي في {})").format(
                updated, future_date.strftime("%Y-%m-%d")
            ),
        )

    renew_ads_90_days.short_description = _("تجديد الإعلانات لمدة 90 يوم")

    def enable_cart_for_ads(self, request, queryset):
        """Enable cart for selected ads"""
        updated = queryset.update(cart_enabled_by_admin=True)
        self.message_user(
            request,
            _("تم تفعيل السلة لـ {} إعلان").format(updated),
        )

    enable_cart_for_ads.short_description = _("تفعيل السلة للإعلانات المحددة")

    def disable_cart_for_ads(self, request, queryset):
        """Disable cart for selected ads"""
        updated = queryset.update(cart_enabled_by_admin=False)
        self.message_user(
            request,
            _("تم تعطيل السلة لـ {} إعلان").format(updated),
        )

    disable_cart_for_ads.short_description = _("تعطيل السلة للإعلانات المحددة")

    def get_list_display(self, request):
        """Add custom display method for resubmitted ads"""
        list_display = list(super().get_list_display(request))
        # Replace is_resubmitted with custom colored display
        if "is_resubmitted" in list_display:
            idx = list_display.index("is_resubmitted")
            list_display[idx] = "resubmitted_badge"
        return tuple(list_display)

    def resubmitted_badge(self, obj):
        """Display colored badge for resubmitted ads"""
        if obj.is_resubmitted:
            return format_html(
                '<span style="background-color: #ff9800; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">'
                '<i class="fas fa-redo"></i> معاد إرساله'
                "</span>"
            )
        return format_html('<span style="color: #999;">-</span>')

    resubmitted_badge.short_description = _("حالة الإرسال")
    resubmitted_badge.admin_order_field = "is_resubmitted"

    fieldsets = (
        (_("معلومات الإعلان - Ad Information"), {"fields": ("user", "category", "title", "description")}),
        (
            _("السعر - Pricing"),
            {
                "fields": (
                    "price",
                    "is_negotiable",
                    "price_display_mode",
                    "hide_price",
                    "price_on_request",
                    "contact_for_price",
                ),
                "description": _(
                    "اختر وضعاً واحداً فقط لعرض السعر — عند الحفظ يُطبَّق الأولوية: "
                    "«تواصل ليصلك عرض سعر» (مدفوع، أعلى أولوية) ← "
                    "«السعر عند الطلب» ← "
                    "«إخفاء السعر / اطلب عرض سعر» ← "
                    "السعر الفعلي (بدون تفعيل أي خيار)."
                ),
            },
        ),
        (_("التقييم - Rating"), {"fields": ("rating", "rating_count")}),
        (_("الموقع - Location"), {"fields": ("country", "city", "address")}),
        (
            _("الظهور والتحكم - Visibility & Access"),
            {
                "fields": (
                    "visibility_type",
                    "require_login_for_contact",
                    "is_hidden",
                    "require_review",
                )
            },
        ),
        (
            _("السلة والحجز - Cart & Reservation"),
            {
                "fields": (
                    "allow_cart",
                    "cart_enabled_by_admin",
                    "reservation_percentage",
                    "reservation_amount",
                    "delivery_terms",
                    "delivery_terms_en",
                )
            },
        ),
        (
            _("المميزات - Features"),
            {
                "fields": (
                    "is_urgent",
                    "is_highlighted",
                    "is_pinned",
                    "auto_refresh",
                    "video_url",
                    "video_file",
                    "is_cart_enabled",
                    "is_delivery_available",
                )
            },
        ),
        (
            _("الحالة والمراجعة - Status & Review"),
            {
                "fields": (
                    "status",
                    "is_paid",
                    "is_resubmitted",
                    "reviewed_by",
                    "reviewed_at",
                    "admin_notes",
                    "expires_at",
                    "views_count",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            _("الحقول المخصصة - Custom Fields"),
            {
                "fields": ("custom_fields_display",),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        # Enforce mutual exclusivity: only the highest-priority price flag stays on.
        # Priority: contact_for_price > price_on_request > hide_price
        active = [
            obj.contact_for_price,
            obj.price_on_request,
            obj.hide_price,
        ]
        if sum(active) > 1:
            if obj.contact_for_price:
                obj.price_on_request = False
                obj.hide_price = False
            elif obj.price_on_request:
                obj.hide_price = False
        super().save_model(request, obj, form, change)

    def price_display_mode(self, obj):
        if obj.contact_for_price:
            return format_html(
                '<span style="background:#7c3aed;color:#fff;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">⭐ تواصل ليصلك عرض سعر (مدفوع)</span>'
            )
        if obj.price_on_request:
            return format_html(
                '<span style="background:#0891b2;color:#fff;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">📋 السعر عند الطلب</span>'
            )
        if obj.hide_price:
            return format_html(
                '<span style="background:#d97706;color:#fff;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">💰 إخفاء السعر — اطلب عرض سعر</span>'
            )
        return format_html(
            '<span style="background:#16a34a;color:#fff;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">💵 السعر الفعلي: {}</span>',
            obj.price or "—",
        )

    price_display_mode.short_description = _("وضع عرض السعر الحالي")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "reviewed_by":
            kwargs["queryset"] = User.objects.filter(
                models.Q(is_staff=True) | models.Q(is_superuser=True)
            ).order_by("username")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def custom_fields_display(self, obj):
        if not obj.pk or not obj.category_id:
            return "—"
        cat_custom_fields = CategoryCustomField.objects.filter(
            category=obj.category, is_active=True
        ).select_related("custom_field").order_by("order", "id")
        if not cat_custom_fields.exists():
            return _("لا توجد حقول مخصصة لهذا القسم")
        values = obj.custom_fields or {}
        rows = []
        for ccf in cat_custom_fields:
            cf = ccf.custom_field
            key = cf.name
            val = values.get(key, "")
            label = cf.label_ar or cf.label or cf.name
            display_val = val if val not in (None, "", []) else "—"
            if isinstance(display_val, list):
                display_val = ", ".join(str(v) for v in display_val)
            rows.append(
                f"<tr>"
                f"<th style='padding:5px 14px 5px 4px;text-align:right;color:#374151;font-weight:600;white-space:nowrap;'>{label}</th>"
                f"<td style='padding:5px;color:#1f2937;'>{display_val}</td>"
                f"</tr>"
            )
        table = (
            "<table style='font-size:0.88em;border-collapse:collapse;'>"
            + "".join(rows)
            + "</table>"
        )
        return format_html("{}", mark_safe(table))

    custom_fields_display.short_description = _("الحقول المخصصة")


@admin.register(AdPackage)
class AdPackageAdmin(admin.ModelAdmin):
    """
    إدارة باقات الإعلانات في لوحة التحكم
    Admin interface for Ad Packages
    """

    list_display = (
        "name",
        "price",
        "ad_count",
        "ad_duration_days",
        "duration_days",
        "is_default",
        "is_recommended",
        "is_popular",
        "is_active",
        "category",
        "display_order",
    )
    list_filter = (
        "is_active",
        "is_default",
        "is_recommended",
        "is_popular",
        "category",
    )
    search_fields = ("name", "name_en", "description", "description_en")
    list_editable = (
        "is_active",
        "is_default",
        "is_recommended",
        "is_popular",
        "display_order",
    )

    fieldsets = (
        (
            _("معلومات أساسية"),
            {
                "fields": (
                    "name",
                    "name_en",
                    "description",
                    "description_en",
                    "category",
                )
            },
        ),
        (
            _("التسعير"),
            {"fields": ("price", "ad_count", "ad_duration_days", "duration_days")},
        ),
        (
            _("أسعار المميزات"),
            {
                "fields": (
                    "feature_pinned_price",
                    "feature_urgent_price",
                    "feature_highlighted_price",
                    "feature_auto_refresh_price",
                    "feature_add_video_price",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("الحالة والعرض"),
            {
                "fields": (
                    "is_active",
                    "is_default",
                    "is_recommended",
                    "is_popular",
                    "display_order",
                )
            },
        ),
        (
            _("المميزات"),
            {
                "fields": ("features",),
                "classes": ("collapse",),
                "description": _(
                    'أدخل قائمة المميزات بصيغة JSON مثل: ["ميزة 1", "ميزة 2"]'
                ),
            },
        ),
    )

    class Media:
        js = ("admin/js/category_cascade.js",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category")


@admin.register(UserPackage)
class UserPackageAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "package",
        "purchase_date",
        "expiry_date",
        "ads_remaining",
        "ads_used",
        "usage_percentage",
        "is_active_status",
    )
    list_filter = ("package", "purchase_date", "expiry_date")
    search_fields = ("user__username", "user__email", "package__name")
    readonly_fields = ("purchase_date", "usage_percentage", "is_active_status")
    date_hierarchy = "purchase_date"

    def is_active_status(self, obj):
        return obj.is_active()

    is_active_status.boolean = True
    is_active_status.short_description = _("نشطة")

    def usage_percentage(self, obj):
        return f"{obj.get_usage_percentage():.1f}%"

    usage_percentage.short_description = _("نسبة الاستخدام")

    actions = ["extend_30_days", "extend_60_days", "extend_90_days", "export_packages_csv"]

    def extend_30_days(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        count = 0
        for pkg in queryset:
            base = pkg.expiry_date if pkg.expiry_date and pkg.expiry_date > timezone.now() else timezone.now()
            pkg.expiry_date = base + timedelta(days=30)
            pkg.save(update_fields=["expiry_date"])
            count += 1
        self.message_user(request, _("تم تمديد {} باقة 30 يوماً").format(count))

    extend_30_days.short_description = _("📅 تمديد 30 يوم")

    def extend_60_days(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        count = 0
        for pkg in queryset:
            base = pkg.expiry_date if pkg.expiry_date and pkg.expiry_date > timezone.now() else timezone.now()
            pkg.expiry_date = base + timedelta(days=60)
            pkg.save(update_fields=["expiry_date"])
            count += 1
        self.message_user(request, _("تم تمديد {} باقة 60 يوماً").format(count))

    extend_60_days.short_description = _("📅 تمديد 60 يوم")

    def extend_90_days(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        count = 0
        for pkg in queryset:
            base = pkg.expiry_date if pkg.expiry_date and pkg.expiry_date > timezone.now() else timezone.now()
            pkg.expiry_date = base + timedelta(days=90)
            pkg.save(update_fields=["expiry_date"])
            count += 1
        self.message_user(request, _("تم تمديد {} باقة 90 يوماً").format(count))

    extend_90_days.short_description = _("📅 تمديد 90 يوم")

    def export_packages_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="user_packages_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow([_("المستخدم"), _("الباقة"), _("إعلانات متبقية"), _("إعلانات مستخدمة"), _("تاريخ الشراء"), _("تاريخ الانتهاء"), _("نشطة")])
        for pkg in queryset.select_related("user", "package"):
            writer.writerow([
                pkg.user.username, pkg.package.name,
                pkg.ads_remaining, pkg.ads_used,
                pkg.purchase_date.strftime("%Y-%m-%d") if pkg.purchase_date else "",
                pkg.expiry_date.strftime("%Y-%m-%d") if pkg.expiry_date else "",
                "نعم" if pkg.is_active() else "لا",
            ])
        self.message_user(request, _("تم تصدير {} باقة").format(queryset.count()))
        return response

    export_packages_csv.short_description = _("📥 تصدير إلى CSV")

    fieldsets = (
        (
            _("معلومات الباقة"),
            {"fields": ("user", "package", "payment")},
        ),
        (
            _("الاستخدام"),
            {"fields": ("ads_remaining", "ads_used")},
        ),
        (
            _("التواريخ"),
            {"fields": ("purchase_date", "expiry_date")},
        ),
    )


@admin.register(AdUpgradeHistory)
class AdUpgradeHistoryAdmin(admin.ModelAdmin):
    """
    إدارة تاريخ ترقيات الإعلانات
    Admin for Ad Upgrade History
    """

    list_display = (
        "ad",
        "upgrade_type",
        "price_paid",
        "duration_days",
        "start_date",
        "end_date",
        "is_active",
        "days_remaining",
    )
    list_filter = (
        "upgrade_type",
        "is_active",
        "start_date",
        "end_date",
    )
    search_fields = (
        "ad__title",
        "ad__user__username",
    )
    readonly_fields = ("start_date", "created_at")
    date_hierarchy = "start_date"
    actions = ["deactivate_upgrades", "activate_upgrades"]

    def days_remaining(self, obj):
        """Calculate days remaining for active upgrades"""
        if not obj.is_active:
            return "-"

        from django.utils import timezone

        if obj.end_date > timezone.now():
            delta = obj.end_date - timezone.now()
            return f"{delta.days} يوم"
        return "منتهي"

    days_remaining.short_description = _("الأيام المتبقية")

    def deactivate_upgrades(self, request, queryset):
        """Deactivate selected upgrades"""
        count = 0
        for upgrade in queryset.filter(is_active=True):
            upgrade.deactivate()
            count += 1
        self.message_user(request, _(f"تم إلغاء تفعيل {count} ترقية"))

    deactivate_upgrades.short_description = _("إلغاء تفعيل الترقيات المحددة")

    def activate_upgrades(self, request, queryset):
        """Activate selected upgrades"""
        from django.utils import timezone

        updated = queryset.filter(end_date__gte=timezone.now()).update(is_active=True)
        self.message_user(request, _(f"تم تفعيل {updated} ترقية"))

    activate_upgrades.short_description = _("تفعيل الترقيات المحددة")

    fieldsets = (
        (
            _("معلومات الترقية"),
            {"fields": ("ad", "upgrade_type", "is_active")},
        ),
        (
            _("التسعير والمدة"),
            {"fields": ("price_paid", "duration_days")},
        ),
        (
            _("التواريخ"),
            {"fields": ("start_date", "end_date", "created_at")},
        ),
    )


@admin.register(AdReview)
class AdReviewAdmin(admin.ModelAdmin):
    """
    إدارة تقييمات الإعلانات
    Admin for Ad Reviews
    """

    list_display = (
        "ad",
        "user",
        "rating",
        "is_approved",
        "created_at",
    )
    list_filter = (
        "rating",
        "is_approved",
        "created_at",
    )
    search_fields = (
        "ad__title",
        "user__username",
        "user__email",
        "comment",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    date_hierarchy = "created_at"
    actions = ["approve_reviews", "disapprove_reviews"]

    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        updated = queryset.update(is_approved=True)
        # Update ad ratings
        for review in queryset:
            review.update_ad_rating()
        self.message_user(request, _(f"تم قبول {updated} تقييم"))

    approve_reviews.short_description = _("قبول التقييمات المحددة")

    def disapprove_reviews(self, request, queryset):
        """Disapprove selected reviews"""
        updated = queryset.update(is_approved=False)
        # Update ad ratings
        for review in queryset:
            review.update_ad_rating()
        self.message_user(request, _(f"تم رفض {updated} تقييم"))

    disapprove_reviews.short_description = _("رفض التقييمات المحددة")

    fieldsets = (
        (
            _("معلومات التقييم"),
            {"fields": ("ad", "user", "rating", "is_approved")},
        ),
        (
            _("التعليق"),
            {"fields": ("comment",)},
        ),
        (
            _("التواريخ"),
            {"fields": ("created_at", "updated_at")},
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    إدارة معاملات الدفع
    Admin for Payment transactions
    """

    list_display = (
        "get_payment_id",
        "user",
        "get_provider_badge",
        "get_amount_display",
        "status",
        "created_at",
        "completed_at",
    )
    list_filter = (
        "status",
        "provider",
        "currency",
        "created_at",
        "completed_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "provider_transaction_id",
        "description",
        "id",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
        "get_payment_metadata",
    )
    date_hierarchy = "created_at"
    actions = [
        "mark_as_completed",
        "mark_as_failed",
        "mark_as_refunded",
        "export_to_csv",
        "resend_payment_notification",
    ]
    list_per_page = 25

    # Colour map for provider badges
    _PROVIDER_COLORS = {
        "paypal":        ("#003087", "#009cde"),   # PayPal blue
        "paymob":        ("#2563eb", "#dbeafe"),   # blue
        "instapay":      ("#7c3aed", "#ede9fe"),   # purple  (InstaPay brand)
        "wallet":        ("#0891b2", "#cffafe"),   # cyan
        "bank_transfer": ("#15803d", "#dcfce7"),   # green
        "cod":           ("#d97706", "#fef3c7"),   # amber
        "cash":          ("#166534", "#bbf7d0"),   # dark-green
    }

    _PROVIDER_LABELS = {
        "paypal":        "PayPal",
        "paymob":        "Paymob",
        "instapay":      "إنستا باي",
        "wallet":        "محفظة إلكترونية",
        "bank_transfer": "تحويل بنكي",
        "cod":           "الدفع عند الاستلام",
        "cash":          "نقداً",
    }

    def get_payment_id(self, obj):
        return format_html(
            '<span style="font-weight:bold;color:#0066cc;">#{}</span>', obj.id
        )

    get_payment_id.short_description = _("رقم الدفعة")
    get_payment_id.admin_order_field = "id"

    def get_provider_badge(self, obj):
        if not obj.provider:
            return format_html(
                '<span style="color:#9ca3af;font-size:0.82em;">غير محدد</span>'
            )
        fg, bg = self._PROVIDER_COLORS.get(obj.provider, ("#374151", "#f3f4f6"))
        label = self._PROVIDER_LABELS.get(obj.provider, obj.get_provider_display())
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;border-radius:20px;'
            'font-size:0.78em;font-weight:600;white-space:nowrap;">{}</span>',
            bg, fg, label,
        )

    get_provider_badge.short_description = _("مزود الدفع")
    get_provider_badge.admin_order_field = "provider"

    def get_amount_display(self, obj):
        """Display formatted amount with currency"""
        color = "#28a745" if obj.status == "completed" else "#6c757d"
        return format_html(
            '<span style="font-weight: bold; color: {};">{} {}</span>',
            color,
            obj.amount,
            obj.currency,
        )

    get_amount_display.short_description = _("المبلغ")
    get_amount_display.admin_order_field = "amount"

    def get_payment_metadata(self, obj):
        """Display formatted metadata"""
        import json

        if obj.metadata:
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>',
                json.dumps(obj.metadata, indent=2, ensure_ascii=False),
            )
        return "-"

    get_payment_metadata.short_description = _("البيانات الإضافية")

    def mark_as_completed(self, request, queryset):
        """Mark payments as completed - triggers signal to activate package"""
        from django.utils import timezone

        count = 0
        for payment in queryset.filter(status="pending"):
            payment.status = "completed"
            payment.completed_at = timezone.now()
            payment.save()  # Use save() instead of update() to trigger signals
            count += 1

        self.message_user(
            request, _(f"تم تحديد {count} دفعة كمكتملة وتفعيل الباقات المرتبطة")
        )

    mark_as_completed.short_description = _("✓ تحديد كمكتملة")

    def mark_as_failed(self, request, queryset):
        """Mark payments as failed"""
        updated = queryset.filter(status="pending").update(status="failed")
        self.message_user(request, _(f"تم تحديد {updated} دفعة كفاشلة"))

    mark_as_failed.short_description = _("✗ تحديد كفاشلة")

    def mark_as_refunded(self, request, queryset):
        """Mark payments as refunded"""
        from django.utils import timezone

        count = 0
        for payment in queryset.filter(status="completed"):
            payment.status = "refunded"
            if not payment.metadata:
                payment.metadata = {}
            payment.metadata["refunded_at"] = timezone.now().isoformat()
            payment.metadata["refunded_by"] = request.user.username
            payment.save()
            count += 1

        self.message_user(request, _(f"تم استرداد {count} دفعة"))

    mark_as_refunded.short_description = _("↩ تحديد كمستردة")

    def export_to_csv(self, request, queryset):
        """Export payments to CSV"""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="payments_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("\ufeff")  # UTF-8 BOM for Excel compatibility

        writer = csv.writer(response)
        writer.writerow(
            [
                _("رقم الدفعة"),
                _("المستخدم"),
                _("البريد الإلكتروني"),
                _("مزود الدفع"),
                _("رقم المعاملة"),
                _("المبلغ"),
                _("العملة"),
                _("الحالة"),
                _("الوصف"),
                _("تاريخ الإنشاء"),
                _("تاريخ الإكمال"),
            ]
        )

        for payment in queryset:
            writer.writerow(
                [
                    payment.id,
                    payment.user.username,
                    payment.user.email,
                    payment.get_provider_display(),
                    payment.provider_transaction_id,
                    payment.amount,
                    payment.currency,
                    payment.get_status_display(),
                    payment.description,
                    payment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    (
                        payment.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                        if payment.completed_at
                        else ""
                    ),
                ]
            )

        self.message_user(request, _(f"تم تصدير {queryset.count()} دفعة"))
        return response

    export_to_csv.short_description = _("📥 تصدير إلى CSV")

    def resend_payment_notification(self, request, queryset):
        """Resend payment notification to users"""
        from .services.email_service import EmailService
        from .models import Notification

        count = 0
        for payment in queryset.filter(status="completed"):
            try:
                Notification.objects.create(
                    user=payment.user,
                    notification_type=Notification.NotificationType.GENERAL,
                    title=_("تأكيد استلام الدفع"),
                    message=_("تم استلام دفعتك بمبلغ {} {} بنجاح.").format(payment.amount, payment.currency),
                )
                count += 1
            except Exception:
                pass

        self.message_user(request, _(f"تم إرسال إشعارات لـ {count} دفعة"))

    resend_payment_notification.short_description = _("📧 إرسال إشعار للمستخدمين")

    fieldsets = (
        (
            _("معلومات الدفع"),
            {"fields": ("user", "provider", "provider_transaction_id")},
        ),
        (
            _("المبلغ"),
            {"fields": ("amount", "currency")},
        ),
        (
            _("الحالة والوصف"),
            {"fields": ("status", "description")},
        ),
        (
            _("البيانات الإضافية"),
            {
                "fields": ("get_payment_metadata",),
                "classes": ("collapse",),
            },
        ),
        (
            _("التواريخ"),
            {"fields": ("created_at", "updated_at", "completed_at")},
        ),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "notification_type_badge",
        "short_message",
        "is_read",
        "created_at",
    )
    list_filter = ("is_read", "notification_type", "created_at")
    search_fields = ("user__username", "user__email", "title", "message")
    list_editable = ("is_read",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50
    actions = ["mark_as_read", "mark_as_unread"]

    def short_message(self, obj):
        return obj.message[:80] + "…" if len(obj.message) > 80 else obj.message
    short_message.short_description = _("الرسالة")

    def notification_type_badge(self, obj):
        colors = {
            "general": "#6c757d",
            "ad_approved": "#28a745",
            "ad_rejected": "#dc3545",
            "ad_expired": "#fd7e14",
            "package_expired": "#e83e8c",
            "saved_search": "#17a2b8",
        }
        color = colors.get(obj.notification_type, "#6c757d")
        label = obj.get_notification_type_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            color,
            label,
        )
    notification_type_badge.short_description = _("النوع")

    @admin.action(description=_("تحديد كمقروءة"))
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, _(f"تم تحديد {updated} إشعار كمقروء."))

    @admin.action(description=_("تحديد كغير مقروءة"))
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, _(f"تم تحديد {updated} إشعار كغير مقروء."))


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "subject_preview", "status_badge", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject", "phone")
    readonly_fields = ("created_at", "updated_at", "replied_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25
    actions = ["mark_as_read", "mark_as_replied", "mark_as_resolved", "export_messages_csv"]

    fieldsets = (
        (_("معلومات المرسل"), {"fields": ("name", "email", "phone", "user")}),
        (_("محتوى الرسالة"), {"fields": ("subject", "message")}),
        (_("الحالة والمتابعة"), {"fields": ("status", "admin_notes", "replied_at")}),
        (_("التواريخ"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }

    def subject_preview(self, obj):
        return obj.subject[:60] + "…" if len(obj.subject) > 60 else obj.subject

    subject_preview.short_description = _("الموضوع")
    subject_preview.admin_order_field = "subject"

    def status_badge(self, obj):
        colors = {
            ContactMessage.Status.PENDING:  ("#fd7e14", "⏳ قيد الانتظار"),
            ContactMessage.Status.READ:     ("#17a2b8", "👁 مقروءة"),
            ContactMessage.Status.REPLIED:  ("#28a745", "↩ تم الرد"),
            ContactMessage.Status.RESOLVED: ("#6c757d", "✔ محلولة"),
        }
        color, label = colors.get(obj.status, ("#6c757d", obj.get_status_display()))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;'
            'font-size:11px;font-weight:600;white-space:nowrap">{}</span>',
            color, label,
        )

    status_badge.short_description = _("الحالة")
    status_badge.admin_order_field = "status"

    def mark_as_read(self, request, queryset):
        updated = queryset.filter(status=ContactMessage.Status.PENDING).update(status=ContactMessage.Status.READ)
        self.message_user(request, _("{} رسالة تم تحديدها كمقروءة").format(updated))

    mark_as_read.short_description = _("✓ تحديد كمقروءة")

    def mark_as_replied(self, request, queryset):
        from django.utils import timezone
        count = 0
        for msg in queryset.exclude(status=ContactMessage.Status.REPLIED):
            msg.status = ContactMessage.Status.REPLIED
            msg.replied_at = timezone.now()
            msg.save(update_fields=["status", "replied_at"])
            count += 1
        self.message_user(request, _("{} رسالة تم تحديدها كـ 'تم الرد'").format(count))

    mark_as_replied.short_description = _("↩ تحديد كـ تم الرد")

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status=ContactMessage.Status.RESOLVED)
        self.message_user(request, _("{} رسالة تم تحديدها كمحلولة").format(updated))

    mark_as_resolved.short_description = _("✔ تحديد كمحلولة")

    def export_messages_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="contact_messages_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow([_("الاسم"), _("البريد الإلكتروني"), _("الهاتف"), _("الموضوع"), _("الحالة"), _("تاريخ الإرسال")])
        for msg in queryset:
            writer.writerow([
                msg.name, msg.email, msg.phone, msg.subject,
                msg.get_status_display(),
                msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        self.message_user(request, _("تم تصدير {} رسالة").format(queryset.count()))
        return response

    export_messages_csv.short_description = _("📥 تصدير إلى CSV")


# --- Enhanced Models Admin ---


class CustomUserAdminForm(forms.ModelForm):
    """Admin form for User with dynamic city dropdown based on selected country."""

    class Meta:
        from .models import User as _User
        model = _User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance") or getattr(self, "instance", None)

        # Determine country and current city
        country = None
        if "country" in self.data:
            try:
                from content.models import Country as _Country
                country = _Country.objects.get(pk=self.data.get("country"))
            except Exception:
                pass
        elif instance and instance.pk and instance.country:
            country = instance.country

        instance_city = (
            instance.city if (instance and instance.pk and instance.city) else None
        )

        # Build choices for the city ChoiceField
        if country and country.cities:
            city_choices = [("", _("--- اختر المدينة ---"))] + [
                (c, c) for c in country.cities
            ]
            if instance_city and instance_city not in country.cities:
                city_choices.append((instance_city, instance_city))
        elif instance_city:
            city_choices = [("", _("--- اختر المدينة ---")), (instance_city, instance_city)]
        else:
            city_choices = [("", _("--- اختر المدينة ---"))]

        self.fields["city"] = forms.ChoiceField(
            required=False,
            label=_("المدينة"),
            choices=city_choices,
            widget=forms.Select(attrs={"id": "id_city"}),
        )

    class Media:
        js = ("admin/js/user_city_loader.js",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm

    list_display = (
        "username",
        "get_display_name_col",
        "email",
        "profile_type",
        "verification_status",
        "is_active",
        "chat_icon",
    )
    list_filter = ("profile_type", "verification_status", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "company_name", "phone", "mobile")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Profile Information",
            {"fields": ("profile_type", "rank", "phone", "mobile", "whatsapp")},
        ),
        (
            "Company Information",
            {
                "fields": (
                    "company_name",
                    "company_name_ar",
                    "tax_number",
                    "commercial_register",
                )
            },
        ),
        (
            "Location",
            {"fields": ("country", "city", "address", "postal_code")},
        ),
        (
            "Verification",
            {"fields": ("verification_status", "verification_document", "verified_at")},
        ),
        ("Bio", {"fields": ("bio", "bio_ar")}),
        (
            "Communication",
            {"fields": ("chat_link",)},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ("chat_link",)
    actions = [
        "activate_users",
        "deactivate_users",
        "verify_users",
        "unverify_users",
        "export_users_csv",
    ]

    def get_display_name_col(self, obj):
        return obj.get_display_name()
    get_display_name_col.short_description = _("الاسم")
    get_display_name_col.admin_order_field = "first_name"

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} مستخدم تم تفعيله").format(updated))

    activate_users.short_description = _("✓ تفعيل المستخدمين المحددين")

    def deactivate_users(self, request, queryset):
        updated = queryset.filter(is_superuser=False).update(is_active=False)
        self.message_user(request, _("{} مستخدم تم إلغاء تفعيله").format(updated))

    deactivate_users.short_description = _("✗ إلغاء تفعيل المستخدمين المحددين")

    def verify_users(self, request, queryset):
        from django.utils import timezone
        count = 0
        for user in queryset:
            user.verification_status = User.VerificationStatus.VERIFIED
            user.verified_at = timezone.now()
            user.save(update_fields=["verification_status", "verified_at"])
            count += 1
        self.message_user(request, _("{} مستخدم تم توثيقه").format(count))

    verify_users.short_description = _("✔ توثيق المستخدمين المحددين")

    def unverify_users(self, request, queryset):
        updated = queryset.filter(is_superuser=False).update(
            verification_status=User.VerificationStatus.UNVERIFIED
        )
        self.message_user(request, _("{} مستخدم تم إلغاء توثيقه").format(updated))

    unverify_users.short_description = _("✗ إلغاء توثيق المستخدمين المحددين")

    def export_users_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow([
            _("اسم المستخدم"), _("البريد الإلكتروني"), _("الاسم الأول"),
            _("الاسم الأخير"), _("نوع الحساب"), _("حالة التوثيق"),
            _("نشط"), _("تاريخ الانضمام"), _("آخر تسجيل دخول"),
        ])
        for user in queryset:
            writer.writerow([
                user.username, user.email, user.first_name, user.last_name,
                user.get_profile_type_display() if hasattr(user, "get_profile_type_display") else user.profile_type,
                user.get_verification_status_display(),
                "نعم" if user.is_active else "لا",
                user.date_joined.strftime("%Y-%m-%d") if user.date_joined else "",
                user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "",
            ])
        self.message_user(request, _("تم تصدير {} مستخدم").format(queryset.count()))
        return response

    export_users_csv.short_description = _("📥 تصدير المستخدمين إلى CSV")

    def get_urls(self):
        """Add custom URLs for chat functionality"""
        from django.urls import path

        urls = super().get_urls()
        info = self.opts.app_label, self.opts.model_name
        custom_urls = [
            path(
                "start-chat/<int:user_id>/",
                self.admin_site.admin_view(self.start_chat_view),
                name="%s_%s_start_chat" % info,
            ),
        ]
        return custom_urls + urls

    def start_chat_view(self, request, user_id):
        """Create or get chat room and redirect to it"""
        from django.shortcuts import redirect, get_object_or_404
        from django.urls import reverse
        from .models import ChatRoom

        user = get_object_or_404(User, id=user_id)

        # Get or create chat room
        chat_room, created = ChatRoom.objects.get_or_create(
            room_type="publisher_admin", publisher=user, defaults={"is_active": True}
        )

        # Redirect to chat room admin change page
        return redirect(reverse("admin:main_chatroom_change", args=[chat_room.pk]))

    def chat_icon(self, obj):
        """Display a chat icon that opens chat with this user"""
        from django.utils.html import format_html
        from django.urls import reverse

        chat_url = reverse("admin:main_user_start_chat", args=[obj.id])

        return format_html(
            '<a href="{}" style="text-decoration: none; font-size: 18px;" '
            'title="Chat with {}">'
            '<i class="fas fa-comments" style="color: #4CAF50;"></i>'
            "</a>",
            chat_url,
            obj.username,
        )

    chat_icon.short_description = "Chat"

    def chat_link(self, obj):
        """Display chat link in user detail page"""
        from django.utils.html import format_html
        from django.urls import reverse
        from .models import ChatRoom

        if not obj.id:
            return "-"

        try:
            chat_room = ChatRoom.objects.filter(
                room_type="publisher_admin", publisher=obj
            ).first()

            if chat_room:
                chat_url = reverse("admin:main_chatroom_change", args=[chat_room.pk])
                button_text = "Open Existing Chat"
                button_class = "default"
            else:
                chat_url = reverse("admin:main_user_start_chat", args=[obj.id])
                button_text = "Start New Chat"
                button_class = "success"

            return format_html(
                '<a href="{}" class="button {}" style="margin-left: 10px;">'
                '<i class="fas fa-comments"></i> {}'
                "</a>",
                chat_url,
                button_class,
                button_text,
            )
        except Exception as e:
            return format_html(
                '<span style="color: red;">Chat unavailable: {}</span>', str(e)
            )

    chat_link.short_description = "Chat with User"


@admin.register(AdFeaturePrice)
class AdFeaturePriceAdmin(admin.ModelAdmin):
    list_display = ("category", "feature_type", "price", "duration_days", "is_active")
    list_filter = ("feature_type", "is_active", "category")
    search_fields = ("category__name", "category__name_ar")
    list_editable = ("price", "duration_days", "is_active")
    ordering = ("category", "feature_type")

    fieldsets = (
        (_("القسم والميزة"), {"fields": ("category", "feature_type")}),
        (_("التسعير"), {"fields": ("price", "duration_days", "is_active")}),
    )

    class Media:
        js = ("admin/js/category_cascade.js",)


@admin.register(CartSettings)
class CartSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "is_enabled",
        "reservation_percentage",
        "minimum_reservation",
    )
    list_filter = ("is_enabled", "category")
    search_fields = ("category__name", "category__name_ar")
    list_editable = ("is_enabled", "reservation_percentage")

    fieldsets = (
        (_("القسم"), {"fields": ("category", "is_enabled")}),
        (
            _("إعدادات الحجز"),
            {"fields": ("reservation_percentage", "minimum_reservation")},
        ),
    )

    class Media:
        js = ("admin/js/category_cascade.js",)


@admin.register(AdTransaction)
class AdTransactionAdmin(admin.ModelAdmin):
    list_display = ("ad", "user", "transaction_type", "amount", "created_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("ad__title", "user__username", "transaction_id")
    readonly_fields = ("created_at", "transaction_id")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = ["export_transactions_csv"]

    def export_transactions_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="transactions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow([_("الإعلان"), _("المستخدم"), _("نوع المعاملة"), _("المبلغ"), _("رقم المعاملة"), _("التاريخ")])
        for tx in queryset.select_related("ad", "user"):
            writer.writerow([
                tx.ad.title if tx.ad else "",
                tx.user.username if tx.user else "",
                tx.get_transaction_type_display() if hasattr(tx, "get_transaction_type_display") else tx.transaction_type,
                tx.amount,
                tx.transaction_id,
                tx.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        self.message_user(request, _("تم تصدير {} معاملة").format(queryset.count()))
        return response

    export_transactions_csv.short_description = _("📥 تصدير إلى CSV")

    fieldsets = (
        (_("معلومات المعاملة"), {"fields": ("ad", "user", "transaction_type")}),
        (_("المبلغ"), {"fields": ("amount", "transaction_id")}),
        (_("التواريخ"), {"fields": ("created_at",), "classes": ("collapse",)}),
    )


class CustomFieldOptionInline(admin.TabularInline):
    """Inline for custom field options."""

    model = CustomFieldOption
    extra = 2
    fields = ("label_ar", "label_en", "value", "order", "is_active")
    ordering = ("order", "label_ar")
    classes = ("collapse",)
    verbose_name = _("خيار الحقل")
    verbose_name_plural = _("خيارات الحقل (للقوائم المنسدلة)")

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related("custom_field")


class CategoryCustomFieldInline(admin.TabularInline):
    """Inline for associating custom fields with categories and subcategories."""

    model = CategoryCustomField
    extra = 1
    fields = (
        "category",
        "is_required",
        "order",
        "is_active",
        "show_on_card",
        "show_in_filters",
    )
    autocomplete_fields = ["category"]
    classes = ("collapse",)
    verbose_name = _("ربط الحقل بقسم")
    verbose_name_plural = _("الأقسام والأقسام الفرعية المرتبطة بهذا الحقل")

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related("category", "custom_field")


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "label_ar",
        "field_type_badge",
        "is_required",
        "is_active",
        "get_categories_count",
        "created_at",
    )
    list_filter = (
        "field_type",
        "is_required",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "label_ar", "label_en", "help_text")
    list_editable = ("is_active", "is_required")
    ordering = ("name",)
    inlines = [CustomFieldOptionInline, CategoryCustomFieldInline]
    date_hierarchy = "created_at"
    actions = [
        "activate_fields",
        "deactivate_fields",
        "mark_as_required",
        "mark_as_optional",
        "duplicate_fields",
    ]

    fieldsets = (
        (
            _("معلومات أساسية"),
            {
                "fields": ("name", "label_ar", "label_en", "field_type"),
                "description": _(
                    "المعلومات الأساسية للحقل المخصص. يمكن ربط هذا الحقل بعدة أقسام أو أقسام فرعية."
                ),
            },
        ),
        (
            _("إعدادات الحقل"),
            {
                "fields": (
                    "is_required",
                    "is_active",
                    "help_text",
                    "placeholder",
                    "default_value",
                )
            },
        ),
        (
            _("قيود التحقق"),
            {
                "fields": (
                    "min_length",
                    "max_length",
                    "min_value",
                    "max_value",
                    "validation_regex",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def field_type_badge(self, obj):
        """Display field type with colored badge"""
        type_colors = {
            "text": "#007bff",
            "number": "#28a745",
            "email": "#17a2b8",
            "phone": "#ffc107",
            "select": "#6f42c1",
            "checkbox": "#fd7e14",
            "radio": "#e83e8c",
            "textarea": "#20c997",
            "date": "#6610f2",
        }
        color = type_colors.get(obj.field_type, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_field_type_display(),
        )

    field_type_badge.short_description = _("نوع الحقل")
    field_type_badge.admin_order_field = "field_type"

    def get_categories_count(self, obj):
        """Get count of categories this field is linked to"""
        count = obj.categories.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
                count,
            )
        return format_html('<span style="color: #dc3545;">لا يوجد</span>')

    get_categories_count.short_description = _("عدد الأقسام المرتبطة")

    def get_queryset(self, request):
        """Optimize queryset with prefetch"""
        qs = super().get_queryset(request)
        return qs.prefetch_related("categories", "field_options")

    # Admin Actions
    def activate_fields(self, request, queryset):
        """Activate selected custom fields"""
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"تم تفعيل {updated} حقل مخصص"))

    activate_fields.short_description = _("✓ تفعيل الحقول المحددة")

    def deactivate_fields(self, request, queryset):
        """Deactivate selected custom fields"""
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"تم إلغاء تفعيل {updated} حقل مخصص"))

    deactivate_fields.short_description = _("✗ إلغاء تفعيل الحقول المحددة")

    def mark_as_required(self, request, queryset):
        """Mark selected fields as required"""
        updated = queryset.update(is_required=True)
        self.message_user(request, _(f"تم تحديد {updated} حقل كإلزامي"))

    mark_as_required.short_description = _("* تحديد كإلزامي")

    def mark_as_optional(self, request, queryset):
        """Mark selected fields as optional"""
        updated = queryset.update(is_required=False)
        self.message_user(request, _(f"تم تحديد {updated} حقل كاختياري"))

    mark_as_optional.short_description = _("○ تحديد كاختياري")

    def duplicate_fields(self, request, queryset):
        """Duplicate selected custom fields"""
        count = 0
        for field in queryset:
            # Create a copy of the field
            new_field = CustomField.objects.create(
                name=f"{field.name}_copy_{count + 1}",
                label_ar=f"{field.label_ar} (نسخة)",
                label_en=f"{field.label_en} (Copy)" if field.label_en else "",
                field_type=field.field_type,
                is_required=field.is_required,
                is_active=False,  # Set as inactive by default
                help_text=field.help_text,
                placeholder=field.placeholder,
                default_value=field.default_value,
                min_length=field.min_length,
                max_length=field.max_length,
                min_value=field.min_value,
                max_value=field.max_value,
                validation_regex=field.validation_regex,
            )

            # Copy field options if any
            for option in field.field_options.all():
                CustomFieldOption.objects.create(
                    custom_field=new_field,
                    label_ar=option.label_ar,
                    label_en=option.label_en,
                    value=option.value,
                    order=option.order,
                    is_active=option.is_active,
                )

            count += 1

        self.message_user(request, _(f"تم نسخ {count} حقل مخصص بنجاح"))

    duplicate_fields.short_description = _("⎘ نسخ الحقول المحددة")


@admin.register(CustomFieldOption)
class CustomFieldOptionAdmin(admin.ModelAdmin):
    list_display = (
        "custom_field",
        "label_ar",
        "label_en",
        "value",
        "order",
        "is_active",
    )
    list_filter = ("custom_field", "is_active")
    search_fields = ("label_ar", "label_en", "value")
    list_editable = ("order", "is_active")
    ordering = ("custom_field", "order")


@admin.register(CategoryCustomField)
class CategoryCustomFieldAdmin(admin.ModelAdmin):
    list_display = (
        "get_category_display",
        "get_field_display",
        "get_field_type",
        "is_required",
        "order",
        "is_active",
        "show_on_card",
        "show_in_filters",
    )
    list_filter = (
        "is_required",
        "is_active",
        "show_on_card",
        "show_in_filters",
        "custom_field__field_type",
        "category__parent",
    )
    search_fields = (
        "category__name",
        "category__name_ar",
        "custom_field__name",
        "custom_field__label_ar",
    )
    list_editable = (
        "is_required",
        "order",
        "is_active",
        "show_on_card",
        "show_in_filters",
    )
    ordering = ("category__name", "order")
    autocomplete_fields = ["category", "custom_field"]
    actions = [
        "activate_links",
        "deactivate_links",
        "show_on_cards",
        "hide_from_cards",
        "add_to_filters",
        "remove_from_filters",
    ]

    fieldsets = (
        (
            _("ربط الحقل بالقسم"),
            {
                "fields": ("category", "custom_field"),
                "description": _(
                    "حدد القسم أو القسم الفرعي والحقل المخصص المراد ربطهما"
                ),
            },
        ),
        (
            _("إعدادات الحقل"),
            {
                "fields": ("is_required", "order", "is_active"),
            },
        ),
        (
            _("إعدادات العرض"),
            {
                "fields": ("show_on_card", "show_in_filters"),
                "description": _(
                    "تحكم في كيفية عرض هذا الحقل في بطاقات الإعلانات والفلاتر"
                ),
            },
        ),
    )

    def get_category_display(self, obj):
        """Display category with parent info"""
        if obj.category.parent:
            return format_html(
                '<div><strong>{}</strong><br/><small style="color: #666;">└─ {}</small></div>',
                obj.category.parent.name_ar or obj.category.parent.name,
                obj.category.name_ar or obj.category.name,
            )
        return format_html(
            "<strong>{}</strong>",
            obj.category.name_ar or obj.category.name,
        )

    get_category_display.short_description = _("القسم")
    get_category_display.admin_order_field = "category"

    def get_field_display(self, obj):
        """Display field name"""
        return format_html(
            '<strong style="color: #007bff;">{}</strong>',
            obj.custom_field.label_ar or obj.custom_field.name,
        )

    get_field_display.short_description = _("الحقل المخصص")
    get_field_display.admin_order_field = "custom_field"

    def get_field_type(self, obj):
        """Display field type badge"""
        type_colors = {
            "text": "#007bff",
            "number": "#28a745",
            "email": "#17a2b8",
            "phone": "#ffc107",
            "select": "#6f42c1",
            "checkbox": "#fd7e14",
            "radio": "#e83e8c",
            "textarea": "#20c997",
            "date": "#6610f2",
        }
        color = type_colors.get(obj.custom_field.field_type, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 10px; font-size: 10px; font-weight: 600;">{}</span>',
            color,
            obj.custom_field.get_field_type_display(),
        )

    get_field_type.short_description = _("النوع")

    def get_queryset(self, request):
        """Optimize queryset"""
        return (
            super()
            .get_queryset(request)
            .select_related("category", "category__parent", "custom_field")
        )

    # Admin Actions
    def activate_links(self, request, queryset):
        """Activate selected category-field links"""
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"تم تفعيل {updated} ربط"))

    activate_links.short_description = _("✓ تفعيل الروابط المحددة")

    def deactivate_links(self, request, queryset):
        """Deactivate selected category-field links"""
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"تم إلغاء تفعيل {updated} ربط"))

    deactivate_links.short_description = _("✗ إلغاء تفعيل الروابط المحددة")

    def show_on_cards(self, request, queryset):
        """Show fields on ad cards"""
        updated = queryset.update(show_on_card=True)
        self.message_user(request, _(f"سيتم عرض {updated} حقل على بطاقات الإعلانات"))

    show_on_cards.short_description = _("📇 إظهار على البطاقات")

    def hide_from_cards(self, request, queryset):
        """Hide fields from ad cards"""
        updated = queryset.update(show_on_card=False)
        self.message_user(request, _(f"تم إخفاء {updated} حقل من بطاقات الإعلانات"))

    hide_from_cards.short_description = _("🚫 إخفاء من البطاقات")

    def add_to_filters(self, request, queryset):
        """Add fields to filter sidebar"""
        updated = queryset.update(show_in_filters=True)
        self.message_user(request, _(f"تمت إضافة {updated} حقل للفلاتر"))

    add_to_filters.short_description = _("🔍 إضافة للفلاتر")

    def remove_from_filters(self, request, queryset):
        """Remove fields from filter sidebar"""
        updated = queryset.update(show_in_filters=False)
        self.message_user(request, _(f"تمت إزالة {updated} حقل من الفلاتر"))

    remove_from_filters.short_description = _("❌ إزالة من الفلاتر")


@admin.register(UserVerificationRequest)
class UserVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at", "reviewed_at", "reviewed_by")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("user", "status", "reviewed_by", "reviewed_at", "created_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = []

    fieldsets = (
        (_("معلومات الطلب"), {"fields": ("user", "status")}),
        (_("مراجعة الطلب"), {"fields": ("reviewed_by", "reviewed_at")}),
        (_("التواريخ"), {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        "ip_address",
        "user",
        "device_type",
        "page_views",
        "first_visit",
        "last_activity",
        "is_online",
    )
    list_filter = ("device_type", "first_visit", "last_activity")
    search_fields = ("ip_address", "user__username", "page_url")
    readonly_fields = ("first_visit", "last_activity", "session_key", "user_agent")
    date_hierarchy = "first_visit"

    actions = ["clear_old_visitors", "export_visitors_csv"]

    def is_online(self, obj):
        return obj.is_online

    is_online.boolean = True
    is_online.short_description = _("متصل الآن")

    def clear_old_visitors(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=30)
        deleted, _ = queryset.filter(last_activity__lt=cutoff).delete()
        self.message_user(request, _("تم حذف {} سجل زيارة قديم (أكثر من 30 يوم)").format(deleted))

    clear_old_visitors.short_description = _("🗑 حذف السجلات الأقدم من 30 يوم")

    def export_visitors_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="visitors_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow([_("IP"), _("المستخدم"), _("الجهاز"), _("الدولة"), _("عدد المشاهدات"), _("أول زيارة"), _("آخر نشاط")])
        for v in queryset:
            writer.writerow([
                v.ip_address,
                v.user.username if v.user else "",
                v.device_type,
                v.country,
                v.page_views,
                v.first_visit.strftime("%Y-%m-%d %H:%M") if v.first_visit else "",
                v.last_activity.strftime("%Y-%m-%d %H:%M") if v.last_activity else "",
            ])
        self.message_user(request, _("تم تصدير {} سجل زيارة").format(queryset.count()))
        return response

    export_visitors_csv.short_description = _("📥 تصدير إلى CSV")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_active",
        "subscribed_at",
        "unsubscribed_at",
    )
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at", "unsubscribed_at", "ip_address", "user_agent")
    date_hierarchy = "subscribed_at"
    actions = ["activate_subscribers", "deactivate_subscribers", "export_emails"]

    fieldsets = (
        (
            None,
            {"fields": ("email", "is_active")},
        ),
        (
            _("Subscription Information"),
            {
                "fields": ("subscribed_at", "unsubscribed_at"),
            },
        ),
        (
            _("Technical Information"),
            {
                "fields": ("ip_address", "user_agent"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path(
                "send/",
                self.admin_site.admin_view(self.send_newsletter_view),
                name="newslettersubscriber_send",
            ),
            path(
                "template-preview/<int:pk>/",
                self.admin_site.admin_view(self.template_preview_view),
                name="newslettersubscriber_template_preview",
            ),
        ]
        return custom + urls

    def changelist_view(self, request, extra_context=None):
        from django.urls import reverse
        extra_context = extra_context or {}
        extra_context["send_newsletter_url"] = reverse("admin:newslettersubscriber_send")
        extra_context["active_count"] = NewsletterSubscriber.objects.filter(is_active=True).count()
        return super().changelist_view(request, extra_context=extra_context)

    def template_preview_view(self, request, pk):
        """Return template subject+body as JSON for AJAX preview."""
        import json
        from django.http import JsonResponse
        try:
            tmpl = EmailTemplate.objects.get(pk=pk, is_active=True)
            return JsonResponse({"subject": tmpl.subject_ar or tmpl.subject, "body": tmpl.body_ar or tmpl.body})
        except EmailTemplate.DoesNotExist:
            return JsonResponse({"subject": "", "body": ""})

    def send_newsletter_view(self, request):
        from django.template.response import TemplateResponse
        from django.contrib import messages as dj_messages
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        from django.utils.html import strip_tags

        templates = EmailTemplate.objects.filter(is_active=True).order_by("key")

        if request.method == "POST":
            subject = request.POST.get("subject", "").strip()
            body_html = request.POST.get("body_html", "").strip()
            test_mode = request.POST.get("test_mode") == "1"

            if not subject:
                dj_messages.error(request, "الموضوع مطلوب.")
            elif not body_html:
                dj_messages.error(request, "محتوى الرسالة مطلوب.")
            else:
                # Collect recipients
                if test_mode:
                    from django.conf import settings as dj_settings
                    recipients = [dj_settings.DEFAULT_FROM_EMAIL]
                else:
                    main_emails = set(
                        NewsletterSubscriber.objects.filter(is_active=True)
                        .values_list("email", flat=True)
                    )
                    try:
                        from content.models import Newsletter as ContentNewsletter
                        content_emails = set(
                            ContentNewsletter.objects.filter(is_active=True, receive_email=True)
                            .values_list("email", flat=True)
                        )
                    except Exception:
                        content_emails = set()
                    recipients = list(main_emails | content_emails)

                if not recipients:
                    dj_messages.warning(request, "لا يوجد مشتركون نشطون.")
                else:
                    from main.services.email_service import EmailService
                    from django.conf import settings as dj_settings
                    from django.core.mail import send_mail

                    plain = strip_tags(body_html)
                    success_count = 0
                    fail_count = 0

                    if test_mode:
                        ok = EmailService.send_email(
                            to_emails=recipients,
                            subject=f"[TEST] {subject}",
                            html_content=body_html,
                            text_content=plain,
                        )
                        if ok:
                            success_count = 1
                        else:
                            fail_count = 1
                    else:
                        # Send via BCC in batches of 100
                        batch_size = 100
                        for i in range(0, len(recipients), batch_size):
                            batch = recipients[i:i + batch_size]
                            try:
                                send_mail(
                                    subject=subject,
                                    message=plain,
                                    from_email=dj_settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=[dj_settings.DEFAULT_FROM_EMAIL],
                                    bcc=batch,
                                    html_message=body_html,
                                    fail_silently=False,
                                )
                                success_count += len(batch)
                            except Exception as exc:
                                fail_count += len(batch)
                                import logging
                                logging.getLogger(__name__).error("Newsletter batch send failed: %s", exc)

                    if success_count:
                        msg = f"تم إرسال النشرة بنجاح إلى {success_count} مشترك." if not test_mode else "تم إرسال رسالة اختبار بنجاح."
                        dj_messages.success(request, msg)
                    if fail_count:
                        dj_messages.error(request, f"فشل الإرسال لـ {fail_count} مشترك.")

                    return HttpResponseRedirect(reverse("admin:newslettersubscriber_send"))

        context = {
            **self.admin_site.each_context(request),
            "title": "إرسال النشرة البريدية",
            "email_templates": templates,
            "active_count": NewsletterSubscriber.objects.filter(is_active=True).count(),
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/main/newslettersubscriber/send_newsletter.html", context)

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, _(f"تم تفعيل {updated} مشترك بنجاح"))

    activate_subscribers.short_description = _("تفعيل المشتركين المحددين")

    def deactivate_subscribers(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, _(f"تم إلغاء تفعيل {updated} مشترك بنجاح"))

    deactivate_subscribers.short_description = _("إلغاء تفعيل المشتركين المحددين")

    def export_emails(self, request, queryset):
        from django.http import HttpResponse
        import csv

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="newsletter_subscribers.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["Email", "Active", "Subscribed At", "Unsubscribed At"])

        for subscriber in queryset:
            writer.writerow(
                [
                    subscriber.email,
                    "Yes" if subscriber.is_active else "No",
                    subscriber.subscribed_at,
                    subscriber.unsubscribed_at or "",
                ]
            )

        return response

    export_emails.short_description = _("تصدير البريد الإلكتروني للمشتركين المحددين")


@admin.register(AdReport)
class AdReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "report_type_badge",
        "status_badge",
        "reporter_info",
        "reported_target",
        "created_at",
        "reviewed_by",
    )
    list_filter = ("status", "report_type", "created_at")
    search_fields = (
        "description",
        "reporter__username",
        "reported_ad__title",
        "reported_user__username",
    )
    readonly_fields = ("created_at", "updated_at", "resolved_at")
    list_per_page = 20
    date_hierarchy = "created_at"
    actions = ["mark_as_reviewing", "mark_as_resolved", "mark_as_rejected_bulk"]

    def mark_as_reviewing(self, request, queryset):
        updated = queryset.filter(status="pending").update(status="reviewing")
        self.message_user(request, _("{} بلاغ تم تحديده كـ 'قيد المراجعة'").format(updated))

    mark_as_reviewing.short_description = _("👁 تحديد كـ قيد المراجعة")

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        count = 0
        for report in queryset.exclude(status="resolved"):
            report.status = "resolved"
            report.resolved_at = timezone.now()
            if not report.reviewed_by:
                report.reviewed_by = request.user
            report.save(update_fields=["status", "resolved_at", "reviewed_by"])
            count += 1
        self.message_user(request, _("{} بلاغ تم تحديده كمحلول").format(count))

    mark_as_resolved.short_description = _("✅ تحديد كمحلول")

    def mark_as_rejected_bulk(self, request, queryset):
        from django.utils import timezone
        count = 0
        for report in queryset.exclude(status="rejected"):
            report.status = "rejected"
            report.resolved_at = timezone.now()
            if not report.reviewed_by:
                report.reviewed_by = request.user
            report.save(update_fields=["status", "resolved_at", "reviewed_by"])
            count += 1
        self.message_user(request, _("{} بلاغ تم رفضه").format(count))

    mark_as_rejected_bulk.short_description = _("❌ رفض البلاغات المحددة")

    fieldsets = (
        (
            "معلومات البلاغ",
            {
                "fields": (
                    "reporter",
                    "report_type",
                    "status",
                )
            },
        ),
        (
            "المبلغ عنه",
            {
                "fields": (
                    "reported_ad",
                    "reported_user",
                )
            },
        ),
        (
            "التفاصيل",
            {
                "fields": (
                    "description",
                    "evidence_url",
                )
            },
        ),
        (
            "ملاحظات الإدارة",
            {
                "fields": (
                    "admin_notes",
                    "reviewed_by",
                )
            },
        ),
        (
            "التواريخ",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "resolved_at",
                )
            },
        ),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "reviewed_by":
            kwargs["queryset"] = User.objects.filter(
                models.Q(is_staff=True) | models.Q(is_superuser=True)
            ).order_by("username")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    _REPORT_TYPE_META = {
        "ad_content":    ("#dc3545", "🚫", "محتوى غير لائق"),
        "fraud":         ("#fd7e14", "💰", "احتيال أو نصب"),
        "spam":          ("#e9a800", "📩", "إعلان متكرر / سبام"),
        "wrong_category":("#0891b2", "📂", "قسم خاطئ"),
        "user_behavior": ("#d63384", "👤", "سلوك غير لائق"),
        "fake_info":     ("#6610f2", "⚠️", "معلومات مضللة"),
        "other":         ("#6c757d", "📋", "أخرى"),
    }

    def report_type_badge(self, obj):
        if not obj.report_type:
            return format_html(
                '<span style="background:#6c757d;color:white;padding:3px 10px;'
                'border-radius:12px;font-size:11px;font-weight:600;">❓ غير محدد</span>'
            )
        color, icon, label = self._REPORT_TYPE_META.get(
            obj.report_type,
            ("#6c757d", "📋", obj.get_report_type_display() or obj.report_type),
        )
        # Short description preview below the badge
        desc = obj.description[:60] + "…" if len(obj.description) > 60 else obj.description
        return format_html(
            '<div>'
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;'
            'font-size:11px;font-weight:600;white-space:nowrap;">{} {}</span>'
            '<br><small style="color:#6c757d;font-size:11px;">{}</small>'
            '</div>',
            color, icon, label, desc,
        )

    report_type_badge.short_description = "نوع البلاغ / الوصف"

    def status_badge(self, obj):
        colors = {
            "pending": "#ffc107",
            "reviewing": "#0dcaf0",
            "resolved": "#198754",
            "rejected": "#dc3545",
        }
        icons = {
            "pending": "⏳",
            "reviewing": "👁️",
            "resolved": "✅",
            "rejected": "❌",
        }
        color = colors.get(obj.status, "#6c757d")
        icon = icons.get(obj.status, "")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{} {}</span>',
            color,
            icon,
            obj.get_status_display(),
        )

    status_badge.short_description = "الحالة"

    def reporter_info(self, obj):
        if obj.reporter:
            verified = "✓" if obj.reporter.is_verified else ""
            return format_html(
                "<strong>{}</strong> {}",
                obj.reporter.username,
                verified,
            )
        return format_html('<span style="color: #6c757d;">غير معروف</span>')

    reporter_info.short_description = "المبلغ"

    def reported_target(self, obj):
        if obj.reported_ad:
            return format_html(
                '<div><strong style="color: #0d6efd;">📢 إعلان:</strong><br/>'
                '<a href="{}" target="_blank" style="color: #198754;">{}</a><br/>'
                '<small style="color: #6c757d;">بواسطة: {}</small></div>',
                obj.reported_ad.get_absolute_url(),
                (
                    obj.reported_ad.title[:40] + "..."
                    if len(obj.reported_ad.title) > 40
                    else obj.reported_ad.title
                ),
                obj.reported_ad.user.username,
            )
        elif obj.reported_user:
            return format_html(
                '<div><strong style="color: #dc3545;">👤 مستخدم:</strong><br/>{}</div>',
                obj.reported_user.username,
            )
        return format_html('<span style="color: #6c757d;">غير محدد</span>')

    reported_target.short_description = "المبلغ عنه"

    def description_preview(self, obj):
        max_length = 80
        if len(obj.description) > max_length:
            text = obj.description[:max_length] + "..."
        else:
            text = obj.description

        evidence = ""
        if obj.evidence_url:
            evidence = f'<br/><a href="{obj.evidence_url}" target="_blank" style="color: #0dcaf0; font-size: 11px;">🔗 دليل مرفق</a>'

        return format_html(
            '<div style="max-width: 300px;">{}{}</div>',
            text,
            evidence,
        )

    description_preview.short_description = "الوصف"

    def save_model(self, request, obj, form, change):
        """Auto-set reviewed_by when status changes to resolved"""
        if obj.status == "resolved" and not obj.reviewed_by:
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)


# ===========================
# ORDER ADMIN
# ===========================


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("ad", "price")
    can_delete = False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "used_count", "max_uses", "valid_from", "valid_until", "is_active")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)
    readonly_fields = ("used_count",)
    ordering = ("-created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "get_order_number_display",
        "user",
        "full_name",
        "phone",
        "city",
        "get_total_amount_display",
        "get_payment_status_display",
        "get_status_display_badge",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "payment_method",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "order_number",
        "user__username",
        "user__email",
        "full_name",
        "phone",
        "address",
        "city",
    )
    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
        "get_order_summary",
        "get_payment_info",
    )
    inlines = [OrderItemInline]
    list_per_page = 25
    actions = [
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
        "mark_payment_as_paid",
        "mark_payment_as_unpaid",
        "mark_payment_as_refunded",
        "confirm_cod_payment",
        "record_partial_payment",
        "export_orders_to_csv",
        "send_order_notification",
        "send_payment_reminder",
    ]

    def get_order_number_display(self, obj):
        """Display formatted order number"""
        return format_html(
            '<span style="font-weight: bold; color: #0066cc; font-family: monospace;">{}</span>',
            obj.order_number,
        )

    get_order_number_display.short_description = _("رقم الطلب")
    get_order_number_display.admin_order_field = "order_number"

    def get_total_amount_display(self, obj):
        from main.templatetags.idrissimart_tags import CURRENCY_SYMBOLS
        sym = CURRENCY_SYMBOLS.get(obj.currency, obj.currency)
        return format_html(
            '<div style="text-align: right;">'
            '<span style="font-weight:bold;color:#28a745;">{} {}</span><br>'
            '<small style="color:#6c757d;">مدفوع: {} {}</small>'
            '</div>',
            f"{float(obj.total_amount):.2f}", sym,
            f"{float(obj.paid_amount):.2f}", sym,
        )

    get_total_amount_display.short_description = _("المبلغ")
    get_total_amount_display.admin_order_field = "total_amount"

    def get_payment_status_display(self, obj):
        """Display payment status with badge"""
        colors = {
            "paid": "#28a745",
            "partial": "#ffc107",
            "unpaid": "#dc3545",
            "refunded": "#6c757d",
        }
        color = colors.get(obj.payment_status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display(),
        )

    get_payment_status_display.short_description = _("حالة الدفع")
    get_payment_status_display.admin_order_field = "payment_status"

    def get_status_display_badge(self, obj):
        """Display order status with colored badge"""
        colors = {
            "pending": "#ffc107",
            "processing": "#17a2b8",
            "shipped": "#007bff",
            "delivered": "#28a745",
            "cancelled": "#dc3545",
            "refunded": "#6c757d",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    get_status_display_badge.short_description = _("حالة الطلب")
    get_status_display_badge.admin_order_field = "status"

    def get_order_summary(self, obj):
        if not obj or not obj.pk:
            return "-"
        from main.templatetags.idrissimart_tags import CURRENCY_SYMBOLS
        sym = CURRENCY_SYMBOLS.get(obj.currency, obj.currency)

        rows = "".join(
            f"<tr>"
            f"<td style='padding:4px 12px 4px 4px;'>{item.ad.title if item.ad else '—'}</td>"
            f"<td style='padding:4px;text-align:left;font-weight:600;'>{float(item.price):.2f} {sym}</td>"
            f"</tr>"
            for item in obj.items.select_related("ad").all()
        )
        items_table = mark_safe(
            f"<table style='border-collapse:collapse;font-size:0.9em;width:100%;'>"
            f"<thead><tr>"
            f"<th style='padding:4px 12px 4px 4px;color:#6c757d;font-weight:600;text-align:right;'>المنتج</th>"
            f"<th style='padding:4px;color:#6c757d;font-weight:600;text-align:left;'>السعر</th>"
            f"</tr></thead>"
            f"<tbody>{rows}</tbody>"
            f"</table>"
        )

        return format_html(
            '<div style="background:#f8f9fa;padding:15px;border-radius:6px;font-size:0.92em;">'
            '<p style="margin:0 0 8px;font-weight:700;">عدد العناصر: {}</p>'
            '{}'
            '<hr style="margin:10px 0;border-color:#dee2e6;">'
            '<p style="margin:4px 0;">رسوم التوصيل: <strong>{} {}</strong></p>'
            '<p style="margin:4px 0;font-size:1.05em;">الإجمالي: '
            '<strong style="color:#28a745;">{} {}</strong></p>'
            '</div>',
            obj.get_items_count(),
            items_table,
            f"{float(obj.delivery_fee):.2f}", sym,
            f"{float(obj.total_amount):.2f}", sym,
        )

    get_order_summary.short_description = _("ملخص الطلب")

    def get_payment_info(self, obj):
        """Display payment information"""
        if not obj or not obj.pk:
            return "-"
        from main.templatetags.idrissimart_tags import CURRENCY_SYMBOLS
        currency_symbol = CURRENCY_SYMBOLS.get(obj.currency, obj.currency)
        percentage = obj.get_payment_percentage() or 0
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            '<h4 style="margin-top: 0;">معلومات الدفع</h4>'
            "<p><strong>طريقة الدفع:</strong> {}</p>"
            "<p><strong>حالة الدفع:</strong> {}</p>"
            "<p><strong>المبلغ الإجمالي:</strong> {} {}</p>"
            '<p><strong>المبلغ المدفوع:</strong> <span style="color: #28a745;">{} {}</span></p>'
            '<p><strong>المبلغ المتبقي:</strong> <span style="color: #dc3545;">{} {}</span></p>'
            '<div style="margin-top: 10px;">'
            '<div style="background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden;">'
            '<div style="background: #28a745; height: 100%; width: {}%; transition: width 0.3s;"></div>'
            "</div>"
            '<small style="color: #6c757d;">نسبة السداد: {:.1f}%</small>'
            "</div>"
            "</div>",
            obj.get_payment_method_display(),
            obj.get_payment_status_display(),
            obj.total_amount,
            currency_symbol,
            obj.paid_amount,
            currency_symbol,
            obj.remaining_amount,
            currency_symbol,
            percentage,
            percentage,
        )

    get_payment_info.short_description = _("معلومات الدفع")

    # Admin Actions
    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing"""
        updated = queryset.filter(status="pending").update(status="processing")
        self.message_user(request, _(f"تم تحديث {updated} طلب إلى قيد المعالجة"))

    mark_as_processing.short_description = _("⚙ تحديد كـ قيد المعالجة")

    def mark_as_shipped(self, request, queryset):
        """Mark selected orders as shipped"""
        updated = queryset.filter(status="processing").update(status="shipped")
        self.message_user(request, _(f"تم تحديث {updated} طلب إلى تم الشحن"))

    mark_as_shipped.short_description = _("📦 تحديد كـ تم الشحن")

    def mark_as_delivered(self, request, queryset):
        """Mark selected orders as delivered"""
        updated = queryset.filter(status="shipped").update(status="delivered")
        self.message_user(request, _(f"تم تحديث {updated} طلب إلى تم التسليم"))

    mark_as_delivered.short_description = _("✓ تحديد كـ تم التسليم")

    def mark_as_cancelled(self, request, queryset):
        """Mark selected orders as cancelled"""
        updated = queryset.update(status="cancelled")
        self.message_user(request, _(f"تم إلغاء {updated} طلب"))

    mark_as_cancelled.short_description = _("✗ إلغاء الطلبات")

    # Payment Status Actions
    def mark_payment_as_paid(self, request, queryset):
        """Mark order payment as fully paid"""
        count = 0
        for order in queryset:
            if order.payment_status != "paid":
                order.paid_amount = order.total_amount
                order.payment_status = "paid"
                order.remaining_amount = 0
                order.save()
                count += 1
        self.message_user(
            request, _(f"تم تحديث حالة الدفع لـ {count} طلب إلى مدفوع بالكامل")
        )

    mark_payment_as_paid.short_description = _("💰 تحديد الدفع كمدفوع بالكامل")

    def mark_payment_as_unpaid(self, request, queryset):
        """Mark order payment as unpaid"""
        count = 0
        for order in queryset:
            if order.payment_status != "unpaid":
                order.paid_amount = 0
                order.payment_status = "unpaid"
                order.remaining_amount = order.total_amount
                order.save()
                count += 1
        self.message_user(
            request, _(f"تم تحديث حالة الدفع لـ {count} طلب إلى غير مدفوع")
        )

    mark_payment_as_unpaid.short_description = _("⏸ تحديد الدفع كغير مدفوع")

    def mark_payment_as_refunded(self, request, queryset):
        """Mark order payment as refunded"""
        from django.utils import timezone

        count = 0
        for order in queryset.filter(payment_status="paid"):
            order.payment_status = "refunded"
            order.status = "refunded"
            # Add refund info to notes
            refund_note = f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] تم استرداد المبلغ {order.paid_amount} من قبل {request.user.username}"
            order.notes = (order.notes or "") + refund_note
            order.save()
            count += 1

        self.message_user(request, _(f"تم استرداد {count} طلب"))

    mark_payment_as_refunded.short_description = _("↩ استرداد المبلغ")

    def confirm_cod_payment(self, request, queryset):
        """Confirm Cash on Delivery payment"""
        from django.utils import timezone

        count = 0
        for order in queryset.filter(payment_method="cod", payment_status="unpaid"):
            order.paid_amount = order.total_amount
            order.payment_status = "paid"
            order.remaining_amount = 0
            # Add confirmation note
            confirm_note = f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] تم تأكيد استلام الدفع عند التسليم من قبل {request.user.username}"
            order.notes = (order.notes or "") + confirm_note
            order.save()
            count += 1

        self.message_user(
            request, _(f"تم تأكيد استلام الدفع لـ {count} طلب (دفع عند الاستلام)")
        )

    confirm_cod_payment.short_description = _("✓ تأكيد الدفع عند الاستلام")

    def send_payment_reminder(self, request, queryset):
        """Send payment reminder to customers with unpaid orders"""
        count = 0
        for order in queryset.filter(payment_status__in=["unpaid", "partial"]):
            # TODO: Implement email/SMS notification
            count += 1
        self.message_user(request, _(f"تم إرسال تذكير دفع لـ {count} طلب"))

    send_payment_reminder.short_description = _("📧 إرسال تذكير بالدفع")

    def record_partial_payment(self, request, queryset):
        """Record partial payment for orders - opens intermediate page"""
        from django.shortcuts import render
        from django import forms
        from decimal import Decimal

        class PartialPaymentForm(forms.Form):
            amount = forms.DecimalField(
                label=_("المبلغ المدفوع"),
                max_digits=10,
                decimal_places=2,
                min_value=Decimal("0.01"),
                widget=forms.NumberInput(
                    attrs={"class": "form-control", "step": "0.01"}
                ),
            )
            payment_note = forms.CharField(
                label=_("ملاحظة الدفع"),
                required=False,
                widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            )

        if "apply" in request.POST:
            form = PartialPaymentForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data["amount"]
                payment_note = form.cleaned_data["payment_note"]
                from django.utils import timezone

                count = 0
                for order in queryset:
                    if order.payment_status in ["unpaid", "partial"]:
                        # Add the partial payment
                        order.paid_amount += amount

                        # Ensure we don't exceed total
                        if order.paid_amount > order.total_amount:
                            order.paid_amount = order.total_amount

                        order.remaining_amount = order.total_amount - order.paid_amount

                        # Update payment status
                        if order.paid_amount >= order.total_amount:
                            order.payment_status = "paid"
                        elif order.paid_amount > 0:
                            order.payment_status = "partial"

                        # Add note
                        from main.templatetags.idrissimart_tags import CURRENCY_SYMBOLS
                        currency_symbol = CURRENCY_SYMBOLS.get(order.currency, order.currency)
                        note = f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] دفعة جزئية: {amount} {currency_symbol} من قبل {request.user.username}"
                        if payment_note:
                            note += f" - {payment_note}"
                        order.notes = (order.notes or "") + note

                        order.save()
                        count += 1

                self.message_user(
                    request, _(f"تم تسجيل دفعة جزئية بمبلغ {amount} {currency_symbol} لـ {count} طلب")
                )
                return None
        else:
            form = PartialPaymentForm()

        return render(
            request,
            "admin/order_partial_payment.html",
            {
                "orders": queryset,
                "form": form,
                "title": _("تسجيل دفعة جزئية"),
                "opts": self.model._meta,
            },
        )

    record_partial_payment.short_description = _("💵 تسجيل دفعة جزئية")

    def export_orders_to_csv(self, request, queryset):
        """Export orders to CSV"""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="orders_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("\ufeff")  # UTF-8 BOM for Excel compatibility

        writer = csv.writer(response)
        writer.writerow(
            [
                _("رقم الطلب"),
                _("المستخدم"),
                _("الاسم الكامل"),
                _("الهاتف"),
                _("المدينة"),
                _("العنوان"),
                _("المبلغ الإجمالي"),
                _("المبلغ المدفوع"),
                _("المبلغ المتبقي"),
                _("طريقة الدفع"),
                _("حالة الدفع"),
                _("حالة الطلب"),
                _("رسوم التوصيل"),
                _("تاريخ الإنشاء"),
                _("ملاحظات"),
            ]
        )

        for order in queryset:
            writer.writerow(
                [
                    order.order_number,
                    order.user.username,
                    order.full_name,
                    order.phone,
                    order.city,
                    order.address,
                    order.total_amount,
                    order.paid_amount,
                    order.remaining_amount,
                    order.get_payment_method_display(),
                    order.get_payment_status_display(),
                    order.get_status_display(),
                    order.delivery_fee,
                    order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    order.notes,
                ]
            )

        self.message_user(request, _(f"تم تصدير {queryset.count()} طلب"))
        return response

    export_orders_to_csv.short_description = _("📥 تصدير إلى CSV")

    def send_order_notification(self, request, queryset):
        """Send order status notification to customers"""
        from .services.email_service import EmailService

        count = 0
        for order in queryset.select_related("user"):
            try:
                EmailService.send_order_status_update_email(
                    email=order.user.email,
                    order=order,
                    user_name=order.user.get_full_name() or order.user.username,
                )
                count += 1
            except Exception:
                pass
        self.message_user(request, _(f"تم إرسال إشعارات لـ {count} طلب"))

    send_order_notification.short_description = _("📧 إرسال إشعار للعملاء")

    fieldsets = (
        (
            _("معلومات الطلب"),
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "get_order_summary",
                )
            },
        ),
        (
            _("معلومات الدفع"),
            {
                "fields": (
                    "currency",
                    "payment_method",
                    "payment_status",
                    "total_amount",
                    "paid_amount",
                    "remaining_amount",
                    "delivery_fee",
                    "get_payment_info",
                    "transaction_photo",
                )
            },
        ),
        (
            _("معلومات التوصيل"),
            {"fields": ("full_name", "phone", "address", "city", "postal_code")},
        ),
        (
            _("ملاحظات ومعلومات إضافية"),
            {
                "fields": ("notes", "expires_at"),
                "classes": ("collapse",),
            },
        ),
        (
            _("التواريخ"),
            {"fields": ("created_at", "updated_at")},
        ),
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("ad", "quantity", "get_total_price_display", "added_at")
    fields = ("ad", "quantity", "get_total_price_display", "added_at")
    can_delete = True

    def get_total_price_display(self, obj):
        try:
            from main.templatetags.idrissimart_tags import CURRENCY_SYMBOLS
            currency = obj.ad.country.currency if obj.ad and obj.ad.country else "EGP"
            symbol = CURRENCY_SYMBOLS.get(currency, currency)
            return f"{obj.get_total_price()} {symbol}"
        except Exception:
            return obj.get_total_price()
    get_total_price_display.short_description = _("المجموع")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "items_count_badge",
        "total_amount_display",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    inlines = [CartItemInline]
    date_hierarchy = "created_at"

    def items_count_badge(self, obj):
        count = obj.get_items_count()
        color = "#28a745" if count > 0 else "#6c757d"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600">{}</span>',
            color, count,
        )
    items_count_badge.short_description = _("العناصر")

    def total_amount_display(self, obj):
        total = obj.get_total_amount()
        return format_html('<strong style="color:#28a745">{}</strong>', total)
    total_amount_display.short_description = _("الإجمالي")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart_user",
        "ad",
        "quantity",
        "total_price_display",
        "added_at",
    )
    list_filter = ("added_at",)
    search_fields = ("cart__user__username", "cart__user__email", "ad__title")
    readonly_fields = ("added_at",)
    ordering = ("-added_at",)
    date_hierarchy = "added_at"

    def cart_user(self, obj):
        return obj.cart.user.username
    cart_user.short_description = _("المستخدم")
    cart_user.admin_order_field = "cart__user__username"

    def total_price_display(self, obj):
        try:
            from main.templatetags.idrissimart_tags import CURRENCY_SYMBOLS
            currency = obj.ad.country.currency if obj.ad and obj.ad.country else "EGP"
            symbol = CURRENCY_SYMBOLS.get(currency, currency)
            return f"{obj.get_total_price()} {symbol}"
        except Exception:
            return obj.get_total_price()
    total_price_display.short_description = _("المجموع")


# ─── Wishlist ────────────────────────────────────────────────────────────────

class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ("ad_link", "ad_status", "added_at")
    fields = ("ad_link", "ad_status", "added_at")
    can_delete = True

    def ad_link(self, obj):
        if not obj.ad:
            return "-"
        url = obj.ad.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
            url,
            obj.ad.title,
        )
    ad_link.short_description = _("الإعلان")

    def ad_status(self, obj):
        if not obj.ad:
            return "-"
        status = obj.ad.status
        colors = {
            "active": "#28a745",
            "pending": "#fd7e14",
            "rejected": "#dc3545",
            "expired": "#6c757d",
        }
        color = colors.get(status, "#6c757d")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 7px;border-radius:10px;font-size:11px">{}</span>',
            color, obj.ad.get_status_display(),
        )
    ad_status.short_description = _("حالة الإعلان")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "user_email", "items_count_badge", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    inlines = [WishlistItemInline]
    date_hierarchy = "created_at"

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _("البريد الإلكتروني")
    user_email.admin_order_field = "user__email"

    def items_count_badge(self, obj):
        count = obj.get_items_count()
        color = "#4b315e" if count > 0 else "#6c757d"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600">{}</span>',
            color, count,
        )
    items_count_badge.short_description = _("المحفوظات")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("wishlist_user", "ad", "ad_status_badge", "added_at")
    list_filter = ("added_at",)
    search_fields = (
        "wishlist__user__username",
        "wishlist__user__email",
        "ad__title",
    )
    readonly_fields = ("added_at",)
    ordering = ("-added_at",)
    date_hierarchy = "added_at"

    def wishlist_user(self, obj):
        return obj.wishlist.user.username
    wishlist_user.short_description = _("المستخدم")
    wishlist_user.admin_order_field = "wishlist__user__username"

    def ad_status_badge(self, obj):
        if not obj.ad:
            return "-"
        colors = {
            "active": "#28a745",
            "pending": "#fd7e14",
            "rejected": "#dc3545",
            "expired": "#6c757d",
        }
        color = colors.get(obj.ad.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 7px;border-radius:10px;font-size:11px">{}</span>',
            color, obj.ad.get_status_display(),
        )
    ad_status_badge.short_description = _("حالة الإعلان")


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    """Admin for FAQ Categories"""

    list_display = (
        "name",
        "name_ar",
        "icon",
        "order",
        "is_active",
        "faq_count",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "name_ar")
    list_editable = ("order", "is_active")
    ordering = ("order", "name")

    fieldsets = (
        (
            _("معلومات أساسية - Basic Information"),
            {"fields": ("name", "name_ar", "icon", "order", "is_active")},
        ),
    )

    actions = ["activate_faq_categories", "deactivate_faq_categories"]

    def activate_faq_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} فئة تم تفعيلها").format(updated))

    activate_faq_categories.short_description = _("✓ تفعيل الفئات المحددة")

    def deactivate_faq_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("{} فئة تم إلغاء تفعيلها").format(updated))

    deactivate_faq_categories.short_description = _("✗ إلغاء تفعيل الفئات المحددة")

    def faq_count(self, obj):
        """Get count of FAQs in this category"""
        return obj.faqs.filter(is_active=True).count()

    faq_count.short_description = _("عدد الأسئلة")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin for FAQs"""

    list_display = (
        "get_question_preview",
        "category",
        "order",
        "is_active",
        "is_popular",
        "views_count",
        "created_at",
    )
    list_filter = ("category", "is_active", "is_popular", "created_at")
    search_fields = ("question", "question_ar", "answer", "answer_ar")
    list_editable = ("order", "is_active", "is_popular")
    ordering = ("category__order", "order")

    fieldsets = (
        (
            _("الفئة - Category"),
            {"fields": ("category",)},
        ),
        (
            _("السؤال - Question"),
            {"fields": ("question", "question_ar")},
        ),
        (
            _("الإجابة - Answer"),
            {"fields": ("answer", "answer_ar")},
        ),
        (
            _("إعدادات - Settings"),
            {"fields": ("order", "is_active", "is_popular")},
        ),
        (
            _("إحصائيات - Statistics"),
            {"fields": ("views_count",), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("views_count",)

    def get_question_preview(self, obj):
        """Get question preview"""
        question = obj.question_ar or obj.question
        return question[:100] + "..." if len(question) > 100 else question

    get_question_preview.short_description = _("السؤال")

    actions = [
        "mark_as_popular",
        "mark_as_not_popular",
        "activate_faqs",
        "deactivate_faqs",
    ]

    def mark_as_popular(self, request, queryset):
        """Mark selected FAQs as popular"""
        updated = queryset.update(is_popular=True)
        self.message_user(request, f"{updated} FAQ(s) marked as popular.")

    mark_as_popular.short_description = _("تحديد كشائع")

    def mark_as_not_popular(self, request, queryset):
        """Mark selected FAQs as not popular"""
        updated = queryset.update(is_popular=False)
        self.message_user(request, f"{updated} FAQ(s) unmarked as popular.")

    mark_as_not_popular.short_description = _("إزالة من الشائع")

    def activate_faqs(self, request, queryset):
        """Activate selected FAQs"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} FAQ(s) activated.")

    activate_faqs.short_description = _("تفعيل")

    def deactivate_faqs(self, request, queryset):
        """Deactivate selected FAQs"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} FAQ(s) deactivated.")

    deactivate_faqs.short_description = _("إلغاء التفعيل")


@admin.register(FacebookShareRequest)
class FacebookShareRequestAdmin(admin.ModelAdmin):
    """Admin interface for Facebook Share Requests"""

    list_display = [
        "id",
        "ad_title",
        "user_link",
        "status_badge",
        "payment_confirmed",
        "requested_at",
        "processed_at",
        "processed_by",
    ]
    list_filter = [
        "status",
        "payment_confirmed",
        "requested_at",
        "processed_at",
    ]
    search_fields = [
        "ad__title",
        "user__username",
        "user__email",
        "admin_notes",
    ]
    readonly_fields = [
        "requested_at",
        "user",
        "ad",
    ]
    fieldsets = (
        (
            _("معلومات الطلب"),
            {
                "fields": (
                    "ad",
                    "user",
                    "status",
                    "requested_at",
                )
            },
        ),
        (
            _("معلومات الدفع"),
            {
                "fields": (
                    "payment_confirmed",
                    "payment_amount",
                )
            },
        ),
        (
            _("معلومات التنفيذ"),
            {
                "fields": (
                    "facebook_post_url",
                    "processed_at",
                    "processed_by",
                    "admin_notes",
                )
            },
        ),
    )
    actions = [
        "mark_as_in_progress",
        "mark_as_completed",
        "mark_as_rejected",
        "confirm_payment",
    ]

    def ad_title(self, obj):
        """Display ad title with link"""
        from django.urls import reverse

        ad_change_url = reverse("admin:main_classifiedad_change", args=[obj.ad.id])
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            ad_change_url,
            obj.ad.title[:50],
        )

    ad_title.short_description = _("الإعلان")

    def user_link(self, obj):
        """Display user with link"""
        from django.urls import reverse

        user_change_url = reverse("admin:main_user_change", args=[obj.user.id])
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            user_change_url,
            obj.user.username,
        )

    user_link.short_description = _("المستخدم")

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            "pending": "#ff9800",
            "in_progress": "#2196f3",
            "completed": "#4caf50",
            "rejected": "#f44336",
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px;">{}</span>',
            colors.get(obj.status, "#999"),
            obj.get_status_display(),
        )

    status_badge.short_description = _("الحالة")

    def mark_as_in_progress(self, request, queryset):
        """Mark selected requests as in progress"""
        updated = queryset.update(status="in_progress")
        self.message_user(request, f"{updated} طلب تم تحديثه إلى 'جاري التنفيذ'")

    mark_as_in_progress.short_description = _("تحديث إلى 'جاري التنفيذ'")

    def mark_as_completed(self, request, queryset):
        """Mark selected requests as completed"""
        for obj in queryset:
            obj.mark_as_completed(admin=request.user)
        self.message_user(request, f"{queryset.count()} طلب تم إكماله بنجاح")

    mark_as_completed.short_description = _("تحديد كمكتمل")

    def mark_as_rejected(self, request, queryset):
        """Mark selected requests as rejected"""
        for obj in queryset:
            obj.mark_as_rejected(admin=request.user)
        self.message_user(request, f"{queryset.count()} طلب تم رفضه")

    mark_as_rejected.short_description = _("رفض الطلب")

    def confirm_payment(self, request, queryset):
        """Confirm payment for selected requests"""
        updated = queryset.update(payment_confirmed=True)
        self.message_user(request, f"{updated} طلب تم تأكيد الدفع له")

    confirm_payment.short_description = _("تأكيد الدفع")


@admin.register(SafetyTip)
class SafetyTipAdmin(admin.ModelAdmin):
    """
    Custom admin for managing safety tips with preview and category filtering
    """

    list_display = [
        "title_display",
        "category_display",
        "icon_preview",
        "color_badge",
        "order",
        "is_active",
        "preview_button",
    ]

    list_filter = [
        "is_active",
        "color_theme",
        "category",
        "created_at",
    ]

    search_fields = [
        "title",
        "title_en",
        "description",
        "description_en",
    ]

    list_editable = ["order", "is_active"]

    fieldsets = (
        (_("معلومات أساسية - Basic Information"), {
            "fields": ("title", "title_en", "description", "description_en")
        }),
        (_("تصميم - Design"), {
            "fields": ("icon_class", "color_theme", "order")
        }),
        (_("الفئات - Categories"), {
            "fields": ("category", "categories"),
            "description": _("اختر فئة واحدة محددة أو عدة فئات. اترك الحقول فارغة للتطبيق على جميع الفئات.")
        }),
        (_("إعدادات - Settings"), {
            "fields": ("is_active",)
        }),
    )

    filter_horizontal = ["categories"]

    ordering = ["order", "id"]

    actions = [
        "activate_tips",
        "deactivate_tips",
        "duplicate_tip",
    ]

    class Media:
        css = {
            "all": ("admin/css/safety_tips_admin.css",)
        }
        js = ("admin/js/safety_tips_admin.js",)

    def title_display(self, obj):
        """Display title with icon"""
        return format_html(
            '<span style="font-weight: 600;"><i class="{}" style="margin-left: 8px; color: #667eea;"></i>{}</span>',
            obj.icon_class,
            obj.title
        )

    title_display.short_description = _("النصيحة - Tip")

    def category_display(self, obj):
        """Display category or 'All Categories'"""
        if obj.category:
            return format_html(
                '<span style="background: #e3f2fd; color: #1976d2; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">{}</span>',
                obj.category.name
            )
        elif obj.categories.exists():
            count = obj.categories.count()
            categories_list = ", ".join([cat.name for cat in obj.categories.all()[:3]])
            if count > 3:
                categories_list += f" +{count - 3}"
            return format_html(
                '<span style="background: #fff3e0; color: #e65100; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">{}</span>',
                categories_list
            )
        else:
            return format_html(
                '<span style="background: #f3e5f5; color: #7b1fa2; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">📌 {}</span>',
                _("جميع الفئات")
            )

    category_display.short_description = _("الفئة - Category")

    def icon_preview(self, obj):
        """Preview the icon"""
        return format_html(
            '<i class="{}" style="font-size: 24px; color: #667eea;"></i>',
            obj.icon_class
        )

    icon_preview.short_description = _("أيقونة - Icon")

    def color_badge(self, obj):
        """Display color theme badge"""
        color_map = {
            "tip-blue": ("#2196f3", "🔵"),
            "tip-green": ("#4caf50", "🟢"),
            "tip-orange": ("#ff9800", "🟠"),
            "tip-red": ("#e91e63", "🔴"),
            "tip-purple": ("#9c27b0", "🟣"),
            "tip-teal": ("#009688", "🔷"),
        }
        color, emoji = color_map.get(obj.color_theme, ("#999", "⚪"))
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 600;">{} {}</span>',
            color,
            emoji,
            obj.get_color_theme_display()
        )

    color_badge.short_description = _("اللون - Color")

    def preview_button(self, obj):
        """Add preview button"""
        from django.urls import reverse

        preview_url = reverse("admin:safetytip_preview")
        return format_html(
            '<a href="{}?tip_id={}" class="button" target="_blank" style="background: #667eea; color: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; font-size: 12px;">'
            '<i class="fas fa-eye"></i> {}</a>',
            preview_url,
            obj.id,
            _("معاينة")
        )

    preview_button.short_description = _("معاينة -Preview")

    def activate_tips(self, request, queryset):
        """Activate selected tips"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ تم تفعيل {updated} نصيحة")

    activate_tips.short_description = _("✅ تفعيل النصائح المحددة")

    def deactivate_tips(self, request, queryset):
        """Deactivate selected tips"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"❌ تم إلغاء تفعيل {updated} نصيحة")

    deactivate_tips.short_description = _("❌ إلغاء تفعيل النصائح المحددة")

    def duplicate_tip(self, request, queryset):
        """Duplicate selected tips for easy creation of similar tips"""
        for tip in queryset:
            tip.pk = None
            tip.title = f"{tip.title} (نسخة)"
            tip.is_active = False
            tip.save()
        self.message_user(request, f"✨ تم تكرار {queryset.count()} نصيحة")

    duplicate_tip.short_description = _("✨ تكرار النصائح المحددة")

    def get_urls(self):
        """Add custom preview URL"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                "preview/",
                self.admin_site.admin_view(self.preview_view),
                name="safetytip_preview",
            ),
        ]
        return custom_urls + urls

    def preview_view(self, request):
        """Custom preview view for safety tips"""
        from django.shortcuts import render
        from django.db.models import Q

        # Get tip_id from query params
        tip_id = request.GET.get("tip_id")
        selected_category = request.GET.get("category")

        # Get all categories for dropdown
        categories = Category.objects.filter(parent__isnull=True)

        # Get tips to preview
        if tip_id:
            tips = SafetyTip.objects.filter(id=tip_id, is_active=True)
        elif selected_category:
            try:
                # Validate selected_category is a valid integer to prevent SQL injection attempts
                selected_category = int(selected_category)
                category = Category.objects.get(id=selected_category)
                tips = SafetyTip.get_tips_for_category(category)
            except (ValueError, TypeError, Category.DoesNotExist):
                tips = SafetyTip.objects.filter(is_active=True).order_by("order")[:8]
        else:
            tips = SafetyTip.objects.filter(is_active=True).order_by("order")[:8]

        context = {
            "tips": tips,
            "categories": categories,
            "selected_category": selected_category,
            "site_header": self.admin_site.site_header,
            "has_permission": True,
        }

        return render(request, "admin/main/safetytip/preview.html", context)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "display_key_label", "display_name_ar", "display_subject_ar",
        "is_active", "updated_at", "action_buttons",
    )
    list_filter = ("is_active", "key")
    search_fields = ("key", "name", "name_ar", "subject", "subject_ar")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "send_newsletter_button", "test_send_button")
    ordering = ("key",)

    fieldsets = (
        (
            _("المعرّف - Identifier"),
            {
                "fields": ("key", "is_active"),
                "description": _(
                    "اختر حدث البريد الإلكتروني المناسب. لكل حدث قالب واحد فقط. "
                    "/ Select the matching email event. One template per event."
                ),
            },
        ),
        (
            _("الاسم - Name"),
            {
                "fields": ("name", "name_ar"),
            },
        ),
        (
            _("الموضوع - Subject"),
            {
                "fields": ("subject", "subject_ar"),
                "description": _(
                    "موضوع الرسالة — يدعم المتغيرات مثل {{site_name}} و{{user_name}} / "
                    "Email subject — supports variables like {{site_name}}, {{user_name}}"
                ),
            },
        ),
        (
            _("المحتوى - Body"),
            {
                "fields": ("body", "body_ar"),
                "description": _(
                    "محتوى الرسالة بتنسيق HTML — استخدم {{variable}} لإدراج القيم الديناميكية / "
                    "HTML body — use {{variable}} to insert dynamic values"
                ),
            },
        ),
        (
            _("المتغيرات المتاحة - Available Variables"),
            {
                "fields": ("available_variables",),
                "classes": ("collapse",),
                "description": _(
                    "سرد المتغيرات المتاحة لهذا القالب، مثال: {{user_name}}, {{site_name}} — "
                    "انسخها كما هي داخل الموضوع أو المحتوى."
                ),
            },
        ),
        (
            _("التواريخ - Dates"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        (
            _("الإجراءات - Actions"),
            {
                "fields": ("test_send_button", "send_newsletter_button"),
                "description": _(
                    "اختبر القالب بإرسال رسالة تجريبية، أو أرسله كنشرة بريدية للمشتركين."
                ),
            },
        ),
    )

    def display_key_label(self, obj):
        return obj.get_key_display() or obj.key
    display_key_label.short_description = _("الحدث - Event")
    display_key_label.admin_order_field = "key"

    def display_name_ar(self, obj):
        return obj.name_ar or obj.name
    display_name_ar.short_description = _("الاسم")

    def display_subject_ar(self, obj):
        return obj.subject_ar or obj.subject
    display_subject_ar.short_description = _("الموضوع")

    def action_buttons(self, obj):
        if not obj.pk:
            return "-"
        from django.urls import reverse
        test_url = reverse("admin:emailtemplate_test_send", args=[obj.pk])
        nl_url = reverse("admin:emailtemplate_send_newsletter", args=[obj.pk])
        return format_html(
            '<a href="{}" style="margin-left:6px; white-space:nowrap;">🧪 اختبار</a>'
            ' | <a href="{}" style="white-space:nowrap;">✉️ نشرة</a>',
            test_url, nl_url,
        )
    action_buttons.short_description = _("إجراءات")

    def test_send_button(self, obj):
        if not obj.pk:
            return _("احفظ القالب أولاً لتتمكن من اختباره.")
        from django.urls import reverse
        url = reverse("admin:emailtemplate_test_send", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" style="background:#417690; color:#fff; padding:8px 18px; '
            'border-radius:4px; font-weight:600; text-decoration:none; display:inline-block; margin-left:8px;">'
            '🧪 إرسال رسالة اختبارية'
            '</a>',
            url,
        )
    test_send_button.short_description = _("اختبار القالب")

    def send_newsletter_button(self, obj):
        if not obj.pk:
            return _("احفظ القالب أولاً لتتمكن من إرساله.")
        from django.urls import reverse
        url = reverse("admin:emailtemplate_send_newsletter", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" style="background:#e8845c; color:#fff; padding:8px 18px; '
            'border-radius:4px; font-weight:600; text-decoration:none; display:inline-block;">'
            '✉️ إرسال كنشرة بريدية'
            '</a>',
            url,
        )
    send_newsletter_button.short_description = _("إرسال النشرة")

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/test-send/",
                self.admin_site.admin_view(self.test_send_view),
                name="emailtemplate_test_send",
            ),
            path(
                "<int:pk>/send-newsletter/",
                self.admin_site.admin_view(self.send_newsletter_view),
                name="emailtemplate_send_newsletter",
            ),
        ]
        return custom + urls

    def test_send_view(self, request, pk):
        """Send a test email using sample variables to the current admin user."""
        from django.template.response import TemplateResponse
        from django.contrib import messages as dj_messages
        from django.http import HttpResponseRedirect
        from django.shortcuts import get_object_or_404
        from constance import config

        template_obj = get_object_or_404(EmailTemplate, pk=pk)

        # Default sample context shared across all templates
        sample_context = {
            "site_name": config.SITE_NAME,
            "site_url": getattr(config, "SITE_URL", "https://idrissimart.com"),
            "user_name": request.user.get_full_name() or request.user.username,
            "username": request.user.username,
            "email": request.user.email,
            "otp_code": "123456",
            "expiry_minutes": "10",
            "reset_link": getattr(config, "SITE_URL", "https://idrissimart.com") + "/password-reset/",
            "verification_link": getattr(config, "SITE_URL", "https://idrissimart.com") + "/verify-email/",
            "ad_title": "إعلان تجريبي - Sample Ad",
            "ad_url": getattr(config, "SITE_URL", "https://idrissimart.com") + "/ad/sample-ad/",
            "ad_status": "active",
            "reject_reason": "يرجى مراجعة محتوى الإعلان / Please review ad content",
            "order_number": "ORD-2026-001",
            "order_total": "250.00",
            "package_name": "باقة ناشر - Publisher Package",
            "ad_count": "10",
            "payment_amount": "99.00",
            "search_name": "بحث: سيارات القاهرة",
            "search_url": getattr(config, "SITE_URL", "https://idrissimart.com") + "/search/?q=test",
            "sender_name": "زائر تجريبي - Test Visitor",
            "sender_email": "test@example.com",
            "message": "هذه رسالة اختبارية من لوحة الإدارة.",
            "subject_text": "استفسار عام",
            "receiver_name": request.user.get_full_name() or request.user.username,
            "sender_name": "ناشر تجريبي - Test Publisher",
            "message_preview": "مرحباً، أريد الاستفسار عن إعلانك...",
            "chat_url": getattr(config, "SITE_URL", "https://idrissimart.com") + "/chat/",
            "unsubscribe_url": getattr(config, "SITE_URL", "https://idrissimart.com") + "/newsletter/unsubscribe/",
            "join_date": "2026-01-01",
            "new_status": "shipped",
        }

        if request.method == "POST":
            to_email = request.POST.get("to_email", request.user.email).strip()
            if not to_email:
                to_email = request.user.email

            # Determine subject and body with variable substitution
            lang = "ar"
            subject = (template_obj.subject_ar or template_obj.subject) or f"[TEST] {template_obj}"
            body = (template_obj.body_ar or template_obj.body) or ""

            for key_var, value in sample_context.items():
                body = body.replace(f"{{{{{key_var}}}}}", str(value))
                subject = subject.replace(f"{{{{{key_var}}}}}", str(value))

            subject = f"[TEST] {subject}"

            if not body:
                dj_messages.error(request, _("القالب لا يحتوي على محتوى (body_ar أو body)."))
            else:
                from main.services.email_service import EmailService
                ok = EmailService.send_email(
                    to_emails=[to_email],
                    subject=subject,
                    html_content=body,
                )
                if ok:
                    dj_messages.success(
                        request,
                        _("✅ تم إرسال رسالة الاختبار بنجاح إلى {}.").format(to_email),
                    )
                else:
                    dj_messages.error(request, _("❌ فشل إرسال رسالة الاختبار — راجع سجلات الخادم."))

            return HttpResponseRedirect(request.path)

        context = {
            **self.admin_site.each_context(request),
            "title": _("اختبار قالب: {}").format(str(template_obj)),
            "email_template": template_obj,
            "admin_email": request.user.email,
            "sample_context": sample_context,
            "opts": self.model._meta,
        }
        return TemplateResponse(
            request, "admin/main/emailtemplate/test_send.html", context
        )

    def send_newsletter_view(self, request, pk):
        from django.template.response import TemplateResponse
        from django.contrib import messages as dj_messages
        from django.http import HttpResponseRedirect
        from django.shortcuts import get_object_or_404
        from django.utils.html import strip_tags
        from django.core.mail import send_mail
        from django.conf import settings as dj_settings

        template = get_object_or_404(EmailTemplate, pk=pk)

        if request.method == "POST":
            subject = request.POST.get("subject", "").strip()
            body_html = request.POST.get("body_html", "").strip()
            test_mode = request.POST.get("test_mode") == "1"

            if not subject:
                dj_messages.error(request, _("الموضوع مطلوب."))
            elif not body_html:
                dj_messages.error(request, _("محتوى الرسالة مطلوب."))
            else:
                if test_mode:
                    recipients = [dj_settings.DEFAULT_FROM_EMAIL]
                else:
                    main_emails = set(
                        NewsletterSubscriber.objects.filter(is_active=True)
                        .values_list("email", flat=True)
                    )
                    try:
                        from content.models import Newsletter as ContentNewsletter
                        content_emails = set(
                            ContentNewsletter.objects.filter(is_active=True, receive_email=True)
                            .values_list("email", flat=True)
                        )
                    except Exception:
                        content_emails = set()
                    recipients = list(main_emails | content_emails)

                if not recipients:
                    dj_messages.warning(request, _("لا يوجد مشتركون نشطون."))
                else:
                    plain = strip_tags(body_html)
                    success_count = 0
                    fail_count = 0

                    if test_mode:
                        from main.services.email_service import EmailService
                        ok = EmailService.send_email(
                            to_emails=recipients,
                            subject=f"[TEST] {subject}",
                            html_content=body_html,
                            text_content=plain,
                        )
                        success_count = 1 if ok else 0
                        fail_count = 0 if ok else 1
                    else:
                        batch_size = 100
                        for i in range(0, len(recipients), batch_size):
                            batch = recipients[i:i + batch_size]
                            try:
                                send_mail(
                                    subject=subject,
                                    message=plain,
                                    from_email=dj_settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=[dj_settings.DEFAULT_FROM_EMAIL],
                                    bcc=batch,
                                    html_message=body_html,
                                    fail_silently=False,
                                )
                                success_count += len(batch)
                            except Exception as exc:
                                fail_count += len(batch)
                                import logging
                                logging.getLogger(__name__).error("Newsletter batch send failed: %s", exc)

                    if success_count:
                        msg = (
                            _("تم إرسال رسالة اختبار بنجاح.") if test_mode
                            else _("تم إرسال النشرة بنجاح إلى {} مشترك.").format(success_count)
                        )
                        dj_messages.success(request, msg)
                    if fail_count:
                        dj_messages.error(request, _("فشل الإرسال لـ {} مشترك.").format(fail_count))

            return HttpResponseRedirect(request.path)

        active_count = NewsletterSubscriber.objects.filter(is_active=True).count()
        try:
            from content.models import Newsletter as ContentNewsletter
            content_count = ContentNewsletter.objects.filter(is_active=True, receive_email=True).count()
        except Exception:
            content_count = 0

        context = {
            **self.admin_site.each_context(request),
            "title": _("إرسال '{}' كنشرة بريدية").format(str(template)),
            "email_template": template,
            "active_count": active_count,
            "content_count": content_count,
            "total_count": active_count + content_count,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/main/emailtemplate/send_newsletter.html", context)


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ("key", "display_name_col", "is_active", "updated_at")
    list_filter = ("is_active", "key")
    search_fields = ("key", "name", "name_ar", "body")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("key",)

    fieldsets = (
        (
            _("المعرّف - Identifier"),
            {"fields": ("key", "is_active")},
        ),
        (
            _("الاسم - Name"),
            {"fields": ("name", "name_ar")},
        ),
        (
            _("نص الرسالة - Message Body"),
            {
                "fields": ("body",),
                "description": _(
                    "نص رسالة SMS المرسلة للعميل. استخدم {{variable}} للمتغيرات المذكورة أدناه. "
                    "مثال: مرحباً، طلبك رقم {{order_number}} تم شحنه."
                ),
            },
        ),
        (
            _("المتغيرات والتواريخ - Variables & Dates"),
            {
                "fields": ("available_variables", "created_at", "updated_at"),
                "classes": ("collapse",),
                "description": _("المتغيرات المتاحة لهذا القالب — انسخها كما هي داخل نص الرسالة."),
            },
        ),
    )

    def display_name_col(self, obj):
        return obj.name_ar or obj.name
    display_name_col.short_description = _("الاسم")


@admin.register(CustomPage)
class CustomPageAdmin(admin.ModelAdmin):
    list_display = (
        "display_title_col",
        "slug",
        "is_active",
        "show_in_navbar",
        "navbar_order",
        "show_in_footer",
        "footer_order",
        "view_link",
        "updated_at",
    )
    list_filter = ("is_active", "show_in_navbar", "show_in_footer")
    search_fields = ("title", "title_ar", "slug")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_active", "show_in_navbar", "navbar_order", "show_in_footer", "footer_order")
    readonly_fields = ("created_at", "updated_at", "view_link")
    ordering = ("navbar_order", "title")

    formfield_overrides = {
        __import__("django.db.models", fromlist=["TextField"]).TextField: {
            "widget": __import__("django_ckeditor_5.widgets", fromlist=["CKEditor5Widget"]).CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        },
    }

    fieldsets = (
        (
            _("المعلومات الأساسية"),
            {"fields": ("title", "title_ar", "slug", "is_active")},
        ),
        (
            _("المحتوى"),
            {"fields": ("body_ar", "body")},
        ),
        (
            _("SEO"),
            {
                "fields": ("meta_description_ar", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        (
            _("ظهور في الشريط والتذييل"),
            {
                "fields": (
                    "show_in_navbar",
                    "navbar_order",
                    "show_in_footer",
                    "footer_order",
                ),
                "description": _(
                    "حدد أين تظهر الصفحة. الترتيب: رقم أصغر = يظهر أولاً."
                ),
            },
        ),
        (
            _("معلومات النظام"),
            {"fields": ("view_link", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def display_title_col(self, obj):
        return obj.title_ar or obj.title
    display_title_col.short_description = _("العنوان")

    def view_link(self, obj):
        if not obj.pk or not obj.slug:
            return "-"
        from django.urls import reverse
        from django.utils import translation
        with translation.override("ar"):
            url = reverse("main:custom_page", kwargs={"slug": obj.slug})
        return format_html(
            '<a href="{}" target="_blank" class="button">'
            '<i class="fas fa-external-link-alt"></i> عرض الصفحة'
            "</a>",
            url,
        )
    view_link.short_description = _("رابط الصفحة")


class PaidBannerAdminForm(forms.ModelForm):
    """Custom admin form that renders target_pages as grouped checkboxes."""

    target_pages = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("الصفحات المستهدفة"),
        help_text=_(
            "اختر الصفحات التي سيظهر عليها الإعلان. "
            "إذا لم تختر أي صفحة سيظهر الإعلان على جميع الصفحات."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Build choices dynamically at render time (new pages appear automatically)
        self.fields["target_pages"].choices = PaidBanner.get_all_site_pages()
        # Pre-fill from the stored JSON list
        if self.instance and self.instance.pk:
            self.initial["target_pages"] = self.instance.target_pages or []

    def clean_target_pages(self):
        return self.cleaned_data.get("target_pages") or []

    def clean(self):
        cleaned_data = super().clean()
        from django.core.files.uploadedfile import UploadedFile

        ad_type = cleaned_data.get("ad_type") or (
            self.instance.ad_type if self.instance and self.instance.pk else None
        )
        specs = PaidBanner.IMAGE_SPECS.get(ad_type) if ad_type else None
        if not specs:
            return cleaned_data

        image        = cleaned_data.get("image")
        mobile_image = cleaned_data.get("mobile_image")

        # Validate desktop image (only when a new file was just uploaded)
        if isinstance(image, UploadedFile):
            try:
                from PIL import Image as PilImage
                image.seek(0)
                w, h = PilImage.open(image).size
                image.seek(0)
                rw, rh = specs["desktop"]
                if (w, h) != (rw, rh):
                    self.add_error(
                        "image",
                        _(
                            "مقاس الصورة %(w)s×%(h)s بكسل غير صحيح — "
                            "المقاس المطلوب لنوع '%(type)s' هو %(rw)s×%(rh)s بكسل."
                        ) % {"w": w, "h": h, "rw": rw, "rh": rh, "type": ad_type},
                    )
            except Exception:
                pass  # PIL unavailable — model.clean() will re-check

        # Validate mobile image (only when a new file was just uploaded)
        if isinstance(mobile_image, UploadedFile) and specs.get("mobile"):
            try:
                from PIL import Image as PilImage
                mobile_image.seek(0)
                w, h = PilImage.open(mobile_image).size
                mobile_image.seek(0)
                mw, mh = specs["mobile"]
                if (w, h) != (mw, mh):
                    self.add_error(
                        "mobile_image",
                        _(
                            "مقاس صورة الموبايل %(w)s×%(h)s بكسل غير صحيح — "
                            "المطلوب %(rw)s×%(rh)s بكسل."
                        ) % {"w": w, "h": h, "rw": mw, "rh": mh},
                    )
            except Exception:
                pass

        # Enforce mandatory mobile image for banner type
        if specs.get("mobile_required"):
            has_mobile = isinstance(mobile_image, UploadedFile) or (
                self.instance
                and self.instance.pk
                and self.instance.mobile_image
                and mobile_image is not False  # False = "clear" checkbox ticked
            )
            if not has_mobile:
                self.add_error(
                    "mobile_image",
                    _(
                        "صورة الموبايل إجبارية لنوع 'بانر إعلاني' — "
                        "المقاس المطلوب %(w)s×%(h)s بكسل."
                    ) % {"w": specs["mobile"][0], "h": specs["mobile"][1]},
                )

        return cleaned_data

    class Meta:
        model = PaidBanner
        fields = "__all__"


@admin.register(PaidBanner)
class PaidBannerAdmin(admin.ModelAdmin):
    """Admin interface for Paid Banners management — accessed via AdvertisingConfig tabs"""

    form = PaidBannerAdminForm

    def has_module_perms(self, request):
        return False  # hide from sidebar; accessible via AdvertisingConfig tab links

    list_display = (
        "title",
        "ad_type_badge",
        "advertising_space",
        "placement_display",
        "target_pages_summary",
        "country",
        "status_badge",
        "payment_status_badge",
        "date_range_display",
        "views_count",
        "clicks_count",
        "ctr_display",
        "priority",
        "is_active",
    )

    list_filter = (
        "status",
        "payment_status",
        "ad_type",
        "placement_type",
        "country",
        "is_active",
        "start_date",
        "end_date",
        "created_at",
    )

    search_fields = (
        "title",
        "title_ar",
        "description",
        "company_name",
        "advertiser__username",
        "advertiser__email",
    )

    readonly_fields = (
        "views_count",
        "clicks_count",
        "ctr_display",
        "created_at",
        "updated_at",
        "approved_by",
        "approved_at",
    )

    fieldsets = (
        (
            _("معلومات أساسية - Basic Information"),
            {
                "fields": (
                    "title",
                    "title_ar",
                    "description",
                    "description_ar",
                    "status",
                    "is_active",
                )
            },
        ),
        (
            _("معلومات المعلن - Advertiser Information"),
            {
                "fields": (
                    "advertiser",
                    "company_name",
                    "contact_email",
                    "contact_phone",
                )
            },
        ),
        (
            _("المحتوى المرئي - Visual Content"),
            {
                "fields": (
                    "image",
                    "mobile_image",
                    "ad_type",
                )
            },
        ),
        (
            _("الرابط والإجراء - Link & CTA"),
            {
                "fields": (
                    "target_url",
                    "cta_text",
                    "cta_text_ar",
                    "open_in_new_tab",
                )
            },
        ),
        (
            _("الموضع والاستهداف - Placement & Targeting"),
            {
                "fields": (
                    "target_pages",
                    "placement_type",
                    "advertising_space",
                    "country",
                    "extra_countries",
                    "category",
                    "subcategory",
                    "categories",
                ),
                "description": _(
                    "اختر الصفحات المستهدفة من القائمة — تُضاف الصفحات الجديدة تلقائياً. "
                    "إذا تُركت فارغة يظهر الإعلان في كل الصفحات. "
                    "تحديد المساحة الإعلانية يسمح لعدة معلنين بمشاركة نفس الموقع مع عرض إعلاناتهم بالتناوب."
                ),
            },
        ),
        (
            _("الجدولة والمدة - Schedule & Duration"),
            {
                "fields": (
                    "duration_days",
                    "start_date",
                    "end_date",
                ),
                "description": _(
                    "المدة تُحدَّد بالأيام من قِبَل المعلن. "
                    "تاريخ البدء والانتهاء يُحسبان تلقائياً عند تفعيل الإعلان."
                ),
            },
        ),
        (
            _("الأولوية والترتيب - Priority & Order"),
            {
                "fields": (
                    "priority",
                    "order",
                )
            },
        ),
        (
            _("التسعير والدفع - Pricing & Payment"),
            {
                "fields": (
                    "price",
                    "currency",
                    "payment_status",
                    "payment_reference",
                )
            },
        ),
        (
            _("إحصائيات - Analytics"),
            {
                "fields": (
                    "views_count",
                    "clicks_count",
                    "ctr_display",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("ملاحظات إدارية - Admin Notes"),
            {
                "fields": (
                    "admin_notes",
                    "approved_by",
                    "approved_at",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    filter_horizontal = ("categories", "extra_countries")

    class Media:
        js = ("admin/js/category_cascade.js", "admin/js/banner_image_hints.js")

    actions = [
        "confirm_payment_and_activate",
        "approve_ads",
        "pause_ads",
        "resume_ads",
        "mark_as_paid",
        "mark_as_expired",
    ]

    def ad_type_badge(self, obj):
        """Display ad type with badge"""
        colors = {
            "banner": "#3498db",
            "sidebar": "#9b59b6",
            "popup": "#e74c3c",
            "featured_box": "#f39c12",
        }
        color = colors.get(obj.ad_type, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_ad_type_display(),
        )
    ad_type_badge.short_description = _("نوع الإعلان")

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            "draft": "#95a5a6",
            "active": "#27ae60",
            "paused": "#f39c12",
            "expired": "#e74c3c",
            "pending": "#3498db",
        }
        color = colors.get(obj.status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = _("الحالة")

    def payment_status_badge(self, obj):
        """Display payment status with colored badge"""
        colors = {
            "unpaid": "#e74c3c",
            "receipt_submitted": "#f39c12",
            "paid": "#27ae60",
            "refunded": "#95a5a6",
        }
        color = colors.get(obj.payment_status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display(),
        )
    payment_status_badge.short_description = _("حالة الدفع")

    def placement_display(self, obj):
        """Display placement information"""
        if obj.placement_type == "general":
            return format_html('<span style="color: #27ae60;"><i class="fas fa-home"></i> الصفحة الرئيسية</span>')
        elif obj.placement_type == "category" and obj.category:
            return format_html('<span style="color: #3498db;"><i class="fas fa-folder"></i> {}</span>', obj.category.name)
        elif obj.placement_type == "subcategory" and obj.subcategory:
            return format_html('<span style="color: #9b59b6;"><i class="fas fa-folder-open"></i> {}</span>', obj.subcategory.name)
        return "-"
    placement_display.short_description = _("الموضع")

    def target_pages_summary(self, obj):
        """Show number of targeted pages or 'all pages' badge."""
        pages = obj.target_pages or []
        if not pages:
            return format_html(
                '<span style="background:#27ae60;color:#fff;padding:2px 8px;border-radius:3px;font-size:11px;">جميع الصفحات</span>'
            )
        count = len(pages)
        # Build a tooltip listing the keys
        tip = ", ".join(pages[:10])
        if count > 10:
            tip += f" … (+{count - 10})"
        return format_html(
            '<span title="{}" style="background:#3498db;color:#fff;padding:2px 8px;border-radius:3px;font-size:11px;">'
            '{} صفحة</span>',
            tip,
            count,
        )
    target_pages_summary.short_description = _("الصفحات المستهدفة")

    def date_range_display(self, obj):
        """Display date range in a compact format"""
        from django.utils import timezone
        now = timezone.now()

        if not obj.start_date or not obj.end_date:
            return format_html(
                '🟡 <small>ينتظر التفعيل</small><br>'
                '<small style="color:#999">مدة: {} يوم</small>',
                obj.duration_days,
            )

        if obj.end_date < now:
            status_icon = '🔴'
            status_text = 'منتهي'
        elif obj.start_date > now:
            status_icon = '🟡'
            status_text = 'قادم'
        else:
            status_icon = '🟢'
            status_text = 'نشط'

        return format_html(
            '{} <small>{}</small><br><small>{} - {}</small>',
            status_icon,
            status_text,
            obj.start_date.strftime('%Y-%m-%d'),
            obj.end_date.strftime('%Y-%m-%d'),
        )
    date_range_display.short_description = _("الفترة")

    def ctr_display(self, obj):
        """Display Click-Through Rate"""
        ctr = obj.ctr
        if ctr >= 5:
            color = "#27ae60"  # Green - excellent
        elif ctr >= 2:
            color = "#f39c12"  # Orange - good
        else:
            color = "#e74c3c"  # Red - needs improvement

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            f'{ctr:.2f}',
        )
    ctr_display.short_description = _("معدل النقر (CTR)")

    # Actions
    def confirm_payment_and_activate(self, request, queryset):
        """Confirm payment receipt AND activate the banner in one step."""
        from .models import Notification
        activated = 0
        skipped = 0
        for ad in queryset.select_related("advertiser"):
            if ad.payment_status not in ("paid", "receipt_submitted"):
                skipped += 1
                continue
            ad.payment_status = "paid"
            ad.approve(request.user)  # sets status=ACTIVE, approved_by, approved_at
            Notification.objects.create(
                user=ad.advertiser,
                notification_type=Notification.NotificationType.AD_APPROVED,
                title=_("تم قبول الدفع وتفعيل إعلانك البانري"),
                message=_(
                    "تم قبول دفع إعلانك البانري «{}» وتفعيله. سيبدأ عرضه في الفترة المحددة."
                ).format(ad.title),
                link="",
            )
            activated += 1
        msg = _("تم تفعيل {} إعلان").format(activated)
        if skipped:
            msg += " — " + _("تم تخطي {} إعلان (لم يُسدَّد بعد)").format(skipped)
        self.message_user(request, msg)
    confirm_payment_and_activate.short_description = _("✅ قبول الدفع وتفعيل البانر")

    def approve_ads(self, request, queryset):
        """Activate ads that already have confirmed payment."""
        from .models import Notification
        count = 0
        skipped = 0
        for ad in queryset.select_related("advertiser"):
            if ad.payment_status != "paid":
                skipped += 1
                continue
            ad.approve(request.user)
            Notification.objects.create(
                user=ad.advertiser,
                notification_type=Notification.NotificationType.AD_APPROVED,
                title=_("تمت الموافقة على إعلانك البانري"),
                message=_(
                    "تمت مراجعة إعلانك البانري «{}» والموافقة عليه. سيبدأ عرضه في الفترة المحددة."
                ).format(ad.title),
                link="",
            )
            count += 1
        msg = _("تم الموافقة على {} إعلان").format(count)
        if skipped:
            msg += " — " + _("تم تخطي {} إعلان (يجب تأكيد الدفع أولاً)").format(skipped)
        self.message_user(request, msg)
    approve_ads.short_description = _("الموافقة على الإعلانات المدفوعة")

    def pause_ads(self, request, queryset):
        """Pause selected ads"""
        count = queryset.update(status=PaidBanner.Status.PAUSED)
        self.message_user(request, _("تم إيقاف {} إعلان مؤقتاً").format(count))
    pause_ads.short_description = _("إيقاف الإعلانات مؤقتاً")

    def resume_ads(self, request, queryset):
        """Resume paused ads"""
        count = 0
        for ad in queryset.filter(status=PaidBanner.Status.PAUSED):
            ad.resume()
            count += 1
        self.message_user(request, _("تم استئناف {} إعلان").format(count))
    resume_ads.short_description = _("استئناف الإعلانات")

    def mark_as_paid(self, request, queryset):
        """Mark ads as paid"""
        count = queryset.update(payment_status="paid")
        self.message_user(request, _("تم تحديد {} إعلان كمدفوع").format(count))
    mark_as_paid.short_description = _("تحديد كمدفوع")

    def mark_as_expired(self, request, queryset):
        """Mark ads as expired"""
        count = queryset.update(status=PaidBanner.Status.EXPIRED)
        self.message_user(request, _("تم تحديد {} إعلان كمنتهي").format(count))
    mark_as_expired.short_description = _("تحديد كمنتهي")


@admin.register(BannerPricing)
class BannerPricingAdmin(admin.ModelAdmin):
    """Admin interface for Banner Pricing — accessed via AdvertisingConfig tabs"""

    def has_module_perms(self, request):
        return False

    list_display = (
        "ad_type_display",
        "placement_type_display",
        "price",
        "currency",
        "is_active",
        "updated_at",
    )
    list_filter = ("ad_type", "placement_type", "is_active", "currency")
    search_fields = ("ad_type", "placement_type")
    list_editable = ("price", "is_active")
    ordering = ["ad_type", "placement_type"]

    fieldsets = (
        (_("نوع الإعلان - Ad Configuration"), {
            "fields": ("ad_type", "placement_type")
        }),
        (_("السعر - Pricing"), {
            "fields": ("price", "currency", "is_active")
        }),
    )

    def ad_type_display(self, obj):
        """Display ad type with badge"""
        colors = {
            'banner': 'primary',
            'sidebar': 'info',
            'popup': 'warning',
            'featured_box': 'success',
        }
        color = colors.get(obj.ad_type, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_ad_type_display()
        )
    ad_type_display.short_description = _("نوع الإعلان")

    def placement_type_display(self, obj):
        """Display placement type with badge"""
        colors = {
            'general': 'success',
            'category': 'info',
            'subcategory': 'warning',
        }
        color = colors.get(obj.placement_type, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_placement_type_display()
        )
    placement_type_display.short_description = _("نوع الموضع")


@admin.register(AdSenseSlot)
class AdSenseSlotAdmin(admin.ModelAdmin):
    """
    Admin interface for Google AdSense slot configuration — accessed via AdvertisingConfig tabs.
    Internal only — not visible to advertisers.
    """

    def has_module_perms(self, request):
        return False

    list_display = (
        "slot_key_badge",
        "country",
        "ad_client_short",
        "ad_slot",
        "ad_format",
        "is_responsive",
        "status_badge",
        "updated_at",
    )
    list_filter = ("slot_key", "country", "is_active", "ad_format")
    list_editable = ("is_responsive",)
    search_fields = ("ad_client", "ad_slot", "country__name", "country__code")
    ordering = ["slot_key", "country__code"]

    fieldsets = (
        (_("الموضع والدولة"), {
            "fields": ("slot_key", "country"),
            "description": _(
                "كل دولة يمكن أن يكون لها إعداد AdSense مختلف لكل موضع. "
                "إذا كان الموضع نشطاً سيحل محل البانر المدفوع."
            ),
        }),
        (_("بيانات Google AdSense"), {
            "fields": ("ad_client", "ad_slot", "ad_format", "is_responsive"),
        }),
        (_("الحالة"), {
            "fields": ("is_active",),
        }),
        (_("معاينة الكود"), {
            "fields": ("adsense_code_preview",),
            "classes": ("collapse",),
            "description": _("الكود الذي سيُدرج في الصفحة"),
        }),
    )

    readonly_fields = ("adsense_code_preview", "updated_at")

    # ── Display methods ──────────────────────────────────────────────

    def slot_key_badge(self, obj):
        colors = {
            "home_banner":   "primary",
            "home_sidebar":  "info",
            "home_featured": "success",
            "category_banner":   "warning",
            "category_sidebar":  "secondary",
            "category_featured": "dark",
        }
        color = colors.get(obj.slot_key, "secondary")
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_slot_key_display()
        )
    slot_key_badge.short_description = _("الموضع")

    def ad_client_short(self, obj):
        return format_html(
            '<code style="font-size:0.8em">{}</code>',
            obj.ad_client[:30] + ("…" if len(obj.ad_client) > 30 else "")
        )
    ad_client_short.short_description = _("Ad Client")

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge bg-success">✓ نشط</span>')
        return format_html('<span class="badge bg-secondary">متوقف</span>')
    status_badge.short_description = _("الحالة")

    def adsense_code_preview(self, obj):
        if not obj.ad_client or not obj.ad_slot:
            return _("أدخل Ad Client و Ad Slot لمعاينة الكود")
        code = (
            f'&lt;!-- Google AdSense: {obj.get_slot_key_display()} --&gt;\n'
            f'&lt;script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={obj.ad_client}" crossorigin="anonymous"&gt;&lt;/script&gt;\n'
            f'&lt;ins class="adsbygoogle"\n'
            f'     style="display:block"\n'
            f'     data-ad-client="{obj.ad_client}"\n'
            f'     data-ad-slot="{obj.ad_slot}"\n'
            f'     data-ad-format="{obj.ad_format}"'
        )
        if obj.is_responsive:
            code += '\n     data-full-width-responsive="true"'
        code += '&gt;&lt;/ins&gt;\n'
        code += '&lt;script&gt;(adsbygoogle = window.adsbygoogle || []).push({});&lt;/script&gt;'
        return format_html(
            '<pre style="background:#1e1e2e;color:#cdd6f4;padding:12px;border-radius:6px;'
            'font-size:0.78em;overflow-x:auto;white-space:pre-wrap;">{}</pre>',
            code
        )
    adsense_code_preview.short_description = _("معاينة كود AdSense")


# ---------------------------------------------------------------------------
# Banner Slots (rotation config)
# ---------------------------------------------------------------------------

@admin.register(BannerSlot)
class BannerSlotAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "slot_key",
        "ad_type",
        "max_capacity",
        "active_count_display",
        "available_spots_display",
        "rotation_seconds",
        "is_active",
    )
    list_filter = ("ad_type", "is_active")
    search_fields = ("name", "name_ar", "slot_key")
    list_editable = ("rotation_seconds", "max_capacity", "is_active")
    ordering = ("ad_type", "name")
    readonly_fields = ("created_at", "updated_at", "active_count_display", "available_spots_display")
    fieldsets = (
        (
            "تعريف السلوت",
            {
                "fields": ("name", "name_ar", "slot_key", "ad_type", "is_active"),
            },
        ),
        (
            "إعدادات التدوير",
            {
                "fields": ("max_capacity", "rotation_seconds"),
                "description": "التحكم في عدد المعلنين ومدة عرض كل بانر.",
            },
        ),
        (
            "معلومات",
            {
                "fields": ("active_count_display", "available_spots_display", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def display_name(self, obj):
        return obj.name_ar or obj.name
    display_name.short_description = "الاسم"

    def active_count_display(self, obj):
        return obj.active_count
    active_count_display.short_description = "معلنون نشطون"

    def available_spots_display(self, obj):
        spots = obj.available_spots
        color = "#27ae60" if spots > 0 else "#e74c3c"
        return format_html('<span style="color:{}">{}</span>', color, spots)
    available_spots_display.short_description = "أماكن شاغرة"


# ---------------------------------------------------------------------------
# Unified Advertising Dashboard  (single admin entry — three tabs)
# ---------------------------------------------------------------------------

@admin.register(AdvertisingConfig)
class AdvertisingConfigAdmin(admin.ModelAdmin):
    """
    Single admin entry that renders PaidBanner + BannerPricing + AdSenseSlot
    in one page with Bootstrap tabs.  The three underlying ModelAdmin classes
    remain registered so their add/change/delete pages still work normally.
    """

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_perms(self, request):
        return True

    def changelist_view(self, request, extra_context=None):
        from django.template.response import TemplateResponse
        from constance import config as constance_config

        # Handle POST: update extra-country fee
        if request.method == "POST" and "extra_country_fee" in request.POST:
            from django.http import HttpResponseRedirect
            try:
                new_fee = float(request.POST["extra_country_fee"])
                if new_fee < 0:
                    raise ValueError("negative")
                constance_config.PAID_BANNER_EXTRA_COUNTRY_FEE_PER_DAY = new_fee
                self.message_user(request, _("تم تحديث رسوم الدولة الإضافية إلى {} ج.م/يوم").format(new_fee))
            except Exception:
                self.message_user(request, _("قيمة غير صالحة."), level="error")
            return HttpResponseRedirect(request.path + "?tab=pricing")

        paid_banners  = PaidBanner.objects.select_related("country", "category", "advertiser").order_by("-created_at")[:200]
        pricing_rows  = BannerPricing.objects.all().order_by("ad_type", "placement_type")
        adsense_slots = AdSenseSlot.objects.select_related("country").order_by("slot_key", "country__code")
        banner_slots  = BannerSlot.objects.all().order_by("ad_type", "name")

        # Quick stats for paid banners
        from django.utils import timezone
        now = timezone.now()
        stats = {
            "total":   PaidBanner.objects.count(),
            "active":  PaidBanner.objects.filter(status=PaidBanner.Status.ACTIVE).count(),
            "pending": PaidBanner.objects.filter(status=PaidBanner.Status.PENDING_APPROVAL).count(),
            "unpaid":  PaidBanner.objects.filter(payment_status="unpaid").count(),
        }

        extra_country_fee = float(getattr(constance_config, "PAID_BANNER_EXTRA_COUNTRY_FEE_PER_DAY", 20.0))

        context = {
            **self.admin_site.each_context(request),
            "title": _("إدارة الإعلانات المدفوعة"),
            "paid_banners":       paid_banners,
            "pricing_rows":       pricing_rows,
            "adsense_slots":      adsense_slots,
            "banner_slots":       banner_slots,
            "stats":              stats,
            "active_tab":         request.GET.get("tab", "banners"),
            "extra_country_fee":  extra_country_fee,
            "opts":               self.model._meta,
            "has_permission":     True,
        }
        return TemplateResponse(request, "admin/advertising_tabs.html", context)
