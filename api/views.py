"""
API ViewSets for mobile application
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import logging

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
    ForgotPasswordSerializer, ResetPasswordSerializer,
    SendOTPSerializer, VerifyOTPSerializer,
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
    PaymentInitiateSerializer, PaymentMethodSerializer, PayPalCaptureSerializer,
    UploadReceiptSerializer,
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
    # Home content serializer
    HomePageSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdOwnerOrReadOnly, IsPublisherOrClient
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
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
    permission_classes = [AllowAny]
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
    Payment management endpoints.

    Supports all payment providers: Paymob (card/wallet), PayPal,
    Bank Transfer, Mobile Wallet, and InstaPay.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

    # ------------------------------------------------------------------
    # GET /payments/methods/
    # ------------------------------------------------------------------

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def methods(self, request):
        """
        Return available payment methods for a given context.

        Query parameters:
          - context: ad_posting | ad_upgrade | package_purchase | product_purchase
        """
        from main.payment_utils import get_allowed_payment_methods
        context = request.query_params.get('context', 'ad_posting')
        allowed = get_allowed_payment_methods(context)
        data = [{'code': code, 'label': str(label)} for code, label in allowed]
        serializer = PaymentMethodSerializer(data, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------------
    # POST /payments/initiate/
    # ------------------------------------------------------------------

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated],
            parser_classes=[JSONParser, MultiPartParser, FormParser])
    def initiate(self, request):
        """
        Initiate a payment with any supported provider.

        **Paymob** — returns `checkout_url` to redirect/open in WebView.
        **PayPal**  — returns `approval_url` to redirect/open in WebView.
        **Offline** (bank_transfer / wallet / instapay) — creates a pending Payment
          record; use `POST /payments/{id}/upload_receipt/` to attach the receipt.
        """
        serializer = PaymentInitiateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        provider = data['provider']
        amount = data['amount']
        currency = data['currency']
        description = data.get('description', '')
        metadata = data.get('metadata', {})

        # Validate method is allowed for the given context
        from main.payment_utils import get_allowed_payment_methods, is_payment_method_allowed
        context = data.get('context', 'ad_posting')
        if not is_payment_method_allowed(provider, context):
            return Response(
                {'error': f"Payment method '{provider}' is not available for context '{context}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a pending Payment record
        payment = Payment.objects.create(
            user=request.user,
            provider=provider if provider in ['paymob', 'paypal', 'bank_transfer'] else 'bank_transfer',
            amount=amount,
            currency=currency,
            status=Payment.PaymentStatus.PENDING,
            description=description,
            metadata={**metadata, 'context': context, 'provider_input': provider},
        )

        # --- Paymob ---
        if provider == 'paymob':
            from main.services.paymob_service import PaymobService
            if not PaymobService.is_enabled():
                payment.mark_failed('Paymob gateway disabled')
                return Response({'error': 'Paymob payment gateway is not configured.'},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)

            billing_data = data.get('billing_data') or {}
            # Enrich billing from user profile if missing
            user = request.user
            billing_data.setdefault('first_name', user.first_name or user.username)
            billing_data.setdefault('last_name', user.last_name or 'N/A')
            billing_data.setdefault('email', user.email or 'noreply@example.com')
            billing_data.setdefault('phone_number', getattr(user, 'phone', None) or getattr(user, 'mobile', None) or 'N/A')
            billing_data.setdefault('city', getattr(user, 'city', None) or 'N/A')
            billing_data.setdefault('country', 'EG')

            success, checkout_url, error, intention_id = PaymobService.process_payment(
                amount=amount,
                order_id=str(payment.id),
                billing_data=billing_data,
                notification_url=data.get('notification_url') or None,
                redirection_url=data.get('redirection_url') or None,
            )

            if not success:
                payment.mark_failed(error)
                return Response({'error': error}, status=status.HTTP_502_BAD_GATEWAY)

            if intention_id:
                payment.provider_transaction_id = intention_id
                payment.save(update_fields=['provider_transaction_id'])

            return Response({
                'payment_id': payment.id,
                'provider': 'paymob',
                'status': payment.status,
                'checkout_url': checkout_url,
            }, status=status.HTTP_201_CREATED)

        # --- PayPal ---
        elif provider == 'paypal':
            from main.services.paypal_service import PayPalService
            if not PayPalService.is_enabled():
                payment.mark_failed('PayPal gateway disabled')
                return Response({'error': 'PayPal payment gateway is not configured.'},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)

            success, order_data, error = PayPalService.create_order(
                amount=amount,
                currency=currency,
                order_id=str(payment.id),
                description=description,
                return_url=data.get('return_url') or None,
                cancel_url=data.get('cancel_url') or None,
            )

            if not success:
                payment.mark_failed(error)
                return Response({'error': error}, status=status.HTTP_502_BAD_GATEWAY)

            paypal_order_id = order_data.get('id')
            approval_url = next(
                (link['href'] for link in order_data.get('links', []) if link['rel'] == 'approve'),
                None,
            )

            payment.provider_transaction_id = paypal_order_id or ''
            payment.save(update_fields=['provider_transaction_id'])

            return Response({
                'payment_id': payment.id,
                'provider': 'paypal',
                'status': payment.status,
                'paypal_order_id': paypal_order_id,
                'approval_url': approval_url,
            }, status=status.HTTP_201_CREATED)

        # --- Offline methods: bank_transfer, wallet, instapay ---
        else:
            # Map provider label for the Payment model (stored as bank_transfer for all offline)
            payment.metadata['offline_method'] = provider
            payment.save(update_fields=['metadata'])
            return Response({
                'payment_id': payment.id,
                'provider': provider,
                'status': payment.status,
                'message': 'Payment record created. Please upload your receipt using POST /payments/{id}/upload_receipt/',
            }, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # POST /payments/{id}/upload_receipt/
    # ------------------------------------------------------------------

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated],
            parser_classes=[MultiPartParser, FormParser])
    def upload_receipt(self, request, pk=None):
        """
        Upload an offline payment receipt (image).
        Only the payment owner can upload.
        """
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        if payment.status not in [Payment.PaymentStatus.PENDING]:
            return Response(
                {'error': 'Receipt can only be uploaded for pending payments.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UploadReceiptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment.offline_payment_receipt = serializer.validated_data['receipt']
        payment.save(update_fields=['offline_payment_receipt'])
        return Response(PaymentSerializer(payment, context={'request': request}).data)

    # ------------------------------------------------------------------
    # POST /payments/paypal/capture/
    # ------------------------------------------------------------------

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated],
            url_path='paypal/capture')
    def paypal_capture(self, request):
        """
        Capture an approved PayPal order.
        Call this after the buyer is redirected back from PayPal's approval page.
        """
        serializer = PayPalCaptureSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment_id = serializer.validated_data['payment_id']
        paypal_order_id = serializer.validated_data['paypal_order_id']

        payment = get_object_or_404(Payment, pk=payment_id, user=request.user)

        if payment.status == Payment.PaymentStatus.COMPLETED:
            return Response(PaymentSerializer(payment, context={'request': request}).data)

        from main.services.paypal_service import PayPalService
        success, capture_data, error = PayPalService.capture_order(paypal_order_id)

        if not success:
            payment.mark_failed(error)
            return Response({'error': error}, status=status.HTTP_502_BAD_GATEWAY)

        capture_id = None
        try:
            capture_id = capture_data['purchase_units'][0]['payments']['captures'][0]['id']
        except (KeyError, IndexError, TypeError):
            pass

        payment.mark_completed(transaction_id=capture_id or paypal_order_id)
        return Response(PaymentSerializer(payment, context={'request': request}).data)

    # ------------------------------------------------------------------
    # GET /payments/{id}/status/
    # ------------------------------------------------------------------

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def payment_status(self, request, pk=None):
        """Get the current status of a payment."""
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        return Response({
            'payment_id': payment.id,
            'status': payment.status,
            'provider': payment.provider,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'provider_transaction_id': payment.provider_transaction_id,
            'created_at': payment.created_at,
            'completed_at': payment.completed_at,
        })


# ==================== Paymob Callback (Webhook) ====================

class PaymobCallbackView(APIView):
    """
    Webhook endpoint for Paymob transaction callbacks.
    No authentication required — validated via HMAC signature.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from main.services.paymob_service import PaymobService

        data = request.data
        if not PaymobService.verify_hmac(data):
            logger.warning("Paymob callback: HMAC verification failed")
            return Response({'error': 'Invalid HMAC'}, status=status.HTTP_400_BAD_REQUEST)

        success = str(data.get('success', '')).lower() == 'true'
        merchant_order_id = data.get('extras', {}).get('merchant_order_id') or data.get('order', {}).get('merchant_order_id')
        transaction_id = str(data.get('id', ''))

        if merchant_order_id:
            try:
                payment = Payment.objects.get(pk=int(merchant_order_id))
                if success:
                    payment.mark_completed(transaction_id=transaction_id)
                    logger.info(f"Paymob payment {payment.id} marked completed via callback")
                else:
                    payment.mark_failed(reason=data.get('data', {}).get('message', 'Payment failed'))
                    logger.info(f"Paymob payment {payment.id} marked failed via callback")
            except (Payment.DoesNotExist, ValueError):
                logger.error(f"Paymob callback: Payment not found for merchant_order_id={merchant_order_id}")

        return Response({'status': 'received'})

    def get(self, request):
        """Paymob sometimes sends GET callbacks with query params."""
        return self.post(request)


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


