from content.models import Country, HomeSlider
from main.models import Notification
from constance import config


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
    """
    return {"home_sliders": HomeSlider.objects.filter(is_active=True).order_by("order")}


def user_preferences(request):
    """
    Context processor for user preferences from session/cookies
    """
    selected_country = request.session.get("selected_country", "EG")

    return {
        "selected_country": selected_country,
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
