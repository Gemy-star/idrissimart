import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from django_ckeditor_5.fields import CKEditor5Field


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
        """Create a standard user (default type, can upgrade via packages)"""
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


class User(AbstractUser):  # This model is correct, no changes needed here.
    """
    Extended user model with comprehensive profile types and permissions
    Based on the platform's user classification system
    """

    class ProfileType(models.TextChoices):
        DEFAULT = "default", _("قياسي - Standard")
        PUBLISHER = "publisher", _("ناشر - Publisher")

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

    # Mobile verification fields
    is_mobile_verified = models.BooleanField(
        default=False,
        verbose_name=_("الجوال موثق - Mobile Verified"),
    )
    mobile_verification_code = models.CharField(
        max_length=6,
        blank=True,
        verbose_name=_("رمز التحقق - Verification Code"),
    )
    mobile_verification_expires = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("انتهاء رمز التحقق - Code Expires"),
    )

    # Email verification fields
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_("البريد الإلكتروني موثق - Email Verified"),
    )
    email_verification_token = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("رمز التحقق من البريد - Email Verification Token"),
    )
    email_verification_expires = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("انتهاء رمز التحقق - Token Expires"),
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
        All users (Default and Publisher) can post classified ads
        """
        return True

    def can_sell_products(self):
        """
        Publishers can sell products in the marketplace
        """
        return self.profile_type == self.ProfileType.PUBLISHER

    def can_offer_services(self):
        """
        Publishers can offer services
        """
        return self.profile_type == self.ProfileType.PUBLISHER

    def can_bid_on_service_requests(self):
        """
        Verified publishers can bid on service requests
        """
        return (
            self.profile_type == self.ProfileType.PUBLISHER
            and self.verification_status == self.VerificationStatus.VERIFIED
        )

    def can_create_courses(self):
        """
        Publishers can create training courses
        """
        return self.profile_type == self.ProfileType.PUBLISHER

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

        if self.profile_type == self.ProfileType.PUBLISHER:
            fields_to_check.extend(["company_name", "specialization"])

        filled_fields = sum(
            1 for field in fields_to_check if getattr(self, field, None)
        )
        return int((filled_fields / len(fields_to_check)) * 100)

    def get_display_name(self):
        """
        Get the appropriate display name based on profile type
        """
        if self.profile_type == self.ProfileType.PUBLISHER and self.company_name:
            return self.company_name
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_verified(self):
        """
        Check if user is verified
        """
        return self.verification_status == self.VerificationStatus.VERIFIED

    @property
    def active_ads_count(self):
        """Returns the count of active classified ads for the user."""
        return self.classified_ads.filter(status=ClassifiedAd.AdStatus.ACTIVE).count()

    @property
    def is_company(self):
        """
        Check if user represents a company/organization
        """
        return self.rank == self.Rank.COMPANY or (
            self.profile_type == self.ProfileType.PUBLISHER and self.company_name
        )

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

    def upgrade_to_publisher(self):
        """
        Upgrade user from default to publisher via package purchase
        Allows users to publish more ads and access publisher features
        Publishers can create ads that are automatically activated without admin approval
        """
        if self.profile_type == self.ProfileType.DEFAULT:
            self.profile_type = self.ProfileType.PUBLISHER
            self.save(update_fields=["profile_type"])

            # Create notification about upgrade
            Notification.objects.create(
                user=self,
                title=_("تمت ترقية حسابك!"),
                message=_(
                    "تم ترقية حسابك إلى ناشر بنجاح. إعلاناتك الآن تُفعّل تلقائياً بدون موافقة الإدارة!"
                ),
                notification_type=Notification.NotificationType.GENERAL,
            )
            return True
        return False

    def can_upgrade_profile(self):
        """
        Check if user can upgrade their profile type
        Only default/standard users can upgrade via packages
        """
        return self.profile_type == self.ProfileType.DEFAULT


class UserPermissionLog(models.Model):  # This model is correct, no changes needed here.
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


class UserVerificationRequest(
    models.Model
):  # This model is correct, no changes needed here.
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


class UserSubscription(models.Model):  # This model is correct, no changes needed here.
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


class CategoryManager(TreeManager):
    def with_ad_counts(self):
        """
        Annotates each category with the total number of active ads in it and its descendants.
        """
        from django.db.models import Count, OuterRef, Subquery

        # Create a subquery that counts active ads for a given category subtree.
        # The subquery filters ClassifiedAd objects where the category's tree_id, lft, and rght
        # fall within the bounds of the outer category reference.
        ad_count_subquery = (
            ClassifiedAd.objects.filter(status=ClassifiedAd.AdStatus.ACTIVE)
            .filter(
                category__tree_id=OuterRef("tree_id"),
                category__lft__gte=OuterRef("lft"),
                category__rght__lte=OuterRef("rght"),
            )
            .values("pk")
            .annotate(c=Count("pk"))
            .values("c")
        )

        return self.get_queryset().annotate(ad_count=Subquery(ad_count_subquery))


class Category(MPTTModel):
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
    parent = TreeForeignKey(
        "self",  # Changed from models.ForeignKey to TreeForeignKey
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    description = CKEditor5Field(
        blank=True,
        verbose_name=_("الوصف - Description"),
        config_name="default",
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

    # Cart and Reservation Settings
    allow_cart = models.BooleanField(
        default=False,
        verbose_name=_("السماح بالسلة"),
        help_text=_("تفعيل نظام السلة لهذا القسم"),
    )
    default_reservation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        verbose_name=_("نسبة الحجز الافتراضية"),
        help_text=_("النسبة المئوية الافتراضية للحجز"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    min_reservation_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأدنى لمبلغ الحجز"),
    )
    max_reservation_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى لمبلغ الحجز"),
    )
    require_admin_approval = models.BooleanField(
        default=True,
        verbose_name=_("يتطلب موافقة الإدارة"),
        help_text=_("الإعلانات تتطلب مراجعة قبل النشر"),
    )

    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = CKEditor5Field(blank=True, config_name="default")
    meta_keywords = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add the custom manager
    objects = CategoryManager()

    class MPTTMeta:
        order_insertion_by = ["order", "name"]

    class Meta:
        db_table = "categories"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["section_type", "order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save to ensure slug_ar is set and add watermark to category images"""
        # Add watermark to category image if it's a new upload
        if self.image and not self.pk:
            from .utils import add_watermark_to_image

            watermarked = add_watermark_to_image(
                self.image, opacity=150, position="bottom-right", scale=0.10
            )

            if watermarked:
                self.image = watermarked

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


class ContactMessage(models.Model):  # This model is correct, no changes needed here.
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


