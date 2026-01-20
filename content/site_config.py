"""
Site Configuration Models using django-solo
Singleton models for managing site-wide settings
Only includes settings NOT covered by django-constance
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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

    # Site Logo
    logo = models.ImageField(
        upload_to="site/logos/",
        blank=True,
        null=True,
        verbose_name=_("شعار الموقع - Site Logo"),
        help_text=_("شعار الموقع الذي يظهر في الإعلانات بدون صور (الشعار الافتراضي)"),
    )

    logo_light = models.ImageField(
        upload_to="site/logos/",
        blank=True,
        null=True,
        verbose_name=_("شعار الموقع - الوضع الفاتح"),
        help_text=_("شعار الموقع الذي يظهر في الوضع الفاتح (Light Mode). إذا تُرك فارغاً، سيُستخدم الشعار الافتراضي"),
    )

    logo_dark = models.ImageField(
        upload_to="site/logos/",
        blank=True,
        null=True,
        verbose_name=_("شعار الموقع - الوضع الداكن"),
        help_text=_("شعار الموقع الذي يظهر في الوضع الداكن (Dark Mode). إذا تُرك فارغاً، سيُستخدم الشعار الافتراضي"),
    )

    logo_mini = models.ImageField(
        upload_to="site/logos/",
        blank=True,
        null=True,
        verbose_name=_("شعار مصغر - Loader"),
        help_text=_("شعار مصغر يظهر في صفحات التحميل (Loader). إذا تُرك فارغاً، سيُستخدم الشعار الافتراضي"),
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

    require_verification_for_free_package = models.BooleanField(
        default=False,
        verbose_name=_("التحقق مطلوب للباقة المجانية"),
        help_text=_(
            "إذا كان مفعلاً، يتم منح الباقة المجانية فقط بعد التحقق من الإيميل ورقم الموبايل"
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

    # Payment Settings - Online & Offline
    allow_online_payment = models.BooleanField(
        default=True,
        verbose_name=_("السماح بالدفع الإلكتروني"),
        help_text=_("تفعيل/تعطيل طرق الدفع الإلكتروني (PayMob, etc.)"),
    )

    allow_offline_payment = models.BooleanField(
        default=True,
        verbose_name=_("السماح بالدفع اليدوي"),
        help_text=_("تفعيل/تعطيل الدفع اليدوي عبر InstaPay أو المحفظة"),
    )

    # InstaPay Settings
    instapay_qr_code = models.ImageField(
        upload_to="payment/instapay/",
        blank=True,
        null=True,
        verbose_name=_("رمز QR لـ InstaPay"),
        help_text=_("قم برفع صورة رمز QR الخاص بحساب InstaPay للدفع اليدوي"),
    )

    instapay_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("رقم هاتف InstaPay"),
        help_text=_("رقم الهاتف المسجل في InstaPay"),
    )

    # Wallet Payment Link
    wallet_payment_link = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_("رابط المحفظة الإلكترونية"),
        help_text=_(
            "رابط للدفع عبر المحفظة الإلكترونية (Vodafone Cash, Orange Money, etc.)"
        ),
    )

    wallet_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("رقم المحفظة الإلكترونية"),
        help_text=_("رقم الهاتف المسجل في المحفظة"),
    )

    # Offline Payment Instructions
    offline_payment_instructions = models.TextField(
        blank=True,
        verbose_name=_("تعليمات الدفع اليدوي"),
        help_text=_("تعليمات للعملاء حول كيفية إتمام الدفع اليدوي"),
    )

    offline_payment_instructions_ar = models.TextField(
        blank=True,
        verbose_name=_("تعليمات الدفع اليدوي بالعربية"),
        default="1. قم بمسح رمز QR أو استخدم رابط المحفظة\n2. أرسل المبلغ المطلوب\n3. احتفظ بإيصال التحويل\n4. سيتم تفعيل الخدمة خلال 24 ساعة",
    )

    # Ad Posting & Feature Pricing
    ad_base_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("رسوم نشر الإعلان الأساسية"),
        help_text=_("رسوم نشر إعلان عادي (0 = مجاني)"),
    )

    featured_ad_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50,
        verbose_name=_("سعر الإعلان المميز"),
        help_text=_("رسوم جعل الإعلان مميزاً (Highlighted)"),
    )

    urgent_ad_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=30,
        verbose_name=_("سعر الإعلان العاجل"),
        help_text=_("رسوم إضافة علامة عاجل للإعلان"),
    )

    pinned_ad_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100,
        verbose_name=_("سعر تثبيت الإعلان"),
        help_text=_("رسوم تثبيت الإعلان في أعلى القائمة"),
    )

    # Cart Service Fee Settings
    cart_service_fee_type = models.CharField(
        max_length=20,
        choices=[("fixed", _("رسوم ثابتة")), ("percentage", _("نسبة مئوية"))],
        default="percentage",
        verbose_name=_("نوع رسوم خدمة السلة"),
        help_text=_("هل رسوم الخدمة ثابتة أم نسبة من سعر المنتج؟"),
    )

    cart_service_fixed_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("رسوم خدمة السلة الثابتة"),
        help_text=_("المبلغ الثابت الذي يتم خصمه من الناشر عند البيع"),
    )

    cart_service_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5,
        verbose_name=_("نسبة رسوم خدمة السلة"),
        help_text=_("النسبة المئوية من سعر المنتج التي يتم خصمها من الناشر"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    cart_service_instructions = models.TextField(
        blank=True,
        verbose_name=_("تعليمات خدمة السلة للناشر"),
        default="عند تفعيل السلة، سيتم خصم رسوم خدمة من ثمن المنتج عند البيع. يجب أن يكون السعر شاملاً لهذه الرسوم ورسوم التوصيل.",
        help_text=_("التعليمات التي تظهر للناشر عند تفعيل السلة"),
    )

    # Ads Retention Settings (Soft Delete)
    deleted_ads_retention_days = models.PositiveIntegerField(
        default=90,
        verbose_name=_("مدة الاحتفاظ بالإعلانات المحذوفة (يوم)"),
        help_text=_(
            "عدد الأيام قبل الحذف النهائي للإعلانات المحذوفة من قاعدة البيانات. القيمة الافتراضية: 90 يوم (3 شهور)"
        ),
        validators=[MinValueValidator(1), MaxValueValidator(730)],
    )

    expired_ads_retention_days = models.PositiveIntegerField(
        default=365,
        verbose_name=_("مدة الاحتفاظ بالإعلانات المنتهية (يوم)"),
        help_text=_(
            "عدد الأيام قبل الحذف النهائي للإعلانات المنتهية من قاعدة البيانات. القيمة الافتراضية: 365 يوم (سنة)"
        ),
        validators=[MinValueValidator(1), MaxValueValidator(1825)],
    )

    show_deleted_ads_to_publisher = models.BooleanField(
        default=True,
        verbose_name=_("إظهار الإعلانات المحذوفة للناشر"),
        help_text=_("السماح للناشر برؤية إعلاناته المحذوفة قبل الحذف النهائي"),
    )

    show_expired_ads_to_publisher = models.BooleanField(
        default=True,
        verbose_name=_("إظهار الإعلانات المنتهية للناشر"),
        help_text=_("السماح للناشر برؤية إعلاناته المنتهية"),
    )

    # Buyer Safety Notes
    buyer_safety_notes_enabled = models.BooleanField(
        default=True,
        verbose_name=_("تفعيل نصائح الأمان للمشترين"),
        help_text=_("إظهار/إخفاء نصائح الأمان في صفحة تفاصيل الإعلان"),
    )

    buyer_safety_notes = CKEditor5Field(
        blank=True,
        verbose_name=_("نصائح الأمان للمشترين"),
        config_name="default",
        default="""
        <ul>
            <li>قابل البائع في مكان عام وآمن</li>
            <li>تحقق من المنتج جيداً قبل الشراء</li>
            <li>لا تحول أي أموال قبل استلام المنتج</li>
            <li>احذر من العروض المشبوهة أو الأسعار المبالغ فيها</li>
            <li>استخدم طرق الدفع الآمنة</li>
        </ul>
        """,
        help_text=_("النصائح الإرشادية التي تظهر للمشتري بجوار الإعلان"),
    )

    buyer_safety_notes_ar = CKEditor5Field(
        blank=True,
        verbose_name=_("نصائح الأمان للمشترين بالعربية"),
        config_name="default",
        default="""
        <ul>
            <li>قابل البائع في مكان عام وآمن</li>
            <li>تحقق من المنتج جيداً قبل الشراء</li>
            <li>لا تحول أي أموال قبل استلام المنتج</li>
            <li>احذر من العروض المشبوهة أو الأسعار المبالغ فيها</li>
            <li>استخدم طرق الدفع الآمنة</li>
        </ul>
        """,
    )

    buyer_safety_notes_title = models.CharField(
        max_length=200,
        default="نصائح للأمان",
        verbose_name=_("عنوان نصائح الأمان"),
    )

    buyer_safety_notes_title_ar = models.CharField(
        max_length=200,
        default="نصائح للأمان",
        verbose_name=_("عنوان نصائح الأمان بالعربية"),
    )

    class Meta:
        verbose_name = _("إعدادات الموقع")
        verbose_name_plural = _("إعدادات الموقع")

    def __str__(self):
        return "Site Configuration"

    def get_logo_for_theme(self, theme='light'):
        """
        Get appropriate logo based on theme
        Args:
            theme: 'light' or 'dark'
        Returns:
            ImageField or None
        """
        if theme == 'light':
            return self.logo_light if self.logo_light else self.logo
        elif theme == 'dark':
            return self.logo_dark if self.logo_dark else self.logo
        return self.logo

    def get_loader_logo(self):
        """
        Get logo for loader/spinner
        Returns mini logo if available, otherwise default logo
        """
        return self.logo_mini if self.logo_mini else self.logo

    def get_logo_url(self, theme='light'):
        """
        Get logo URL based on theme
        Args:
            theme: 'light' or 'dark'
        Returns:
            str: URL of the logo or empty string
        """
        logo = self.get_logo_for_theme(theme)
        return logo.url if logo else ""

    def get_loader_logo_url(self):
        """
        Get loader logo URL
        Returns:
            str: URL of the loader logo or empty string
        """
        logo = self.get_loader_logo()
        return logo.url if logo else ""


class AboutPage(SingletonModel):
    """About Us page content"""

    title = models.CharField(
        max_length=200, default="About Us", verbose_name=_("العنوان - Title")
    )
    title_ar = models.CharField(
        max_length=200, default="من نحن", verbose_name=_("العنوان بالعربية")
    )

    # Hero Section - First Heading (Tagline)
    tagline = models.CharField(
        max_length=200,
        default="منصة تجمع سوق واحد",
        verbose_name=_("الشعار - Tagline"),
        help_text=_("العنوان الأول الذي يظهر أسفل العنوان الرئيسي")
    )
    tagline_ar = models.CharField(
        max_length=200,
        default="منصة تجمع سوق واحد",
        verbose_name=_("الشعار بالعربية")
    )

    subtitle = models.TextField(
        blank=True,
        default="متخصص يستفيد منه المتخصصون والجمهور العام الذي يحتاج إلى أي من خدمات هذا السوق",
        verbose_name=_("العنوان الفرعي - Subtitle")
    )
    subtitle_ar = models.TextField(
        blank=True,
        default="متخصص يستفيد منه المتخصصون والجمهور العام الذي يحتاج إلى أي من خدمات هذا السوق",
        verbose_name=_("العنوان الفرعي بالعربية")
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

    # What We Offer Section
    what_we_offer_title = models.CharField(
        max_length=200,
        default="ماذا نقدم؟",
        verbose_name=_("عنوان قسم ماذا نقدم - What We Offer Title")
    )
    what_we_offer_title_ar = models.CharField(
        max_length=200,
        default="ماذا نقدم؟",
        verbose_name=_("عنوان قسم ماذا نقدم بالعربية")
    )

    featured_image = models.ImageField(
        upload_to="about/", blank=True, null=True, verbose_name=_("صورة مميزة")
    )

    class Meta:
        verbose_name = _("صفحة من نحن")
        verbose_name_plural = _("صفحة من نحن")

    def __str__(self):
        return "About Page"


class AboutPageSection(models.Model):
    """Dynamic sections for 'What We Offer' on About page"""

    about_page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("صفحة من نحن")
    )

    tab_title = models.CharField(
        max_length=100,
        verbose_name=_("عنوان التبويب - Tab Title"),
        help_text=_("العنوان الذي يظهر في زر التبويب (مثل: للأفراد، للشركات)")
    )
    tab_title_ar = models.CharField(
        max_length=100,
        verbose_name=_("عنوان التبويب بالعربية")
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("الأيقونة - Icon"),
        help_text=_("أيقونة إيموجي أو رمز (مثل: 📢، 🛒، 🔧)")
    )

    content = CKEditor5Field(
        blank=True,
        verbose_name=_("المحتوى - Content"),
        config_name="default",
        help_text=_("محتوى القسم بتنسيق HTML")
    )
    content_ar = CKEditor5Field(
        blank=True,
        verbose_name=_("المحتوى بالعربية"),
        config_name="default"
    )

    order = models.IntegerField(
        default=0,
        verbose_name=_("الترتيب - Order"),
        help_text=_("ترتيب ظهور التبويب")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط - Active")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("قسم من نحن - ماذا نقدم")
        verbose_name_plural = _("أقسام من نحن - ماذا نقدم")
        ordering = ["order", "id"]

    def __str__(self):
        return self.tab_title_ar or self.tab_title


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

    # Why Choose Us Section
    show_why_choose_us = models.BooleanField(
        default=True,
        verbose_name=_("عرض قسم لماذا نحن - Show Why Choose Us")
    )

    why_choose_us_title = models.CharField(
        max_length=200,
        default="Why Choose Us?",
        verbose_name=_("عنوان قسم لماذا نحن - Why Choose Us Title"),
    )
    why_choose_us_title_ar = models.CharField(
        max_length=200,
        default="لماذا إدريسي مارت للمساحة؟",
        verbose_name=_("عنوان قسم لماذا نحن بالعربية"),
    )

    why_choose_us_subtitle = models.TextField(
        blank=True,
        verbose_name=_("عنوان فرعي - Subtitle"),
        help_text=_("نص توضيحي قصير أسفل العنوان (اختياري)"),
    )
    why_choose_us_subtitle_ar = models.TextField(
        blank=True,
        verbose_name=_("عنوان فرعي بالعربية"),
    )

    # Featured sections
    show_featured_categories = models.BooleanField(
        default=True, verbose_name=_("عرض الأقسام المميزة")
    )

    show_featured_ads = models.BooleanField(
        default=True, verbose_name=_("عرض الإعلانات المميزة")
    )

    # Statistics Section
    show_statistics = models.BooleanField(
        default=True,
        verbose_name=_("عرض قسم الإحصائيات - Show Statistics")
    )

    # Statistic 1
    stat1_value = models.IntegerField(
        default=15,
        verbose_name=_("الإحصائية 1 - القيمة"),
        help_text=_("القيمة العددية (مثل: 15)")
    )
    stat1_title = models.CharField(
        max_length=200,
        default="Active Advertisers",
        verbose_name=_("الإحصائية 1 - العنوان"),
    )
    stat1_title_ar = models.CharField(
        max_length=200,
        default="معلنين نشطين",
        verbose_name=_("الإحصائية 1 - العنوان بالعربية"),
    )
    stat1_subtitle = models.CharField(
        max_length=300,
        blank=True,
        default="Offices, Engineers & Companies",
        verbose_name=_("الإحصائية 1 - العنوان الفرعي"),
    )
    stat1_subtitle_ar = models.CharField(
        max_length=300,
        blank=True,
        default="مكاتب، مهندسين، وشركات",
        verbose_name=_("الإحصائية 1 - العنوان الفرعي بالعربية"),
    )
    stat1_icon = models.CharField(
        max_length=100,
        default="fas fa-user-friends",
        verbose_name=_("الإحصائية 1 - الأيقونة"),
        help_text=_("أيقونة FontAwesome (مثل: fas fa-user-friends)")
    )

    # Statistic 2
    stat2_value = models.IntegerField(
        default=150,
        verbose_name=_("الإحصائية 2 - القيمة"),
        help_text=_("القيمة العددية (مثل: 150)")
    )
    stat2_title = models.CharField(
        max_length=200,
        default="Published Ads",
        verbose_name=_("الإحصائية 2 - العنوان"),
    )
    stat2_title_ar = models.CharField(
        max_length=200,
        default="إعلانات منشورة",
        verbose_name=_("الإحصائية 2 - العنوان بالعربية"),
    )
    stat2_subtitle = models.CharField(
        max_length=300,
        blank=True,
        default="Services, Equipment & Job Opportunities",
        verbose_name=_("الإحصائية 2 - العنوان الفرعي"),
    )
    stat2_subtitle_ar = models.CharField(
        max_length=300,
        blank=True,
        default="خدمات، معدات، وفرص عمل",
        verbose_name=_("الإحصائية 2 - العنوان الفرعي بالعربية"),
    )
    stat2_icon = models.CharField(
        max_length=100,
        default="fas fa-bullhorn",
        verbose_name=_("الإحصائية 2 - الأيقونة"),
        help_text=_("أيقونة FontAwesome (مثل: fas fa-bullhorn)")
    )

    # Statistic 3
    stat3_value = models.IntegerField(
        default=500,
        verbose_name=_("الإحصائية 3 - القيمة"),
        help_text=_("القيمة العددية (مثل: 500)")
    )
    stat3_title = models.CharField(
        max_length=200,
        default="Monthly Visits",
        verbose_name=_("الإحصائية 3 - العنوان"),
    )
    stat3_title_ar = models.CharField(
        max_length=200,
        default="زيارات شهرية",
        verbose_name=_("الإحصائية 3 - العنوان بالعربية"),
    )
    stat3_subtitle = models.CharField(
        max_length=300,
        blank=True,
        default="Interested in Surveying Field",
        verbose_name=_("الإحصائية 3 - العنوان الفرعي"),
    )
    stat3_subtitle_ar = models.CharField(
        max_length=300,
        blank=True,
        default="مهتمون بالمجال المساحي",
        verbose_name=_("الإحصائية 3 - العنوان الفرعي بالعربية"),
    )
    stat3_icon = models.CharField(
        max_length=100,
        default="fas fa-chart-line",
        verbose_name=_("الإحصائية 3 - الأيقونة"),
        help_text=_("أيقونة FontAwesome (مثل: fas fa-chart-line)")
    )

    # Statistic 4
    stat4_value = models.IntegerField(
        default=250,
        verbose_name=_("الإحصائية 4 - القيمة"),
        help_text=_("القيمة العددية (مثل: 250)")
    )
    stat4_title = models.CharField(
        max_length=200,
        default="Supported Specializations",
        verbose_name=_("الإحصائية 4 - العنوان"),
    )
    stat4_title_ar = models.CharField(
        max_length=200,
        default="تخصصات مدعومة",
        verbose_name=_("الإحصائية 4 - العنوان بالعربية"),
    )
    stat4_subtitle = models.CharField(
        max_length=300,
        blank=True,
        default="Surveying - Engineering - GIS",
        verbose_name=_("الإحصائية 4 - العنوان الفرعي"),
    )
    stat4_subtitle_ar = models.CharField(
        max_length=300,
        blank=True,
        default="مساحة – هندسة – GIS",
        verbose_name=_("الإحصائية 4 - العنوان الفرعي بالعربية"),
    )
    stat4_icon = models.CharField(
        max_length=100,
        default="fas fa-th-large",
        verbose_name=_("الإحصائية 4 - الأيقونة"),
        help_text=_("أيقونة FontAwesome (مثل: fas fa-th-large)")
    )

    class Meta:
        verbose_name = _("محتوى الصفحة الرئيسية")
        verbose_name_plural = _("محتوى الصفحة الرئيسية")

    def __str__(self):
        return "Home Page Content"


class WhyChooseUsFeature(models.Model):
    """Features for Why Choose Us section on homepage"""

    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="why_choose_us_features",
        verbose_name=_("الصفحة الرئيسية - Home Page")
    )

    title = models.CharField(
        max_length=200,
        verbose_name=_("العنوان - Title"),
        help_text=_("عنوان الميزة (مثل: دقة عالية)")
    )
    title_ar = models.CharField(
        max_length=200,
        verbose_name=_("العنوان بالعربية")
    )

    description = models.TextField(
        verbose_name=_("الوصف - Description"),
        help_text=_("وصف الميزة")
    )
    description_ar = models.TextField(
        verbose_name=_("الوصف بالعربية")
    )

    icon = models.CharField(
        max_length=50,
        default="fas fa-check-circle",
        verbose_name=_("الأيقونة - Icon"),
        help_text=_("أيقونة FontAwesome (مثل: fas fa-check-circle, fas fa-star, fas fa-award)")
    )

    order = models.IntegerField(
        default=0,
        verbose_name=_("الترتيب - Order"),
        help_text=_("ترتيب ظهور الميزة")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط - Active")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("ميزة - لماذا نحن")
        verbose_name_plural = _("مميزات - لماذا نحن")
        ordering = ["order", "id"]

    def __str__(self):
        return self.title_ar or self.title


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
