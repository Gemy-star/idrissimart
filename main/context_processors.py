"""
Context processors for the main app
Provides cart, wishlist counts, and ad balance to all templates
"""

from main.models import Cart, Wishlist, UserPackage
from django.utils import timezone


def cart_wishlist_counts(request):
    """
    Add cart, wishlist counts, and user ad balance to the context for all templates
    Supports both authenticated and guest users for cart
    """
    context = {
        "cart_count": 0,
        "wishlist_count": 0,
        "ads_remaining": 0,
        "has_ad_balance": False,
    }

    if request.user.is_authenticated:
        try:
            # Get or create cart
            cart, _ = Cart.objects.get_or_create(user=request.user)
            context["cart_count"] = cart.get_items_count()
        except Exception:
            context["cart_count"] = 0

        try:
            # Get or create wishlist
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            context["wishlist_count"] = wishlist.get_items_count()
        except Exception:
            context["wishlist_count"] = 0

        # Get user's ad balance (ads_remaining)
        try:
            active_package = (
                UserPackage.objects.filter(
                    user=request.user,
                    expiry_date__gte=timezone.now(),
                    ads_remaining__gt=0,
                )
                .order_by("expiry_date")
                .first()
            )
            if active_package:
                context["ads_remaining"] = active_package.ads_remaining
                context["has_ad_balance"] = True
        except Exception:
            context["ads_remaining"] = 0
            context["has_ad_balance"] = False
    else:
        # Guest users - get cart count from session
        try:
            session_cart = request.session.get("cart", {})
            context["cart_count"] = sum(
                item["quantity"] for item in session_cart.values()
            )
        except Exception:
            context["cart_count"] = 0

    return context