class ClassifiedAdManager(models.Manager):
    """Custom manager for ClassifiedAd with country filtering support"""

    def get_queryset(self):
        """Return the base queryset"""
        return (
            super()
            .get_queryset()
            .select_related("user", "category", "country")
            .prefetch_related("images", "features")
        )

    def for_country(self, country_code):
        """Filter ads by country code"""
        if not country_code:
            return self.get_queryset()
        return self.get_queryset().filter(country__code=country_code)

    def active(self):
        """Get only active ads"""
        return self.get_queryset().filter(status=self.model.AdStatus.ACTIVE)

    def active_for_country(self, country_code):
        """Get active ads for a specific country"""
        return (
            self.active().filter(country__code=country_code)
            if country_code
            else self.active()
        )

    def featured_for_country(self, country_code):
        """Get featured/upgraded ads for a specific country"""
        from django.utils import timezone

        # Get ads with active upgrades (highlighted, urgent, or pinned)
        featured_ad_pks = (
            AdUpgradeHistory.objects.filter(
                end_date__gte=timezone.now(),
                is_active=True,
                ad__country__code=country_code if country_code else "EG",
            )
            .values_list("ad_id", flat=True)
            .distinct()
        )

        return (
            self.get_queryset()
            .filter(pk__in=featured_ad_pks, status=self.model.AdStatus.ACTIVE)
            .order_by("-is_pinned", "-is_urgent", "-is_highlighted", "-created_at")
        )

    def highlighted(self):
        """Get highlighted ads"""
        return self.get_queryset().filter(
            is_highlighted=True, status=self.model.AdStatus.ACTIVE
        )

    def urgent(self):
        """Get urgent ads"""
        return self.get_queryset().filter(
            is_urgent=True, status=self.model.AdStatus.ACTIVE
        )

    def pinned(self):
        """Get pinned ads"""
        return self.get_queryset().filter(
            is_pinned=True, status=self.model.AdStatus.ACTIVE
        )

    def pending_review(self):
        """Get ads pending admin review"""
        return (
            self.get_queryset()
            .filter(status=self.model.AdStatus.PENDING, require_review=True)
            .order_by("-created_at")
        )

    def draft_ads(self, user):
        """Get user's draft ads"""
        return (
            self.get_queryset()
            .filter(user=user, status=self.model.AdStatus.DRAFT)
            .order_by("-updated_at")
        )


