import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager for creating different types of users
    """

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The Username must be set")
        if not email:
            raise ValueError("The Email must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create a regular user"""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("profile_type", "default")
        extra_fields.setdefault("rank", "visitor")
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create a superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("verification_status", "verified")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)

    def create_service_provider(self, username, email, password, **extra_fields):
        """
        Create a service provider user
        خدمي - Service Provider (Technician, Engineer, Company)
        """
        extra_fields["profile_type"] = "service"
        extra_fields.setdefault("rank", "technical")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_merchant(
        self,
        username,
        email,
        password,
        company_name=None,
        **extra_fields,
    ):
        """
        Create a merchant user
        تاجر - Merchant (Company selling products)
        """
        extra_fields["profile_type"] = "merchant"
        extra_fields.setdefault("rank", "company")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if company_name:
            extra_fields["company_name"] = company_name

        return self._create_user(username, email, password, **extra_fields)

    def create_educational(self, username, email, password, **extra_fields):
        """
        Create an educational institution user
        تعليمي - Educational (Lecturer or training company)
        """
        extra_fields["profile_type"] = "educational"
        extra_fields.setdefault("rank", "lecturer")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def verified_users(self):
        """Get all verified users"""
        return self.filter(verification_status="verified")

    def premium_users(self):
        """Get all premium users with active subscriptions"""
        return self.filter(
            is_premium=True,
            subscription_end__gte=timezone.now().date(),
        )

    def by_profile_type(self, profile_type):
        """Get users by profile type"""
        return self.filter(profile_type=profile_type)

    def service_providers(self):
        """Get all service providers"""
        return self.filter(profile_type="service")

    def merchants(self):
        """Get all merchants"""
        return self.filter(profile_type="merchant")

    def educators(self):
        """Get all educational users"""
        return self.filter(profile_type="educational")


