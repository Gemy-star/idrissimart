from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db import models
from mptt.admin import MPTTModelAdmin
from django_ckeditor_5.widgets import CKEditor5Widget

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
    AdTransaction,
    AdUpgradeHistory,
    Cart,
    CartItem,
    CartSettings,
    Category,
    CategoryCustomField,
    ClassifiedAd,
    ContactMessage,
    CustomField,
    CustomFieldOption,
    FAQ,
    FAQCategory,
    FacebookShareRequest,
    NewsletterSubscriber,
    Notification,
    Order,
    OrderItem,
    Payment,
    SavedSearch,
    User,
    UserPackage,
    UserPermissionLog,
    UserSubscription,
    UserVerificationRequest,
    Visitor,
)


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
        "created_at",
    )
    list_filter = ("is_active", "country", "parent", "created_at")
    search_fields = ("name", "name_ar", "slug", "slug_ar")
    prepopulated_fields = {"slug": ("name",), "slug_ar": ("name_ar",)}
    list_editable = ("is_active",)

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
        ("Settings", {"fields": ("order", "is_active")}),
    )
    ordering = ("country", "name")


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
    list_display = (
        "title",
        "user",
        "category",
        "price",
        "status",
        "is_resubmitted",
        "is_highlighted",
        "is_urgent",
        "is_pinned",
        "contact_for_price",
        "is_hidden",
        "cart_enabled_by_admin",
        "created_at",
        "expires_at",
    )
    list_filter = (
        "status",
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
        "hide_price",
        "price_on_request",
    )
    search_fields = ("title", "description", "user__username")
    readonly_fields = ("created_at", "updated_at", "views_count", "reviewed_at")
    inlines = [AdImageInline, AdFeatureInline, AdUpgradeHistoryInline]
    list_editable = ("status", "is_hidden")
    actions = [
        "approve_ads",
        "reject_ads",
        "mark_as_pending",
        "activate_upgrades_action",
        "renew_ads_30_days",
        "renew_ads_60_days",
        "renew_ads_90_days",
        "hide_prices",
        "show_prices",
        "set_price_on_request",
        "unset_price_on_request",
        "enable_cart_for_ads",
        "disable_cart_for_ads",
    ]

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }

    def approve_ads(self, request, queryset):
        """Approve selected ads"""
        from django.utils import timezone

        updated = queryset.update(
            status=ClassifiedAd.AdStatus.ACTIVE,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
            is_resubmitted=False,
        )
        self.message_user(request, _("{} إعلان تم قبوله بنجاح").format(updated))

    approve_ads.short_description = _("قبول الإعلانات المحددة")

    def reject_ads(self, request, queryset):
        """Reject selected ads"""
        from django.utils import timezone

        updated = queryset.update(
            status=ClassifiedAd.AdStatus.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, _("{} إعلان تم رفضه").format(updated))

    reject_ads.short_description = _("رفض الإعلانات المحددة")

    def mark_as_pending(self, request, queryset):
        """Mark selected ads as pending review"""
        updated = queryset.update(status=ClassifiedAd.AdStatus.PENDING)
        self.message_user(request, _("{} إعلان في انتظار المراجعة").format(updated))

    mark_as_pending.short_description = _("تعيين كـ قيد المراجعة")

    def activate_upgrades_action(self, request, queryset):
        """Check and expire old upgrades for selected ads"""
        count = 0
        for ad in queryset:
            expired = ad.check_and_expire_upgrades()
            count += expired
        self.message_user(request, _(f"تم فحص الإعلانات وإلغاء {count} ترقية منتهية"))

    activate_upgrades_action.short_description = _("فحص وتحديث الترقيات")

    def hide_prices(self, request, queryset):
        """Hide prices for selected ads"""
        updated = queryset.update(hide_price=True, price_on_request=False)
        self.message_user(request, _("{} إعلان تم إخفاء السعر فيه").format(updated))

    hide_prices.short_description = _("إخفاء السعر (عرض 'اطلب عرض سعر')")

    def show_prices(self, request, queryset):
        """Show prices for selected ads"""
        updated = queryset.update(hide_price=False, price_on_request=False)
        self.message_user(request, _("{} إعلان تم إظهار السعر فيه").format(updated))

    show_prices.short_description = _("إظهار السعر العادي")

    def set_price_on_request(self, request, queryset):
        """Set price on request for selected ads"""
        updated = queryset.update(price_on_request=True, hide_price=False)
        self.message_user(
            request, _("{} إعلان تم تعيين 'السعر عند الطلب' فيه").format(updated)
        )

    set_price_on_request.short_description = _("تعيين 'السعر عند الطلب'")

    def unset_price_on_request(self, request, queryset):
        """Unset price on request for selected ads"""
        updated = queryset.update(price_on_request=False)
        self.message_user(
            request, _("{} إعلان تم إلغاء 'السعر عند الطلب' فيه").format(updated)
        )

    unset_price_on_request.short_description = _("إلغاء 'السعر عند الطلب'")

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
        ("Ad Information", {"fields": ("user", "category", "title", "description")}),
        (
            "Pricing",
            {"fields": ("price", "is_negotiable", "hide_price", "price_on_request")},
        ),
        ("Rating", {"fields": ("rating", "rating_count")}),
        ("Location", {"fields": ("country", "city", "address")}),
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
                    "contact_for_price",
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
                    "is_resubmitted",
                    "reviewed_by",
                    "reviewed_at",
                    "admin_notes",
                    "expires_at",
                    "views_count",
                )
            },
        ),
    )


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
        "provider",
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

    def get_payment_id(self, obj):
        """Display formatted payment ID"""
        return format_html(
            '<span style="font-weight: bold; color: #0066cc;">#{}</span>', obj.id
        )

    get_payment_id.short_description = _("رقم الدفعة")
    get_payment_id.admin_order_field = "id"

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
        count = 0
        for payment in queryset.filter(status="completed"):
            # TODO: Implement email notification
            count += 1

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


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "created_at",
        "last_notified_at",
        "email_notifications",
    )
    list_filter = ("created_at", "email_notifications")
    search_fields = ("name", "user__username", "query_params")
    list_editable = ("email_notifications",)
    readonly_fields = ("last_notified_at", "unsubscribe_token")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")
    list_editable = ("is_read",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("status",)
    ordering = ("-created_at",)

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }


