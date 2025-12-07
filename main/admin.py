from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
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
        "is_highlighted",
        "is_urgent",
        "is_pinned",
        "status",
        "is_hidden",
        "cart_enabled_by_admin",
        "created_at",
        "expires_at",
    )
    list_filter = (
        "status",
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
        "hide_prices",
        "show_prices",
        "set_price_on_request",
        "unset_price_on_request",
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
    readonly_fields = ("purchase_date", "expiry_date", "ads_remaining", "ads_used")
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
        "user",
        "provider",
        "amount",
        "currency",
        "status",
        "created_at",
        "completed_at",
    )
    list_filter = (
        "status",
        "provider",
        "currency",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "provider_transaction_id",
        "description",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
    )
    date_hierarchy = "created_at"
    actions = ["mark_as_completed", "mark_as_failed"]

    def mark_as_completed(self, request, queryset):
        """Mark payments as completed"""
        from django.utils import timezone

        updated = queryset.filter(status="pending").update(
            status="completed", completed_at=timezone.now()
        )
        self.message_user(request, _(f"تم تحديد {updated} دفعة كمكتملة"))

    mark_as_completed.short_description = _("تحديد كمكتملة")

    def mark_as_failed(self, request, queryset):
        """Mark payments as failed"""
        updated = queryset.filter(status="pending").update(status="failed")
        self.message_user(request, _(f"تم تحديد {updated} دفعة كفاشلة"))

    mark_as_failed.short_description = _("تحديد كفاشلة")

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
                "fields": ("metadata",),
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
    fields = ("category", "is_required", "order", "is_active", "show_on_card")
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
    list_display = ("category", "custom_field", "is_required", "order", "is_active")
    list_filter = ("category", "is_required", "is_active")
    search_fields = ("category__name", "custom_field__name")
    list_editable = ("is_required", "order", "is_active")
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
        "report_type",
        "status",
        "reporter",
        "reported_ad",
        "reported_user",
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
        "order_number",
        "user",
        "full_name",
        "phone",
        "city",
        "total_amount",
        "payment_method",
        "status",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order_number", "user__username", "full_name", "phone")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]

    fieldsets = (
        (
            "معلومات الطلب",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "payment_method",
                    "total_amount",
                )
            },
        ),
        (
            "معلومات التوصيل",
            {"fields": ("full_name", "phone", "address", "city", "postal_code")},
        ),
        ("ملاحظات", {"fields": ("notes",)}),
        ("التواريخ", {"fields": ("created_at", "updated_at")}),
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
