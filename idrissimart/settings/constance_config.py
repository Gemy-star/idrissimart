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
        "+1234567890",
        _("Twilio Phone Number"),
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
    ),
    "SMS Settings - Twilio": (
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
    ),
    "Security Settings": (
        "ENABLE_MOBILE_VERIFICATION",
        "OTP_EXPIRY_MINUTES",
        "MAX_OTP_ATTEMPTS",
    ),
}
