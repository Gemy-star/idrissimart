"""
Serializers for API endpoints
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from main.models import (
    Category, ClassifiedAd, AdImage, AdReview, AdFeature, AdPackage,
    Payment, UserPackage, SavedSearch, Notification, CustomField,
    CustomFieldOption, CategoryCustomField, Wishlist, WishlistItem,
    ChatRoom, ChatMessage, FAQ, FAQCategory, SafetyTip, ContactMessage,
    AdTransaction, UserSubscription, AdUpgradeHistory, AdFeaturePrice,
    CartSettings, PaidAdvertisement
)
from content.models import (
    Country, Blog, BlogCategory, Comment, HomeSlider,
    PaymentMethodConfig, SiteConfiguration, AboutPage, AboutPageSection,
    ContactPage, HomePage, WhyChooseUsFeature, TermsPage, PrivacyPage
)

User = get_user_model()


# ==================== User Serializers ====================

class UserListSerializer(serializers.ModelSerializer):
    """Minimal user info for listings"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'profile_image', 'verification_status', 'average_rating',
            'is_premium', 'profile_type', 'rank'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user profile"""
    total_ads = serializers.SerializerMethodField()
    active_ads = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'mobile', 'whatsapp', 'profile_type', 'rank',
            'verification_status', 'is_mobile_verified', 'is_email_verified',
            'profile_image', 'cover_image', 'bio', 'bio_ar',
            'company_name', 'company_name_ar', 'country', 'city', 'address',
            'specialization', 'years_of_experience', 'website',
            'facebook', 'twitter', 'instagram', 'linkedin',
            'is_premium', 'subscription_end', 'average_rating', 'total_reviews',
            'total_ads', 'active_ads', 'date_joined'
        ]
        read_only_fields = [
            'id', 'verification_status', 'average_rating', 'total_reviews',
            'total_ads', 'active_ads', 'date_joined'
        ]

    def get_total_ads(self, obj):
        return obj.classified_ads.count()

    def get_active_ads(self, obj):
        return obj.classified_ads.filter(status='active').count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'mobile',
            'profile_type', 'rank', 'country', 'city'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user profile"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'mobile', 'whatsapp',
            'bio', 'bio_ar', 'profile_image', 'cover_image',
            'company_name', 'company_name_ar', 'city', 'address',
            'specialization', 'years_of_experience',
            'website', 'facebook', 'twitter', 'instagram', 'linkedin'
        ]


class ForgotPasswordSerializer(serializers.Serializer):
    """Request a password reset link"""
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """Confirm password reset with token"""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class SendOTPSerializer(serializers.Serializer):
    """Send OTP to a phone number for verification"""
    phone = serializers.CharField(max_length=20)


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP code to confirm phone ownership"""
    otp_code = serializers.CharField(min_length=4, max_length=6)


# ==================== Country Serializers ====================

class CountrySerializer(serializers.ModelSerializer):
    """Country serializer"""
    class Meta:
        model = Country
        fields = ['id', 'name', 'name_en', 'code', 'flag_emoji', 'phone_code', 'currency', 'cities', 'is_active', 'order']


# ==================== Category Serializers ====================

