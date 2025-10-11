from .models import Country


def countries(request):
    """
    Context processor to make countries available in all templates
    """
    return {
        "countries": Country.objects.filter(is_active=True).order_by("order", "name")
    }


def user_preferences(request):
    """
    Context processor for user preferences from session/cookies
    """
    selected_country = request.session.get("selected_country", "SA")

    return {
        "selected_country": selected_country,
    }
