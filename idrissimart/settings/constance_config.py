from django.utils.translation import gettext_lazy as _

CONSTANCE_CONFIG = {
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
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Email Settings": (
        "SAVED_SEARCH_EMAIL_SUBJECT",
        "SAVED_SEARCH_FROM_EMAIL",
        "ENABLE_SAVED_SEARCH_NOTIFICATIONS",
    ),
}