class CategoryListSerializer(serializers.ModelSerializer):
    """Minimal category info for listings"""
    subcategories_count = serializers.SerializerMethodField()
    ads_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'name_ar', 'slug', 'slug_ar',
            'section_type', 'icon', 'image', 'parent',
            'subcategories_count', 'ads_count', 'allow_cart'
        ]

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()

    def get_ads_count(self, obj):
        return obj.classified_ads.filter(status='active').count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Detailed category with subcategories"""
    subcategories = CategoryListSerializer(many=True, read_only=True)
    custom_fields = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'name_ar', 'slug', 'slug_ar',
            'section_type', 'parent', 'description', 'icon', 'image',
            'country', 'countries', 'custom_field_schema', 'allow_cart',
            'cart_instructions', 'default_reservation_percentage',
            'min_reservation_amount', 'max_reservation_amount',
            'subcategories', 'custom_fields'
        ]

    def get_custom_fields(self, obj):
        # Get custom fields for this category
        category_fields = CategoryCustomField.objects.filter(category=obj)
        return CustomFieldSerializer([cf.custom_field for cf in category_fields], many=True).data


# ==================== ClassifiedAd Serializers ====================

class AdImageSerializer(serializers.ModelSerializer):
    """Ad image serializer"""
    class Meta:
        model = AdImage
        fields = ['id', 'image', 'order']


class AdReviewSerializer(serializers.ModelSerializer):
    """Ad review serializer"""
    reviewer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    reviewer_image = serializers.ImageField(source='user.profile_image', read_only=True)

    class Meta:
        model = AdReview
        fields = [
            'id', 'user', 'reviewer_name', 'reviewer_image',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClassifiedAdListSerializer(serializers.ModelSerializer):
    """Minimal ad info for listings"""
    user = UserListSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = ClassifiedAd
        fields = [
            'id', 'title', 'slug', 'category', 'user',
            'price', 'is_negotiable', 'primary_image',
            'city', 'country', 'status', 'is_highlighted', 'is_urgent',
            'is_favorited', 'views_count', 'created_at', 'expires_at'
        ]

    def get_primary_image(self, obj):
        image = obj.images.first()  # Get first image by order
        if image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.image.url)
        return None

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WishlistItem.objects.filter(
                wishlist__user=request.user, ad=obj
            ).exists()
        return False


class ClassifiedAdDetailSerializer(serializers.ModelSerializer):
    """Detailed ad info"""
    user = UserListSerializer(read_only=True)
    category = CategoryDetailSerializer(read_only=True)
    images = AdImageSerializer(many=True, read_only=True)
    reviews = AdReviewSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = ClassifiedAd
        fields = [
            'id', 'title', 'slug', 'category', 'user',
            'description', 'price', 'is_negotiable',
            'images', 'city', 'country', 'address',
            'status', 'is_highlighted', 'is_urgent', 'is_pinned',
            'views_count', 'created_at', 'updated_at', 'expires_at',
            'reviews', 'is_favorited',
            'custom_fields', 'is_cart_enabled', 'video_url',
            'rating', 'rating_count'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WishlistItem.objects.filter(
                wishlist__user=request.user, ad=obj
            ).exists()
        return False


class ClassifiedAdCreateSerializer(serializers.ModelSerializer):
    """Create/Update classified ad"""
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = ClassifiedAd
        fields = [
            'title', 'category', 'description',
            'price', 'is_negotiable', 'country', 'city', 'address',
            'is_highlighted', 'is_urgent', 'custom_fields',
            'is_cart_enabled', 'video_url', 'images'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        user = self.context['request'].user
        ad = ClassifiedAd.objects.create(user=user, **validated_data)

        # Create images
        for index, image in enumerate(images_data):
            AdImage.objects.create(
                ad=ad,
                image=image,
                order=index,
                is_primary=(index == 0)
            )

        return ad

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update images if provided
        if images_data is not None:
            instance.images.all().delete()
            for index, image in enumerate(images_data):
                AdImage.objects.create(
                    ad=instance,
                    image=image,
                    order=index,
                    is_primary=(index == 0)
                )

        return instance


# ==================== Blog Serializers ====================

class BlogCategorySerializer(serializers.ModelSerializer):
    """Blog category serializer"""
    blogs_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'name_en', 'slug', 'description', 'icon', 'color', 'order', 'is_active', 'blogs_count']

    def get_blogs_count(self, obj):
        return obj.get_blogs_count()


class BlogListSerializer(serializers.ModelSerializer):
    """Minimal blog info for listings"""
    author = UserListSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'image',
            'published_date', 'views_count', 'likes_count', 'is_liked', 'is_published'
        ]

    def get_likes_count(self, obj):
        return obj.get_likes_count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class BlogDetailSerializer(serializers.ModelSerializer):
    """Detailed blog info"""
    author = UserListSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'content',
            'image', 'published_date', 'updated_date', 'views_count',
            'likes_count', 'is_liked', 'is_published', 'comments', 'tags'
        ]

    def get_comments(self, obj):
        comments = obj.comments.filter(active=True, parent__isnull=True)
        return CommentSerializer(comments, many=True).data

    def get_likes_count(self, obj):
        return obj.get_likes_count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_tags(self, obj):
        return list(obj.tags.values_list('name', flat=True))


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer with nested replies"""
    author = UserListSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'blog', 'author', 'body', 'created_on', 'active', 'parent', 'replies']
        read_only_fields = ['id', 'created_on']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(active=True), many=True).data
        return []


# ==================== Chat Serializers ====================

