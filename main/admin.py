from django.contrib import admin

from .models import AboutPage, Category, CompanyValue, ContactInfo, ContactMessage


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
