from django.utils.translation import gettext_lazy as _

CONSTANCE_CONFIG = {
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
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Email Settings": (
        "SAVED_SEARCH_EMAIL_SUBJECT",
        "SAVED_SEARCH_FROM_EMAIL",
        "ENABLE_SAVED_SEARCH_NOTIFICATIONS",
        "AD_APPROVAL_EMAIL_SUBJECT",
        "AD_APPROVAL_FROM_EMAIL",
    ),
}