class ChatMessageSerializer(serializers.ModelSerializer):
    """Chat message serializer"""
    sender = UserListSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'message', 'attachment', 'created_at', 'is_read', 'read_at']
        read_only_fields = ['id', 'created_at', 'is_read', 'read_at']


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Chat room list serializer"""
    publisher = UserListSerializer(read_only=True)
    client = UserListSerializer(read_only=True)
    ad_title = serializers.CharField(source='ad.title', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'room_type', 'publisher', 'client', 'ad', 'ad_title',
            'last_message', 'unread_count', 'created_at', 'updated_at', 'is_active'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'message': last_msg.message,
                'sender': last_msg.sender.username,
                'created_at': last_msg.created_at
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_unread_count(request.user)
        return 0


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    """Chat room detail with messages"""
    publisher = UserListSerializer(read_only=True)
    client = UserListSerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    ad = ClassifiedAdListSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'room_type', 'publisher', 'client', 'ad',
            'messages', 'created_at', 'updated_at', 'is_active'
        ]


# ==================== Wishlist Serializers ====================

class WishlistItemSerializer(serializers.ModelSerializer):
    """Wishlist item serializer"""
    ad = ClassifiedAdListSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ['id', 'ad', 'added_at']


class WishlistSerializer(serializers.ModelSerializer):
    """Wishlist serializer"""
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']


# ==================== Notification Serializers ====================

class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title',
            'message', 'link', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ==================== Package & Payment Serializers ====================

class AdFeatureSerializer(serializers.ModelSerializer):
    """Ad feature serializer"""
    feature_type_display = serializers.CharField(source='get_feature_type_display', read_only=True)

    class Meta:
        model = AdFeature
        fields = ['id', 'ad', 'feature_type', 'feature_type_display', 'start_date', 'end_date', 'is_active']


class AdPackageSerializer(serializers.ModelSerializer):
    """Ad package serializer"""
    class Meta:
        model = AdPackage
        fields = [
            'id', 'name', 'name_en', 'description', 'description_en',
            'price', 'ad_count', 'ad_duration_days', 'duration_days',
            'feature_pinned_price', 'feature_urgent_price', 'feature_highlighted_price',
            'feature_contact_for_price', 'feature_auto_refresh_price', 'feature_add_video_price',
            'is_active', 'is_recommended', 'is_default'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'provider', 'provider_transaction_id',
            'amount', 'currency', 'status', 'description', 'metadata',
            'offline_payment_receipt', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating a payment"""
    PROVIDER_CHOICES = [
        ('paymob', 'Paymob (Card / Wallet)'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Mobile Wallet'),
        ('instapay', 'InstaPay'),
    ]
    CONTEXT_CHOICES = [
        ('ad_posting', 'Ad Posting'),
        ('ad_upgrade', 'Ad Upgrade'),
        ('package_purchase', 'Package Purchase'),
        ('product_purchase', 'Product Purchase'),
        ('paid_banner', 'Paid Banner Ad'),
    ]

    provider = serializers.ChoiceField(choices=PROVIDER_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='EGP')
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    context = serializers.ChoiceField(choices=CONTEXT_CHOICES, default='ad_posting')
    metadata = serializers.JSONField(required=False, default=dict)

    # Paymob-specific fields
    billing_data = serializers.JSONField(required=False, default=dict,
        help_text="Required for Paymob: first_name, last_name, email, phone_number, etc.")
    notification_url = serializers.URLField(required=False, allow_blank=True,
        help_text="Paymob webhook callback URL")
    redirection_url = serializers.URLField(required=False, allow_blank=True,
        help_text="Paymob redirection URL after payment")

    # PayPal-specific fields
    return_url = serializers.URLField(required=False, allow_blank=True,
        help_text="PayPal: URL to redirect after successful payment")
    cancel_url = serializers.URLField(required=False, allow_blank=True,
        help_text="PayPal: URL to redirect if payment is cancelled")

    # Paid banner-specific fields
    paid_ad_id = serializers.IntegerField(required=False,
        help_text="Required for paid_banner context: the PaidAdvertisement ID to pay for")


class PaymentMethodSerializer(serializers.Serializer):
    """Represents a single available payment method"""
    code = serializers.CharField()
    label = serializers.CharField()


class PayPalCaptureSerializer(serializers.Serializer):
    """Serializer for capturing a PayPal order"""
    payment_id = serializers.IntegerField(help_text="Internal Payment record ID")
    paypal_order_id = serializers.CharField(help_text="PayPal order ID returned after buyer approval")


class UploadReceiptSerializer(serializers.Serializer):
    """Serializer for uploading an offline payment receipt"""
    receipt = serializers.ImageField(help_text="Image or screenshot of the payment receipt")


class UserPackageSerializer(serializers.ModelSerializer):
    """User package serializer"""
    package = AdPackageSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserPackage
        fields = [
            'id', 'user', 'package', 'payment', 'purchase_date', 'expiry_date',
            'ads_remaining', 'ads_used', 'is_active'
        ]

    def get_is_active(self, obj):
        return obj.is_active()


# ==================== FAQ Serializers ====================

class FAQCategorySerializer(serializers.ModelSerializer):
    """FAQ category serializer"""
    class Meta:
        model = FAQCategory
        fields = ['id', 'name', 'name_ar', 'icon', 'order', 'is_active']


class FAQSerializer(serializers.ModelSerializer):
    """FAQ serializer"""
    category = FAQCategorySerializer(read_only=True)

    class Meta:
        model = FAQ
        fields = ['id', 'category', 'question', 'question_ar', 'answer', 'answer_ar', 'order', 'is_active', 'is_popular']


# ==================== Safety Tips Serializers ====================

class SafetyTipSerializer(serializers.ModelSerializer):
    """Safety tip serializer"""
    class Meta:
        model = SafetyTip
        fields = ['id', 'title', 'title_en', 'description', 'description_en', 'icon_class', 'order', 'is_active']


# ==================== Contact Serializers ====================

class ContactMessageSerializer(serializers.ModelSerializer):
    """Contact message serializer"""
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'status', 'created_at', 'replied_at']
        read_only_fields = ['id', 'created_at', 'replied_at']


