from content.models import Country, HomeSlider
from main.models import Notification
from constance import config
from django.db import models


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
        currency = country.currency or "SAR"
    except Country.DoesNotExist:
        currency = "SAR"  # Default to SAR if country not found

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

    # Get only classified ad categories for the header
    categories = (
        Category.get_root_categories(
            section_type="classified", country_code=selected_country
        )
        .filter(is_active=True)
        .order_by("order", "name")[:8]
    )  # Limit to 8 categories for header

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
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.get_items_count()

        # Get or create wishlist
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_count = wishlist.get_items_count()

        return {
            "cart_count": cart_count,
            "wishlist_count": wishlist_count,
        }

    return {
        "cart_count": 0,
        "wishlist_count": 0,
    }
