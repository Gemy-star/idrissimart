# admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = [
        "flag_display",
        "name",
        "name_en",
        "code",
        "phone_code",
        "currency",
        "is_active",
        "order",
    ]
    list_filter = ["is_active", "currency"]
    search_fields = ["name", "name_en", "code", "phone_code"]
    list_editable = ["is_active", "order"]
    ordering = ["order", "name"]

    fieldsets = (
        ("معلومات أساسية", {"fields": ("name", "name_en", "code", "flag_emoji")}),
        (
            "معلومات إضافية",
            {"fields": ("phone_code", "currency", "order", "is_active")},
        ),
        (
            "التواريخ",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ["created_at", "updated_at"]

    def flag_display(self, obj):
        """Display flag emoji in admin list"""
        return format_html('<span style="font-size: 1.5rem;">{}</span>', obj.flag_emoji)

    flag_display.short_description = "العلم"

    actions = ["activate_countries", "deactivate_countries"]

    def activate_countries(self, request, queryset):
        """Activate selected countries"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"تم تفعيل {updated} دولة")

    activate_countries.short_description = "تفعيل الدول المحددة"

    def deactivate_countries(self, request, queryset):
        """Deactivate selected countries"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"تم إلغاء تفعيل {updated} دولة")

    deactivate_countries.short_description = "إلغاء تفعيل الدول المحددة"
