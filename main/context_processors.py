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

        # Add chat view counts for admin users
        if request.user.is_staff:
            try:
                from main.models import ChatRoom, ChatMessage, Notification
                from django.db.models import Q
                from django.utils import timezone
                from datetime import timedelta

                # Support chat statistics
                context["unread_support_messages"] = ChatMessage.objects.filter(
                    room__room_type="publisher_admin",
                    is_read=False,
                    sender__is_staff=False,  # Messages from publishers
                ).count()

                context["active_support_chats"] = ChatRoom.objects.filter(
                    room_type="publisher_admin", is_active=True
                ).count()

                context["total_support_chats"] = ChatRoom.objects.filter(
                    room_type="publisher_admin"
                ).count()

                # Recent activity (last 24 hours)
                yesterday = timezone.now() - timedelta(hours=24)
                context["recent_chat_activity"] = ChatMessage.objects.filter(
                    created_at__gte=yesterday
                ).count()

                # Notification counts for different user types
                context["total_notifications"] = Notification.objects.count()
                context["unread_notifications"] = Notification.objects.filter(
                    is_read=False
                ).count()

                # Admin notifications (general system notifications)
                context["admin_notifications"] = Notification.objects.filter(
                    Q(notification_type="general") | Q(user__is_staff=True)
                ).count()

                # Customer notifications (regular users)
                context["customer_notifications"] = Notification.objects.filter(
                    user__is_staff=False, user__groups__isnull=True  # No special groups
                ).count()

                # Publisher notifications (users with ads)
                context["publisher_notifications"] = (
                    Notification.objects.filter(
                        Q(
                            notification_type__in=[
                                "ad_approved",
                                "ad_rejected",
                                "ad_expired",
                                "package_expired",
                            ]
                        )
                        | Q(user__classifiedad__isnull=False)
                    )
                    .distinct()
                    .count()
                )

                # Unread counts by type
                context["unread_admin_notifications"] = Notification.objects.filter(
                    Q(notification_type="general") | Q(user__is_staff=True),
                    is_read=False,
                ).count()

                context["unread_customer_notifications"] = Notification.objects.filter(
                    user__is_staff=False, user__groups__isnull=True, is_read=False
                ).count()

                context["unread_publisher_notifications"] = (
                    Notification.objects.filter(
                        Q(
                            notification_type__in=[
                                "ad_approved",
                                "ad_rejected",
                                "ad_expired",
                                "package_expired",
                            ]
                        )
                        | Q(user__classifiedad__isnull=False),
                        is_read=False,
                    )
                    .distinct()
                    .count()
                )

            except Exception:
                context["unread_support_messages"] = 0
                context["active_support_chats"] = 0
                context["total_support_chats"] = 0
                context["recent_chat_activity"] = 0
                context["total_notifications"] = 0
                context["unread_notifications"] = 0
                context["admin_notifications"] = 0
                context["customer_notifications"] = 0
                context["publisher_notifications"] = 0
                context["unread_admin_notifications"] = 0
                context["unread_customer_notifications"] = 0
                context["unread_publisher_notifications"] = 0
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
