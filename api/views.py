"""
API ViewSets for mobile application
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404

from main.models import (
    Category, ClassifiedAd, AdImage, AdReview, AdFeature, AdPackage,
    Payment, UserPackage, SavedSearch, Notification, CustomField,
    CustomFieldOption, CategoryCustomField, Wishlist, WishlistItem,
    ChatRoom, ChatMessage, FAQ, FAQCategory, SafetyTip, ContactMessage,
    AdTransaction, UserSubscription
)
from content.models import (
    Country, Blog, BlogCategory, Comment, HomeSlider,
    PaymentMethodConfig, SiteConfiguration, AboutPage, ContactPage,
    TermsPage, PrivacyPage, WhyChooseUsFeature
)
from .serializers import (
    # User serializers
    UserListSerializer, UserDetailSerializer, UserRegistrationSerializer, UserUpdateSerializer,
    # Country serializers
    CountrySerializer,
    # Category serializers
    CategoryListSerializer, CategoryDetailSerializer,
    # Ad serializers
    ClassifiedAdListSerializer, ClassifiedAdDetailSerializer, ClassifiedAdCreateSerializer,
    AdImageSerializer, AdReviewSerializer,
    # Blog serializers
    BlogCategorySerializer, BlogListSerializer, BlogDetailSerializer, CommentSerializer,
    # Chat serializers
    ChatRoomListSerializer, ChatRoomDetailSerializer, ChatMessageSerializer,
    # Wishlist serializers
    WishlistSerializer, WishlistItemSerializer,
    # Notification serializers
    NotificationSerializer,
    # Package & Payment serializers
    AdFeatureSerializer, AdPackageSerializer, PaymentSerializer, UserPackageSerializer,
    # FAQ serializers
    FAQCategorySerializer, FAQSerializer,
    # Safety Tips serializers
    SafetyTipSerializer,
    # Contact serializers
    ContactMessageSerializer,
    # Home page serializers
    HomeSliderSerializer, WhyChooseUsFeatureSerializer,
    SiteConfigurationSerializer, AboutPageSerializer, ContactPageSerializer,
    TermsPageSerializer, PrivacyPageSerializer,
    # Custom field serializers
    CustomFieldSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdOwnerOrReadOnly, IsPublisherOrClient
from django.contrib.auth import get_user_model

User = get_user_model()


# ==================== User ViewSets ====================

class UserViewSet(viewsets.ModelViewSet):
    """
    User management endpoints
    """
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def ads(self, request, pk=None):
        """Get user's ads"""
        user = self.get_object()
        ads = ClassifiedAd.objects.filter(user=user, status='active')
        serializer = ClassifiedAdListSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get user's reviews"""
        user = self.get_object()
        reviews = AdReview.objects.filter(ad__user=user)
        serializer = AdReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)


# ==================== Country ViewSets ====================

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Country listing endpoint
    """
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'name_en', 'code']
    ordering_fields = ['order', 'name']
    ordering = ['order']


# ==================== Category ViewSets ====================

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category listing endpoint
    """
    queryset = Category.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['section_type', 'parent', 'country']
    search_fields = ['name', 'name_ar']
    ordering_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategoryListSerializer

    @action(detail=True, methods=['get'])
    def ads(self, request, pk=None):
        """Get ads in this category"""
        category = self.get_object()
        ads = ClassifiedAd.objects.filter(
            category=category, status='active'
        ).order_by('-created_at')

        # Apply filters
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        city = request.query_params.get('city')

        if min_price:
            ads = ads.filter(price__gte=min_price)
        if max_price:
            ads = ads.filter(price__lte=max_price)
        if city:
            ads = ads.filter(city=city)

        page = self.paginate_queryset(ads)
        if page is not None:
            serializer = ClassifiedAdListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ClassifiedAdListSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def root_categories(self, request):
        """Get only root categories"""
        categories = Category.objects.filter(parent__isnull=True)
        section_type = request.query_params.get('section_type')
        if section_type:
            categories = categories.filter(section_type=section_type)

        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


# ==================== ClassifiedAd ViewSets ====================

