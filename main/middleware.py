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


class VisitorTrackingMiddleware:
    """
    Middleware to track website visitors for analytics.
    Records visitor information including IP, user agent, device type, etc.
    """

    # Paths to exclude from tracking
    EXCLUDED_PATHS = [
        "/static/",
        "/media/",
        "/favicon.ico",
        "/robots.txt",
        "/__debug__/",
        "/admin/",  # Django admin
        "/api/",  # API endpoints
        "/.well-known/",
    ]

    # Common bot user agents to exclude
    BOT_USER_AGENTS = [
        "bot",
        "crawler",
        "spider",
        "scraper",
        "curl",
        "wget",
        "python-requests",
        "googlebot",
        "bingbot",
        "slurp",
        "duckduckbot",
        "baiduspider",
        "yandexbot",
        "facebookexternalhit",
        "linkedinbot",
        "twitterbot",
        "whatsapp",
        "telegram",
        "headlesschrome",
        "phantomjs",
        "nightmarejs",
        "selenium",
        "playwright",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track visitor before processing the request
        self._track_visitor(request)
        response = self.get_response(request)
        return response

    def _should_track(self, request):
        """Determine if this request should be tracked"""
        path = request.path

        # Skip excluded paths
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return False

        # Only track GET requests (actual page views)
        if request.method != "GET":
            return False

        # Skip AJAX requests
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return False

        # Skip API requests
        if request.content_type and "application/json" in request.content_type:
            return False

        # Skip bots and crawlers
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        if any(bot in user_agent for bot in self.BOT_USER_AGENTS):
            return False

        return True

    def _get_client_ip(self, request):
        """Get the client's real IP address from various proxy headers"""
        # Check multiple headers in order of preference
        headers_to_check = [
            "HTTP_X_REAL_IP",
            "HTTP_CF_CONNECTING_IP",  # Cloudflare
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_FORWARDED",
            "HTTP_FORWARDED_FOR",
            "HTTP_FORWARDED",
            "REMOTE_ADDR",
        ]

        for header in headers_to_check:
            ip = request.META.get(header)
            if ip:
                # X-Forwarded-For can contain multiple IPs, get the first one
                if "," in ip:
                    ip = ip.split(",")[0].strip()
                # Validate IP format
                if self._is_valid_ip(ip):
                    return ip

        return request.META.get("REMOTE_ADDR", "127.0.0.1")

    def _is_valid_ip(self, ip):
        """Validate IP address format"""
        import re

        # Simple IPv4 validation
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        # Simple IPv6 validation
        ipv6_pattern = r"^([\da-fA-F]{1,4}:){7}[\da-fA-F]{1,4}$|^::1$"

        if re.match(ipv4_pattern, ip):
            parts = ip.split(".")
            return all(0 <= int(part) <= 255 for part in parts)
        elif re.match(ipv6_pattern, ip):
            return True
        return False

    def _get_device_type(self, user_agent):
        """Determine device type from user agent with better detection"""
        user_agent_lower = user_agent.lower()

        # Mobile devices
        mobile_patterns = [
            "mobile",
            "android",
            "iphone",
            "ipod",
            "blackberry",
            "windows phone",
            "opera mini",
        ]
        if any(pattern in user_agent_lower for pattern in mobile_patterns):
            return "mobile"

        # Tablet devices
        tablet_patterns = [
            "ipad",
            "tablet",
            "kindle",
            "playbook",
            "nexus 7",
            "nexus 10",
        ]
        if any(pattern in user_agent_lower for pattern in tablet_patterns):
            return "tablet"

        # Desktop/Laptop
        return "desktop"

    def _get_browser_info(self, user_agent):
        """Extract browser name from user agent"""
        user_agent_lower = user_agent.lower()

        browsers = {
            "edg": "Edge",
            "chrome": "Chrome",
            "safari": "Safari",
            "firefox": "Firefox",
            "opera": "Opera",
            "msie": "IE",
            "trident": "IE",
        }

        for key, name in browsers.items():
            if key in user_agent_lower:
                return name

        return "Other"

    def _track_visitor(self, request):
        """Track visitor information with improved accuracy"""
        if not self._should_track(request):
            return

        try:
            from .models import Visitor
            from django.utils import timezone
            from datetime import timedelta

            # Get visitor information
            ip_address = self._get_client_ip(request)
            session_key = request.session.session_key

            # Create session key if it doesn't exist
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            user_agent = request.META.get("HTTP_USER_AGENT", "")
            device_type = self._get_device_type(user_agent)
            page_url = request.build_absolute_uri()
            referrer = request.META.get("HTTP_REFERER", "")

            # Get country from session if available
            country = request.session.get("selected_country", "")

            # Check if this is a unique visitor (not seen in last 30 minutes)
            now = timezone.now()
            recent_threshold = now - timedelta(minutes=30)

            # Get or create visitor record
            visitor, created = Visitor.objects.get_or_create(
                ip_address=ip_address,
                session_key=session_key,
                defaults={
                    "user": request.user if request.user.is_authenticated else None,
                    "user_agent": user_agent[:500],  # Limit length
                    "page_url": page_url[:500],
                    "referrer": referrer[:500],
                    "device_type": device_type,
                    "country": country[:2] if country else "",
                },
            )

            # Update existing visitor only if they're returning after some time
            if not created:
                # Only increment page views if it's a different page or after 1 minute
                should_count = (
                    visitor.page_url != page_url[:500]
                    or (now - visitor.last_activity).total_seconds() > 60
                )

                update_fields = ["last_activity"]
                visitor.last_activity = now

                if should_count:
                    visitor.page_views += 1
                    update_fields.append("page_views")

                # Always update current page URL
                visitor.page_url = page_url[:500]
                update_fields.append("page_url")

                # Update user if authenticated and not set
                if request.user.is_authenticated and not visitor.user:
                    visitor.user = request.user
                    update_fields.append("user")

                # Update country if available
                if country and not visitor.country:
                    visitor.country = country[:2]
                    update_fields.append("country")

                visitor.save(update_fields=update_fields)

        except Exception as e:
            # Log error but don't break the request
            logger.error(f"Error tracking visitor: {e}", exc_info=True)