class ClassifiedAd(models.Model):  # This model is correct, no changes needed here.
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
    slug = models.SlugField(
        max_length=300,
        unique=True,
        blank=True,
        verbose_name=_("الرابط الصديق لمحركات البحث"),
        help_text=_("يتم إنشاؤه تلقائياً من عنوان الإعلان"),
    )
    description = CKEditor5Field(verbose_name=_("وصف الإعلان"), config_name="default")
    price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("السعر")
    )
    features_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر الميزات الإضافية"),
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

    # Price Display Options
    hide_price = models.BooleanField(
        default=False,
        verbose_name=_("إخفاء السعر"),
        help_text=_("إخفاء السعر وإظهار زر 'الحصول على عرض سعر'"),
    )
    price_on_request = models.BooleanField(
        default=False,
        verbose_name=_("السعر عند الطلب"),
        help_text=_("إظهار 'السعر عند الطلب' بدلاً من السعر الفعلي"),
    )

    # Rating
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("التقييم"),
        help_text=_("تقييم الإعلان من 0 إلى 5"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    rating_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("عدد التقييمات"),
        help_text=_("عدد المستخدمين الذين قيموا هذا الإعلان"),
    )

    # Badge Features
    is_urgent = models.BooleanField(default=False, verbose_name=_("إعلان عاجل"))
    is_highlighted = models.BooleanField(default=False, verbose_name=_("إعلان مميز"))
    is_pinned = models.BooleanField(default=False, verbose_name=_("إعلان مثبت"))

    # Visibility and Access Control
    class VisibilityType(models.TextChoices):
        PUBLIC = "public", _("عام - متاح للجميع")
        MEMBERS_ONLY = "members_only", _("للأعضاء المسجلين فقط")
        VERIFIED_ONLY = "verified_only", _("للأعضاء الموثقين فقط")

    visibility_type = models.CharField(
        max_length=20,
        choices=VisibilityType.choices,
        default=VisibilityType.PUBLIC,
        verbose_name=_("نوع الظهور"),
        help_text=_("تحديد من يمكنه مشاهدة الإعلان"),
    )
    require_login_for_contact = models.BooleanField(
        default=False,
        verbose_name=_("تسجيل الدخول مطلوب للتواصل"),
        help_text=_("إذا كان نشطاً، يجب على الزوار تسجيل الدخول لرؤية معلومات الاتصال"),
    )

    # Cart and Reservation Settings
    allow_cart = models.BooleanField(
        default=False,
        verbose_name=_("السماح بالسلة"),
        help_text=_("تفعيل نظام السلة والحجز لهذا الإعلان"),
    )
    cart_enabled_by_admin = models.BooleanField(
        default=False,
        verbose_name=_("السلة مفعلة من الإدارة"),
        help_text=_("يتم تفعيلها بعد استلام المنتج"),
    )
    reservation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("نسبة الحجز"),
        help_text=_("نسبة مئوية من السعر الإجمالي للحجز"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    reservation_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("مبلغ الحجز"),
        help_text=_("المبلغ المطلوب للحجز"),
    )
    delivery_terms = CKEditor5Field(
        blank=True,
        verbose_name=_("شروط التوصيل والتحصيل"),
        help_text=_("شروط خدمة التوصيل والتحصيل"),
        config_name="default",
    )
    delivery_terms_en = CKEditor5Field(
        blank=True,
        verbose_name=_("شروط التوصيل والتحصيل (EN)"),
        config_name="default",
    )

    # Admin Control
    is_hidden = models.BooleanField(
        default=False,
        verbose_name=_("مخفي"),
        help_text=_("الإعلان مخفي من قبل الإدارة"),
    )
    require_review = models.BooleanField(
        default=True,
        verbose_name=_("يتطلب مراجعة"),
        help_text=_(
            "يتطلب موافقة الإدارة قبل النشر (الأعضاء الموثقين يتم نشرهم تلقائياً)"
        ),
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_ads",
        verbose_name=_("تمت المراجعة بواسطة"),
    )
    reviewed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ المراجعة")
    )
    admin_notes = CKEditor5Field(
        blank=True, verbose_name=_("ملاحظات الإدارة"), config_name="admin"
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

    # Custom manager
    objects = ClassifiedAdManager()

    class Meta:
        db_table = "classified_ads"
        verbose_name = _("Classified Ad")
        verbose_name_plural = _("Classified Ads")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_safe_description(self):
        """Return sanitized description with scripts and dangerous tags removed"""
        from bs4 import BeautifulSoup

        # Parse the HTML content
        soup = BeautifulSoup(self.description, "html.parser")

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
        is_new = not self.pk

        # Generate slug from title if not set
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            # Ensure slug is unique
            while ClassifiedAd.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)

        # Calculate reservation amount if percentage is set
        if self.reservation_percentage > 0 and self.price:
            calculated_amount = (self.price * self.reservation_percentage) / 100
            # Apply min/max limits from category settings if available
            if hasattr(self.category, "min_reservation_amount"):
                calculated_amount = max(
                    calculated_amount, self.category.min_reservation_amount or 0
                )
            if hasattr(self.category, "max_reservation_amount"):
                calculated_amount = min(
                    calculated_amount,
                    self.category.max_reservation_amount or calculated_amount,
                )
            self.reservation_amount = calculated_amount

        # Auto-activate ads for PUBLISHER users, require approval for DEFAULT users
        if is_new:  # New ad
            # Check if draft status is explicitly set
            if self.status == self.AdStatus.DRAFT:
                # Keep as draft, don't change anything
                pass
            elif self.user.profile_type == User.ProfileType.PUBLISHER:
                # Publishers get auto-activated ads
                self.status = self.AdStatus.ACTIVE
                self.reviewed_at = timezone.now()
                self.require_review = False
            elif self.user.profile_type == User.ProfileType.DEFAULT:
                # Default users require admin approval
                self.status = self.AdStatus.PENDING
                self.require_review = True

            # Staff/Superusers bypass approval
            if self.user.is_staff or self.user.is_superuser:
                self.status = self.AdStatus.ACTIVE
                self.reviewed_at = timezone.now()
                self.require_review = False

        super().save(*args, **kwargs)

    def calculate_reservation_amount(self):
        """Calculate the reservation amount based on percentage"""
        if self.reservation_percentage > 0 and self.price:
            return (self.price * self.reservation_percentage) / 100
        return self.reservation_amount

    def can_user_view(self, user):
        """Check if user can view this ad based on visibility settings"""
        if self.is_hidden:
            return False

        if self.visibility_type == self.VisibilityType.PUBLIC:
            return True
        elif self.visibility_type == self.VisibilityType.MEMBERS_ONLY:
            return user.is_authenticated
        elif self.visibility_type == self.VisibilityType.VERIFIED_ONLY:
            return (
                user.is_authenticated
                and user.verification_status == User.VerificationStatus.VERIFIED
            )

        return True

    def can_view_contact_info(self, user):
        """Check if user can view contact information"""
        if not self.require_login_for_contact:
            return True
        return user.is_authenticated

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("main:ad_detail", kwargs={"slug": self.slug})

    def get_custom_fields_for_card(self):
        """Get custom fields that should be displayed on the ad card"""
        if not self.custom_fields or not self.category:
            return []

        # Get all custom fields for this category that should show on card
        category_custom_fields = (
            CategoryCustomField.objects.filter(
                category=self.category, show_on_card=True, is_active=True
            )
            .select_related("custom_field")
            .order_by("order")
        )

        fields_to_display = []
        for cat_cf in category_custom_fields:
            field_key = cat_cf.custom_field.key
            if field_key in self.custom_fields:
                field_value = self.custom_fields[field_key]

                # Skip empty values
                if not field_value:
                    continue

                # For select/radio fields, get the option label
                if cat_cf.custom_field.field_type in ["select", "radio"]:
                    try:
                        option = CustomFieldOption.objects.get(
                            custom_field=cat_cf.custom_field, value=field_value
                        )
                        field_value = option.label
                    except CustomFieldOption.DoesNotExist:
                        pass

                # For checkbox fields
                elif cat_cf.custom_field.field_type == "checkbox":
                    field_value = _("نعم") if field_value else _("لا")

                fields_to_display.append(
                    {
                        "label": cat_cf.custom_field.label,
                        "value": field_value,
                        "icon": cat_cf.custom_field.icon or "fa-info-circle",
                    }
                )

        return fields_to_display

    def check_and_expire_upgrades(self):
        """Check and deactivate expired upgrades"""
        expired_upgrades = self.upgrade_history.filter(
            is_active=True, end_date__lt=timezone.now()
        )

        for upgrade in expired_upgrades:
            upgrade.deactivate()

        return expired_upgrades.count()

    def get_active_upgrades(self):
        """Get list of active upgrades"""
        return self.upgrade_history.filter(
            is_active=True, end_date__gte=timezone.now()
        ).order_by("-created_at")

    def has_upgrade(self, upgrade_type):
        """Check if ad has a specific active upgrade"""
        return self.upgrade_history.filter(
            upgrade_type=upgrade_type, is_active=True, end_date__gte=timezone.now()
        ).exists()

    def get_display_priority(self):
        """Calculate display priority for sorting (higher = more important)"""
        priority = 0

        # Pinned ads get highest priority
        if self.is_pinned:
            priority += 1000

        # Urgent ads get high priority
        if self.is_urgent:
            priority += 500

        # Highlighted ads get medium priority
        if self.is_highlighted:
            priority += 250

        # Publisher users get slight boost
        if self.user.profile_type == User.ProfileType.PUBLISHER:
            priority += 50

        # Verified users get slight boost
        if self.user.verification_status == User.VerificationStatus.VERIFIED:
            priority += 25

        return priority

    def can_be_edited(self, user):
        """Check if user can edit this ad"""
        # Owner can edit
        if self.user == user:
            return True

        # Staff/Superuser can edit
        if user.is_staff or user.is_superuser:
            return True

        return False

    def can_be_upgraded(self):
        """Check if ad can be upgraded"""
        # Only active or pending ads can be upgraded
        return self.status in [self.AdStatus.ACTIVE, self.AdStatus.PENDING]

    def approve(self, admin_user):
        """Approve pending ad"""
        if self.status == self.AdStatus.PENDING:
            self.status = self.AdStatus.ACTIVE
            self.reviewed_by = admin_user
            self.reviewed_at = timezone.now()
            self.require_review = False
            self.save()
            return True
        return False

    def reject(self, admin_user, reason=""):
        """Reject pending ad"""
        if self.status == self.AdStatus.PENDING:
            self.status = self.AdStatus.REJECTED
            self.reviewed_by = admin_user
            self.reviewed_at = timezone.now()
            if reason:
                self.admin_notes = reason
            self.save()
            return True
        return False