# ==================== Custom Fields Serializers ====================

class CustomFieldOptionSerializer(serializers.ModelSerializer):
    """Custom field option serializer"""
    class Meta:
        model = CustomFieldOption
        fields = ['id', 'label_ar', 'label_en', 'value', 'order', 'is_active']


class CustomFieldSerializer(serializers.ModelSerializer):
    """Custom field serializer"""
    options = CustomFieldOptionSerializer(many=True, read_only=True, source='field_options')

    class Meta:
        model = CustomField
        fields = [
            'id', 'name', 'label_ar', 'label_en', 'field_type', 'is_required',
            'help_text', 'placeholder', 'default_value',
            'min_length', 'max_length', 'min_value', 'max_value',
            'validation_regex', 'is_active', 'options'
        ]


# ==================== Home Page Serializers ====================

class HomeSliderSerializer(serializers.ModelSerializer):
    """Home slider serializer"""
    class Meta:
        model = HomeSlider
        fields = [
            'id', 'title', 'title_ar', 'subtitle', 'subtitle_ar',
            'description', 'description_ar', 'image', 'button_text',
            'button_text_ar', 'button_url', 'country', 'background_color',
            'text_color', 'is_active', 'order'
        ]


class WhyChooseUsFeatureSerializer(serializers.ModelSerializer):
    """Why choose us feature serializer"""
    class Meta:
        model = WhyChooseUsFeature
        fields = ['id', 'title', 'title_ar', 'description', 'description_ar', 'icon', 'order', 'is_active']


class SiteConfigurationSerializer(serializers.ModelSerializer):
    """Site configuration serializer"""
    class Meta:
        model = SiteConfiguration
        fields = [
            'id', 'meta_keywords', 'meta_keywords_ar', 'footer_text', 'footer_text_ar',
            'copyright_text', 'logo', 'logo_light', 'logo_dark', 'logo_mini',
            'require_email_verification', 'require_phone_verification',
            'require_verification_for_services', 'allow_online_payment', 'allow_offline_payment'
        ]


# ==================== Static Pages Serializers ====================

class AboutPageSectionSerializer(serializers.ModelSerializer):
    """About page section serializer"""
    class Meta:
        model = AboutPageSection
        fields = ['id', 'tab_title', 'tab_title_ar', 'icon', 'content', 'content_ar', 'order', 'is_active']


class AboutPageSerializer(serializers.ModelSerializer):
    """About page serializer"""
    sections = AboutPageSectionSerializer(many=True, read_only=True)

    class Meta:
        model = AboutPage
        fields = ['id', 'content', 'content_ar', 'sections']


class ContactPageSerializer(serializers.ModelSerializer):
    """Contact page serializer"""
    class Meta:
        model = ContactPage
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'enable_contact_form', 'notification_email',
            'show_phone', 'show_address', 'show_office_hours', 'show_map',
            'office_hours', 'office_hours_ar', 'map_embed_code'
        ]


class TermsPageSerializer(serializers.ModelSerializer):
    """Terms page serializer"""
    class Meta:
        model = TermsPage
        fields = ['id', 'content', 'content_ar']


class PrivacyPageSerializer(serializers.ModelSerializer):
    """Privacy page serializer"""
    class Meta:
        model = PrivacyPage
        fields = ['id', 'content', 'content_ar']


# ==================== Home Page Content Serializer ====================

