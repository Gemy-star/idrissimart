"""
API URL Configuration
"""
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    # User ViewSets
    UserViewSet,
    # Password reset views
    ForgotPasswordView, ResetPasswordView,
    # Country ViewSets
    CountryViewSet,
    # Category ViewSets
    CategoryViewSet,
    # Ad ViewSets
    ClassifiedAdViewSet,
    # Blog ViewSets
    BlogCategoryViewSet, BlogViewSet,
    # Chat ViewSets
    ChatRoomViewSet,
    # Wishlist ViewSets
    WishlistViewSet,
    # Notification ViewSets
    NotificationViewSet,
    # Package & Payment ViewSets
    AdFeatureViewSet, AdPackageViewSet, PaymentViewSet, UserPackageViewSet,
    # FAQ ViewSets
    FAQCategoryViewSet, FAQViewSet,
    # Safety Tips ViewSets
    SafetyTipViewSet,
    # Contact ViewSets
    ContactMessageViewSet,
    # Home Page ViewSets
    HomeSliderViewSet, WhyChooseUsFeatureViewSet,
    # Site Configuration ViewSets
    SiteConfigurationViewSet,
    # Static Pages ViewSets
    AboutPageViewSet, ContactPageViewSet, TermsPageViewSet, PrivacyPageViewSet,
    # Custom Fields ViewSets
    CustomFieldViewSet,
    # Home Content
    HomeAPIView,
    # Payment Callback
    PaymobCallbackView,
    # Phone OTP Verification
    SendOTPView, VerifyOTPView,
)

app_name = 'api'

# Create router and register viewsets
router = DefaultRouter()

# User endpoints
router.register(r'users', UserViewSet, basename='user')

# Country endpoints
router.register(r'countries', CountryViewSet, basename='country')

# Category endpoints
router.register(r'categories', CategoryViewSet, basename='category')

# Classified ads endpoints
router.register(r'ads', ClassifiedAdViewSet, basename='ad')

# Blog endpoints
router.register(r'blog-categories', BlogCategoryViewSet, basename='blog-category')
router.register(r'blogs', BlogViewSet, basename='blog')

# Chat endpoints
router.register(r'chat-rooms', ChatRoomViewSet, basename='chat-room')

# Wishlist endpoints
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# Notification endpoints
router.register(r'notifications', NotificationViewSet, basename='notification')

# Package & Payment endpoints
router.register(r'ad-features', AdFeatureViewSet, basename='ad-feature')
router.register(r'ad-packages', AdPackageViewSet, basename='ad-package')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'user-packages', UserPackageViewSet, basename='user-package')

# FAQ endpoints
router.register(r'faq-categories', FAQCategoryViewSet, basename='faq-category')
router.register(r'faqs', FAQViewSet, basename='faq')

# Safety Tips endpoints
router.register(r'safety-tips', SafetyTipViewSet, basename='safety-tip')

# Contact endpoints
router.register(r'contact-messages', ContactMessageViewSet, basename='contact-message')

# Home Page endpoints
router.register(r'home-sliders', HomeSliderViewSet, basename='home-slider')
router.register(r'why-choose-us', WhyChooseUsFeatureViewSet, basename='why-choose-us')

# Site Configuration endpoints
router.register(r'site-config', SiteConfigurationViewSet, basename='site-config')

# Static Pages endpoints
router.register(r'about-page', AboutPageViewSet, basename='about-page')
router.register(r'contact-page', ContactPageViewSet, basename='contact-page')
router.register(r'terms-page', TermsPageViewSet, basename='terms-page')
router.register(r'privacy-page', PrivacyPageViewSet, basename='privacy-page')

# Custom Fields endpoints
router.register(r'custom-fields', CustomFieldViewSet, basename='custom-field')

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Idrissimart API",
        default_version='v1',
        description="""
        # Idrissimart REST API Documentation

        This API provides comprehensive endpoints for the Idrissimart classified ads platform.

        ## Authentication

        This API uses JWT (JSON Web Token) authentication. To authenticate:

        1. Obtain token: POST to `/api/auth/token/` with username and password
        2. Use the access token in the Authorization header: `Bearer {access_token}`
        3. Refresh token when expired: POST to `/api/auth/token/refresh/` with refresh token

        ## Features

        - User management and authentication
        - Classified ads CRUD operations
        - Blog posts and comments
        - Real-time chat system
        - Wishlist/favorites
        - Notifications
        - Packages and payments
        - Search and filtering
        - Multi-language support (Arabic/English)

        ## Rate Limiting

        API requests are rate-limited to prevent abuse. Default limits:
        - 100 requests per minute for authenticated users
        - 20 requests per minute for unauthenticated users

        ## Support

        For API support: support@idrissimart.com
        """,
        terms_of_service="https://www.idrissimart.com/terms/",
        contact=openapi.Contact(email="support@idrissimart.com"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Home content endpoint
    path('home/', HomeAPIView.as_view(), name='home'),

    # Payment gateway callbacks (no auth)
    path('payments/paymob/callback/', PaymobCallbackView.as_view(), name='paymob-callback'),

    # JWT token endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Password reset endpoints
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    # Phone OTP verification endpoints
    path('auth/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

    # API endpoints
    path('', include(router.urls)),
]
