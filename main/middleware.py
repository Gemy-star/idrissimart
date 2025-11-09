from content.models import Country
import logging

logger = logging.getLogger(__name__)


class BlockMaliciousRequestsMiddleware:
    """
    Block common attack patterns and malicious bot requests
    """

    # Patterns that indicate malicious requests
    BLOCKED_PATHS = [
        "telescope",
        "wp-admin",
        "wp-login",
        "wp-json",
        "wordpress",
        "xmlrpc.php",
        "info.php",
        "phpinfo",
        ".env",
        "config.php",
        ".git",
        "admin.php",
        "wp-config",
        "phpmyadmin",
        "shell",
        "eval-stdin.php",
        "wp-includes",
        "wp-content",
    ]

    BLOCKED_QUERY_PARAMS = [
        "rest_route",
        "wp_",
        "XDEBUG",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.http import HttpResponseNotFound

        # Check path for malicious patterns
        path = request.path.lower()
        for blocked in self.BLOCKED_PATHS:
            if blocked in path:
                logger.warning(
                    f"Blocked malicious request to {request.path} from {self.get_client_ip(request)}"
                )
                return HttpResponseNotFound()

        # Check query parameters
        query_string = request.META.get("QUERY_STRING", "").lower()
        for blocked_param in self.BLOCKED_QUERY_PARAMS:
            if blocked_param in query_string:
                logger.warning(
                    f"Blocked malicious query {query_string} from {self.get_client_ip(request)}"
                )
                return HttpResponseNotFound()

        # Check for PHP files
        if path.endswith((".php", ".asp", ".aspx", ".jsp")):
            logger.warning(
                f"Blocked request to {path} from {self.get_client_ip(request)}"
            )
            return HttpResponseNotFound()

        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address from the request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


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