class User(AbstractUser):
    """
    Extended user model with comprehensive profile types and permissions
    Based on the platform's user classification system
    """

    class ProfileType(models.TextChoices):
        DEFAULT = "default", _("افتراضي - Default")
        SERVICE = "service", _("خدمي - Service Provider")
        MERCHANT = "merchant", _("تاجر - Merchant")
        EDUCATIONAL = "educational", _("تعليمي - Educational")

    class Rank(models.TextChoices):
        VISITOR = "visitor", _("زائر - Visitor")
        TECHNICAL = "technical", _("فني - Technical")
        ENGINEER = "engineer", _("مهندس - Engineer")
        COMPANY = "company", _("شركة - Company")
        LECTURER = "lecturer", _("محاضر - Lecturer")
        OTHER = "other", _("أخرى - Other")

    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "unverified", _("غير موثق - Unverified")
        PENDING = "pending", _("قيد المراجعة - Pending Review")
        VERIFIED = "verified", _("موثق - Verified")
        REJECTED = "rejected", _("مرفوض - Rejected")

    # Basic Profile Information
    profile_type = models.CharField(
        max_length=20,
        choices=ProfileType.choices,
        default=ProfileType.DEFAULT,
        verbose_name=_("نوع الحساب - Profile Type"),
    )
    rank = models.CharField(
        max_length=20,
        choices=Rank.choices,
        default=Rank.VISITOR,
        verbose_name=_("الرتبة - Rank"),
    )

    # Contact Information
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("الهاتف - Phone"),
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("الجوال - Mobile"),
    )
    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("واتساب - WhatsApp"),
    )

    # Verification System
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
        verbose_name=_("حالة التوثيق - Verification Status"),
    )
    verification_document = models.FileField(
        upload_to="verifications/",
        blank=True,
        null=True,
        verbose_name=_("وثيقة التحقق - Verification Document"),
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التوثيق"),
    )

    # Company/Organization Information
    company_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("اسم الشركة - Company Name"),
    )
    company_name_ar = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("اسم الشركة بالعربية"),
    )
    tax_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("الرقم الضريبي - Tax Number"),
    )
    commercial_register = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("السجل التجاري - Commercial Register"),
    )

    # Profile Details
    bio = models.TextField(
        blank=True,
        verbose_name=_("نبذة تعريفية - Bio"),
    )
    bio_ar = models.TextField(
        blank=True,
        verbose_name=_("نبذة تعريفية بالعربية"),
    )
    profile_image = models.ImageField(
        upload_to="profiles/avatars/",
        blank=True,
        null=True,
        verbose_name=_("صورة الملف الشخصي"),
    )
    cover_image = models.ImageField(
        upload_to="profiles/covers/",
        blank=True,
        null=True,
        verbose_name=_("صورة الغلاف - Cover Image"),
    )

    # Location Information
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("الدولة - Country"),
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("المدينة - City"),
    )
    address = models.TextField(
        blank=True,
        verbose_name=_("العنوان - Address"),
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("الرمز البريدي"),
    )

    # Professional Information (for Service Providers)
    specialization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("التخصص - Specialization"),
    )
    years_of_experience = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("سنوات الخبرة - Years of Experience"),
    )
    certifications = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("الشهادات - Certifications"),
    )
    portfolio = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("معرض الأعمال - Portfolio"),
    )

    # Social Media Links
    website = models.URLField(
        blank=True,
        verbose_name=_("الموقع الإلكتروني - Website"),
    )
    facebook = models.URLField(blank=True, verbose_name=_("فيسبوك"))
    twitter = models.URLField(blank=True, verbose_name=_("تويتر"))
    instagram = models.URLField(blank=True, verbose_name=_("انستغرام"))
    linkedin = models.URLField(blank=True, verbose_name=_("لينكدإن"))

    # Subscription & Premium Features
    is_premium = models.BooleanField(
        default=False,
        verbose_name=_("عضوية مميزة - Premium Membership"),
    )
    subscription_start = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("بداية الاشتراك"),
    )
    subscription_end = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("نهاية الاشتراك"),
    )
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ("monthly", _("شهري - Monthly")),
            ("yearly", _("سنوي - Yearly")),
        ],
        blank=True,
        verbose_name=_("نوع الاشتراك"),
    )

    # Platform Statistics
    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي المبيعات"),
    )
    total_purchases = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("إجمالي المشتريات"),
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name=_("التقييم - Rating"),
    )
    total_reviews = models.IntegerField(
        default=0,
        verbose_name=_("عدد التقييمات"),
    )

    # Account Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط - Active"),
    )
    is_suspended = models.BooleanField(
        default=False,
        verbose_name=_("معلق - Suspended"),
    )
    suspension_reason = models.TextField(
        blank=True,
        verbose_name=_("سبب التعليق"),
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث"),
    )
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all "
            "permissions granted to each of their groups."
        ),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    # Custom manager
    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = [
            # Classified Ads Permissions
            (
                "can_post_classified_ads",
                "يمكنه نشر الإعلانات المبوبة - Can post classified ads",
            ),
            (
                "can_feature_classified_ads",
                "يمكنه تمييز الإعلانات - Can feature classified ads",
            ),
            # Marketplace Permissions
            (
                "can_sell_products",
                "يمكنه بيع المنتجات - Can sell products",
            ),
            (
                "can_manage_store",
                "يمكنه إدارة المتجر - Can manage store",
            ),
            (
                "can_view_sales_reports",
                "يمكنه عرض تقارير المبيعات - Can view sales reports",
            ),
            # Service Permissions
            (
                "can_offer_services",
                "يمكنه تقديم الخدمات - Can offer services",
            ),
            (
                "can_bid_on_services",
                "يمكنه تقديم عروض على طلبات الخدمات - Can bid on service requests",
            ),
            (
                "can_request_services",
                "يمكنه طلب الخدمات - Can request services",
            ),
            # Training Course Permissions
            (
                "can_create_courses",
                "يمكنه إنشاء الدورات التدريبية - Can create training courses",
            ),
            (
                "can_manage_courses",
                "يمكنه إدارة الدورات - Can manage courses",
            ),
            (
                "can_enroll_courses",
                "يمكنه التسجيل في الدورات - Can enroll in courses",
            ),
            # Job Permissions
            (
                "can_post_jobs",
                "يمكنه نشر الوظائف - Can post jobs",
            ),
            (
                "can_apply_jobs",
                "يمكنه التقديم على الوظائف - Can apply for jobs",
            ),
            # Review & Rating Permissions
            (
                "can_review_products",
                "يمكنه تقييم المنتجات - Can review products",
            ),
            (
                "can_review_services",
                "يمكنه تقييم الخدمات - Can review services",
            ),
            (
                "can_review_courses",
                "يمكنه تقييم الدورات - Can review courses",
            ),
            (
                "can_review_users",
                "يمكنه تقييم المستخدمين - Can review users",
            ),
            # Premium Features
            (
                "can_access_premium_features",
                "يمكنه الوصول للمزايا المميزة - Can access premium features",
            ),
            (
                "can_boost_listings",
                "يمكنه تعزيز الإعلانات - Can boost listings",
            ),
        ]

    def __str__(self):
        return self.username

    # Permission Check Methods
    def can_post_classified_ads(self):
        """
        Default and Merchant users can post classified ads
        """
        return self.profile_type in [
            self.ProfileType.DEFAULT,
            self.ProfileType.MERCHANT,
        ]

    def can_sell_products(self):
        """
        Only Merchant users can sell products in the marketplace
        """
        return self.profile_type == self.ProfileType.MERCHANT

    def can_offer_services(self):
        """
        Service providers can offer services
        """
        return self.profile_type == self.ProfileType.SERVICE

    def can_bid_on_service_requests(self):
        """
        Service providers can bid on service requests
        """
        return (
            self.profile_type == self.ProfileType.SERVICE
            and self.verification_status == self.VerificationStatus.VERIFIED
        )

    def can_create_courses(self):
        """
        Educational users can create training courses
        """
        return self.profile_type == self.ProfileType.EDUCATIONAL

    def can_post_jobs(self):
        """
        Verified companies and merchants can post job listings
        """
        return (
            self.verification_status == self.VerificationStatus.VERIFIED
            and self.rank
            in [
                self.Rank.COMPANY,
                self.Rank.OTHER,
            ]
        )

    def can_leave_reviews(self):
        """
        All verified users can leave reviews
        """
        return self.verification_status == self.VerificationStatus.VERIFIED

    def has_premium_access(self):
        """
        Check if user has active premium subscription
        """
        if not self.is_premium or not self.subscription_end:
            return False

        return self.subscription_end >= timezone.now().date()

    def get_profile_completeness(self):
        """
        Calculate profile completion percentage
        """
        fields_to_check = [
            "email",
            "phone",
            "bio",
            "profile_image",
            "city",
            "country",
        ]

        if self.profile_type == self.ProfileType.SERVICE:
            fields_to_check.extend(["specialization", "years_of_experience"])
        elif self.profile_type == self.ProfileType.MERCHANT:
            fields_to_check.extend(["company_name", "tax_number"])
        elif self.profile_type == self.ProfileType.EDUCATIONAL:
            fields_to_check.extend(["company_name", "certifications"])

        filled_fields = sum(
            1 for field in fields_to_check if getattr(self, field, None)
        )
        return int((filled_fields / len(fields_to_check)) * 100)

    def get_display_name(self):
        """
        Get the appropriate display name based on profile type
        """
        if self.profile_type in [
            self.ProfileType.MERCHANT,
            self.ProfileType.EDUCATIONAL,
        ]:
            return self.company_name or self.username
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def can_perform_action(self, action):
        """
        Centralized permission checking
        """
        permission_map = {
            "post_classified_ad": self.can_post_classified_ads(),
            "sell_product": self.can_sell_products(),
            "offer_service": self.can_offer_services(),
            "bid_service": self.can_bid_on_service_requests(),
            "create_course": self.can_create_courses(),
            "post_job": self.can_post_jobs(),
            "leave_review": self.can_leave_reviews(),
        }
        return permission_map.get(action, False)


