from django.utils import translation


class ForceAdminEnglishMiddleware:
    """Force English language for the admin panel (/super-admin/)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/super-admin/"):
            with translation.override("en"):
                request.LANGUAGE_CODE = "en"
                return self.get_response(request)
        return self.get_response(request)


class ForceArabicDefaultMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/super-admin/"):
            return self.get_response(request)
        if "django_language" not in request.COOKIES:
            translation.activate("ar")
            request.LANGUAGE_CODE = "ar"
        return self.get_response(request)
