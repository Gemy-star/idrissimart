# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import JSONField, Textarea
from django_ckeditor_5.widgets import CKEditor5Widget
from solo.admin import SingletonModelAdmin

from .models import (
    Blog,
    BlogCategory,
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
        "cities_count",
        "is_active",
        "order",
    ]
    list_filter = ["is_active", "currency"]
    search_fields = ["name", "name_en", "code", "phone_code"]
    list_editable = ["is_active", "order"]
    ordering = ["order", "name"]

    # Use a better widget for JSON field
    formfield_overrides = {
        models.JSONField: {
            "widget": Textarea(
                attrs={"rows": 10, "cols": 80, "style": "font-family: monospace;"}
            )
        },
    }

    fieldsets = (
        ("معلومات أساسية", {"fields": ("name", "name_en", "code", "flag_emoji")}),
        (
            "معلومات إضافية",
            {"fields": ("phone_code", "currency", "order", "is_active")},
        ),
        (
            "المدن",
            {
                "fields": ("cities",),
                "description": "قائمة المدن بصيغة JSON. استخدم الأمر populate_cities لملء البيانات تلقائياً أو استخدم الإجراء 'تحديث المدن' من القائمة أعلاه.",
            },
        ),
        (
            "التواريخ",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def cities_count(self, obj):
        """Display number of cities for this country"""
        if obj.cities:
            return f"{len(obj.cities)} مدينة"
        return "0 مدينة"

    cities_count.short_description = "عدد المدن"

    readonly_fields = ["created_at", "updated_at"]

    actions = ["populate_cities_action"]

    def populate_cities_action(self, request, queryset):
        """Admin action to populate cities for selected countries"""
        from django.core.management import call_command
        from io import StringIO

        updated = 0
        for country in queryset:
            if country.code in ["SA", "EG", "AE", "KW", "QA", "BH"]:
                # Trigger the populate_cities command
                out = StringIO()
                call_command("populate_cities", stdout=out)
                updated += 1

        if updated > 0:
            self.message_user(request, f"تم تحديث المدن لـ {updated} دولة بنجاح")
        else:
            self.message_user(
                request,
                "لم يتم تحديث أي دولة. تأكد من تحديد دول مدعومة (SA, EG, AE, KW, QA, BH)",
            )

    populate_cities_action.short_description = "تحديث المدن للدول المحددة"

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


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "icon_display",
        "name",
        "name_en",
        "color_display",
        "order",
        "is_active",
        "blogs_count",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "name_en", "slug"]
    list_editable = ["order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order", "name"]

    fieldsets = (
        (
            "معلومات أساسية",
            {
                "fields": (
                    "name",
                    "name_en",
                    "slug",
                    "description",
                    "description_en",
                )
            },
        ),
        (
            "التخصيص",
            {"fields": ("icon", "color", "order", "is_active")},
        ),
        (
            "التواريخ",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def icon_display(self, obj):
        return format_html(
            '<i class="{}" style="color: {}; font-size: 20px;"></i>',
            obj.icon,
            obj.color,
        )

    icon_display.short_description = "الأيقونة"

    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border-radius: 3px; border: 1px solid #ddd;"></span> {}',
            obj.color,
            obj.color,
        )

    color_display.short_description = "اللون"

    def blogs_count(self, obj):
        return obj.get_blogs_count()

    blogs_count.short_description = "عدد المدونات"


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
    list_display = (
        "title",
        "author",
        "category",
        "published_date",
        "views_count",
        "is_published",
    )
    list_filter = ("is_published", "author", "category")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"
    ordering = ("-published_date",)

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")


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
        (
            "إعدادات التحقق من الحسابات",
            {
                "fields": (
                    "require_email_verification",
                    "require_phone_verification",
                    "require_verification_for_services",
                    "verification_services_message",
                    "verification_services_message_ar",
                ),
                "description": "إعدادات التحقق من البريد الإلكتروني ورقم الهاتف أثناء التسجيل وعند استخدام خدمات الموقع",
            },
        ),
        (
            "إعدادات الدفع - InstaPay",
            {
                "fields": ("instapay_qr_code",),
                "description": "قم برفع صورة رمز QR الخاص بحساب InstaPay لتفعيل خيار الدفع عبر InstaPay في صفحة الدفع",
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
        (
            "إعدادات الإظهار",
            {
                "fields": (
                    "show_phone",
                    "show_address",
                    "show_office_hours",
                    "show_map",
                ),
                "description": "تحكم في إظهار أو إخفاء العناصر في صفحة اتصل بنا",
            },
        ),
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
