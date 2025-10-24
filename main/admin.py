from django.contrib import admin

from .models import (
    AboutPage,
    AdFeature,
    AdImage,
    AdPackage,
    Category,
    ClassifiedAd,
    CompanyValue,
    ContactInfo,
    ContactMessage,
    SavedSearch,
    UserPackage,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
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
        ("Settings", {"fields": ("order", "is_active")}),
    )
    ordering = ("country", "name")


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ("title", "tagline", "is_active", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("title", "tagline", "description")
    list_editable = ("is_active",)
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "tagline", "description", "is_active")},
        ),
        ("Vision & Mission", {"fields": ("vision", "mission")}),
        (
            "Statistics",
            {
                "fields": (
                    "customers_count",
                    "vendors_count",
                    "products_count",
                    "countries_count",
                )
            },
        ),
    )


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("email", "phone", "address", "is_active")
    list_filter = ("is_active",)
    search_fields = ("email", "phone", "address")
    fieldsets = (
        ("Contact Details", {"fields": ("email", "phone", "whatsapp", "address")}),
        ("Maps & Location", {"fields": ("google_maps_link", "map_embed_url")}),
        ("Social Media", {"fields": ("facebook", "twitter", "instagram", "linkedin")}),
        ("Business Hours", {"fields": ("working_hours",)}),
        ("Settings", {"fields": ("is_active",)}),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("status",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")

    fieldsets = (
        ("Message Information", {"fields": ("name", "email", "subject", "message")}),
        ("User Information", {"fields": ("user", "phone")}),
        (
            "Status & Timestamps",
            {"fields": ("status", "admin_notes", "created_at", "updated_at")},
        ),
    )


@admin.register(CompanyValue)
class CompanyValueAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_class", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    list_editable = ("order", "is_active")
    ordering = ("order",)


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
        "created_at",
        "expires_at",
    )
    list_filter = ("status", "category", "is_cart_enabled", "is_delivery_available")
    search_fields = ("title", "description", "user__username")
    readonly_fields = ("created_at", "updated_at", "views_count")
    inlines = [AdImageInline, AdFeatureInline]
    fieldsets = (
        ("Ad Information", {"fields": ("user", "category", "title", "description")}),
        ("Pricing", {"fields": ("price", "is_negotiable")}),
        ("Location", {"fields": ("country", "city", "address")}),
        (
            "Features",
            {
                "fields": (
                    "video_url",
                    "video_file",
                    "is_cart_enabled",
                    "is_delivery_available",
                )
            },
        ),
        ("Status", {"fields": ("status", "expires_at", "views_count")}),
    )


@admin.register(AdPackage)
class AdPackageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "ad_count",
        "duration_days",
        "is_default",
        "is_active",
        "category",
    )
    list_filter = ("is_active", "is_default", "category")
    search_fields = ("name", "description")
    list_editable = ("is_active", "is_default")


@admin.register(UserPackage)
class UserPackageAdmin(admin.ModelAdmin):
    list_display = ("user", "package", "purchase_date", "expiry_date", "ads_remaining")
    list_filter = ("package", "purchase_date", "expiry_date")
    search_fields = ("user__username", "package__name")
    readonly_fields = ("purchase_date", "expiry_date", "ads_remaining")


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
