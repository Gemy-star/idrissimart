from content.models import Country


class UserPermissionMiddleware:
    """
    Middleware to add user permissions to request context
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user_permissions = {
                "can_post_classified_ads": request.user.can_post_classified_ads(),
                "can_sell_products": request.user.can_sell_products(),
                "can_offer_services": request.user.can_offer_services(),
                "can_create_courses": request.user.can_create_courses(),
                "can_post_jobs": request.user.can_post_jobs(),
                "is_premium": request.user.has_premium_access(),
            }

        response = self.get_response(request)
        return response


class CountryFilterMiddleware:
    """
    Middleware to handle country filtering for all views consistently
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set default country if not already set
        if "selected_country" not in request.session:
            request.session["selected_country"] = "EG"  # Default to Egypt
            try:
                country = Country.objects.get(code="EG")
                request.session["selected_country_name"] = country.name
            except Country.DoesNotExist:
                request.session["selected_country_name"] = "Egypt"

        # Add selected country info to request for easy access
        request.selected_country = request.session.get("selected_country", "EG")
        request.selected_country_name = request.session.get(
            "selected_country_name", "Egypt"
        )

        try:
            request.country_obj = Country.objects.get(code=request.selected_country)
        except Country.DoesNotExist:
            # Fallback to Egypt if selected country doesn't exist
            request.selected_country = "EG"
            request.session["selected_country"] = "EG"
            try:
                request.country_obj = Country.objects.get(code="EG")
                request.selected_country_name = request.country_obj.name
                request.session["selected_country_name"] = request.country_obj.name
            except Country.DoesNotExist:
                request.country_obj = None
                request.selected_country_name = "Egypt"

        response = self.get_response(request)
        return response
