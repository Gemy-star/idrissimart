import os
from django.utils.translation import gettext_lazy as _

CONSTANCE_CONFIG = {
    # Site Information
    "SITE_NAME": (
        "إدريسي مارت",
        _("Site Name"),
    ),
    "SITE_URL": (
        "https://idrissimart.com",
        _("Site URL"),
    ),
    "SITE_DESCRIPTION": (
        "منصة شاملة تجمع كافة الخدمات والمنتجات في مكان واحد",
        _("Site Description"),
    ),
    # Contact Information
    "CONTACT_EMAIL": (
        "info@idrissimart.com",
        _("Contact Email"),
    ),
    "CONTACT_PHONE": (
        "+20 11 27078236",
        _("Contact Phone"),
    ),
    "WHATSAPP_NUMBER": (
        "201127078236",
        _("WhatsApp Number (without +)"),
    ),
    # Social Media Links
    "FACEBOOK_URL": (
        "https://facebook.com/idrissimart",
        _("Facebook Page URL"),
    ),
    "TWITTER_URL": (
        "https://twitter.com/idrissimart",
        _("Twitter Profile URL"),
    ),
    "INSTAGRAM_URL": (
        "https://instagram.com/idrissimart",
        _("Instagram Profile URL"),
    ),
    "LINKEDIN_URL": (
        "https://linkedin.com/company/idrissimart",
        _("LinkedIn Company URL"),
    ),
    "YOUTUBE_URL": (
        "https://youtube.com/@idrissimart",
        _("YouTube Channel URL"),
    ),
    "TIKTOK_URL": (
        "https://tiktok.com/@idrissimart",
        _("TikTok Profile URL"),
    ),
    # Social Media Followers Count
    "FACEBOOK_FOLLOWERS": (
        "10000",
        _("Facebook Followers Count"),
    ),
    "TWITTER_FOLLOWERS": (
        "5000",
        _("Twitter Followers Count"),
    ),
    "INSTAGRAM_FOLLOWERS": (
        "15000",
        _("Instagram Followers Count"),
    ),
    "LINKEDIN_FOLLOWERS": (
        "3000",
        _("LinkedIn Followers Count"),
    ),
    "YOUTUBE_SUBSCRIBERS": (
        "2000",
        _("YouTube Subscribers Count"),
    ),
    # Saved Search Emails
    "SAVED_SEARCH_EMAIL_SUBJECT": (
        'New Ads Matching Your Search: "{search_name}"',
        _("Saved Search Email Subject"),
    ),
    "SAVED_SEARCH_FROM_EMAIL": (
        "noreply@idrissimart.com",
        _('Saved Search "From" Email Address'),
    ),
    "ENABLE_SAVED_SEARCH_NOTIFICATIONS": (
        True,
        _("Enable All Saved Search Notifications"),
        bool,
    ),
    # Global Notification Toggles
    "ENABLE_EMAIL_NOTIFICATIONS": (
        True,
        _("Enable Email Notifications (global toggle for all transactional emails)"),
        bool,
    ),
    "ENABLE_SMS_NOTIFICATIONS": (
        True,
        _("Enable SMS Notifications (global toggle for all transactional SMS, requires Twilio credentials)"),
        bool,
    ),
    # Ad Approval Emails
    "AD_APPROVAL_EMAIL_SUBJECT": (
        'Your Ad "{ad_title}" Has Been Approved!',
        _("Ad Approval Email Subject"),
    ),
    "AD_APPROVAL_FROM_EMAIL": (
        "noreply@idrissimart.com",
        _('Ad Approval "From" Email Address'),
    ),
    # Payment Settings - PayPal
    # Note: Sensitive keys are loaded from environment variables for security
    "PAYPAL_CLIENT_ID": (
        os.getenv("PAYPAL_CLIENT_ID", ""),
        _("PayPal Client ID (loaded from environment)"),
    ),
    "PAYPAL_CLIENT_SECRET": (
        os.getenv("PAYPAL_CLIENT_SECRET", ""),
        _("PayPal Client Secret (loaded from environment)"),
    ),
    "PAYPAL_MODE": (
        os.getenv("PAYPAL_MODE", "sandbox"),
        _("PayPal Mode (sandbox or live)"),
    ),
    "PAYPAL_EGP_TO_USD_RATE": (
        50.0,
        _("سعر تحويل الجنيه المصري إلى الدولار لـ PayPal (EGP per 1 USD)"),
        float,
    ),
    # Payment Settings - Paymob
    # All Paymob settings are managed exclusively via Django Admin → Constance.
    # Set real values there; the .env file is no longer used for these keys.
    "PAYMOB_API_KEY": (
        "",
        _("Paymob API Key"),
    ),
    "PAYMOB_SECRET_KEY": (
        "",
        _("Paymob Secret Key (egy_sk_...)"),
    ),
    "PAYMOB_PUBLIC_KEY": (
        "",
        _("Paymob Public Key (egy_pk_...)"),
    ),
    "PAYMOB_INTEGRATION_ID": (
        "",
        _("Paymob Integration ID (card / default)"),
    ),
    "PAYMOB_IFRAME_ID": (
        "",
        _("Paymob iFrame ID"),
    ),
    "PAYMOB_HMAC_SECRET": (
        "",
        _("Paymob HMAC Secret"),
    ),
    "PAYMOB_MASTERCARD_INTEGRATION_ID": (
        "",
        _("Paymob Mastercard Integration ID"),
    ),
    "PAYMOB_VISA_INTEGRATION_ID": (
        "",
        _("Paymob Visa Integration ID"),
    ),
    "PAYMOB_WALLET_INTEGRATION_ID": (
        "",
        _("Paymob Wallet Integration ID (Vodafone Cash / Orange Money)"),
    ),
    "PAYMOB_ENABLED": (
        True,
        _("Enable Paymob payment gateway"),
        bool,
    ),
    "PAYMOB_CURRENCY": (
        "EGP",
        _("Paymob payment currency"),
    ),
    # Payment General Settings
    # Note: ALLOW_ONLINE_PAYMENT moved to SiteConfiguration model
    "TAX_RATE": (
        15.0,
        _("نسبة الضريبة (%) - Tax Rate"),
        float,
    ),
    # Google reCAPTCHA v2 Settings
    "RECAPTCHA_SITE_KEY": (
        "6LcUMSYsAAAAAGKWlIEtHtmD7ecT5U1Vi3B098dD",
        _("Google reCAPTCHA Site Key (Public)"),
    ),
    "RECAPTCHA_SECRET_KEY": (
        "6LcUMSYsAAAAAARBEdYizpNQTn9SbrZWutEkfuPq",
        _("Google reCAPTCHA Secret Key (Private)"),
    ),
    "RECAPTCHA_ENABLED": (
        True,
        _("Enable reCAPTCHA verification on forms"),
        bool,
    ),
    # Social Authentication Settings
    "SOCIAL_AUTH_ENABLED": (
        False,
        _("Enable Social Authentication (Google, Facebook)"),
        bool,
    ),
    # Google OAuth Settings
    "GOOGLE_OAUTH_CLIENT_ID": (
        os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
        _("Google OAuth Client ID"),
    ),
    "GOOGLE_OAUTH_SECRET": (
        os.getenv("GOOGLE_OAUTH_SECRET", ""),
        _("Google OAuth Client Secret"),
    ),
    # Facebook OAuth Settings
    "FACEBOOK_APP_ID": (
        os.getenv("FACEBOOK_APP_ID", ""),
        _("Facebook App ID"),
    ),
    "FACEBOOK_APP_SECRET": (
        os.getenv("FACEBOOK_APP_SECRET", ""),
        _("Facebook App Secret"),
    ),
    # SMS Settings - Twilio
    # Note: Sensitive keys are loaded from environment variables for security
    "TWILIO_ACCOUNT_SID": (
        os.getenv("TWILIO_ACCOUNT_SID", ""),
        _("Twilio Account SID (loaded from environment)"),
    ),
    "TWILIO_AUTH_TOKEN": (
        os.getenv("TWILIO_AUTH_TOKEN", ""),
        _("Twilio Auth Token (loaded from environment)"),
    ),
    "TWILIO_PHONE_NUMBER": (
        os.getenv("TWILIO_PHONE_NUMBER", ""),
        _("Twilio Phone Number (loaded from environment)"),
    ),
    "TWILIO_ENABLED": (
        True,
        _("Enable Twilio SMS service"),
        bool,
    ),
    "TWILIO_DEVELOPMENT_MODE": (
        os.getenv("TWILIO_DEVELOPMENT_MODE", "False").lower() == "true",
        _("تفعيل وضع التطوير (يطبع OTP في الكونسول بدلاً من إرساله)"),
        bool,
    ),
    # Security Settings
    "ENABLE_MOBILE_VERIFICATION": (
        True,
        _("Enable Mobile Number Verification"),
        bool,
    ),
    "ENABLE_EMAIL_VERIFICATION": (
        True,
        _("Enable Email Verification during registration"),
        bool,
    ),
    "OTP_EXPIRY_MINUTES": (
        10,
        _("OTP Expiry Time (minutes)"),
        int,
    ),
    "MAX_OTP_ATTEMPTS": (
        3,
        _("Maximum OTP Attempts"),
        int,
    ),
    # Verification Settings
    # Note: Verification settings moved to SiteConfiguration model for better multi-language support
    # and to avoid duplication. Use SiteConfiguration instead of constance for:
    # - require_email_verification
    # - require_phone_verification
    # - require_verification_for_services
    # - require_verification_for_free_package
    # - verification_services_message / verification_services_message_ar
    # Publishing Settings
    "PUBLISHING_MODE": (
        "direct",
        _("Publishing Mode (direct or review)"),
    ),
    "VERIFIED_AUTO_PUBLISH": (
        True,
        _("Auto-publish ads from verified users"),
        bool,
    ),
    "ALLOW_GUEST_VIEWING": (
        True,
        _("Allow guest users to view ads"),
        bool,
    ),
    "ALLOW_GUEST_CONTACT": (
        False,
        _("Allow guest users to contact sellers"),
        bool,
    ),
    "MEMBERS_ONLY_CONTACT": (
        True,
        _("Only members can contact sellers"),
        bool,
    ),
    "MEMBERS_ONLY_MESSAGING": (
        True,
        _("Only members can use messaging"),
        bool,
    ),
    # Delivery Settings
    "DELIVERY_SERVICE_ENABLED": (
        True,
        _("Enable delivery service"),
        bool,
    ),
    "DELIVERY_REQUIRES_APPROVAL": (
        True,
        _("Delivery requests require admin approval"),
        bool,
    ),
    "DELIVERY_FEE_PERCENTAGE": (
        5,
        _("Delivery fee percentage"),
        int,
    ),
    "DELIVERY_FEE_MIN": (
        10,
        _("Minimum delivery fee"),
        int,
    ),
    "DELIVERY_FEE_MAX": (
        500,
        _("Maximum delivery fee"),
        int,
    ),
    # Cart & Reservation Settings
    "CART_SYSTEM_ENABLED": (
        True,
        _("Enable cart system"),
        bool,
    ),
    "CART_BY_MAIN_CATEGORY": (
        False,
        _("Enable cart per main category"),
        bool,
    ),
    "CART_BY_SUBCATEGORY": (
        True,
        _("Enable cart per subcategory"),
        bool,
    ),
    "CART_PER_AD": (
        True,
        _("Enable cart per individual ad"),
        bool,
    ),
    "DEFAULT_RESERVATION_PERCENTAGE": (
        20,
        _("Default reservation percentage"),
        int,
    ),
    "MIN_RESERVATION_AMOUNT": (
        50,
        _("Minimum reservation amount"),
        int,
    ),
    "MAX_RESERVATION_AMOUNT": (
        5000,
        _("Maximum reservation amount"),
        int,
    ),
    # Ad Upgrade Pricing (7 Days)
    "FEATURED_AD_PRICE_7DAYS": (
        50.00,
        _("Featured ad price for 7 days (EGP)"),
        float,
    ),
    "PINNED_AD_PRICE_7DAYS": (
        75.00,
        _("Pinned ad price for 7 days (EGP)"),
        float,
    ),
    "URGENT_AD_PRICE_7DAYS": (
        30.00,
        _("Urgent ad price for 7 days (EGP)"),
        float,
    ),
    # Ad Upgrade Pricing (14 Days)
    "FEATURED_AD_PRICE_14DAYS": (
        80.00,
        _("Featured ad price for 14 days (EGP)"),
        float,
    ),
    "PINNED_AD_PRICE_14DAYS": (
        120.00,
        _("Pinned ad price for 14 days (EGP)"),
        float,
    ),
    "URGENT_AD_PRICE_14DAYS": (
        48.00,
        _("Urgent ad price for 14 days (EGP)"),
        float,
    ),
    # Ad Upgrade Pricing (30 Days)
    "FEATURED_AD_PRICE_30DAYS": (
        100.00,
        _("Featured ad price for 30 days (EGP)"),
        float,
    ),
    "PINNED_AD_PRICE_30DAYS": (
        150.00,
        _("Pinned ad price for 30 days (EGP)"),
        float,
    ),
    "URGENT_AD_PRICE_30DAYS": (
        60.00,
        _("Urgent ad price for 30 days (EGP)"),
        float,
    ),
    # Ad Upgrade Pricing — Top Search
    "TOP_SEARCH_AD_PRICE_7DAYS": (
        60.00,
        _("Top search placement price for 7 days (EGP)"),
        float,
    ),
    "TOP_SEARCH_AD_PRICE_14DAYS": (
        96.00,
        _("Top search placement price for 14 days (EGP)"),
        float,
    ),
    "TOP_SEARCH_AD_PRICE_30DAYS": (
        120.00,
        _("Top search placement price for 30 days (EGP)"),
        float,
    ),
    # Ad Upgrade Pricing — Contact for Price
    "CONTACT_PRICE_AD_PRICE_7DAYS": (
        25.00,
        _("Contact-for-price upgrade price for 7 days (EGP)"),
        float,
    ),
    "CONTACT_PRICE_AD_PRICE_14DAYS": (
        40.00,
        _("Contact-for-price upgrade price for 14 days (EGP)"),
        float,
    ),
    "CONTACT_PRICE_AD_PRICE_30DAYS": (
        50.00,
        _("Contact-for-price upgrade price for 30 days (EGP)"),
        float,
    ),
    # Paid Banner — Multi-country extra fees
    "PAID_BANNER_EXTRA_COUNTRY_FEE_PER_DAY": (
        20.00,
        _("Extra fee per day for each additional country on a paid banner (EGP)"),
        float,
    ),
    # Ad Upgrade Pricing — One-time features
    "FACEBOOK_SHARE_AD_PRICE": (
        35.00,
        _("Facebook share upgrade price — one-time (EGP)"),
        float,
    ),
    "VIDEO_AD_PRICE": (
        45.00,
        _("Video feature upgrade price — one-time (EGP)"),
        float,
    ),
    # Ad Feature Prices at Creation Time (used when user has no free ads remaining)
    "FEATURE_HIGHLIGHTED_PRICE": (
        50.00,
        _("Featured/highlighted ad price at creation (EGP)"),
        float,
    ),
    "FEATURE_URGENT_PRICE": (
        30.00,
        _("Urgent ad price at creation (EGP)"),
        float,
    ),
    "FEATURE_PINNED_PRICE": (
        75.00,
        _("Pinned ad price at creation (EGP)"),
        float,
    ),
    "FEATURE_AUTO_REFRESH_PRICE": (
        35.00,
        _("Auto-refresh ad price at creation (EGP)"),
        float,
    ),
    "FEATURE_ADD_VIDEO_PRICE": (
        25.00,
        _("Add video to ad price at creation (EGP)"),
        float,
    ),
    "FEATURE_CONTACT_FOR_PRICE": (
        0.00,
        _("Contact-for-price ad feature price at creation (EGP)"),
        float,
    ),
    # Admin Notification Settings
    "NOTIFY_ADMIN_NEW_ADS": (
        True,
        _("Notify admin of new ads"),
        bool,
    ),
    "NOTIFY_ADMIN_PENDING_REVIEW": (
        True,
        _("Notify admin of pending reviews"),
        bool,
    ),
    "NOTIFY_ADMIN_NEW_USERS": (
        True,
        _("Notify admin of new user registrations"),
        bool,
    ),
    "NOTIFY_ADMIN_PAYMENTS": (
        True,
        _("Notify admin of payments"),
        bool,
    ),
    "ADMIN_NOTIFICATION_EMAIL": (
        "admin@idrissimart.com",
        _("Admin notification email address"),
    ),
    "SITE_NAME_IN_EMAILS": (
        "إدريسي مارت",
        _("Site name in email communications"),
    ),
    "ADS_NOTIFICATION_FREQUENCY": (
        "hourly",
        _("Ads notification frequency (hourly/daily/weekly)"),
    ),
    "STATS_REPORT_FREQUENCY": (
        "daily",
        _("Statistics report frequency (daily/weekly/monthly)"),
    ),
    # User Registration Settings
    "ENABLE_SERVICE_PROVIDER_REGISTRATION": (
        False,
        _("Enable Service Provider registration type"),
        bool,
    ),
    "ENABLE_MERCHANT_REGISTRATION": (
        False,
        _("Enable Merchant registration type"),
        bool,
    ),
    "ENABLE_EDUCATIONAL_REGISTRATION": (
        False,
        _("Enable Educational registration type"),
        bool,
    ),
    # User Verification Payment Settings
    "VERIFICATION_FEE_ENABLED": (
        False,
        _("Enable verification fee requirement"),
        bool,
    ),
    "VERIFICATION_FEE_AMOUNT": (
        100.00,
        _("Verification fee amount"),
        float,
    ),
    "VERIFICATION_FEE_CURRENCY": (
        "EGP",
        _("Verification fee currency code"),
    ),
    "VERIFICATION_AUTO_APPROVE_ON_PAYMENT": (
        False,
        _("Auto-approve verification requests after successful payment"),
        bool,
    ),
    "VERIFICATION_REVIEW_PERIOD_DAYS": (
        3,
        _("Number of days to review verification requests"),
        int,
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Site Information": (
        "SITE_NAME",
        "SITE_URL",
        "SITE_DESCRIPTION",
    ),
    "Contact Information": (
        "CONTACT_EMAIL",
        "CONTACT_PHONE",
        "WHATSAPP_NUMBER",
    ),
    "Social Media Links": (
        "FACEBOOK_URL",
        "TWITTER_URL",
        "INSTAGRAM_URL",
        "LINKEDIN_URL",
        "YOUTUBE_URL",
        "TIKTOK_URL",
    ),
    "Social Media Stats": (
        "FACEBOOK_FOLLOWERS",
        "TWITTER_FOLLOWERS",
        "INSTAGRAM_FOLLOWERS",
        "LINKEDIN_FOLLOWERS",
        "YOUTUBE_SUBSCRIBERS",
    ),
    "Email Settings": (
        "ENABLE_EMAIL_NOTIFICATIONS",
        "SAVED_SEARCH_EMAIL_SUBJECT",
        "SAVED_SEARCH_FROM_EMAIL",
        "ENABLE_SAVED_SEARCH_NOTIFICATIONS",
        "AD_APPROVAL_EMAIL_SUBJECT",
        "AD_APPROVAL_FROM_EMAIL",
    ),
    "SMS Settings - Global": (
        "ENABLE_SMS_NOTIFICATIONS",
    ),
    "Payment Settings - PayPal": (
        "PAYPAL_CLIENT_ID",
        "PAYPAL_CLIENT_SECRET",
        "PAYPAL_MODE",
        "PAYPAL_EGP_TO_USD_RATE",
    ),
    "Payment Settings - Paymob": (
        "PAYMOB_ENABLED",
        "PAYMOB_CURRENCY",
        "PAYMOB_API_KEY",
        "PAYMOB_SECRET_KEY",
        "PAYMOB_PUBLIC_KEY",
        "PAYMOB_INTEGRATION_ID",
        "PAYMOB_IFRAME_ID",
        "PAYMOB_HMAC_SECRET",
        "PAYMOB_MASTERCARD_INTEGRATION_ID",
        "PAYMOB_VISA_INTEGRATION_ID",
        "PAYMOB_WALLET_INTEGRATION_ID",
    ),
    "Payment General Settings": ("TAX_RATE",),
    "Security & Verification - reCAPTCHA": (
        "RECAPTCHA_ENABLED",
        "RECAPTCHA_SITE_KEY",
        "RECAPTCHA_SECRET_KEY",
    ),
    "Social Authentication": (
        "SOCIAL_AUTH_ENABLED",
        "GOOGLE_OAUTH_CLIENT_ID",
        "GOOGLE_OAUTH_SECRET",
        "FACEBOOK_APP_ID",
        "FACEBOOK_APP_SECRET",
    ),
    "SMS Settings - Twilio": (
        "TWILIO_ENABLED",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "TWILIO_DEVELOPMENT_MODE",
    ),
    "Security Settings": (
        "ENABLE_MOBILE_VERIFICATION",
        "ENABLE_EMAIL_VERIFICATION",
        "OTP_EXPIRY_MINUTES",
        "MAX_OTP_ATTEMPTS",
    ),
    # Note: Verification Settings section removed - now in SiteConfiguration model
    "Publishing Settings": (
        "PUBLISHING_MODE",
        "VERIFIED_AUTO_PUBLISH",
        "ALLOW_GUEST_VIEWING",
        "ALLOW_GUEST_CONTACT",
        "MEMBERS_ONLY_CONTACT",
        "MEMBERS_ONLY_MESSAGING",
    ),
    "Delivery Settings": (
        "DELIVERY_SERVICE_ENABLED",
        "DELIVERY_REQUIRES_APPROVAL",
        "DELIVERY_FEE_PERCENTAGE",
        "DELIVERY_FEE_MIN",
        "DELIVERY_FEE_MAX",
    ),
    "Cart & Reservation Settings": (
        "CART_SYSTEM_ENABLED",
        "CART_BY_MAIN_CATEGORY",
        "CART_BY_SUBCATEGORY",
        "CART_PER_AD",
        "DEFAULT_RESERVATION_PERCENTAGE",
        "MIN_RESERVATION_AMOUNT",
        "MAX_RESERVATION_AMOUNT",
    ),
    "Paid Banner Ads": (
        "PAID_BANNER_EXTRA_COUNTRY_FEE_PER_DAY",
    ),
    "Ad Upgrade Pricing": (
        "FEATURED_AD_PRICE_7DAYS",
        "FEATURED_AD_PRICE_14DAYS",
        "FEATURED_AD_PRICE_30DAYS",
        "PINNED_AD_PRICE_7DAYS",
        "PINNED_AD_PRICE_14DAYS",
        "PINNED_AD_PRICE_30DAYS",
        "URGENT_AD_PRICE_7DAYS",
        "URGENT_AD_PRICE_14DAYS",
        "URGENT_AD_PRICE_30DAYS",
        "TOP_SEARCH_AD_PRICE_7DAYS",
        "TOP_SEARCH_AD_PRICE_14DAYS",
        "TOP_SEARCH_AD_PRICE_30DAYS",
        "CONTACT_PRICE_AD_PRICE_7DAYS",
        "CONTACT_PRICE_AD_PRICE_14DAYS",
        "CONTACT_PRICE_AD_PRICE_30DAYS",
        "FACEBOOK_SHARE_AD_PRICE",
        "VIDEO_AD_PRICE",
    ),
    "Ad Feature Prices (Creation — no free ads)": (
        "FEATURE_HIGHLIGHTED_PRICE",
        "FEATURE_URGENT_PRICE",
        "FEATURE_PINNED_PRICE",
        "FEATURE_AUTO_REFRESH_PRICE",
        "FEATURE_ADD_VIDEO_PRICE",
        "FEATURE_CONTACT_FOR_PRICE",
    ),
    "Admin Notifications": (
        "NOTIFY_ADMIN_NEW_ADS",
        "NOTIFY_ADMIN_PENDING_REVIEW",
        "NOTIFY_ADMIN_NEW_USERS",
        "NOTIFY_ADMIN_PAYMENTS",
        "ADMIN_NOTIFICATION_EMAIL",
        "SITE_NAME_IN_EMAILS",
        "ADS_NOTIFICATION_FREQUENCY",
        "STATS_REPORT_FREQUENCY",
    ),
    "User Registration": (
        "ENABLE_SERVICE_PROVIDER_REGISTRATION",
        "ENABLE_MERCHANT_REGISTRATION",
        "ENABLE_EDUCATIONAL_REGISTRATION",
    ),
    "Verification Payment Settings": (
        "VERIFICATION_FEE_ENABLED",
        "VERIFICATION_FEE_AMOUNT",
        "VERIFICATION_FEE_CURRENCY",
        "VERIFICATION_AUTO_APPROVE_ON_PAYMENT",
        "VERIFICATION_REVIEW_PERIOD_DAYS",
    ),
}