class AdUpgradeHistory(models.Model):
    """
    تتبع تاريخ ترقيات الإعلانات
    Track ad upgrade history for features like highlighted, urgent, pinned
    """

    class UpgradeType(models.TextChoices):
        HIGHLIGHTED = "highlighted", _("مميز - Highlighted")
        URGENT = "urgent", _("عاجل - Urgent")
        PINNED = "pinned", _("مثبت - Pinned")

    ad = models.ForeignKey(
        ClassifiedAd, on_delete=models.CASCADE, related_name="upgrade_history"
    )
    upgrade_type = models.CharField(
        max_length=20, choices=UpgradeType.choices, verbose_name=_("نوع الترقية")
    )
    price_paid = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("المبلغ المدفوع")
    )
    duration_days = models.IntegerField(verbose_name=_("المدة بالأيام"))
    start_date = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ البدء"))
    end_date = models.DateTimeField(verbose_name=_("تاريخ الانتهاء"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ad_upgrade_history"
        verbose_name = _("Ad Upgrade History")
        verbose_name_plural = _("Ad Upgrade Histories")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ad.title} - {self.get_upgrade_type_display()}"

    def save(self, *args, **kwargs):
        # Calculate end_date based on start_date and duration
        if not self.end_date:
            self.end_date = timezone.now() + timezone.timedelta(days=self.duration_days)

        # Update the ad's upgrade flags
        if self.is_active:
            if self.upgrade_type == self.UpgradeType.HIGHLIGHTED:
                self.ad.is_highlighted = True
            elif self.upgrade_type == self.UpgradeType.URGENT:
                self.ad.is_urgent = True
            elif self.upgrade_type == self.UpgradeType.PINNED:
                self.ad.is_pinned = True
            self.ad.save()

        super().save(*args, **kwargs)

    def deactivate(self):
        """Deactivate this upgrade and update the ad"""
        self.is_active = False

        # Remove the flag from ad if no other active upgrades exist
        if self.upgrade_type == self.UpgradeType.HIGHLIGHTED:
            if (
                not AdUpgradeHistory.objects.filter(
                    ad=self.ad,
                    upgrade_type=self.UpgradeType.HIGHLIGHTED,
                    is_active=True,
                    end_date__gt=timezone.now(),
                )
                .exclude(pk=self.pk)
                .exists()
            ):
                self.ad.is_highlighted = False

        elif self.upgrade_type == self.UpgradeType.URGENT:
            if (
                not AdUpgradeHistory.objects.filter(
                    ad=self.ad,
                    upgrade_type=self.UpgradeType.URGENT,
                    is_active=True,
                    end_date__gt=timezone.now(),
                )
                .exclude(pk=self.pk)
                .exists()
            ):
                self.ad.is_urgent = False

        elif self.upgrade_type == self.UpgradeType.PINNED:
            if (
                not AdUpgradeHistory.objects.filter(
                    ad=self.ad,
                    upgrade_type=self.UpgradeType.PINNED,
                    is_active=True,
                    end_date__gt=timezone.now(),
                )
                .exclude(pk=self.pk)
                .exists()
            ):
                self.ad.is_pinned = False

        self.ad.save()
        self.save()


class AdImage(models.Model):  # This model is correct, no changes needed here.
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

    def save(self, *args, **kwargs):
        """Add watermark to image before saving"""
        if self.image and not self.pk:  # Only for new uploads
            from .utils import add_watermark_to_image

            watermarked = add_watermark_to_image(
                self.image,
                opacity=180,  # Semi-transparent
                position="bottom-right",
                scale=0.12,  # 12% of image width
            )

            if watermarked:
                self.image = watermarked

        super().save(*args, **kwargs)


class AdReview(models.Model):
    """Model for ad reviews and ratings"""

    ad = models.ForeignKey(
        ClassifiedAd,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("الإعلان"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ad_reviews",
        verbose_name=_("المستخدم"),
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name=_("التقييم"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("تقييم من 1 إلى 5 نجوم"),
    )
    comment = models.TextField(
        verbose_name=_("التعليق"), blank=True, help_text=_("تعليق اختياري")
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name=_("معتمد"),
        help_text=_("يمكن للإدارة إخفاء التعليقات غير اللائقة"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        db_table = "ad_reviews"
        verbose_name = _("تقييم إعلان")
        verbose_name_plural = _("تقييمات الإعلانات")
        ordering = ["-created_at"]
        unique_together = ("ad", "user")  # One review per user per ad
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["ad", "is_approved"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.ad.title} ({self.rating}★)"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Update ad rating and count
        if is_new or "rating" in (kwargs.get("update_fields") or []):
            self.update_ad_rating()

    def update_ad_rating(self):
        """Update the ad's average rating and count"""
        from django.db.models import Avg, Count

        stats = self.ad.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg("rating"), count=Count("id")
        )

        self.ad.rating = stats["avg_rating"]
        self.ad.rating_count = stats["count"]
        self.ad.save(update_fields=["rating", "rating_count"])


class AdFeature(models.Model):  # This model is correct, no changes needed here.
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
    """
    نموذج باقات نشر الإعلانات
    Model for ad posting packages with enhanced pricing system
    """

    name = models.CharField(max_length=100, verbose_name=_("اسم الباقة"))
    name_en = models.CharField(
        max_length=100, blank=True, verbose_name=_("Package Name (English)")
    )
    description = models.TextField(blank=True, verbose_name=_("وصف الباقة"))
    description_en = models.TextField(
        blank=True, verbose_name=_("Description (English)")
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("السعر")
    )

    # Package limits - عدد الإعلانات غير مرتبطة بوقت
    ad_count = models.PositiveIntegerField(
        verbose_name=_("عدد الإعلانات"),
        help_text=_("عدد الإعلانات المسموحة في هذه الباقة (غير مرتبطة بوقت)"),
    )

    # مدة ظهور الإعلان
    ad_duration_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_("مدة ظهور الإعلان الواحد (بالأيام)"),
        help_text=_("كم يوم سيظل كل إعلان ظاهراً"),
    )

    # Package validity period
    duration_days = models.PositiveIntegerField(
        verbose_name=_("صلاحية الباقة (بالأيام)"), help_text=_("صلاحية الباقة للمستخدم")
    )

    # أسعار تمييز الإعلان
    feature_pinned_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر التثبيت"),
        help_text=_("سعر إضافي لتثبيت الإعلان"),
    )
    feature_urgent_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر العاجل"),
        help_text=_("سعر إضافي لجعل الإعلان عاجل"),
    )
    feature_highlighted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("سعر التمييز"),
        help_text=_("سعر إضافي لتمييز الإعلان"),
    )

    # Status flags - خطة نشطة او لا - موصي بها او لا
    is_default = models.BooleanField(
        default=False, verbose_name=_("باقة افتراضية للمستخدمين الجدد")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    is_recommended = models.BooleanField(
        default=False,
        verbose_name=_("موصى بها"),
        help_text=_("عرض شارة 'موصى بها' على هذه الباقة"),
    )
    is_popular = models.BooleanField(default=False, verbose_name=_("الأكثر شعبية"))

    # نص او مميزات الخطة
    features = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("مميزات الباقة"),
        help_text=_("قائمة بمميزات الباقة بصيغة JSON"),
    )

    # تحديد القسم الرئيسي والفرعى
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packages",
        verbose_name=_("القسم"),
        help_text=_("إذا تم تحديده، ستكون هذه الباقة مخصصة لهذا القسم فقط"),
    )

    # Display order
    display_order = models.PositiveIntegerField(
        default=0, verbose_name=_("ترتيب العرض")
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ad_packages"
        verbose_name = _("Ad Package")
        verbose_name_plural = _("Ad Packages")
        ordering = ["display_order", "-is_recommended", "price"]

    def __str__(self):
        category_name = f" - {self.category.name}" if self.category else ""
        return f"{self.name}{category_name}"

    def get_features_list(self):
        """Return features as a list"""
        if isinstance(self.features, list):
            return self.features
        return []


class Payment(models.Model):
    """Model to track payment transactions"""

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار - Pending")
        COMPLETED = "completed", _("مكتمل - Completed")
        FAILED = "failed", _("فاشل - Failed")
        CANCELLED = "cancelled", _("ملغي - Cancelled")
        REFUNDED = "refunded", _("مسترد - Refunded")

    class PaymentProvider(models.TextChoices):
        PAYPAL = "paypal", _("PayPal")
        PAYMOB = "paymob", _("Paymob")
        BANK_TRANSFER = "bank_transfer", _("تحويل بنكي - Bank Transfer")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(
        max_length=20,
        choices=PaymentProvider.choices,
        verbose_name=_("مزود الدفع - Payment Provider"),
    )
    provider_transaction_id = models.CharField(
        max_length=255, blank=True, verbose_name=_("معرف المعاملة - Transaction ID")
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("المبلغ - Amount")
    )
    currency = models.CharField(
        max_length=3, default="SAR", verbose_name=_("العملة - Currency")
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_("حالة الدفع - Payment Status"),
    )
    description = models.TextField(blank=True, verbose_name=_("الوصف - Description"))
    metadata = models.JSONField(
        default=dict, blank=True, verbose_name=_("بيانات إضافية - Metadata")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ الإكمال - Completion Date")
    )

    class Meta:
        db_table = "payments"
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} - {self.get_status_display()}"

    def mark_completed(self, transaction_id=None):
        """Mark payment as completed"""
        self.status = self.PaymentStatus.COMPLETED
        self.completed_at = timezone.now()
        if transaction_id:
            self.provider_transaction_id = transaction_id
        self.save(update_fields=["status", "completed_at", "provider_transaction_id"])

    def mark_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = self.PaymentStatus.FAILED
        if reason:
            self.metadata["failure_reason"] = reason
        self.save(update_fields=["status", "metadata"])


