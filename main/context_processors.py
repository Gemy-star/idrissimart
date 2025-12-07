"""
Context processors for the main app
Provides cart, wishlist counts, and ad balance to all templates
"""

from main.models import Cart, Wishlist, UserPackage
from django.utils import timezone
from django.conf import settings


def cart_wishlist_counts(request):
    """
    Add cart, wishlist counts, and user ad balance to the context for all templates
    Only for authenticated users - guest users cannot access cart/wishlist
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

        # Add notification and message counts for authenticated users
        try:
            from main.models import ChatRoom, ChatMessage, Notification
            from django.db.models import Q
            from django.utils import timezone
            from datetime import timedelta
            import logging

            logger = logging.getLogger(__name__)

            # Basic notification counts for all users
            context["user_unread_notifications"] = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()

            context["user_total_notifications"] = Notification.objects.filter(
                user=request.user
            ).count()

            logger.info(
                f"User {request.user.username} - Unread notifications: {context['user_unread_notifications']}"
            )

            # Chat message counts for publishers
            if (
                hasattr(request.user, "classifiedad_set")
                and request.user.classifiedad_set.exists()
            ):
                # User is a publisher - get chat messages
                context["unread_chat_messages"] = (
                    ChatMessage.objects.filter(
                        room__publisher=request.user,
                        is_read=False,
                    )
                    .exclude(sender=request.user)
                    .count()
                )  # Messages from others
            else:
                context["unread_chat_messages"] = 0

            # Admin-specific counts
            if request.user.is_staff:
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

                logger.info(
                    f"Admin {request.user.username} - Unread support: {context['unread_support_messages']}, Total chats: {context['total_support_chats']}"
                )

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

                # Customer notifications (regular users without staff status and no special groups)
                customer_notifications_qs = Notification.objects.filter(
                    user__is_staff=False, user__groups__isnull=True
                )
                context["customer_notifications"] = customer_notifications_qs.count()
                context["unread_customer_notifications"] = (
                    customer_notifications_qs.filter(is_read=False).count()
                )

                # Publisher notifications (users with published ads)
                # Check for users who have classifieds
                from main.models import ClassifiedAd

                publisher_user_ids = ClassifiedAd.objects.values_list(
                    "user_id", flat=True
                ).distinct()
                publisher_notifications_qs = Notification.objects.filter(
                    user_id__in=publisher_user_ids
                )
                context["publisher_notifications"] = publisher_notifications_qs.count()
                context["unread_publisher_notifications"] = (
                    publisher_notifications_qs.filter(is_read=False).count()
                )

                # Admin notifications - general or for staff users
                admin_notifications_qs = Notification.objects.filter(
                    Q(notification_type="general") | Q(user__is_staff=True)
                )
                context["admin_notifications"] = admin_notifications_qs.count()
                context["unread_admin_notifications"] = admin_notifications_qs.filter(
                    is_read=False
                ).count()

                logger.info(
                    f"Admin {request.user.username} - Total notifications: {context['total_notifications']}, "
                    f"Unread: {context['unread_notifications']}, "
                    f"Customer unread: {context['unread_customer_notifications']}, "
                    f"Publisher unread: {context['unread_publisher_notifications']}"
                )
            else:
                # Non-admin users - set admin-specific counts to 0
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

        except Exception as e:
            # Fallback values if queries fail
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Error in context processor for user {request.user.username}: {str(e)}"
            )
            context["user_unread_notifications"] = 0
            context["user_total_notifications"] = 0
            context["unread_chat_messages"] = 0
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
    # Guest users get 0 counts since they cannot access cart/wishlist
    return context


def recaptcha_keys(request):
    """Add Google reCAPTCHA keys to context"""
    return {
        "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
    }
