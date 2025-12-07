# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget
from solo.admin import SingletonModelAdmin

from .models import (
    Blog,
    Comment,
    Country,
    HomeSlider,
    SiteConfiguration,
    AboutPage,
    ContactPage,
    HomePage,
    TermsPage,
    PrivacyPage,
)


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


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = [
        "image_preview",
        "title_display",
        "country_display",
        "is_active",
        "order",
        "created_at",
    ]
    list_filter = ["is_active", "country", "created_at"]
    search_fields = ["title", "title_ar", "subtitle", "subtitle_ar"]
    list_editable = ["is_active", "order"]
    ordering = ["order", "-created_at"]

    fieldsets = (
        (
            "الدولة",
            {
                "fields": ("country",),
            },
        ),
        (
            "العنوان",
            {
                "fields": ("title", "title_ar"),
            },
        ),
        (
            "العنوان الفرعي",
            {
                "fields": ("subtitle", "subtitle_ar"),
            },
        ),
        (
            "الوصف",
            {
                "fields": ("description", "description_ar"),
                "classes": ("collapse",),
            },
        ),
        (
            "الصورة والألوان",
            {
                "fields": ("image", "background_color", "text_color"),
            },
        ),
        (
            "الزر",
            {
                "fields": ("button_text", "button_text_ar", "button_url"),
            },
        ),
        (
            "الإعدادات",
            {
                "fields": ("is_active", "order"),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="default")},
    }

    def image_preview(self, obj):
        """Display image preview in admin list"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "الصورة"

    def title_display(self, obj):
        """Display title with fallback"""
        return obj.title_ar or obj.title

    title_display.short_description = "العنوان"

    def country_display(self, obj):
        """Display country flag and name"""
        if obj.country:
            return format_html(
                "<span>{} {}</span>",
                obj.country.flag_emoji,
                obj.country.name,
            )
        return format_html(
            '<span style="color: #999;">{% trans "عام - All Countries" %}</span>'
        )

    country_display.short_description = "الدولة"

    actions = ["activate_slides", "deactivate_slides"]

    def activate_slides(self, request, queryset):
        """Activate selected slides"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"تم تفعيل {updated} شريحة")

    activate_slides.short_description = "تفعيل الشرائح المحددة"

    def deactivate_slides(self, request, queryset):
        """Deactivate selected slides"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"تم إلغاء تفعيل {updated} شريحة")

    deactivate_slides.short_description = "إلغاء تفعيل الشرائح المحددة"


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_date", "is_published", "tag_list")
    list_filter = ("is_published", "author")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"
    ordering = ("-published_date",)

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())

    tag_list.short_description = "Tags"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "body", "blog", "created_on", "active")
    list_filter = ("active", "created_on")
    search_fields = ("author__username", "body")
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


# Solo Model Admins for Site Configuration
@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            "SEO و الكلمات المفتاحية",
            {
                "fields": (
                    "meta_keywords",
                    "meta_keywords_ar",
                )
            },
        ),
        (
            "محتوى التذييل",
            {
                "fields": (
                    "footer_text",
                    "footer_text_ar",
                    "copyright_text",
                )
            },
        ),
    )

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="default")},
    }


@admin.register(AboutPage)
class AboutPageAdmin(SingletonModelAdmin):
    fieldsets = (
        ("العنوان", {"fields": ("title", "title_ar")}),
        ("المحتوى الرئيسي", {"fields": ("content", "content_ar", "featured_image")}),
        ("رسالتنا", {"fields": ("mission", "mission_ar"), "classes": ("collapse",)}),
        ("رؤيتنا", {"fields": ("vision", "vision_ar"), "classes": ("collapse",)}),
        ("قيمنا", {"fields": ("values", "values_ar"), "classes": ("collapse",)}),
    )


@admin.register(ContactPage)
class ContactPageAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            "العنوان والوصف",
            {"fields": ("title", "title_ar", "description", "description_ar")},
        ),
        ("إعدادات النموذج", {"fields": ("enable_contact_form", "notification_email")}),
        ("ساعات العمل", {"fields": ("office_hours", "office_hours_ar")}),
        ("الخريطة", {"fields": ("map_embed_code",), "classes": ("collapse",)}),
    )


@admin.register(HomePage)
class HomePageAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            "قسم البطل (Hero Section)",
            {
                "fields": (
                    "hero_title",
                    "hero_title_ar",
                    "hero_subtitle",
                    "hero_subtitle_ar",
                    "hero_image",
                    "hero_button_text",
                    "hero_button_text_ar",
                    "hero_button_url",
                )
            },
        ),
        (
            "نافذة الإعلان (Modal)",
            {
                "fields": (
                    "show_modal",
                    "modal_title",
                    "modal_title_ar",
                    "modal_content",
                    "modal_content_ar",
                    "modal_image",
                    "modal_button_text",
                    "modal_button_text_ar",
                    "modal_button_url",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "الأقسام المميزة",
            {
                "fields": ("show_featured_categories", "show_featured_ads"),
                "classes": ("collapse",),
            },
        ),
    )

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="default")},
    }

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    approve_comments.short_description = "Approve selected comments"


@admin.register(TermsPage)
class TermsPageAdmin(SingletonModelAdmin):
    fieldsets = (
        ("العنوان", {"fields": ("title", "title_ar")}),
        ("المحتوى", {"fields": ("content", "content_ar")}),
        ("معلومات التحديث", {"fields": ("last_updated",), "classes": ("collapse",)}),
    )

    readonly_fields = ("last_updated",)

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="default")},
    }


@admin.register(PrivacyPage)
class PrivacyPageAdmin(SingletonModelAdmin):
    fieldsets = (
        ("العنوان", {"fields": ("title", "title_ar")}),
        ("المحتوى", {"fields": ("content", "content_ar")}),
        ("معلومات التحديث", {"fields": ("last_updated",), "classes": ("collapse",)}),
    )

    readonly_fields = ("last_updated",)

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="default")},
    }
