from django.utils import translation


class ForceAdminEnglishMiddleware:
    """Force English language for the admin panel (/super-admin/)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/super-admin/"):
            translation.activate("en")
            request.LANGUAGE_CODE = "en"
            response = self.get_response(request)
            response.set_cookie("django_language", "en")
            return response
        return self.get_response(request)


class ForceArabicDefaultMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "django_language" not in request.COOKIES:
            translation.activate("ar")
            request.LANGUAGE_CODE = "ar"
        return self.get_response(request)
