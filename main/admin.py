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
    AboutPage,
    AdFeature,
    AdFeaturePrice,
    AdImage,
    AdPackage,
    AdReservation,
    AdTransaction,
    CartSettings,
    Category,
    ClassifiedAd,
    CompanyValue,
    ContactInfo,
    ContactMessage,
    CustomField,
    Notification,
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
        models.TextField: {'widget': CKEditor5Widget(config_name='admin')},
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


@admin.register(ClassifiedAd)
class ClassifiedAdAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "category",
        "price",
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
    )
    search_fields = ("title", "description", "user__username")
    readonly_fields = ("created_at", "updated_at", "views_count", "reviewed_at")
    inlines = [AdImageInline, AdFeatureInline]
    list_editable = ("status", "is_hidden")
    actions = ["approve_ads", "reject_ads", "mark_as_pending"]

    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='admin')},
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

    fieldsets = (
        ("Ad Information", {"fields": ("user", "category", "title", "description")}),
        ("Pricing", {"fields": ("price", "is_negotiable")}),
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
        "is_active_status",
    )
    list_filter = ("package", "purchase_date", "expiry_date")
    search_fields = ("user__username", "user__email", "package__name")
    readonly_fields = ("purchase_date", "expiry_date", "ads_remaining")

    def is_active_status(self, obj):
        return obj.is_active()

    is_active_status.boolean = True
    is_active_status.short_description = _("نشطة")


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


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ("title", "tagline", "is_active", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("title", "tagline", "who_we_are_content")
    list_editable = ("is_active",)

    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='admin')},
    }


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("email", "phone", "address", "is_active")
    list_filter = ("is_active",)
    search_fields = ("email", "phone", "address")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("status",)
    ordering = ("-created_at",)

    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='admin')},
    }


@admin.register(CompanyValue)
class CompanyValueAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_class", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    list_editable = ("order", "is_active")
    ordering = ("order",)

    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='admin')},
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


@admin.register(AdReservation)
class AdReservationAdmin(admin.ModelAdmin):
    list_display = (
        "ad",
        "user",
        "status",
        "reservation_amount",
        "created_at",
        "expires_at",
    )
    list_filter = ("status", "created_at", "expires_at")
    search_fields = ("ad__title", "user__username", "user__email")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(AdTransaction)
class AdTransactionAdmin(admin.ModelAdmin):
    list_display = ("ad", "user", "transaction_type", "amount", "created_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("ad__title", "user__username", "transaction_id")
    readonly_fields = ("created_at", "transaction_id")
    date_hierarchy = "created_at"


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "name",
        "label_ar",
        "field_type",
        "is_required",
        "is_active",
        "order",
    )
    list_filter = ("field_type", "is_required", "is_active", "category")
    search_fields = ("name", "label_ar", "label_en")
    list_editable = ("order", "is_active", "is_required")
    ordering = ("category", "order", "name")


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
