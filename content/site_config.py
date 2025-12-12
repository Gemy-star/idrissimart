"""
Site Configuration Models using django-solo
Singleton models for managing site-wide settings
Only includes settings NOT covered by django-constance
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel
from django_ckeditor_5.fields import CKEditor5Field


class SiteConfiguration(SingletonModel):
    """
    Site-wide configuration settings
    Note: Basic contact info and social media are in django-constance
    This model handles additional UI/content settings
    """

    # SEO Meta tags
    meta_keywords = models.CharField(
        max_length=500, blank=True, verbose_name=_("الكلمات المفتاحية - Meta Keywords")
    )
    meta_keywords_ar = models.CharField(
        max_length=500, blank=True, verbose_name=_("الكلمات المفتاحية بالعربية")
    )

    # Footer content
    footer_text = CKEditor5Field(
        blank=True, verbose_name=_("نص التذييل - Footer Text"), config_name="default"
    )
    footer_text_ar = CKEditor5Field(
        blank=True, verbose_name=_("نص التذييل بالعربية"), config_name="default"
    )

    # Copyright
    copyright_text = models.CharField(
        max_length=200,
        default="© 2024 إدريسي مارت. جميع الحقوق محفوظة.",
        verbose_name=_("نص حقوق النشر"),
    )

    # Verification Settings
    require_email_verification = models.BooleanField(
        default=False,
        verbose_name=_("التحقق من البريد الإلكتروني إلزامي"),
        help_text=_(
            "إذا كان مفعلاً، يجب على المستخدمين تأكيد بريدهم الإلكتروني أثناء التسجيل"
        ),
    )

    require_phone_verification = models.BooleanField(
        default=False,
        verbose_name=_("التحقق من رقم الهاتف إلزامي"),
        help_text=_("إذا كان مفعلاً، يجب على المستخدمين تأكيد رقم هاتفهم أثناء التسجيل"),
    )

    require_verification_for_services = models.BooleanField(
        default=False,
        verbose_name=_("التحقق مطلوب لاستخدام الخدمات"),
        help_text=_(
            "إذا كان مفعلاً، يجب التحقق من الحساب لاستخدام خدمات الموقع (نشر إعلانات، إضافة للسلة، إلخ)"
        ),
    )

    verification_services_message = models.TextField(
        default="يجب التحقق من حسابك لاستخدام هذه الخدمة",
        verbose_name=_("رسالة التحقق للخدمات"),
        help_text=_(
            "الرسالة التي تظهر للمستخدمين غير المتحققين عند محاولة استخدام الخدمات"
        ),
    )
    verification_services_message_ar = models.TextField(
        default="يجب التحقق من حسابك لاستخدام هذه الخدمة",
        verbose_name=_("رسالة التحقق للخدمات بالعربية"),
    )

    # Payment Settings - InstaPay QR Code
    instapay_qr_code = models.ImageField(
        upload_to="payment/instapay/",
        blank=True,
        null=True,
        verbose_name=_("رمز QR لـ InstaPay"),
        help_text=_(
            "قم برفع صورة رمز QR الخاص بحساب InstaPay للدفع غير المتصل بالإنترنت"
        ),
    )

    class Meta:
        verbose_name = _("إعدادات الموقع")
        verbose_name_plural = _("إعدادات الموقع")

    def __str__(self):
        return "Site Configuration"


class AboutPage(SingletonModel):
    """About Us page content"""

    title = models.CharField(
        max_length=200, default="About Us", verbose_name=_("العنوان - Title")
    )
    title_ar = models.CharField(
        max_length=200, default="من نحن", verbose_name=_("العنوان بالعربية")
    )

    content = CKEditor5Field(
        blank=True, verbose_name=_("المحتوى - Content"), config_name="default"
    )
    content_ar = CKEditor5Field(
        blank=True, verbose_name=_("المحتوى بالعربية"), config_name="default"
    )

    mission = CKEditor5Field(
        blank=True, verbose_name=_("رسالتنا - Mission"), config_name="default"
    )
    mission_ar = CKEditor5Field(
        blank=True, verbose_name=_("رسالتنا بالعربية"), config_name="default"
    )

    vision = CKEditor5Field(
        blank=True, verbose_name=_("رؤيتنا - Vision"), config_name="default"
    )
    vision_ar = CKEditor5Field(
        blank=True, verbose_name=_("رؤيتنا بالعربية"), config_name="default"
    )

    values = CKEditor5Field(
        blank=True, verbose_name=_("قيمنا - Values"), config_name="default"
    )
    values_ar = CKEditor5Field(
        blank=True, verbose_name=_("قيمنا بالعربية"), config_name="default"
    )

    featured_image = models.ImageField(
        upload_to="about/", blank=True, null=True, verbose_name=_("صورة مميزة")
    )

    class Meta:
        verbose_name = _("صفحة من نحن")
        verbose_name_plural = _("صفحة من نحن")

    def __str__(self):
        return "About Page"


class ContactPage(SingletonModel):
    """Contact page content and settings"""

    title = models.CharField(
        max_length=200, default="Contact Us", verbose_name=_("العنوان - Title")
    )
    title_ar = models.CharField(
        max_length=200, default="اتصل بنا", verbose_name=_("العنوان بالعربية")
    )

    description = CKEditor5Field(
        blank=True, verbose_name=_("الوصف - Description"), config_name="default"
    )
    description_ar = CKEditor5Field(
        blank=True, verbose_name=_("الوصف بالعربية"), config_name="default"
    )

    # Contact form settings
    enable_contact_form = models.BooleanField(
        default=True, verbose_name=_("تفعيل نموذج التواصل")
    )

    notification_email = models.EmailField(
        blank=True,
        verbose_name=_("البريد الإلكتروني لاستقبال الرسائل"),
        help_text=_("البريد الذي سيتم إرسال رسائل التواصل إليه"),
    )

    # Display settings for contact info cards
    show_phone = models.BooleanField(
        default=True,
        verbose_name=_("إظهار بطاقة الهاتف"),
        help_text=_("إظهار أو إخفاء بطاقة معلومات الهاتف"),
    )

    show_address = models.BooleanField(
        default=True,
        verbose_name=_("إظهار بطاقة العنوان"),
        help_text=_("إظهار أو إخفاء بطاقة معلومات العنوان"),
    )

    show_office_hours = models.BooleanField(
        default=True,
        verbose_name=_("إظهار بطاقة ساعات العمل"),
        help_text=_("إظهار أو إخفاء بطاقة ساعات العمل"),
    )

    show_map = models.BooleanField(
        default=True,
        verbose_name=_("إظهار الخريطة"),
        help_text=_("إظهار أو إخفاء قسم الخريطة"),
    )

    # Office hours
    office_hours = CKEditor5Field(
        blank=True, verbose_name=_("ساعات العمل - Office Hours"), config_name="default"
    )
    office_hours_ar = CKEditor5Field(
        blank=True, verbose_name=_("ساعات العمل بالعربية"), config_name="default"
    )

    # Map
    map_embed_code = CKEditor5Field(
        blank=True,
        verbose_name=_("كود الخريطة - Map Embed Code"),
        help_text=_("كود HTML من Google Maps"),
        config_name="default",
    )

    class Meta:
        verbose_name = _("صفحة اتصل بنا")
        verbose_name_plural = _("صفحة اتصل بنا")

    def __str__(self):
        return "Contact Page"


class HomePage(SingletonModel):
    """Home page hero section and content"""

    # Hero Section
    hero_title = models.CharField(
        max_length=200,
        default="Welcome to Idrissimart",
        verbose_name=_("عنوان البطل - Hero Title"),
    )
    hero_title_ar = models.CharField(
        max_length=200,
        default="مرحباً بك في إدريسي مارت",
        verbose_name=_("عنوان البطل بالعربية"),
    )

    hero_subtitle = CKEditor5Field(
        blank=True, verbose_name=_("العنوان الفرعي - Subtitle"), config_name="default"
    )
    hero_subtitle_ar = CKEditor5Field(
        blank=True, verbose_name=_("العنوان الفرعي بالعربية"), config_name="default"
    )

    hero_image = models.ImageField(
        upload_to="homepage/hero/",
        blank=True,
        null=True,
        verbose_name=_("صورة البطل - Hero Image"),
    )

    hero_button_text = models.CharField(
        max_length=100, default="Get Started", verbose_name=_("نص الزر - Button Text")
    )
    hero_button_text_ar = models.CharField(
        max_length=100, default="ابدأ الآن", verbose_name=_("نص الزر بالعربية")
    )

    hero_button_url = models.CharField(
        max_length=200, default="/ads/", verbose_name=_("رابط الزر - Button URL")
    )

    # Modal/Announcement
    show_modal = models.BooleanField(
        default=False,
        verbose_name=_("إظهار نافذة الإعلان"),
        help_text=_("عرض نافذة منبثقة عند زيارة الصفحة الرئيسية"),
    )

    modal_title = models.CharField(
        max_length=200, blank=True, verbose_name=_("عنوان الإعلان - Modal Title")
    )
    modal_title_ar = models.CharField(
        max_length=200, blank=True, verbose_name=_("عنوان الإعلان بالعربية")
    )

    modal_content = CKEditor5Field(
        blank=True,
        verbose_name=_("محتوى الإعلان - Modal Content"),
        config_name="default",
    )
    modal_content_ar = CKEditor5Field(
        blank=True, verbose_name=_("محتوى الإعلان بالعربية"), config_name="default"
    )

    modal_image = models.ImageField(
        upload_to="homepage/modal/",
        blank=True,
        null=True,
        verbose_name=_("صورة الإعلان"),
    )

    modal_button_text = models.CharField(
        max_length=100, blank=True, verbose_name=_("نص زر الإعلان")
    )
    modal_button_text_ar = models.CharField(
        max_length=100, blank=True, verbose_name=_("نص زر الإعلان بالعربية")
    )

    modal_button_url = models.CharField(
        max_length=200, blank=True, verbose_name=_("رابط زر الإعلان")
    )

    # Featured sections
    show_featured_categories = models.BooleanField(
        default=True, verbose_name=_("عرض الأقسام المميزة")
    )

    show_featured_ads = models.BooleanField(
        default=True, verbose_name=_("عرض الإعلانات المميزة")
    )

    class Meta:
        verbose_name = _("محتوى الصفحة الرئيسية")
        verbose_name_plural = _("محتوى الصفحة الرئيسية")

    def __str__(self):
        return "Home Page Content"


class TermsPage(SingletonModel):
    """Terms and Conditions page content"""

    title = models.CharField(
        max_length=200,
        default="Terms and Conditions",
        verbose_name=_("العنوان - Title"),
    )
    title_ar = models.CharField(
        max_length=200, default="الشروط والأحكام", verbose_name=_("العنوان بالعربية")
    )

    content = CKEditor5Field(
        blank=True, verbose_name=_("المحتوى - Content"), config_name="default"
    )
    content_ar = CKEditor5Field(
        blank=True, verbose_name=_("المحتوى بالعربية"), config_name="default"
    )

    last_updated = models.DateField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _("صفحة الشروط والأحكام")
        verbose_name_plural = _("صفحة الشروط والأحكام")

    def __str__(self):
        return "Terms Page"


class PrivacyPage(SingletonModel):
    """Privacy Policy page content"""

    title = models.CharField(
        max_length=200, default="Privacy Policy", verbose_name=_("العنوان - Title")
    )
    title_ar = models.CharField(
        max_length=200, default="سياسة الخصوصية", verbose_name=_("العنوان بالعربية")
    )

    content = CKEditor5Field(
        blank=True, verbose_name=_("المحتوى - Content"), config_name="default"
    )
    content_ar = CKEditor5Field(
        blank=True, verbose_name=_("المحتوى بالعربية"), config_name="default"
    )

    last_updated = models.DateField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _("صفحة سياسة الخصوصية")
        verbose_name_plural = _("صفحة سياسة الخصوصية")

    def __str__(self):
        return "Privacy Page"
