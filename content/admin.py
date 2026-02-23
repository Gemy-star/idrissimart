# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
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
    AboutPageSection,
    ContactPage,
    HomePage,
    WhyChooseUsFeature,
    TermsPage,
    PaymentMethodConfig,
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
    list_filter = ["is_active", "currency", "created_at"]
    search_fields = ["name", "name_en", "code", "phone_code"]
    list_editable = ["is_active", "order"]
    ordering = ["order", "name"]
    date_hierarchy = "created_at"
    list_per_page = 25

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
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "name_en", "slug", "description"]
    list_editable = ["order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order", "name"]
    date_hierarchy = "created_at"
    list_per_page = 25
    actions = ["activate_categories", "deactivate_categories"]

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

    def activate_categories(self, request, queryset):
        """Activate selected blog categories"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"تم تفعيل {updated} تصنيف")

    activate_categories.short_description = "تفعيل التصنيفات المحددة"

    def deactivate_categories(self, request, queryset):
        """Deactivate selected blog categories"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"تم إلغاء تفعيل {updated} تصنيف")

    deactivate_categories.short_description = "إلغاء تفعيل التصنيفات المحددة"


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
    list_filter = ("is_published", "author", "category", "published_date")
    search_fields = ("title", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"
    ordering = ("-published_date",)
    list_per_page = 25
    readonly_fields = ("views_count", "published_date")
    actions = ["publish_blogs", "unpublish_blogs"]

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="admin")},
    }

    fieldsets = (
        (
            _("معلومات أساسية"),
            {"fields": ("title", "slug", "author", "category")},
        ),
        (
            _("المحتوى"),
            {"fields": ("content", "featured_image")},
        ),
        (
            _("الحالة والإحصائيات"),
            {"fields": ("is_published", "published_date", "views_count")},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category", "author")

    def publish_blogs(self, request, queryset):
        """Publish selected blogs"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"تم نشر {updated} مدونة")

    publish_blogs.short_description = _("نشر المدونات المحددة")

    def unpublish_blogs(self, request, queryset):
        """Unpublish selected blogs"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"تم إلغاء نشر {updated} مدونة")

    unpublish_blogs.short_description = _("إلغاء نشر المدونات المحددة")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "body_preview", "blog", "created_on", "active")
    list_filter = ("active", "created_on")
    search_fields = ("author__username", "body", "blog__title")
    readonly_fields = ("created_on",)
    date_hierarchy = "created_on"
    list_per_page = 25
    actions = ["approve_comments", "disapprove_comments"]

    def body_preview(self, obj):
        """Display comment preview"""
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body

    body_preview.short_description = _("التعليق")

    def approve_comments(self, request, queryset):
        """Approve selected comments"""
        updated = queryset.update(active=True)
        self.message_user(request, f"تم قبول {updated} تعليق")

    approve_comments.short_description = _("قبول التعليقات")

    def disapprove_comments(self, request, queryset):
        """Disapprove selected comments"""
        updated = queryset.update(active=False)
        self.message_user(request, f"تم رفض {updated} تعليق")

    disapprove_comments.short_description = _("رفض التعليقات")


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
            "شعارات الموقع",
            {
                "fields": (
                    "logo",
                    "logo_light",
                    "logo_dark",
                    "logo_mini",
                ),
                "description": "قم برفع الشعارات المختلفة للموقع. الشعار الافتراضي يُستخدم إذا لم يتم رفع الشعارات الأخرى."
            },
        ),
        (
            "إعدادات التحقق من الحسابات",
            {
                "fields": (
                    "require_email_verification",
                    "require_phone_verification",
                    "require_verification_for_services",
                    "require_verification_for_free_package",
                    "verification_services_message",
                    "verification_services_message_ar",
                ),
                "description": "إعدادات التحقق من البريد الإلكتروني ورقم الهاتف أثناء التسجيل وعند استخدام خدمات الموقع والباقات المجانية",
            },
        ),
        (
            "إعدادات الدفع العام",
            {
                "fields": ("allow_online_payment", "allow_offline_payment"),
                "description": "تفعيل أو تعطيل طرق الدفع الإلكتروني واليدوي على مستوى الموقع",
            },
        ),
        (
            "إعدادات الدفع - InstaPay",
            {
                "fields": ("instapay_qr_code", "instapay_phone"),
                "description": "قم برفع صورة رمز QR الخاص بحساب InstaPay لتفعيل خيار الدفع عبر InstaPay في صفحة الدفع",
            },
        ),
        (
            "إعدادات المحفظة الإلكترونية",
            {
                "fields": ("wallet_payment_link", "wallet_phone"),
                "description": "رابط ورقم المحفظة الإلكترونية (Vodafone Cash، Orange Money، إلخ) لتفعيل خيار الدفع عبر المحفظة",
            },
        ),
        (
            "إعدادات رسوم خدمة السلة",
            {
                "fields": (
                    "cart_service_fee_type",
                    "cart_service_fixed_fee",
                    "cart_service_percentage",
                    "cart_service_instructions",
                ),
                "description": "إعدادات رسوم الخدمة التي يتم خصمها من الناشر عند البيع عبر المنصة",
            },
        ),
        (
            "نصائح الأمان للمشترين",
            {
                "fields": (
                    "buyer_safety_notes_enabled",
                    "buyer_safety_notes_title",
                    "buyer_safety_notes_title_ar",
                    "buyer_safety_notes",
                    "buyer_safety_notes_ar",
                ),
                "description": "النصائح الإرشادية التي تظهر للمشتري بجوار الإعلان لتوعيتهم بكيفية التعامل الآمن",
            },
        ),
    )

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="default")},
    }


