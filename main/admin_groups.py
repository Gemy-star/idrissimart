"""
Admin group constants and permission helpers.

Groups define what sections a staff (non-superuser) admin can access.
Superusers always have full access regardless of groups.

Usage:
    from main.admin_groups import can_admin, ADMIN_GROUPS

    # Check in a view
    if not can_admin(request.user, 'ads'):
        return HttpResponseForbidden()

    # In a template context (available via context processor or view mixin)
    {% if request.user|can_admin:'ads' %}
"""

from django.contrib.auth.models import Group

# ── Canonical group names ──────────────────────────────────────────────
ADMIN_GROUPS = {
    "ads":           "admin_ads",           # Approve/reject/manage classified ads
    "users":         "admin_users",         # Manage user accounts
    "accounting":    "admin_accounting",    # Payments, orders, financials
    "content":       "admin_content",       # Categories, FAQ, blog, translations, site config
    "reports":       "admin_reports",       # View-only reports and analytics
    "reviews":       "admin_reviews",       # Verification requests, user reviews
    "support":       "admin_support",       # Support chats
    "notifications": "admin_notifications", # Send / manage notifications
}

# Human-readable labels (Arabic) used in the management UI
ADMIN_GROUP_LABELS = {
    "admin_ads":           "إدارة الإعلانات",
    "admin_users":         "إدارة المستخدمين",
    "admin_accounting":    "المحاسبة والمدفوعات",
    "admin_content":       "إدارة المحتوى",
    "admin_reports":       "التقارير والإحصائيات",
    "admin_reviews":       "التحقق والمراجعات",
    "admin_support":       "الدعم الفني",
    "admin_notifications": "الإشعارات",
}

ALL_ADMIN_GROUP_NAMES = list(ADMIN_GROUPS.values())


# ── Helper functions ───────────────────────────────────────────────────

def can_admin(user, section: str) -> bool:
    """
    Return True if the user may access the given admin section.

    - Superusers always return True.
    - Staff users return True only when they belong to the matching group.
    - Anonymous / regular users return False.

    section: key from ADMIN_GROUPS dict  (e.g. 'ads', 'users', 'accounting')
             OR the full group name      (e.g. 'admin_ads')
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not user.is_staff:
        return False

    group_name = ADMIN_GROUPS.get(section, section)
    return user.groups.filter(name=group_name).exists()


def is_any_admin(user) -> bool:
    """Return True if user is superuser OR belongs to at least one admin group."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not user.is_staff:
        return False
    return user.groups.filter(name__in=ALL_ADMIN_GROUP_NAMES).exists()


def get_user_admin_groups(user):
    """Return queryset of admin Group objects the user belongs to."""
    if user.is_superuser:
        return Group.objects.filter(name__in=ALL_ADMIN_GROUP_NAMES)
    return user.groups.filter(name__in=ALL_ADMIN_GROUP_NAMES)


def get_admin_permissions_context(user) -> dict:
    """
    Build a dict of booleans for use in templates.
    Keys: can_admin_ads, can_admin_users, can_admin_accounting, ...
    Plus:  is_superadmin, is_any_admin
    """
    ctx = {"is_superadmin": user.is_superuser, "is_any_admin": is_any_admin(user)}
    for key in ADMIN_GROUPS:
        ctx[f"can_admin_{key}"] = can_admin(user, key)
    return ctx


def ensure_admin_groups_exist():
    """Create all predefined admin groups if they do not exist yet."""
    for group_name in ALL_ADMIN_GROUP_NAMES:
        Group.objects.get_or_create(name=group_name)