class UserPackage(models.Model):  # This model is correct, no changes needed here.
    """Model to track user's purchased packages"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ad_packages")
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packages",
        verbose_name=_("الدفعة - Payment"),
    )
    package = models.ForeignKey(
        AdPackage,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text=_("الباقة المرتبطة - يمكن أن تكون فارغة للإعلانات المجانية"),
    )
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    ads_remaining = models.PositiveIntegerField()
    ads_used = models.PositiveIntegerField(
        default=0,
        verbose_name=_("الإعلانات المستخدمة"),
        help_text=_("عدد الإعلانات التي تم استخدامها من هذه الباقة"),
    )

    class Meta:
        db_table = "user_packages"
        verbose_name = _("User Package")
        verbose_name_plural = _("User Packages")
        ordering = ["-purchase_date"]

    def __str__(self):
        package_name = self.package.name if self.package else _("إعلان مجاني")
        return f"{self.user.username} - {package_name}"

    def save(self, *args, **kwargs):
        if not self.pk:  # On creation
            # Only set from package if package exists
            if self.package:
                if not self.ads_remaining:
                    self.ads_remaining = self.package.ad_count
                if not self.expiry_date:
                    self.expiry_date = timezone.now() + timezone.timedelta(
                        days=self.package.duration_days
                    )
        super().save(*args, **kwargs)

    def is_active(self):
        """Check if the package is still active and has ads remaining."""
        return self.expiry_date >= timezone.now() and self.ads_remaining > 0

    def is_expired(self):
        """Check if package has expired"""
        return self.expiry_date < timezone.now()

    def total_ads(self):
        """Get total ads in package"""
        return self.ads_used + self.ads_remaining

    def use_ad(self):
        """Decrement the ad count for the package."""
        if self.is_active():
            self.ads_remaining -= 1
            self.ads_used += 1
            self.save(update_fields=["ads_remaining", "ads_used"])
            return True
        return False

    def restore_ad(self):
        """Restore an ad credit (e.g., when ad is deleted)"""
        if self.ads_used > 0:
            self.ads_remaining += 1
            self.ads_used -= 1
            self.save(update_fields=["ads_remaining", "ads_used"])
            return True
        return False

    def get_usage_percentage(self):
        """Get percentage of package used"""
        total = self.total_ads()
        if total == 0:
            return 0
        return (self.ads_used / total) * 100


class SavedSearch(models.Model):  # This model is correct, no changes needed here.
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
    unsubscribe_token = models.UUIDField(editable=False, unique=True, db_index=True)

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

    def save(self, *args, **kwargs):
        # Ensure a new UUID is generated for new instances, avoiding migration issues.
        if not self.pk:
            self.unsubscribe_token = uuid.uuid4()
        super().save(*args, **kwargs)


class Notification(models.Model):  # This model is correct, no changes needed here.
    """Model for user notifications"""

    class NotificationType(models.TextChoices):
        GENERAL = "general", _("عام")
        AD_APPROVED = "ad_approved", _("الإعلان معتمد")
        AD_REJECTED = "ad_rejected", _("الإعلان مرفوض")
        AD_EXPIRED = "ad_expired", _("الإعلان منتهي")
        PACKAGE_EXPIRED = "package_expired", _("الباقة منتهية")
        SAVED_SEARCH = "saved_search", _("نتائج البحث المحفوظ")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200, verbose_name=_("العنوان"))
    message = models.TextField(verbose_name=_("الرسالة"))
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices
    )
    link = models.URLField(
        max_length=500, blank=True, null=True, verbose_name=_("الرابط")
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]


# New models for enhanced features
class AdFeaturePrice(models.Model):
    """Pricing for ad features per category"""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="feature_prices",
        verbose_name=_("القسم"),
    )
    feature_type = models.CharField(
        max_length=20,
        choices=AdFeature.FeatureType.choices,
        verbose_name=_("نوع الميزة"),
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("السعر")
    )
    duration_days = models.PositiveIntegerField(
        default=7, verbose_name=_("مدة الميزة (بالأيام)")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        db_table = "ad_feature_prices"
        verbose_name = _("Ad Feature Price")
        verbose_name_plural = _("Ad Feature Prices")
        unique_together = ("category", "feature_type")


class CartSettings(models.Model):
    """Settings for cart functionality per category"""

    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name="cart_settings",
        verbose_name=_("القسم"),
    )
    is_enabled = models.BooleanField(default=False, verbose_name=_("تفعيل سلة الحجز"))
    reservation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        help_text=_("نسبة مبلغ الحجز من السعر الكامل"),
        verbose_name=_("نسبة الحجز %"),
    )
    minimum_reservation = models.DecimalField(
        max_digits=10, decimal_places=2, default=50.00, verbose_name=_("أقل مبلغ حجز")
    )
    maximum_reservation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("أعلى مبلغ حجز"),
    )
    delivery_enabled = models.BooleanField(
        default=False, verbose_name=_("تفعيل التوصيل")
    )
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name=_("رسوم التوصيل")
    )

    class Meta:
        db_table = "cart_settings"
        verbose_name = _("Cart Settings")
        verbose_name_plural = _("Cart Settings")


class AdReservation(models.Model):
    """Model for ad reservations through cart system"""

    class ReservationStatus(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار")
        CONFIRMED = "confirmed", _("مؤكد")
        CANCELLED = "cancelled", _("ملغي")
        COMPLETED = "completed", _("مكتمل")
        REFUNDED = "refunded", _("مسترد")

    ad = models.ForeignKey(
        ClassifiedAd,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name=_("الإعلان"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name=_("المستخدم"),
    )
    reservation_amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("مبلغ الحجز")
    )
    full_amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("المبلغ الكامل")
    )
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
        verbose_name=_("حالة الحجز"),
    )
    notes = models.TextField(blank=True, verbose_name=_("ملاحظات"))
    delivery_address = models.TextField(blank=True, verbose_name=_("عنوان التوصيل"))
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name=_("رسوم التوصيل")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        verbose_name=_("ينتهي في"), help_text=_("وقت انتهاء الحجز")
    )

    class Meta:
        db_table = "ad_reservations"
        verbose_name = _("Ad Reservation")
        verbose_name_plural = _("Ad Reservations")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Default reservation expires in 48 hours
            self.expires_at = timezone.now() + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)

    def calculate_total_amount(self):
        """Calculate total amount including delivery fee"""
        return self.reservation_amount + self.delivery_fee

    def is_expired(self):
        """Check if reservation has expired"""
        return timezone.now() > self.expires_at

    def get_remaining_amount(self):
        """Get remaining amount to be paid"""
        return self.full_amount - self.reservation_amount


class AdTransaction(models.Model):
    """Model to track all ad-related financial transactions"""

    class TransactionType(models.TextChoices):
        AD_POST = "ad_post", _("نشر إعلان")
        FEATURE_PURCHASE = "feature_purchase", _("شراء ميزة")
        PACKAGE_PURCHASE = "package_purchase", _("شراء باقة")
        RESERVATION = "reservation", _("حجز")
        PAYMENT_COMPLETION = "payment_completion", _("إكمال دفع")
        REFUND = "refund", _("استرداد")
        COMMISSION = "commission", _("عمولة المنصة")

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار")
        COMPLETED = "completed", _("مكتمل")
        FAILED = "failed", _("فاشل")
        CANCELLED = "cancelled", _("ملغي")
        REFUNDED = "refunded", _("مسترد")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("المستخدم"),
    )
    ad = models.ForeignKey(
        ClassifiedAd,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name=_("الإعلان"),
    )
    reservation = models.ForeignKey(
        AdReservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name=_("الحجز"),
    )
    transaction_type = models.CharField(
        max_length=20, choices=TransactionType.choices, verbose_name=_("نوع المعاملة")
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("المبلغ")
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_("حالة الدفع"),
    )
    payment_method = models.CharField(
        max_length=50, blank=True, verbose_name=_("طريقة الدفع")
    )
    transaction_id = models.CharField(
        max_length=100, blank=True, verbose_name=_("رقم المعاملة")
    )
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ad_transactions"
        verbose_name = _("Ad Transaction")
        verbose_name_plural = _("Ad Transactions")
        ordering = ["-created_at"]


class CustomField(models.Model):
    """Model for custom fields that can be shared across categories."""

    class FieldType(models.TextChoices):
        TEXT = "text", _("نص")
        NUMBER = "number", _("رقم")
        EMAIL = "email", _("بريد إلكتروني")
        URL = "url", _("رابط")
        PHONE = "phone", _("هاتف")
        SELECT = "select", _("خيارات متعددة")
        CHECKBOX = "checkbox", _("خانة اختيار")
        RADIO = "radio", _("اختيار واحد")
        TEXTAREA = "textarea", _("نص طويل")
        DATE = "date", _("تاريخ")
        TIME = "time", _("وقت")
        DATETIME = "datetime", _("تاريخ ووقت")
        COLOR = "color", _("لون")
        RANGE = "range", _("نطاق")
        FILE = "file", _("ملف")

    # Remove direct category FK - will use M2M through CategoryCustomField
    name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم الحقل"))
    label_ar = models.CharField(max_length=100, verbose_name=_("التسمية بالعربية"))
    label_en = models.CharField(
        max_length=100, blank=True, verbose_name=_("التسمية بالإنجليزية")
    )
    field_type = models.CharField(
        max_length=20, choices=FieldType.choices, verbose_name=_("نوع الحقل")
    )
    is_required = models.BooleanField(default=False, verbose_name=_("مطلوب افتراضياً"))
    help_text = models.TextField(blank=True, verbose_name=_("نص المساعدة"))
    placeholder = models.CharField(
        max_length=200, blank=True, verbose_name=_("نص تذكيري")
    )
    default_value = models.CharField(
        max_length=500, blank=True, verbose_name=_("القيمة الافتراضية")
    )
    min_length = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("الحد الأدنى للطول")
    )
    max_length = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("الحد الأقصى للطول")
    )
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأدنى للقيمة"),
    )
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الحد الأقصى للقيمة"),
    )
    validation_regex = models.CharField(
        max_length=200, blank=True, verbose_name=_("نمط التحقق (Regex)")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # M2M relationship with categories
    categories = models.ManyToManyField(
        Category,
        through="CategoryCustomField",
        related_name="custom_fields",
        verbose_name=_("الأقسام"),
        blank=True,
    )

    class Meta:
        db_table = "custom_fields"
        verbose_name = _("حقل مخصص")
        verbose_name_plural = _("الحقول المخصصة")
        ordering = ["name"]

    def __str__(self):
        return f"{self.label_ar or self.name}"

    @property
    def label(self):
        """Return the appropriate label based on current language."""
        return self.label_ar or self.name


class CustomFieldOption(models.Model):
    """Model for custom field options (for select, radio, checkbox fields)."""

    custom_field = models.ForeignKey(
        CustomField,
        on_delete=models.CASCADE,
        related_name="field_options",
        verbose_name=_("الحقل المخصص"),
    )
    label_ar = models.CharField(max_length=200, verbose_name=_("الخيار بالعربية"))
    label_en = models.CharField(
        max_length=200, blank=True, verbose_name=_("الخيار بالإنجليزية")
    )
    value = models.CharField(max_length=200, verbose_name=_("القيمة"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("الترتيب"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        db_table = "custom_field_options"
        verbose_name = _("خيار الحقل المخصص")
        verbose_name_plural = _("خيارات الحقول المخصصة")
        ordering = ["custom_field", "order", "label_ar"]
        unique_together = [["custom_field", "value"]]

    def __str__(self):
        return f"{self.custom_field.name} - {self.label_ar}"

    @property
    def label(self):
        """Return the appropriate label based on current language."""
        from django.utils.translation import get_language

        if get_language() == "en" and self.label_en:
            return self.label_en
        return self.label_ar


class CategoryCustomField(models.Model):
    """Through model for Category and CustomField relationship."""

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name=_("القسم")
    )
    custom_field = models.ForeignKey(
        CustomField, on_delete=models.CASCADE, verbose_name=_("الحقل المخصص")
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("مطلوب في هذا القسم"),
        help_text=_("تجاوز الإعداد الافتراضي للحقل"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتيب العرض"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط في هذا القسم"))
    show_on_card = models.BooleanField(
        default=False,
        verbose_name=_("إظهار على بطاقة الإعلان"),
        help_text=_("إظهار قيمة هذا الحقل على بطاقة الإعلان من الخارج"),
    )

    class Meta:
        db_table = "category_custom_fields"
        verbose_name = _("حقل مخصص للقسم")
        verbose_name_plural = _("الحقول المخصصة للأقسام")
        ordering = ["category", "order"]
        unique_together = [["category", "custom_field"]]

    def __str__(self):
        return f"{self.category.name} - {self.custom_field.label}"


class Wishlist(models.Model):
    """Model for user wishlist"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name=_("المستخدم - User"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wishlists"
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    def get_items_count(self):
        """Get total items in wishlist"""
        return self.items.count()