class ClassifiedAdViewSet(viewsets.ModelViewSet):
    """
    Classified ads CRUD endpoint
    """
    queryset = ClassifiedAd.objects.filter(status='active')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'country', 'city', 'status', 'is_highlighted', 'is_urgent', 'is_pinned']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'views_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ClassifiedAdCreateSerializer
        elif self.action == 'retrieve':
            return ClassifiedAdDetailSerializer
        return ClassifiedAdListSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdOwnerOrReadOnly()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by user's ads (if authenticated)
        my_ads = self.request.query_params.get('my_ads')
        if my_ads and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving ad"""
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        """Add/remove ad from favorites"""
        ad = self.get_object()
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, ad=ad).first()
        if wishlist_item:
            wishlist_item.delete()
            return Response({'status': 'removed', 'message': 'Ad removed from favorites'})
        else:
            WishlistItem.objects.create(wishlist=wishlist, ad=ad)
            return Response({'status': 'added', 'message': 'Ad added to favorites'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, pk=None):
        """Add review to ad"""
        ad = self.get_object()
        serializer = AdReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ad=ad, reviewer=request.user)

        # Update ad average rating
        ad.update_rating()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured ads"""
        ads = self.get_queryset().filter(is_featured=True)[:10]
        serializer = ClassifiedAdListSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent ads"""
        ads = self.get_queryset().filter(is_urgent=True)[:10]
        serializer = ClassifiedAdListSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent ads"""
        ads = self.get_queryset()[:20]
        serializer = ClassifiedAdListSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_ads(self, request):
        """Get current user's ads"""
        ads = ClassifiedAd.objects.filter(user=request.user).order_by('-created_at')

        page = self.paginate_queryset(ads)
        if page is not None:
            serializer = ClassifiedAdListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ClassifiedAdListSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)


# ==================== Blog ViewSets ====================