# ==================== Home Content API View ====================

class HomeAPIView(APIView):
    """
    Single endpoint that returns all data needed to render the home page.

    Query Parameters:
        country (str): Country code (e.g. "EG"). Falls back to "EG" if omitted.
        latest_ads_limit (int): Max number of latest ads to return (default 20).
        featured_ads_limit (int): Max number of featured ads to return (default 20).
        blogs_limit (int): Max number of latest blogs to return (default 10).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from content.site_config import HomePage
        from content.models import HomeSlider, WhyChooseUsFeature, Blog
        from main.utils import get_selected_country_from_request

        # Resolve country: prefer explicit query param, then request middleware/session
        country_code = request.query_params.get('country') or get_selected_country_from_request(request)

        # Limits
        try:
            latest_limit = int(request.query_params.get('latest_ads_limit', 20))
            featured_limit = int(request.query_params.get('featured_ads_limit', 20))
            blogs_limit = int(request.query_params.get('blogs_limit', 10))
        except (ValueError, TypeError):
            latest_limit = featured_limit = 20
            blogs_limit = 10

        # HomePage singleton
        home_page = HomePage.get_solo()

        # Sliders filtered by country (include global sliders with no country)
        sliders = HomeSlider.objects.filter(is_active=True).filter(
            Q(country__code=country_code) | Q(country__isnull=True)
        ).order_by('order')

        # Categories by section (root + level-1, active, for this country)
        categories_qs = (
            Category.objects.filter(
                section_type__isnull=False,
                country__code=country_code,
                level__lte=1,
                is_active=True,
            )
            .select_related('parent')
            .prefetch_related('subcategories')
            .order_by('section_type', 'level', 'order', 'name')
        )

        categories_by_section = {}
        for cat in categories_qs:
            section = cat.section_type
            if section not in categories_by_section:
                categories_by_section[section] = []
            if cat.level == 0:  # root only in the grouped list
                categories_by_section[section].append(cat)

        categories_data = [
            {
                'section_type': section,
                'section_name': dict(Category.SectionType.choices).get(section, section),
                'categories': CategoryDetailSerializer(
                    cats, many=True, context={'request': request}
                ).data,
            }
            for section, cats in categories_by_section.items()
        ]

        # Latest ads
        latest_ads_qs = ClassifiedAd.objects.active_for_country(country_code)[:latest_limit]

        # Featured ads (fall back to latest if empty)
        featured_ads_qs = ClassifiedAd.objects.featured_for_country(country_code)[:featured_limit]
        if not featured_ads_qs.exists():
            featured_ads_qs = ClassifiedAd.objects.active_for_country(country_code)[:featured_limit]

        # Latest blogs
        latest_blogs_qs = (
            Blog.objects.filter(is_published=True)
            .order_by('-published_date')
            .select_related('author', 'category')
        )[:blogs_limit]

        return Response({
            'home_page': HomePageSerializer(home_page, context={'request': request}).data,
            'sliders': HomeSliderSerializer(sliders, many=True, context={'request': request}).data,
            'categories_by_section': categories_data,
            'latest_ads': ClassifiedAdListSerializer(
                latest_ads_qs, many=True, context={'request': request}
            ).data,
            'featured_ads': ClassifiedAdListSerializer(
                featured_ads_qs, many=True, context={'request': request}
            ).data,
            'latest_blogs': BlogListSerializer(
                latest_blogs_qs, many=True, context={'request': request}
            ).data,
        })


# ==================== Password Reset API Views ====================

class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/

    Accepts { "email": "user@example.com" } and sends a password-reset
    email containing a uid + token pair when the address is registered.
    Always returns 200 so as not to leak whether an account exists.
    """
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer  # for Swagger

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Return success anyway to avoid email enumeration
            return Response({'detail': 'If that email is registered, a reset link has been sent.'})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        from main.services.email_service import EmailService
        from constance import config

        reset_url = f"{request.scheme}://{request.get_host()}/api/auth/reset-password/?uid={uid}&token={token}"

        html_content = f"""
        <p>Hello {user.get_full_name() or user.username},</p>
        <p>You requested a password reset for your {config.SITE_NAME} account.</p>
        <p>Use the following credentials to reset your password via the API:</p>
        <ul>
            <li><strong>uid:</strong> {uid}</li>
            <li><strong>token:</strong> {token}</li>
        </ul>
        <p>Or follow this link: <a href="{reset_url}">{reset_url}</a></p>
        <p>This link expires in 24 hours. If you did not request a reset, ignore this email.</p>
        """

        EmailService.send_email(
            to_emails=[user.email],
            subject=f"{config.SITE_NAME} - Password Reset",
            html_content=html_content,
        )

        return Response({'detail': 'If that email is registered, a reset link has been sent.'})


