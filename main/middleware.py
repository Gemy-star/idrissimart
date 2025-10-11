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
