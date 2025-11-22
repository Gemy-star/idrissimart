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
    "PAYPAL_CLIENT_ID": (
        "AQnjmPBtvIVbTH0Ims4qnmEMVXZ-NcI3aNugVKmEkHIKi7tbJQYIfl4OSPrhd6_w9tfNIn_LDjWD1foq",
        _("PayPal Client ID"),
    ),
    "PAYPAL_CLIENT_SECRET": (
        "EJmH3ZcwaNpD-Mesof6fcMQws8JRDRJwdiVrb85NY_uxqyjUNaJYaPuZrIi46wnybdb38tWH_1UWwYYr",
        _("PayPal Client Secret"),
    ),
    "PAYPAL_MODE": (
        "sandbox",
        _("PayPal Mode (sandbox or live)"),
    ),
    # Payment Settings - Paymob
    "PAYMOB_API_KEY": (
        "",
        _("Paymob API Key"),
    ),
    "PAYMOB_INTEGRATION_ID": (
        "",
        _("Paymob Integration ID"),
    ),
    "PAYMOB_IFRAME_ID": (
        "",
        _("Paymob iFrame ID"),
    ),
    "PAYMOB_MASTERCARD_INTEGRATION_ID": (
        "",
        _("Paymob Mastercard Integration ID"),
    ),
    "PAYMOB_VISA_INTEGRATION_ID": (
        "",
        _("Paymob Visa Integration ID"),
    ),
    # SMS Settings - Twilio
    "TWILIO_ACCOUNT_SID": (
        "ACbda2c87d81ac899a614f26b69c25c8af",
        _("Twilio Account SID"),
    ),
    "TWILIO_AUTH_TOKEN": (
        "f8cad167753ac2bacca2c70db8a4f541",
        _("Twilio Auth Token"),
    ),
    "TWILIO_PHONE_NUMBER": (
        "+12605822569",
        _("Twilio Phone Number"),
    ),
    "TWILIO_DEVELOPMENT_MODE": (
        False,
        _("تفعيل وضع التطوير (يطبع OTP في الكونسول بدلاً من إرساله)"),
        bool,
    ),
    # Security Settings
    "ENABLE_MOBILE_VERIFICATION": (
        True,
        _("Enable Mobile Number Verification"),
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
        _("Featured ad price for 7 days (SAR)"),
        float,
    ),
    "PINNED_AD_PRICE_7DAYS": (
        75.00,
        _("Pinned ad price for 7 days (SAR)"),
        float,
    ),
    "URGENT_AD_PRICE_7DAYS": (
        30.00,
        _("Urgent ad price for 7 days (SAR)"),
        float,
    ),
    # Ad Upgrade Pricing (14 Days)
    "FEATURED_AD_PRICE_14DAYS": (
        80.00,
        _("Featured ad price for 14 days (SAR)"),
        float,
    ),
    "PINNED_AD_PRICE_14DAYS": (
        120.00,
        _("Pinned ad price for 14 days (SAR)"),
        float,
    ),
    "URGENT_AD_PRICE_14DAYS": (
        48.00,
        _("Urgent ad price for 14 days (SAR)"),
        float,
    ),
    # Ad Upgrade Pricing (30 Days)
    "FEATURED_AD_PRICE_30DAYS": (
        100.00,
        _("Featured ad price for 30 days (SAR)"),
        float,
    ),
    "PINNED_AD_PRICE_30DAYS": (
        150.00,
        _("Pinned ad price for 30 days (SAR)"),
        float,
    ),
    "URGENT_AD_PRICE_30DAYS": (
        60.00,
        _("Urgent ad price for 30 days (SAR)"),
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
        "SAVED_SEARCH_EMAIL_SUBJECT",
        "SAVED_SEARCH_FROM_EMAIL",
        "ENABLE_SAVED_SEARCH_NOTIFICATIONS",
        "AD_APPROVAL_EMAIL_SUBJECT",
        "AD_APPROVAL_FROM_EMAIL",
    ),
    "Payment Settings - PayPal": (
        "PAYPAL_CLIENT_ID",
        "PAYPAL_CLIENT_SECRET",
        "PAYPAL_MODE",
    ),
    "Payment Settings - Paymob": (
        "PAYMOB_API_KEY",
        "PAYMOB_INTEGRATION_ID",
        "PAYMOB_IFRAME_ID",
        "PAYMOB_MASTERCARD_INTEGRATION_ID",
        "PAYMOB_VISA_INTEGRATION_ID",
    ),
    "SMS Settings - Twilio": (
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "TWILIO_DEVELOPMENT_MODE",
    ),
    "Security Settings": (
        "ENABLE_MOBILE_VERIFICATION",
        "OTP_EXPIRY_MINUTES",
        "MAX_OTP_ATTEMPTS",
    ),
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
        "FEATURED_AD_PRICE_7DAYS",
        "PINNED_AD_PRICE_7DAYS",
        "URGENT_AD_PRICE_7DAYS",
        "FEATURED_AD_PRICE_14DAYS",
        "PINNED_AD_PRICE_14DAYS",
        "URGENT_AD_PRICE_14DAYS",
        "FEATURED_AD_PRICE_30DAYS",
        "PINNED_AD_PRICE_30DAYS",
        "URGENT_AD_PRICE_30DAYS",
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
}