class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/

    Accepts { "uid": "…", "token": "…", "new_password": "…", "new_password_confirm": "…" }
    and sets the new password when the uid/token pair is valid.
    """
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer  # for Swagger

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {'detail': 'Invalid reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, serializer.validated_data['token']):
            return Response(
                {'detail': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'detail': 'Password has been reset successfully.'})


# ==================== Phone OTP Verification API Views ====================

class SendOTPView(APIView):
    """
    POST /api/auth/send-otp/

    Sends a one-time password (OTP) to the given phone number.
    Requires authentication. The phone number is saved on the user
    profile and an SMS is dispatched via the configured SMS provider.

    Request body: { "phone": "+201234567890" }
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        from main.services.mobile_verification_service import MobileVerificationService
        service = MobileVerificationService()
        success, message = service.initiate_verification(request.user, phone)

        if success:
            return Response({'detail': str(message)})
        return Response({'detail': str(message)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp/

    Verifies the OTP code previously sent to the user's phone.
    On success, the user's phone is marked as verified.

    Request body: { "otp_code": "123456" }

    GET /api/auth/verify-otp/

    Returns the current phone verification status for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyOTPSerializer

    def get(self, request):
        return Response({
            'is_mobile_verified': request.user.is_mobile_verified,
            'phone': getattr(request.user, 'mobile', None) or getattr(request.user, 'phone', None),
        })

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp_code']

        from main.services.mobile_verification_service import MobileVerificationService
        service = MobileVerificationService()
        success, message = service.verify_mobile_for_ad(request.user, otp_code)

        if success:
            return Response({
                'detail': str(message),
                'is_mobile_verified': True,
            })
        return Response({'detail': str(message)}, status=status.HTTP_400_BAD_REQUEST)
