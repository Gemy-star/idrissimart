from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
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
        from django.utils import timezone

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

        from django.utils import timezone

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
    slug = models.SlugField(unique=True)
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