class UserPermissionLog(models.Model):
    """
    Log of permission changes and actions
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="permission_logs",
    )
    action = models.CharField(
        max_length=100,
        verbose_name=_("الإجراء - Action"),
    )
    description = models.TextField(verbose_name=_("الوصف - Description"))
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_permission_logs"
        verbose_name = _("Permission Log")
        verbose_name_plural = _("Permission Logs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.action}"


class UserVerificationRequest(models.Model):
    """
    Handle user verification requests
    """

    class DocumentType(models.TextChoices):
        NATIONAL_ID = "national_id", _("بطاقة الهوية - National ID")
        PASSPORT = "passport", _("جواز السفر - Passport")
        COMMERCIAL_REGISTER = (
            "commercial_register",
            _("السجل التجاري - Commercial Register"),
        )
        TAX_CERTIFICATE = (
            "tax_certificate",
            _("شهادة ضريبية - Tax Certificate"),
        )
        PROFESSIONAL_LICENSE = (
            "professional_license",
            _("رخصة مهنية - Professional License"),
        )
        OTHER = "other", _("أخرى - Other")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_requests",
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
    )
    document_file = models.FileField(upload_to="verification_documents/")
    additional_documents = models.JSONField(default=list, blank=True)
    notes = models.TextField(
        blank=True,
        verbose_name=_("ملاحظات - Notes"),
    )

    status = models.CharField(
        max_length=20,
        choices=User.VerificationStatus.choices,
        default=User.VerificationStatus.PENDING,
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name=_("ملاحظات الإدارة"),
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_verifications",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_verification_requests"
        verbose_name = _("Verification Request")
        verbose_name_plural = _("Verification Requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Verification Request - {self.user.username}"


class UserSubscription(models.Model):
    """
    Handle user premium subscriptions
    """

    class SubscriptionPlan(models.TextChoices):
        MONTHLY = "monthly", _("شهري - Monthly")
        YEARLY = "yearly", _("سنوي - Yearly")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(
        default=True,
        verbose_name=_("التجديد التلقائي"),
    )
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_subscriptions"
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.plan}"


class Category(models.Model):
    """Categories for different sections of the platform"""

    class SectionType(models.TextChoices):
        JOB = "job", _("التوظيف - Jobs")
        COURSE = "course", _("الدورات التدريبية - Training Courses")
        SERVICE = "service", _("طلب خدمة - Services")
        PRODUCT = "product", _("متجر - Marketplace")
        CLASSIFIED = "classified", _("إعلانات مبوبة - Classified Ads")

    name = models.CharField(
        max_length=200,
        verbose_name=_("الاسم - Name"),
    )
    name_ar = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("الاسم بالعربية"),
    )
    slug = models.SlugField(unique=True, verbose_name=_("الرابط الإنجليزي"))
    slug_ar = models.SlugField(
        unique=True,
        blank=True,
        verbose_name=_("الرابط العربي - Arabic Slug"),
        help_text=_("رابط صديق للعربية يمكن استخدامه في عناوين URL"),
    )
    section_type = models.CharField(
        max_length=20,
        choices=SectionType.choices,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("الوصف - Description"),
    )
    icon = models.CharField(max_length=100, blank=True)
    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
    )

    # Country relationship for filtering
    country = models.ForeignKey(
        "content.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categories",
        verbose_name=_("الدولة - Country"),
        help_text=_("القسم متاح في هذه الدولة"),
    )

    # Multiple countries support
    countries = models.ManyToManyField(
        "content.Country",
        blank=True,
        related_name="available_categories",
        verbose_name=_("الدول المتاحة - Available Countries"),
        help_text=_("الدول التي يتوفر فيها هذا القسم"),
    )
    custom_field_schema = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("مخطط الحقول المخصصة"),
        help_text=_(
            'A list of custom field names applicable to this category, e.g., ["brand", "condition"]'
        ),
    )

    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["section_type", "order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save to ensure slug_ar is set if not provided"""
        if not self.slug_ar and self.name_ar:
            import re

            from django.utils.text import slugify

            # Clean Arabic text and create slug
            # Remove Arabic diacritics and normalize
            clean_text = re.sub(
                r"[\u064B-\u065F\u0670\u0640]", "", self.name_ar
            )  # Remove diacritics
            clean_text = re.sub(
                r"[^\u0600-\u06FF\u0750-\u077F\w\s-]", "", clean_text
            )  # Keep Arabic, alphanumeric, spaces, hyphens

            # Create slug allowing Unicode (Arabic) characters
            base_slug = slugify(clean_text.strip(), allow_unicode=True)

            if not base_slug:  # Fallback if slugify fails with Arabic
                # Simple replacement approach
                base_slug = clean_text.strip().replace(" ", "-").lower()
                base_slug = re.sub(r"[^\u0600-\u06FF\u0750-\u077F\w-]", "", base_slug)

            # Ensure uniqueness
            slug_ar = base_slug[:50]  # Limit length
            counter = 1
            while Category.objects.filter(slug_ar=slug_ar).exclude(pk=self.pk).exists():
                suffix = f"-{counter}"
                max_length = 50 - len(suffix)
                slug_ar = f"{base_slug[:max_length]}{suffix}"
                counter += 1

            self.slug_ar = slug_ar

        super().save(*args, **kwargs)

    def get_absolute_url(self, language="en"):
        """Get URL using appropriate slug based on language"""
        if language == "ar" and self.slug_ar:
            return f"/categories/{self.slug_ar}/"
        return f"/categories/{self.slug}/"

    def get_full_name(self):
        """Get full category name including parent"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def get_all_subcategories(self):
        """Get all subcategories recursively"""
        subcats = list(self.subcategories.filter(is_active=True))
        for subcat in list(subcats):
            subcats.extend(subcat.get_all_subcategories())
        return subcats

    def is_subcategory(self):
        """Check if this is a subcategory"""
        return self.parent is not None

    def get_root_category(self):
        """Get the root (top-level) category"""
        if self.parent:
            return self.parent.get_root_category()
        return self

    @classmethod
    def get_by_country(cls, country_code):
        """Get categories filtered by country"""
        from content.models import Country

        try:
            country = Country.objects.get(code=country_code, is_active=True)
            return cls.objects.filter(
                models.Q(country=country)
                | models.Q(countries=country)
                | models.Q(country__isnull=True, countries__isnull=True)
            ).distinct()
        except Country.DoesNotExist:
            return cls.objects.none()

    @classmethod
    def get_by_section_and_country(cls, section_type, country_code):
        """Get categories filtered by section type and country"""
        return cls.get_by_country(country_code).filter(
            section_type=section_type, is_active=True
        )

    @classmethod
    def get_root_categories(cls, section_type=None, country_code=None):
        """Get only root (parent) categories"""
        queryset = cls.objects.filter(parent__isnull=True, is_active=True)

        if section_type:
            queryset = queryset.filter(section_type=section_type)

        if country_code:
            from content.models import Country

            try:
                country = Country.objects.get(code=country_code, is_active=True)
                queryset = queryset.filter(
                    models.Q(country=country)
                    | models.Q(countries=country)
                    | models.Q(country__isnull=True, countries__isnull=True)
                ).distinct()
            except Country.DoesNotExist:
                pass

        return queryset


class ContactInfo(models.Model):
    """Contact information for the platform"""

    phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم الهاتف - Phone"),
        help_text=_("رقم الهاتف الرئيسي للمنصة"),
    )
    email = models.EmailField(
        verbose_name=_("البريد الإلكتروني - Email"),
        help_text=_("البريد الإلكتروني الرئيسي للمنصة"),
    )
    address = models.TextField(
        verbose_name=_("العنوان - Address"), help_text=_("عنوان المكتب الرئيسي")
    )
    working_hours = models.CharField(
        max_length=100,
        default="السبت - الخميس، 9:00 ص - 5:00 م",
        verbose_name=_("ساعات العمل - Working Hours"),
    )
    whatsapp = models.CharField(
        max_length=20, blank=True, verbose_name=_("واتساب - WhatsApp")
    )
    facebook = models.URLField(blank=True, verbose_name=_("فيسبوك - Facebook"))
    twitter = models.URLField(blank=True, verbose_name=_("تويتر - Twitter"))
    instagram = models.URLField(blank=True, verbose_name=_("انستغرام - Instagram"))
    linkedin = models.URLField(blank=True, verbose_name=_("لينكدإن - LinkedIn"))
    map_embed_url = models.TextField(
        blank=True,
        verbose_name=_("رابط الخريطة - Map Embed URL"),
        help_text=_("رابط الخريطة من Google Maps"),
    )
    google_maps_link = models.URLField(
        blank=True,
        verbose_name=_("رابط Google Maps - Google Maps Link"),
        help_text=_("رابط مباشر إلى الموقع على Google Maps"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط - Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contact_info"
        verbose_name = _("Contact Information")
        verbose_name_plural = _("Contact Information")

    def __str__(self):
        return f"Contact Info - {self.email}"

    @classmethod
    def get_active_info(cls):
        """Get the active contact information"""
        return cls.objects.filter(is_active=True).first()


class ContactMessage(models.Model):
    """Contact messages from users"""

    class Status(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار - Pending")
        READ = "read", _("مقروءة - Read")
        REPLIED = "replied", _("تم الرد - Replied")
        RESOLVED = "resolved", _("محلولة - Resolved")

    name = models.CharField(max_length=100, verbose_name=_("الاسم - Name"))
    email = models.EmailField(verbose_name=_("البريد الإلكتروني - Email"))
    phone = models.CharField(
        max_length=20, blank=True, verbose_name=_("رقم الهاتف - Phone")
    )
    subject = models.CharField(max_length=200, verbose_name=_("الموضوع - Subject"))
    message = models.TextField(verbose_name=_("الرسالة - Message"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("الحالة - Status"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages",
        verbose_name=_("المستخدم - User"),
    )
    admin_notes = models.TextField(
        blank=True, verbose_name=_("ملاحظات الإدارة - Admin Notes")
    )
    replied_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ الرد - Reply Date")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإرسال - Created At")
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contact_messages"
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def mark_as_read(self):
        """Mark message as read"""
        if self.status == self.Status.PENDING:
            self.status = self.Status.READ
            self.save()

    def mark_as_replied(self):
        """Mark message as replied"""
        from django.utils import timezone

        self.status = self.Status.REPLIED
        self.replied_at = timezone.now()
        self.save()


class AboutPage(models.Model):
    """About page content management"""

    title = models.CharField(
        max_length=200, default="إدريسي مارت", verbose_name=_("العنوان - Title")
    )
    tagline = models.CharField(
        max_length=200, default="تميّزك… ملموس", verbose_name=_("الشعار - Tagline")
    )
    subtitle = models.CharField(
        max_length=300,
        default="منصتك للتجارة الإلكترونية المتكاملة",
        verbose_name=_("العنوان الفرعي - Subtitle"),
    )
    who_we_are_title = models.CharField(
        max_length=100, default="من نحن؟", verbose_name=_("عنوان من نحن")
    )
    who_we_are_content = models.TextField(
        verbose_name=_("محتوى من نحن - Who We Are Content")
    )
    vision_title = models.CharField(
        max_length=100, default="رؤيتنا", verbose_name=_("عنوان الرؤية")
    )
    vision_content = models.TextField(verbose_name=_("محتوى الرؤية - Vision Content"))
    mission_title = models.CharField(
        max_length=100, default="رسالتنا", verbose_name=_("عنوان الرسالة")
    )
    mission_content = models.TextField(
        verbose_name=_("محتوى الرسالة - Mission Content")
    )
    values_title = models.CharField(
        max_length=100, default="قيمنا", verbose_name=_("عنوان القيم")
    )
    # Statistics
    vendors_count = models.IntegerField(
        default=500, verbose_name=_("عدد البائعين - Vendors Count")
    )
    products_count = models.IntegerField(
        default=5000, verbose_name=_("عدد المنتجات - Products Count")
    )
    customers_count = models.IntegerField(
        default=10000, verbose_name=_("عدد العملاء - Customers Count")
    )
    categories_count = models.IntegerField(
        default=20, verbose_name=_("عدد الفئات - Categories Count")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط - Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "about_page"
        verbose_name = _("About Page")
        verbose_name_plural = _("About Pages")

    def __str__(self):
        return f"About Page - {self.title}"

    @classmethod
    def get_active_content(cls):
        """Get the active about page content"""
        return cls.objects.filter(is_active=True).first()


class CompanyValue(models.Model):
    """Company values for about page"""

    title = models.CharField(max_length=100, verbose_name=_("العنوان - Title"))
    description = models.TextField(verbose_name=_("الوصف - Description"))
    icon_class = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("فئة الأيقونة - Icon Class"),
        help_text=_("مثال: fas fa-check"),
    )
    svg_icon = models.TextField(
        blank=True,
        verbose_name=_("أيقونة SVG - SVG Icon"),
        help_text=_("كود SVG للأيقونة"),
    )
    order = models.IntegerField(default=0, verbose_name=_("الترتيب - Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط - Active"))
    about_page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("صفحة من نحن"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "company_values"
        verbose_name = _("Company Value")
        verbose_name_plural = _("Company Values")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class ClassifiedAd(models.Model):
    """Model for classified ads"""

    class AdStatus(models.TextChoices):
        DRAFT = "draft", _("مسودة - Draft")
        PENDING = "pending", _("قيد المراجعة - Pending")
        ACTIVE = "active", _("نشط - Active")
        EXPIRED = "expired", _("منتهي - Expired")
        SOLD = "sold", _("مباع - Sold")
        REJECTED = "rejected", _("مرفوض - Rejected")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="classified_ads"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="classified_ads"
    )
    title = models.CharField(max_length=255, verbose_name=_("عنوان الإعلان"))
    description = models.TextField(verbose_name=_("وصف الإعلان"))
    price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("السعر")
    )
    is_negotiable = models.BooleanField(
        default=False, verbose_name=_("السعر قابل للتفاوض")
    )
    custom_fields = models.JSONField(
        default=dict, blank=True, verbose_name=_("حقول مخصصة")
    )

    # Location
    country = models.ForeignKey(
        "content.Country", on_delete=models.SET_NULL, null=True, blank=True
    )
    city = models.CharField(max_length=100, verbose_name=_("المدينة"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("العنوان"))

    # Features
    video_url = models.URLField(blank=True, null=True, verbose_name=_("رابط فيديو"))
    video_file = models.FileField(
        upload_to="ads/videos/", blank=True, null=True, verbose_name=_("ملف فيديو")
    )
    is_cart_enabled = models.BooleanField(
        default=False, verbose_name=_("تفعيل سلة الحجز")
    )
    is_delivery_available = models.BooleanField(
        default=False, verbose_name=_("توفير التوصيل")
    )

    # Status and Timestamps
    status = models.CharField(
        max_length=20, choices=AdStatus.choices, default=AdStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ الانتهاء")
    )
    views_count = models.PositiveIntegerField(
        default=0, verbose_name=_("عدد المشاهدات")
    )

    class Meta:
        db_table = "classified_ads"
        verbose_name = _("Classified Ad")
        verbose_name_plural = _("Classified Ads")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("main:ad_detail", kwargs={"pk": self.pk})


class AdImage(models.Model):
    """Model for multiple ad images"""

    ad = models.ForeignKey(
        ClassifiedAd, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="ads/images/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "ad_images"
        verbose_name = _("Ad Image")
        verbose_name_plural = _("Ad Images")
        ordering = ["order"]


class AdFeature(models.Model):
    """Model for paid ad features"""

    class FeatureType(models.TextChoices):
        PINNED = "pinned", _("تثبيت - Pinned")
        TOP_SEARCH = "top_search", _("أعلى نتائج البحث - Top Search")
        FEATURED_SECTION = "featured_section", _("قسم مميز - Featured Section")
        VIDEO = "video", _("إضافة فيديو - Video")

    ad = models.ForeignKey(
        ClassifiedAd, on_delete=models.CASCADE, related_name="features"
    )
    feature_type = models.CharField(max_length=20, choices=FeatureType.choices)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "ad_features"
        verbose_name = _("Ad Feature")
        verbose_name_plural = _("Ad Features")

    def is_feature_active(self):
        return self.is_active and self.end_date >= timezone.now()


class AdPackage(models.Model):
    """Model for ad posting packages"""

    name = models.CharField(max_length=100, verbose_name=_("اسم الباقة"))
    description = models.TextField(blank=True, verbose_name=_("وصف الباقة"))
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("السعر")
    )
    ad_count = models.PositiveIntegerField(verbose_name=_("عدد الإعلانات"))
    duration_days = models.PositiveIntegerField(
        verbose_name=_("صلاحية الباقة (بالأيام)")
    )
    is_default = models.BooleanField(
        default=False, verbose_name=_("باقة افتراضية للمستخدمين الجدد")
    )
    is_active = models.BooleanField(default=True)

    # Can be restricted to a specific category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packages",
        help_text=_("إذا تم تحديده، ستكون هذه الباقة مخصصة لهذا القسم فقط"),
    )

    class Meta:
        db_table = "ad_packages"
        verbose_name = _("Ad Package")
        verbose_name_plural = _("Ad Packages")

    def __str__(self):
        return self.name


class UserPackage(models.Model):
    """Model to track user's purchased packages"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ad_packages")
    package = models.ForeignKey(AdPackage, on_delete=models.PROTECT)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    ads_remaining = models.PositiveIntegerField()

    class Meta:
        db_table = "user_packages"
        verbose_name = _("User Package")
        verbose_name_plural = _("User Packages")
        ordering = ["-purchase_date"]

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"

    def save(self, *args, **kwargs):
        if not self.pk:  # On creation
            self.ads_remaining = self.package.ad_count
            self.expiry_date = timezone.now() + timezone.timedelta(
                days=self.package.duration_days
            )
        super().save(*args, **kwargs)

    def is_active(self):
        """Check if the package is still active and has ads remaining."""
        return self.expiry_date >= timezone.now() and self.ads_remaining > 0

    def use_ad(self):
        """Decrement the ad count for the package."""
        if self.is_active():
            self.ads_remaining -= 1
            self.save(update_fields=["ads_remaining"])
            return True
        return False


class SavedSearch(models.Model):
    """Model to store user's saved search queries."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="saved_searches"
    )
    name = models.CharField(max_length=100, verbose_name=_("اسم البحث"))
    query_params = models.TextField(verbose_name=_("معلمات البحث"))
    email_notifications = models.BooleanField(
        default=True, verbose_name=_("تفعيل إشعارات البريد الإلكتروني")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_notified_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("آخر إشعار أرسل في")
    )
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )

    class Meta:
        db_table = "saved_searches"
        verbose_name = _("Saved Search")
        verbose_name_plural = _("Saved Searches")
        ordering = ["-created_at"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return f"{reverse('main:ad_list')}?{self.query_params}"