class HomePageSerializer(serializers.ModelSerializer):
    """Serializer for the HomePage singleton (hero + statistics + section flags)"""
    why_choose_us_features = WhyChooseUsFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = HomePage
        fields = [
            # Hero
            'hero_title', 'hero_title_ar',
            'hero_subtitle', 'hero_subtitle_ar',
            'hero_image',
            'hero_button_text', 'hero_button_text_ar', 'hero_button_url',
            # Why choose us
            'show_why_choose_us',
            'why_choose_us_title', 'why_choose_us_title_ar',
            'why_choose_us_subtitle', 'why_choose_us_subtitle_ar',
            'why_choose_us_features',
            # Section visibility
            'show_featured_categories', 'show_featured_ads', 'show_statistics',
            # Statistics
            'stat1_value', 'stat1_title', 'stat1_title_ar',
            'stat1_subtitle', 'stat1_subtitle_ar', 'stat1_icon',
            'stat2_value', 'stat2_title', 'stat2_title_ar',
            'stat2_subtitle', 'stat2_subtitle_ar', 'stat2_icon',
            'stat3_value', 'stat3_title', 'stat3_title_ar',
            'stat3_subtitle', 'stat3_subtitle_ar', 'stat3_icon',
            'stat4_value', 'stat4_title', 'stat4_title_ar',
            'stat4_subtitle', 'stat4_subtitle_ar', 'stat4_icon',
        ]


# ==================== Paid Advertisement Serializers ====================

class PaidAdvertisementSerializer(serializers.ModelSerializer):
    """Paid advertisement serializer (read)"""
    advertiser = UserListSerializer(read_only=True)
    category_detail = CategoryListSerializer(source='category', read_only=True)

    class Meta:
        model = PaidAdvertisement
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'advertiser', 'company_name', 'contact_email', 'contact_phone',
            'image', 'mobile_image', 'target_url', 'cta_text', 'cta_text_ar',
            'open_in_new_tab', 'ad_type', 'placement_type',
            'country', 'category', 'category_detail',
            'start_date', 'end_date',
            'status', 'is_active', 'priority', 'order',
            'price', 'currency', 'payment_status', 'payment_reference',
            'views_count', 'clicks_count',
            'created_at', 'updated_at',
        ]


class PaidAdvertisementCreateSerializer(serializers.ModelSerializer):
    """Create a paid advertisement (publisher)"""

    class Meta:
        model = PaidAdvertisement
        fields = [
            'title', 'title_ar', 'description', 'description_ar',
            'company_name', 'contact_email', 'contact_phone',
            'image', 'mobile_image', 'target_url', 'cta_text', 'cta_text_ar',
            'open_in_new_tab', 'ad_type', 'placement_type',
            'country', 'category',
            'start_date', 'end_date',
        ]

    def validate(self, data):
        placement = data.get('placement_type', PaidAdvertisement.PlacementType.GENERAL)
        if placement == PaidAdvertisement.PlacementType.CATEGORY and not data.get('category'):
            raise serializers.ValidationError(
                {'category': 'Category is required for category placement type.'}
            )
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError(
                {'end_date': 'End date must be after start date.'}
            )
        return data

    def create(self, validated_data):
        from constance import config as cc
        from decimal import Decimal

        ad_type = validated_data.get('ad_type', PaidAdvertisement.AdType.BANNER)
        try:
            pricing = {
                PaidAdvertisement.AdType.BANNER: Decimal(str(getattr(cc, 'PAID_AD_BANNER_PRICE', '200'))),
                PaidAdvertisement.AdType.SIDEBAR: Decimal(str(getattr(cc, 'PAID_AD_SIDEBAR_PRICE', '150'))),
                PaidAdvertisement.AdType.POPUP: Decimal(str(getattr(cc, 'PAID_AD_POPUP_PRICE', '250'))),
                PaidAdvertisement.AdType.FEATURED_BOX: Decimal(str(getattr(cc, 'PAID_AD_FEATURED_PRICE', '180'))),
            }
        except Exception:
            pricing = {
                PaidAdvertisement.AdType.BANNER: Decimal('200'),
                PaidAdvertisement.AdType.SIDEBAR: Decimal('150'),
                PaidAdvertisement.AdType.POPUP: Decimal('250'),
                PaidAdvertisement.AdType.FEATURED_BOX: Decimal('180'),
            }

        price = pricing.get(ad_type, Decimal('200'))
        country = validated_data.get('country')
        currency = getattr(country, 'currency', None) or 'EGP'
        user = self.context['request'].user

        return PaidAdvertisement.objects.create(
            advertiser=user,
            status=PaidAdvertisement.Status.DRAFT,
            payment_status='unpaid',
            price=price,
            currency=currency,
            **validated_data,
        )
