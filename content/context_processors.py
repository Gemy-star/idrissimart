from content.models import Country, HomeSlider
from main.models import Notification
from constance import config
from django.db import models
from content.verification_utils import get_verification_requirements
from content.site_config import SiteConfiguration


def countries(request):
    """
    Context processor to make countries available in all templates
    """
    return {
        "countries": Country.objects.filter(is_active=True).order_by("order", "name")
    }


def home_sliders(request):
    """
    Context processor to make home sliders available in templates
    Filters sliders based on selected country
    """
    selected_country = request.session.get("selected_country", "EG")

    try:
        country = Country.objects.get(code=selected_country, is_active=True)
        # Get sliders for selected country or sliders without country (legacy/global)
        sliders = (
            HomeSlider.objects.filter(is_active=True)
            .filter(models.Q(country=country) | models.Q(country__isnull=True))
            .order_by("order")
        )
    except Country.DoesNotExist:
        # Fallback to sliders without country assignment
        sliders = HomeSlider.objects.filter(
            is_active=True, country__isnull=True
        ).order_by("order")

    return {"home_sliders": sliders}


def user_preferences(request):
    """
    Context processor for user preferences from session/cookies
    """
    selected_country = request.session.get("selected_country", "EG")

    # Get currency for selected country
    try:
        country = Country.objects.get(code=selected_country, is_active=True)
        currency = country.currency or "EGP"
    except Country.DoesNotExist:
        currency = "EGP"  # Default to EGP if country not found

    return {
        "selected_country": selected_country,
        "selected_currency": currency,
    }


def header_categories(request):
    """
    Context processor to make classified ad categories available in header
    """
    from main.models import Category

    selected_country = request.session.get("selected_country", "EG")

    # Get classified ad subcategories for the header
    # First find the classified root category, then show its children
    from django.db import models as db_models
    from content.models import Country

    try:
        country = Country.objects.get(code=selected_country, is_active=True)
        # Show main (root) categories in the header
        categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True,
            section_type="classified",
        ).filter(
            db_models.Q(country=country)
            | db_models.Q(countries=country)
            | db_models.Q(country__isnull=True, countries__isnull=True)
        ).order_by("order", "name")[:20]
    except Country.DoesNotExist:
        categories = Category.objects.none()

    return {
        "header_categories": categories,
        "config": config,
    }


def notifications(request):
    """Adds notification count to the context for authenticated users."""
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user, is_read=False
        )
        unread_count = unread_notifications.count()
        return {
            "unread_notifications_count": unread_count,
            "latest_notifications": unread_notifications[:5],
        }
    return {}


def cart_wishlist_counts(request):
    """
    Context processor to add cart and wishlist counts to all templates
    """
    if request.user.is_authenticated:
        from main.models import Cart, Wishlist

        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.get_items_count()

        # Debug logging
        print(f"[CONTEXT_PROCESSOR] User: {request.user.username}")
        print(f"[CONTEXT_PROCESSOR] Cart ID: {cart.id}, Created: {created}")
        print(f"[CONTEXT_PROCESSOR] Cart count: {cart_count}")

        # Get or create wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_count = wishlist.get_items_count()

        print(f"[CONTEXT_PROCESSOR] Wishlist ID: {wishlist.id}, Created: {created}")
        print(f"[CONTEXT_PROCESSOR] Wishlist count: {wishlist_count}")

        return {
            "cart_count": cart_count,
            "wishlist_count": wishlist_count,
        }

    return {
        "cart_count": 0,
        "wishlist_count": 0,
    }


def verification_settings(request):
    """
    Context processor to add verification requirements to all templates
    """
    context = {
        "verification_requirements": get_verification_requirements(),
    }

    # Add user verification status if authenticated
    if request.user.is_authenticated:
        context["user_verification_status"] = {
            "is_email_verified": request.user.is_email_verified,
            "is_phone_verified": request.user.is_mobile_verified,
            "needs_verification": not (
                request.user.is_email_verified or request.user.is_mobile_verified
            ),
        }

    return context


def site_configuration(request):
    """
    Context processor to add site configuration to all templates
    Includes helper functions to get appropriate logo based on theme
    """
    site_config = SiteConfiguration.get_solo()

    return {
        "site_config": site_config,
        "get_theme_logo": lambda theme='light': site_config.get_logo_for_theme(theme),
        "get_loader_logo": lambda: site_config.get_loader_logo(),
    }
