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
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="blog_likes", blank=True
    )
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("content:blog_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # If slugify returns empty string (e.g., Arabic-only titles), use ID
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