class WishlistItem(models.Model):
    """Model for wishlist items"""

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("قائمة الأمنيات"),
    )
    ad = models.ForeignKey(
        ClassifiedAd,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name=_("الإعلان"),
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإضافة"))

    class Meta:
        db_table = "wishlist_items"
        verbose_name = _("Wishlist Item")
        verbose_name_plural = _("Wishlist Items")
        unique_together = [["wishlist", "ad"]]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.wishlist.user.username} - {self.ad.title}"


class Cart(models.Model):
    """Model for user shopping cart"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("المستخدم - User"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def get_items_count(self):
        """Get total items in cart"""
        return self.items.count()

    def get_total_amount(self):
        """Calculate total cart amount"""
        total = sum(item.get_total_price() for item in self.items.all())
        return total


class CartItem(models.Model):
    """Model for cart items"""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("السلة"),
    )
    ad = models.ForeignKey(
        ClassifiedAd,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("الإعلان"),
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("الكمية"))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإضافة"))

    class Meta:
        db_table = "cart_items"
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        unique_together = [["cart", "ad"]]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.cart.user.username} - {self.ad.title} (x{self.quantity})"

    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.ad.price * self.quantity


# ===========================
# CHAT MODELS
# ===========================


class ChatRoom(models.Model):
    """
    Chat room for conversations between users
    Supports: Publisher-Client and Publisher-Admin chats
    """

    ROOM_TYPES = [
        ("publisher_client", _("Publisher-Client")),
        ("publisher_admin", _("Publisher-Admin")),
    ]

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPES,
        default="publisher_client",
        verbose_name=_("نوع المحادثة"),
    )

    # Participants
    publisher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="publisher_chat_rooms",
        verbose_name=_("الناشر"),
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_chat_rooms",
        null=True,
        blank=True,
        verbose_name=_("العميل"),
    )

    # Related ad (for publisher-client chats)
    ad = models.ForeignKey(
        ClassifiedAd,
        on_delete=models.CASCADE,
        related_name="chat_rooms",
        null=True,
        blank=True,
        verbose_name=_("الإعلان"),
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        db_table = "chat_rooms"
        verbose_name = _("Chat Room")
        verbose_name_plural = _("Chat Rooms")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["publisher", "client"]),
            models.Index(fields=["room_type", "is_active"]),
        ]

    def __str__(self):
        if self.room_type == "publisher_client":
            return f"Chat: {self.publisher.username} <-> {self.client.username if self.client else 'Unknown'}"
        return f"Support: {self.publisher.username} <-> Admin"

    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def mark_as_read(self, user):
        """Mark all messages as read for a specific user"""
        self.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)


class ChatMessage(models.Model):
    """
    Individual chat messages within a room
    """

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("غرفة المحادثة"),
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        verbose_name=_("المرسل"),
    )
    message = models.TextField(verbose_name=_("الرسالة"))

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت الإرسال"))
    is_read = models.BooleanField(default=False, verbose_name=_("مقروءة"))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_("وقت القراءة"))

    # Optional: File attachments
    attachment = models.FileField(
        upload_to="chat_attachments/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("مرفق"),
    )

    class Meta:
        db_table = "chat_messages"
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room", "created_at"]),
            models.Index(fields=["sender", "is_read"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"

    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class Visitor(models.Model):
    """
    Track website visitors for analytics.
    Stores unique visitors by IP and session.
    """

    ip_address = models.GenericIPAddressField(verbose_name=_("عنوان IP"))
    session_key = models.CharField(
        max_length=40, db_index=True, verbose_name=_("مفتاح الجلسة")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visits",
        verbose_name=_("المستخدم"),
    )
    user_agent = models.TextField(blank=True, verbose_name=_("متصفح المستخدم"))
    page_url = models.CharField(
        max_length=500, blank=True, verbose_name=_("رابط الصفحة")
    )
    referrer = models.CharField(max_length=500, blank=True, verbose_name=_("المصدر"))
    country = models.CharField(max_length=2, blank=True, verbose_name=_("الدولة"))
    city = models.CharField(max_length=100, blank=True, verbose_name=_("المدينة"))
    device_type = models.CharField(
        max_length=20,
        choices=[
            ("mobile", _("موبايل")),
            ("tablet", _("تابلت")),
            ("desktop", _("كمبيوتر")),
        ],
        default="desktop",
        verbose_name=_("نوع الجهاز"),
    )
    first_visit = models.DateTimeField(auto_now_add=True, verbose_name=_("أول زيارة"))
    last_activity = models.DateTimeField(
        auto_now=True, db_index=True, verbose_name=_("آخر نشاط")
    )
    page_views = models.PositiveIntegerField(default=1, verbose_name=_("عدد الصفحات"))

    class Meta:
        db_table = "visitors"
        verbose_name = _("Visitor")
        verbose_name_plural = _("Visitors")
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["ip_address", "session_key"]),
            models.Index(fields=["last_activity"]),
            models.Index(fields=["first_visit"]),
        ]
        unique_together = [["ip_address", "session_key"]]

    def __str__(self):
        if self.user:
            return f"{self.user.username} ({self.ip_address})"
        return f"Guest ({self.ip_address})"

    @property
    def is_online(self):
        """Check if visitor is currently online (active in last 15 minutes)"""
        threshold = timezone.now() - timedelta(minutes=15)
        return self.last_activity >= threshold

    @classmethod
    def get_online_count(cls):
        """Get count of currently online visitors"""
        threshold = timezone.now() - timedelta(minutes=15)
        return cls.objects.filter(last_activity__gte=threshold).count()

    @classmethod
    def get_unique_visitors(cls, start_date=None, end_date=None):
        """Get unique visitor count for a date range"""
        queryset = cls.objects.all()
        if start_date:
            queryset = queryset.filter(first_visit__gte=start_date)
        if end_date:
            queryset = queryset.filter(first_visit__lte=end_date)
        return queryset.values("ip_address").distinct().count()


class NewsletterSubscriber(models.Model):
    """
    Newsletter subscription model for managing email subscribers.
    """

    email = models.EmailField(unique=True, verbose_name=_("البريد الإلكتروني"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الاشتراك")
    )
    unsubscribed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ إلغاء الاشتراك")
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name=_("عنوان IP")
    )
    user_agent = models.TextField(blank=True, verbose_name=_("متصفح المستخدم"))

    class Meta:
        db_table = "newsletter_subscribers"
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newsletter Subscribers")
        ordering = ["-subscribed_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["subscribed_at"]),
        ]

    def __str__(self):
        status = _("نشط") if self.is_active else _("غير نشط")
        return f"{self.email} - {status}"

    def unsubscribe(self):
        """Mark subscriber as inactive"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()