class AboutPageSectionInline(admin.TabularInline):
    """Inline editor for About Page Sections"""
    model = AboutPageSection
    extra = 1
    fields = ('tab_title', 'tab_title_ar', 'icon', 'order', 'is_active')
    ordering = ['order', 'id']


@admin.register(AboutPage)
class AboutPageAdmin(SingletonModelAdmin):
    fieldsets = (
        ("العنوان", {"fields": ("title", "title_ar")}),
        (
            "قسم البطل - Hero Section",
            {
                "fields": ("tagline", "tagline_ar", "subtitle", "subtitle_ar"),
                "description": "الشعار والعنوان الفرعي الذي يظهر في أعلى الصفحة"
            }
        ),
        ("المحتوى الرئيسي", {"fields": ("content", "content_ar", "featured_image")}),
        ("رسالتنا", {"fields": ("mission", "mission_ar"), "classes": ("collapse",)}),
        ("رؤيتنا", {"fields": ("vision", "vision_ar"), "classes": ("collapse",)}),
        ("قيمنا", {"fields": ("values", "values_ar"), "classes": ("collapse",)}),
        (
            "قسم ماذا نقدم - What We Offer",
            {
                "fields": ("what_we_offer_title", "what_we_offer_title_ar"),
                "description": "عنوان قسم ماذا نقدم. استخدم الأقسام أدناه لإضافة محتوى ديناميكي"
            }
        ),
    )
    inlines = [AboutPageSectionInline]


