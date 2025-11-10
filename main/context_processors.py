"""
Context processors for the main app
Provides cart and wishlist counts to all templates
"""

from main.models import Cart, Wishlist


def cart_wishlist_counts(request):
    """
    Add cart and wishlist counts to the context for all templates
    """
    context = {
        "cart_count": 0,
        "wishlist_count": 0,
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

    return context