"""
AdReport model - to be added to main/models.py
"""


class AdReport(models.Model):
    """Model for reporting ads or users"""

    class ReportType(models.TextChoices):
        AD_CONTENT = "ad_content", _("محتوى إعلان غير لائق")
        FRAUD = "fraud", _("احتيال أو نصب")
        SPAM = "spam", _("إعلان متكرر أو سبام")
        WRONG_CATEGORY = "wrong_category", _("قسم خاطئ")
        USER_BEHAVIOR = "user_behavior", _("سلوك مستخدم غير لائق")
        FAKE_INFO = "fake_info", _("معلومات مضللة")
        OTHER = "other", _("أخرى")

    class Status(models.TextChoices):
        PENDING = "pending", _("قيد المراجعة")
        REVIEWING = "reviewing", _("تحت المراجعة")
        RESOLVED = "resolved", _("تم الحل")
        REJECTED = "rejected", _("مرفوض")

    # Report details
    reporter = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports_made",
        verbose_name=_("المبلغ"),
    )
    report_type = models.CharField(
        max_length=20, choices=ReportType.choices, verbose_name=_("نوع البلاغ")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("الحالة"),
    )

    # What is being reported (either ad or user)
    reported_ad = models.ForeignKey(
        "ClassifiedAd",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports",
        verbose_name=_("الإعلان المبلغ عنه"),
    )
    reported_user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports_received",
        verbose_name=_("المستخدم المبلغ عنه"),
    )

    # Report content
    description = models.TextField(
        verbose_name=_("وصف البلاغ"), help_text=_("يرجى تقديم تفاصيل حول البلاغ")
    )
    evidence_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("رابط دليل"),
        help_text=_("رابط لصورة أو دليل إضافي"),
    )

    # Admin notes
    admin_notes = models.TextField(
        blank=True, null=True, verbose_name=_("ملاحظات الإدارة")
    )
    reviewed_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports_reviewed",
        verbose_name=_("تمت المراجعة بواسطة"),
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))
    resolved_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ الحل")
    )

    class Meta:
        db_table = "ad_reports"
        verbose_name = _("بلاغ")
        verbose_name_plural = _("البلاغات")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["report_type"]),
        ]

    def __str__(self):
        if self.reported_ad:
            return f"بلاغ عن إعلان: {self.reported_ad.title}"
        elif self.reported_user:
            return f"بلاغ عن مستخدم: {self.reported_user.username}"
        return f"بلاغ #{self.id}"

    def clean(self):
        """Ensure either ad or user is reported, not both"""
        from django.core.exceptions import ValidationError

        if not self.reported_ad and not self.reported_user:
            raise ValidationError(_("يجب تحديد إعلان أو مستخدم للإبلاغ عنه"))
        if self.reported_ad and self.reported_user:
            raise ValidationError(_("لا يمكن الإبلاغ عن إعلان ومستخدم في نفس الوقت"))

    def save(self, *args, **kwargs):
        # Only call full_clean if validate parameter is True (default)
        if kwargs.pop("validate", True):
            self.full_clean()
        super().save(*args, **kwargs)

    def mark_as_resolved(self, admin_user, notes=""):
        """Mark report as resolved"""
        self.status = self.Status.RESOLVED
        self.resolved_at = timezone.now()
        self.reviewed_by = admin_user
        if notes:
            self.admin_notes = notes
        self.save()