class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Blog category listing endpoint
    """
    queryset = BlogCategory.objects.filter(is_active=True)
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]
    ordering = ['order']


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Blog listing endpoint
    """
    queryset = Blog.objects.filter(is_published=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['published_date', 'views_count']
    ordering = ['-published_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogDetailSerializer
        return BlogListSerializer

    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving blog"""
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like/unlike blog post"""
        blog = self.get_object()
        if blog.likes.filter(id=request.user.id).exists():
            blog.likes.remove(request.user)
            return Response({'status': 'unliked', 'likes_count': blog.get_likes_count()})
        else:
            blog.likes.add(request.user)
            return Response({'status': 'liked', 'likes_count': blog.get_likes_count()})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        """Add comment to blog"""
        blog = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(blog=blog, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ==================== Chat ViewSets ====================

class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    Chat room management endpoint
    """
    queryset = ChatRoom.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatRoomDetailSerializer
        return ChatRoomListSerializer

    def get_queryset(self):
        """Return user's chat rooms"""
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ChatRoom.objects.none()

        user = self.request.user
        return ChatRoom.objects.filter(
            Q(publisher=user) | Q(client=user),
            is_active=True
        ).order_by('-updated_at')

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send message in chat room"""
        room = self.get_object()

        # Verify user is participant
        if request.user not in [room.publisher, room.client]:
            return Response(
                {'error': 'You are not a participant in this chat'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(room=room, sender=request.user)

        # Update room timestamp
        room.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in room as read"""
        room = self.get_object()
        room.mark_as_read(request.user)
        return Response({'status': 'success'})

    @action(detail=False, methods=['post'])
    def create_or_get(self, request):
        """Create or get existing chat room with another user about an ad"""
        ad_id = request.data.get('ad_id')

        if not ad_id:
            return Response(
                {'error': 'ad_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ad = get_object_or_404(ClassifiedAd, pk=ad_id)

        # Check if room already exists
        room = ChatRoom.objects.filter(
            publisher=ad.user,
            client=request.user,
            ad=ad,
            room_type='publisher_client'
        ).first()

        if not room:
            room = ChatRoom.objects.create(
                publisher=ad.user,
                client=request.user,
                ad=ad,
                room_type='publisher_client'
            )

        serializer = ChatRoomDetailSerializer(room, context={'request': request})
        return Response(serializer.data)


# ==================== Wishlist ViewSets ====================

class WishlistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Wishlist/Favorites endpoint
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def items(self, request):
        """Get wishlist items"""
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        items = wishlist.items.all()
        serializer = WishlistItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)


# ==================== Notification ViewSets ====================

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Notifications endpoint
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'success'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'success'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})


# ==================== Package & Payment ViewSets ====================

class AdFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ad features listing endpoint
    """
    queryset = AdFeature.objects.filter(is_active=True)
    serializer_class = AdFeatureSerializer
    permission_classes = [AllowAny]


class AdPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ad packages listing endpoint
    """
    queryset = AdPackage.objects.filter(is_active=True)
    serializer_class = AdPackageSerializer
    permission_classes = [AllowAny]
    ordering = ['order']


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Payment management endpoint
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        return Payment.objects.filter(user=self.request.user)


class UserPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User packages endpoint
    """
    serializer_class = UserPackageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return UserPackage.objects.none()
        return UserPackage.objects.filter(user=self.request.user)


# ==================== FAQ ViewSets ====================

class FAQCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    FAQ categories endpoint
    """
    queryset = FAQCategory.objects.filter(is_active=True)
    serializer_class = FAQCategorySerializer
    permission_classes = [AllowAny]
    ordering = ['order']


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    FAQ endpoint
    """
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['question', 'question_en', 'answer', 'answer_en']
    ordering = ['order']


# ==================== Safety Tips ViewSets ====================

class SafetyTipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Safety tips endpoint
    """
    queryset = SafetyTip.objects.filter(is_active=True)
    serializer_class = SafetyTipSerializer
    permission_classes = [AllowAny]
    ordering = ['order']


# ==================== Contact ViewSets ====================

class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    Contact messages endpoint
    """
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    queryset = ContactMessage.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


# ==================== Home Page ViewSets ====================

class HomeSliderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Home page slider endpoint
    """
    queryset = HomeSlider.objects.filter(is_active=True)
    serializer_class = HomeSliderSerializer
    permission_classes = [AllowAny]
    ordering = ['order']

    def get_queryset(self):
        queryset = super().get_queryset()
        country_id = self.request.query_params.get('country')
        if country_id:
            queryset = queryset.filter(
                Q(country_id=country_id) | Q(country__isnull=True)
            )
        return queryset


class WhyChooseUsFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Why choose us features endpoint
    """
    queryset = WhyChooseUsFeature.objects.filter(is_active=True)
    serializer_class = WhyChooseUsFeatureSerializer
    permission_classes = [AllowAny]
    ordering = ['order']


# ==================== Site Configuration ViewSets ====================

class SiteConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Site configuration endpoint
    """
    queryset = SiteConfiguration.objects.all()
    serializer_class = SiteConfigurationSerializer
    permission_classes = [AllowAny]


# ==================== Static Pages ViewSets ====================

class AboutPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    About page endpoint
    """
    queryset = AboutPage.objects.all()
    serializer_class = AboutPageSerializer
    permission_classes = [AllowAny]


class ContactPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Contact page endpoint
    """
    queryset = ContactPage.objects.all()
    serializer_class = ContactPageSerializer
    permission_classes = [AllowAny]


class TermsPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Terms and conditions page endpoint
    """
    queryset = TermsPage.objects.all()
    serializer_class = TermsPageSerializer
    permission_classes = [AllowAny]


class PrivacyPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Privacy policy page endpoint
    """
    queryset = PrivacyPage.objects.all()
    serializer_class = PrivacyPageSerializer
    permission_classes = [AllowAny]


# ==================== Custom Fields ViewSets ====================

class CustomFieldViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Custom fields endpoint
    """
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get custom fields for a specific category"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'category_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        category_fields = CategoryCustomField.objects.filter(category_id=category_id)
        fields = [cf.custom_field for cf in category_fields]
        serializer = self.get_serializer(fields, many=True)
        return Response(serializer.data)