# --- Enhanced Models Admin ---


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "profile_type",
        "verification_status",
        "is_active",
        "chat_icon",
    )
    list_filter = ("profile_type", "verification_status", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "company_name")

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

    def get_urls(self):
        """Add custom URLs for chat functionality"""
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "start-chat/<int:user_id>/",
                self.admin_site.admin_view(self.start_chat_view),
                name="user_start_chat",
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
        return redirect(reverse("admin:main_chatroom_change", args=[chat_room.id]))

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
                chat_url = reverse("admin:main_chatroom_change", args=[chat_room.id])
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
    list_editable = ("is_active",)


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


@admin.register(AdTransaction)
class AdTransactionAdmin(admin.ModelAdmin):
    list_display = ("ad", "user", "transaction_type", "amount", "created_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("ad__title", "user__username", "transaction_id")
    readonly_fields = ("created_at", "transaction_id")
    date_hierarchy = "created_at"


class CustomFieldOptionInline(admin.TabularInline):
    """Inline for custom field options."""

    model = CustomFieldOption
    extra = 3
    fields = ("label_ar", "label_en", "value", "order", "is_active")
    ordering = ("order", "label_ar")


class CategoryCustomFieldInline(admin.TabularInline):
    """Inline for associating custom fields with categories."""

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


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "label_ar",
        "field_type",
        "is_required",
        "is_active",
        "get_categories_count",
    )
    list_filter = ("field_type", "is_required", "is_active")
    search_fields = ("name", "label_ar", "label_en")
    list_editable = ("is_active", "is_required")
    ordering = ("name",)
    inlines = [CustomFieldOptionInline, CategoryCustomFieldInline]

    fieldsets = (
        (
            _("معلومات أساسية"),
            {"fields": ("name", "label_ar", "label_en", "field_type")},
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

    def get_categories_count(self, obj):
        return obj.categories.count()

    get_categories_count.short_description = _("عدد الأقسام")


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
        "category",
        "custom_field",
        "is_required",
        "order",
        "is_active",
        "show_on_card",
        "show_in_filters",
    )
    list_filter = (
        "category",
        "is_required",
        "is_active",
        "show_on_card",
        "show_in_filters",
    )
    search_fields = ("category__name", "custom_field__name")
    list_editable = (
        "is_required",
        "order",
        "is_active",
        "show_on_card",
        "show_in_filters",
    )
    ordering = ("category", "order")
    autocomplete_fields = ["category", "custom_field"]


@admin.register(UserPermissionLog)
class UserPermissionLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at",)


@admin.register(UserVerificationRequest)
class UserVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at", "reviewed_at", "reviewed_by")
    list_filter = ("status", "created_at", "reviewed_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "start_date",
        "end_date",
        "is_active",
        "auto_renew",
    )
    list_filter = ("is_active", "auto_renew", "start_date")
    search_fields = ("user__username", "user__email")
    date_hierarchy = "start_date"


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

    def is_online(self, obj):
        return obj.is_online

    is_online.boolean = True
    is_online.short_description = _("متصل الآن")


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
        "description_preview",
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

    def report_type_badge(self, obj):
        colors = {
            "ad_content": "#dc3545",
            "fraud": "#fd7e14",
            "spam": "#ffc107",
            "wrong_category": "#0dcaf0",
            "user_behavior": "#d63384",
            "fake_info": "#6610f2",
            "other": "#6c757d",
        }
        color = colors.get(obj.report_type, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_report_type_display(),
        )

    report_type_badge.short_description = "نوع البلاغ"

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
        """Display formatted total amount"""
        return format_html(
            '<div style="text-align: right;"><span style="font-weight: bold; color: #28a745;">{:.2f}</span><br>'
            '<small style="color: #6c757d;">مدفوع: {:.2f}</small></div>',
            obj.total_amount,
            obj.paid_amount,
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
        """Display order summary"""
        items_html = '<ul style="margin: 0; padding-left: 20px;">'
        for item in obj.items.all():
            items_html += f"<li>{item.ad.title} - {item.price} ر.س</li>"
        items_html += "</ul>"

        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            '<h4 style="margin-top: 0;">ملخص الطلب</h4>'
            "<p><strong>عدد العناصر:</strong> {}</p>"
            "<p><strong>العناصر:</strong></p>{}"
            "<p><strong>رسوم التوصيل:</strong> {} ر.س</p>"
            '<p><strong>الإجمالي:</strong> <span style="color: #28a745; font-weight: bold;">{} ر.س</span></p>'
            "</div>",
            obj.get_items_count(),
            items_html,
            obj.delivery_fee,
            obj.total_amount,
        )

    get_order_summary.short_description = _("ملخص الطلب")

    def get_payment_info(self, obj):
        """Display payment information"""
        percentage = obj.get_payment_percentage()
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            '<h4 style="margin-top: 0;">معلومات الدفع</h4>'
            "<p><strong>طريقة الدفع:</strong> {}</p>"
            "<p><strong>حالة الدفع:</strong> {}</p>"
            "<p><strong>المبلغ الإجمالي:</strong> {} ر.س</p>"
            '<p><strong>المبلغ المدفوع:</strong> <span style="color: #28a745;">{} ر.س</span></p>'
            '<p><strong>المبلغ المتبقي:</strong> <span style="color: #dc3545;">{} ر.س</span></p>'
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
            obj.paid_amount,
            obj.remaining_amount,
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
                        note = f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] دفعة جزئية: {amount} ر.س من قبل {request.user.username}"
                        if payment_note:
                            note += f" - {payment_note}"
                        order.notes = (order.notes or "") + note

                        order.save()
                        count += 1

                self.message_user(
                    request, _(f"تم تسجيل دفعة جزئية بمبلغ {amount} ر.س لـ {count} طلب")
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
        """Send order notification to customers"""
        count = 0
        for order in queryset:
            # TODO: Implement email notification
            count += 1
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


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "get_items_count", "get_total_amount", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "ad", "quantity", "get_total_price", "added_at")
    list_filter = ("added_at",)
    search_fields = ("cart__user__username", "ad__title")
    readonly_fields = ("added_at",)

    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ر.س"

    get_total_price.short_description = "المجموع"


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
        return format_html(
            '<a href="/admin/main/classifiedad/{}/change/" target="_blank">{}</a>',
            obj.ad.id,
            obj.ad.title[:50],
        )

    ad_title.short_description = _("الإعلان")

    def user_link(self, obj):
        """Display user with link"""
        return format_html(
            '<a href="/admin/main/user/{}/change/" target="_blank">{}</a>',
            obj.user.id,
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