@admin.register(AboutPageSection)
class AboutPageSectionAdmin(admin.ModelAdmin):
    """Detailed admin for About Page Sections"""
    list_display = ['tab_title_ar', 'tab_title', 'icon', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['tab_title', 'tab_title_ar', 'content', 'content_ar']
    ordering = ['order', 'id']

    fieldsets = (
        (
            "عنوان التبويب",
            {
                "fields": ("about_page", "tab_title", "tab_title_ar", "icon"),
                "description": "عنوان التبويب الذي سيظهر في الأزرار"
            }
        ),
        (
            "المحتوى",
            {
                "fields": ("content", "content_ar"),
                "description": "محتوى القسم بتنسيق HTML الغني"
            }
        ),
        (
            "الإعدادات",
            {
                "fields": ("order", "is_active"),
                "description": "ترتيب ظهور القسم وحالته"
            }
        ),
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


class WhyChooseUsFeatureInline(admin.TabularInline):
    """Inline editor for Why Choose Us Features"""
    model = WhyChooseUsFeature
    extra = 1
    fields = ('title_ar', 'title', 'description_ar', 'icon', 'order', 'is_active')
    ordering = ['order', 'id']


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
            "قسم لماذا نحن (Why Choose Us)",
            {
                "fields": (
                    "show_why_choose_us",
                    "why_choose_us_title",
                    "why_choose_us_title_ar",
                    "why_choose_us_subtitle",
                    "why_choose_us_subtitle_ar",
                ),
                "description": "عنوان القسم. استخدم المميزات أدناه لإضافة محتوى ديناميكي"
            },
        ),
        (
            "قسم الإحصائيات (Statistics Section)",
            {
                "fields": (
                    "show_statistics",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "الإحصائية 1",
            {
                "fields": (
                    "stat1_value",
                    "stat1_title",
                    "stat1_title_ar",
                    "stat1_subtitle",
                    "stat1_subtitle_ar",
                    "stat1_icon",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "الإحصائية 2",
            {
                "fields": (
                    "stat2_value",
                    "stat2_title",
                    "stat2_title_ar",
                    "stat2_subtitle",
                    "stat2_subtitle_ar",
                    "stat2_icon",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "الإحصائية 3",
            {
                "fields": (
                    "stat3_value",
                    "stat3_title",
                    "stat3_title_ar",
                    "stat3_subtitle",
                    "stat3_subtitle_ar",
                    "stat3_icon",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "الإحصائية 4",
            {
                "fields": (
                    "stat4_value",
                    "stat4_title",
                    "stat4_title_ar",
                    "stat4_subtitle",
                    "stat4_subtitle_ar",
                    "stat4_icon",
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

    inlines = [WhyChooseUsFeatureInline]

    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="default")},
    }

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    approve_comments.short_description = "Approve selected comments"


@admin.register(WhyChooseUsFeature)
class WhyChooseUsFeatureAdmin(admin.ModelAdmin):
    """Detailed admin for Why Choose Us Features"""
    list_display = ['icon_display', 'title_ar', 'title', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'title_ar', 'description', 'description_ar']
    ordering = ['order', 'id']

    fieldsets = (
        (
            "عنوان الميزة",
            {
                "fields": ("home_page", "title", "title_ar", "icon"),
                "description": "عنوان الميزة والأيقونة"
            }
        ),
        (
            "الوصف",
            {
                "fields": ("description", "description_ar"),
                "description": "وصف تفصيلي للميزة"
            }
        ),
        (
            "الإعدادات",
            {
                "fields": ("order", "is_active"),
                "description": "ترتيب ظهور الميزة وحالتها"
            }
        ),
    )

    def icon_display(self, obj):
        """Display icon preview"""
        return format_html(
            '<i class="{}" style="font-size: 20px; color: #6b4c7a;"></i>',
            obj.icon,
        )

    icon_display.short_description = "الأيقونة"


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


@admin.register(PaymentMethodConfig)
class PaymentMethodConfigAdmin(admin.ModelAdmin):
    """Admin interface for payment method configuration"""

    list_display = [
        "context_display",
        "visa_status",
        "paypal_status",
        "wallet_status",
        "instapay_status",
        "cod_status",
        "partial_status",
        "is_active",
        "updated_at",
    ]
    list_filter = ["is_active", "context"]
    search_fields = ["context", "notes"]

    fieldsets = (
        (
            _("معلومات أساسية"),
            {
                "fields": ("context", "is_active", "notes"),
            },
        ),
        (
            _("وسائل الدفع المتاحة"),
            {
                "fields": (
                    "visa_enabled",
                    "paypal_enabled",
                    "wallet_enabled",
                    "instapay_enabled",
                    "cod_enabled",
                    "partial_enabled",
                ),
                "description": _("حدد وسائل الدفع المتاحة لهذا النوع من المعاملات"),
            },
        ),
        (
            _("إعدادات الدفع عند الاستلام (COD)"),
            {
                "fields": (
                    "cod_requires_deposit",
                    "cod_deposit_type",
                    "cod_deposit_amount",
                    "cod_deposit_percentage",
                ),
                "description": _("إعدادات مبلغ الحجز المطلوب للدفع عند الاستلام"),
                "classes": ("collapse",),
            },
        ),
        (
            _("معلومات إضافية"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]

    def context_display(self, obj):
        """Display context in Arabic"""
        return obj.get_context_display()

    context_display.short_description = _("سياق الدفع")

    def visa_status(self, obj):
        return "✅" if obj.visa_enabled else "❌"

    visa_status.short_description = _("فيزا/ماستركارد")

    def paypal_status(self, obj):
        return "✅" if obj.paypal_enabled else "❌"

    paypal_status.short_description = _("باي بال")

    def wallet_status(self, obj):
        return "✅" if obj.wallet_enabled else "❌"

    wallet_status.short_description = _("محفظة")

    def instapay_status(self, obj):
        return "✅" if obj.instapay_enabled else "❌"

    instapay_status.short_description = _("إنستا باي")

    def cod_status(self, obj):
        return "✅" if obj.cod_enabled else "❌"

    cod_status.short_description = _("COD")

    def partial_status(self, obj):
        return "✅" if obj.partial_enabled else "❌"

    partial_status.short_description = _("دفع جزئي")

    def save_model(self, request, obj, form, change):
        """Override to add validation"""
        # Ensure at least one payment method is enabled
        if not any(
            [
                obj.visa_enabled,
                obj.paypal_enabled,
                obj.wallet_enabled,
                obj.instapay_enabled,
                obj.cod_enabled,
                obj.partial_enabled,
            ]
        ):
            from django.contrib import messages

            messages.warning(
                request,
                _("تحذير: لا توجد وسائل دفع مفعلة! يجب تفعيل وسيلة واحدة على الأقل."),
            )

        super().save_model(request, obj, form, change)
