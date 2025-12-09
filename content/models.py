# models.py
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field

# Import site configuration models
from .site_config import (
    SiteConfiguration,
    AboutPage,
    ContactPage,
    HomePage,
    TermsPage,
    PrivacyPage,
)


class Country(models.Model):
    """Model for storing country information"""

    name = models.CharField(max_length=100, verbose_name=_("اسم الدولة"))
    name_en = models.CharField(
        max_length=100, verbose_name=_("Country Name"), blank=True
    )
    code = models.CharField(max_length=3, unique=True, verbose_name=_("كود الدولة"))
    flag_emoji = models.CharField(
        max_length=10, blank=True, verbose_name=_("علم الدولة")
    )
    phone_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("كود الهاتف")
    )
    currency = models.CharField(max_length=10, blank=True, verbose_name=_("العملة"))
    cities = models.JSONField(default=list, blank=True, verbose_name=_("المدن"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    order = models.IntegerField(default=0, verbose_name=_("الترتيب"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("دولة")
        verbose_name_plural = _("الدول")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.flag_emoji} {self.name}"

    @classmethod
    def get_default_countries(cls):
        """Returns list of default countries for initial data"""
        return [
            {
                "name": "السعودية",
                "name_en": "Saudi Arabia",
                "code": "SA",
                "flag_emoji": "🇸🇦",
                "phone_code": "+966",
                "currency": "SAR",
                "order": 1,
            },
            {
                "name": "الإمارات",
                "name_en": "UAE",
                "code": "AE",
                "flag_emoji": "🇦🇪",
                "phone_code": "+971",
                "currency": "AED",
                "order": 2,
            },
            {
                "name": "مصر",
                "name_en": "Egypt",
                "code": "EG",
                "flag_emoji": "🇪🇬",
                "phone_code": "+20",
                "currency": "EGP",
                "order": 3,
            },
            {
                "name": "الكويت",
                "name_en": "Kuwait",
                "code": "KW",
                "flag_emoji": "🇰🇼",
                "phone_code": "+965",
                "currency": "KWD",
                "order": 4,
            },
            {
                "name": "قطر",
                "name_en": "Qatar",
                "code": "QA",
                "flag_emoji": "🇶🇦",
                "phone_code": "+974",
                "currency": "QAR",
                "order": 5,
            },
            {
                "name": "البحرين",
                "name_en": "Bahrain",
                "code": "BH",
                "flag_emoji": "🇧🇭",
                "phone_code": "+973",
                "currency": "BHD",
                "order": 6,
            },
            {
                "name": "عُمان",
                "name_en": "Oman",
                "code": "OM",
                "flag_emoji": "🇴🇲",
                "phone_code": "+968",
                "currency": "OMR",
                "order": 7,
            },
            {
                "name": "الأردن",
                "name_en": "Jordan",
                "code": "JO",
                "flag_emoji": "🇯🇴",
                "phone_code": "+962",
                "currency": "JOD",
                "order": 8,
            },
        ]


class BlogCategory(models.Model):
    """Blog Category Model"""

    name = models.CharField(max_length=100, verbose_name=_("الاسم"))
    name_en = models.CharField(
        max_length=100, blank=True, verbose_name=_("الاسم بالإنجليزية")
    )
    slug = models.SlugField(
        max_length=100, unique=True, blank=True, verbose_name=_("الرابط")
    )
    description = models.TextField(blank=True, verbose_name=_("الوصف"))
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="fas fa-folder",
        verbose_name=_("أيقونة"),
        help_text=_("أيقونة FontAwesome مثل: fas fa-book"),
    )
    color = models.CharField(
        max_length=7,
        default="#6b4c7a",
        verbose_name=_("اللون"),
        help_text=_("كود اللون بصيغة HEX"),
    )
    order = models.IntegerField(default=0, verbose_name=_("الترتيب"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("فئة المدونة")
        verbose_name_plural = _("فئات المدونات")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(self.name, allow_unicode=True)
            if not self.slug:
                self.slug = (
                    slugify(self.name_en) if self.name_en else f"category-{self.pk}"
                )
        super().save(*args, **kwargs)

    def get_blogs_count(self):
        """Get count of published blogs in this category"""
        return self.blogs.filter(is_published=True).count()


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts"
    )
    content = CKEditor5Field(config_name="admin")
    image = models.ImageField(upload_to="blogs/", blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(
        default=0, verbose_name=_("عدد المشاهدات")
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="blog_likes", blank=True
    )
    tags = TaggableManager(blank=True)
    category = models.ForeignKey(
        "BlogCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blogs",
        verbose_name=_("الفئة"),
    )

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("content:blog_detail", kwargs={"slug": self.slug})

    def increment_views(self):
        """Increment the views count"""
        self.views_count += 1
        self.save(update_fields=["views_count"])

    def get_likes_count(self):
        """Get the number of likes"""
        return self.likes.count()

    def get_safe_content(self):
        """Return sanitized content with scripts and dangerous tags removed"""
        from bs4 import BeautifulSoup

        # Parse the HTML content
        soup = BeautifulSoup(self.content, "html.parser")

        # Remove all script tags
        for script in soup.find_all("script"):
            script.decompose()

        # Remove all style tags (optional, keep if you want inline styles)
        for style in soup.find_all("style"):
            style.decompose()

        # Remove potentially dangerous tags
        dangerous_tags = ["iframe", "object", "embed", "applet", "link"]
        for tag in dangerous_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove on* event attributes (onclick, onload, etc.)
        for tag in soup.find_all(True):
            attrs_to_remove = [attr for attr in tag.attrs if attr.startswith("on")]
            for attr in attrs_to_remove:
                del tag[attr]

        # Return cleaned HTML
        return str(soup)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            # Try to create slug with Unicode support (for Arabic titles)
            self.slug = slugify(self.title, allow_unicode=True)

            # If slugify returns empty string, use UUID
            if not self.slug:
                # For new objects without ID yet, use a temporary slug
                if not self.pk:
                    import uuid

                    self.slug = f"blog-{str(uuid.uuid4())[:8]}"
                else:
                    self.slug = f"blog-{self.pk}"

        # Ensure slug is never empty
        if not self.slug or self.slug.strip() == "":
            if self.pk:
                self.slug = f"blog-{self.pk}"
            else:
                import uuid

                self.slug = f"blog-{str(uuid.uuid4())[:8]}"

        super().save(*args, **kwargs)

        # If slug was temporary (UUID-based), update it with the actual ID
        if self.slug.startswith("blog-") and not self.slug.startswith("blog-temp-"):
            parts = self.slug.split("-")
            if len(parts) == 2 and len(parts[1]) == 8 and not parts[1].isdigit():
                # It's a UUID, replace with ID
                new_slug = f"blog-{self.pk}"
                # Ensure uniqueness
                counter = 1
                while Blog.objects.filter(slug=new_slug).exclude(pk=self.pk).exists():
                    new_slug = f"blog-{self.pk}-{counter}"
                    counter += 1
                Blog.objects.filter(pk=self.pk).update(slug=new_slug)
                self.slug = new_slug


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    body = CKEditor5Field(config_name="default")
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)  # To allow for moderation
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment by {self.author} on {self.blog}"


class HomeSlider(models.Model):
    """Model for homepage slider/carousel"""

    title = models.CharField(max_length=200, verbose_name=_("العنوان - Title"))
    title_ar = models.CharField(
        max_length=200, blank=True, verbose_name=_("العنوان بالعربية")
    )

    subtitle = models.TextField(blank=True, verbose_name=_("العنوان الفرعي - Subtitle"))
    subtitle_ar = models.TextField(
        blank=True, verbose_name=_("العنوان الفرعي بالعربية")
    )

    description = CKEditor5Field(
        blank=True,
        verbose_name=_("الوصف - Description"),
        config_name="default",
    )
    description_ar = CKEditor5Field(
        blank=True, verbose_name=_("الوصف بالعربية"), config_name="default"
    )

    image = models.ImageField(
        upload_to="homepage/slider/",
        verbose_name=_("الصورة - Image"),
        help_text=_("الحجم الموصى به: 1920x800 بكسل"),
    )

    button_text = models.CharField(
        max_length=100, blank=True, verbose_name=_("نص الزر - Button Text")
    )
    button_text_ar = models.CharField(
        max_length=100, blank=True, verbose_name=_("نص الزر بالعربية")
    )

    button_url = models.CharField(
        max_length=500, blank=True, verbose_name=_("رابط الزر - Button URL")
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="home_sliders",
        verbose_name=_("الدولة - Country"),
        help_text=_("اختر الدولة التي سيظهر فيها هذا السلايدر"),
        null=True,
        blank=True,
    )

    background_color = models.CharField(
        max_length=20,
        default="#4B315E",
        verbose_name=_("لون الخلفية"),
        help_text=_("كود اللون hex مثل: #4B315E"),
    )

    text_color = models.CharField(
        max_length=20,
        default="#FFFFFF",
        verbose_name=_("لون النص"),
        help_text=_("كود اللون hex مثل: #FFFFFF"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("نشط - Active"))

    order = models.IntegerField(
        default=0,
        verbose_name=_("الترتيب - Order"),
        help_text=_("يتم عرض الشرائح حسب الترتيب التصاعدي"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("شريحة الصفحة الرئيسية")
        verbose_name_plural = _("شرائح الصفحة الرئيسية")
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title_ar or self.title

    def get_title(self, language="ar"):
        """Get title based on language"""
        if language == "ar":
            return self.title_ar or self.title
        return self.title

    def get_subtitle(self, language="ar"):
        """Get subtitle based on language"""
        if language == "ar":
            return self.subtitle_ar or self.subtitle
        return self.subtitle

    def get_description(self, language="ar"):
        """Get description based on language"""
        if language == "ar":
            return self.description_ar or self.description
        return self.description

    def get_button_text(self, language="ar"):
        """Get button text based on language"""
        if language == "ar":
            return self.button_text_ar or self.button_text
        return self.button_text
