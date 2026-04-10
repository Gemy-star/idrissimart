"""
Chat Views for User-to-User Communication
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q, Max, Count
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import json
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage

User = get_user_model()


@login_required
def chat_list(request):
    """
    Display list of all chat rooms for the current user
    """
    user = request.user

    # Get all chat rooms where user is either publisher or client
    chat_rooms = (
        ChatRoom.objects.filter(Q(publisher=user) | Q(client=user), is_active=True)
        .select_related("publisher", "client", "ad")
        .annotate(
            last_message_time=Max("messages__created_at"),
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user),
            ),
        )
        .order_by("-last_message_time")
    )

    # Get last message for each room
    for room in chat_rooms:
        room.last_message = room.messages.order_by("-created_at").first()
        # Determine other user - handle admin chat rooms where client can be None
        if room.room_type == "publisher_admin":
            # For admin chats, if current user is staff, other_user is the publisher
            # If current user is the publisher, other_user represents admin/support
            room.other_user = room.publisher if user.is_staff else None
        else:
            room.other_user = room.client if room.publisher == user else room.publisher

    context = {
        "chat_rooms": chat_rooms,
    }

    return render(request, "chat/chat_list.html", context)


@login_required
def chat_room(request, room_id=None):
    """
    Display chat room or create new one
    """
    user = request.user
    chat_room = None
    other_user = None

    if room_id:
        # Load existing chat room
        chat_room = get_object_or_404(ChatRoom, id=room_id, is_active=True)

        # Check if user is participant (handle admin chats where client can be None)
        if chat_room.room_type == "publisher_admin":
            # Admin chats: allow publisher or staff
            if user != chat_room.publisher and not user.is_staff:
                return redirect("main:chat_list")
        else:
            # Regular chats: must be publisher or client
            if user not in [chat_room.publisher, chat_room.client]:
                return redirect("main:chat_list")

        # Mark messages as read
        chat_room.mark_as_read(user)

        # Determine other user
        if chat_room.room_type == "publisher_admin":
            # For admin chats, other_user is the publisher if viewing as staff, None otherwise
            other_user = chat_room.publisher if user.is_staff else None
        else:
            other_user = (
                chat_room.client if chat_room.publisher == user else chat_room.publisher
            )

    else:
        # Create new chat room (from query params)
        other_user_id = request.GET.get("user_id")
        ad_id = request.GET.get("ad_id")

        if other_user_id:
            other_user = get_object_or_404(User, id=other_user_id)

            # Check if chat room already exists
            existing_room = ChatRoom.objects.filter(
                Q(publisher=user, client=other_user)
                | Q(publisher=other_user, client=user),
                is_active=True,
            ).first()

            if existing_room:
                return redirect("main:chat_room", room_id=existing_room.id)

            # Determine who is publisher and who is client
            # If ad_id is provided, get the ad's publisher
            from .models import ClassifiedAd

            if ad_id:
                try:
                    ad = ClassifiedAd.objects.get(id=ad_id)
                    ad_publisher = ad.user

                    # Publisher is the ad owner, client is the other user
                    if user == ad_publisher:
                        # Current user is the ad owner
                        publisher = user
                        client = other_user
                    else:
                        # Other user is the ad owner
                        publisher = other_user
                        client = user
                except ClassifiedAd.DoesNotExist:
                    # If ad doesn't exist, use default logic
                    publisher = other_user
                    client = user
            else:
                # If no ad_id, the other_user is assumed to be the publisher
                publisher = other_user
                client = user

            # Create new room
            chat_room = ChatRoom.objects.create(
                room_type="publisher_client",
                publisher=publisher,
                client=client,
                ad_id=ad_id if ad_id else None,
            )

            return redirect("main:chat_room", room_id=chat_room.id)

    # Get messages
    messages = []
    if chat_room:
        messages = chat_room.messages.select_related("sender").order_by("created_at")

    context = {
        "chat_room": chat_room,
        "other_user": other_user,
        "messages": messages,
    }

    return render(request, "chat/chat_room.html", context)


@login_required
@require_POST
def send_message(request, room_id):
    """
    Send a message in a chat room (AJAX)
    """
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({"error": "Chat room not found.", "is_inactive": False}, status=404)
    if not chat_room.is_active:
        return JsonResponse({"error": "This chat room has been closed.", "is_inactive": True}, status=403)

    # Check if user is participant (handle admin chats where client can be None)
    if chat_room.room_type == "publisher_admin":
        if request.user != chat_room.publisher and not request.user.is_staff:
            return JsonResponse({"error": "Unauthorized"}, status=403)
    else:
        if request.user not in [chat_room.publisher, chat_room.client]:
            return JsonResponse({"error": "Unauthorized"}, status=403)

    # Handle both JSON and form data
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            message_text = data.get("message", "").strip()
        else:
            message_text = request.POST.get("message", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not message_text:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    # Create message
    message = ChatMessage.objects.create(
        room=chat_room, sender=request.user, message=message_text
    )

    # Update room timestamp
    chat_room.updated_at = timezone.now()
    chat_room.save(update_fields=["updated_at"])

    # Determine receiver (the other participant)
    receiver = None
    if chat_room.room_type == "publisher_admin":
        # For admin chats: if sender is publisher, receiver is admin/staff
        # if sender is staff, receiver is publisher
        if request.user == chat_room.publisher:
            # Sender is publisher, notify admins (we'll skip this for now)
            pass
        else:
            # Sender is staff, notify publisher
            receiver = chat_room.publisher
    else:
        # For publisher-client chats
        receiver = chat_room.client if chat_room.publisher == request.user else chat_room.publisher

    # Send notification and email to receiver
    if receiver:
        # Create in-app notification
        from .models import Notification

        sender_name = request.user.get_full_name() or request.user.username
        ad_title = chat_room.ad.title if chat_room.ad else ""

        notification_title = f"رسالة جديدة من {sender_name}"
        notification_message = f"لديك رسالة جديدة"
        if ad_title:
            notification_message += f" بخصوص إعلانك: {ad_title}"

        # Build chat URL
        from django.urls import reverse
        chat_url = reverse("main:chat_room", kwargs={"room_id": chat_room.id})

        # Create notification
        Notification.objects.create(
            user=receiver,
            title=notification_title,
            message=notification_message,
            notification_type=Notification.NotificationType.GENERAL,
            link=chat_url,
        )

        # Send email notification if user has email notifications enabled
        receiver_email = receiver.email
        notify_new_messages = getattr(receiver, "notify_new_messages", True)

        if receiver_email and notify_new_messages:
            from .services.email_service import EmailService
            from django.contrib.sites.shortcuts import get_current_site

            receiver_name = receiver.get_full_name() or receiver.username
            current_site = get_current_site(request)
            protocol = "https" if request.is_secure() else "http"
            full_chat_url = f"{protocol}://{current_site.domain}{chat_url}"

            # Truncate message for preview
            message_preview = message_text[:200] if len(message_text) > 200 else message_text

            # Send email asynchronously (optional: use Celery or Django-Q)
            try:
                EmailService.send_new_message_email(
                    email=receiver_email,
                    receiver_name=receiver_name,
                    sender_name=sender_name,
                    message_preview=message_preview,
                    chat_url=full_chat_url,
                    ad_title=ad_title,
                )
            except Exception as e:
                # Log error but don't fail the request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send new message email: {e}")

    return JsonResponse(
        {
            "success": True,
            "message": {
                "id": message.id,
                "sender_id": message.sender.id,
                "sender_name": message.sender.get_full_name()
                or message.sender.username,
                "message": message.message,
                "created_at": message.created_at.isoformat(),
                "is_read": message.is_read,
            },
        }
    )


@login_required
@require_http_methods(["GET"])
def get_messages(request, room_id):
    """
    Get messages for a chat room (AJAX polling)
    """
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({"error": "Chat room not found.", "is_inactive": False}, status=404)
    if not chat_room.is_active:
        return JsonResponse({"error": "This chat room has been closed.", "is_inactive": True}, status=403)

    # Check if user is participant (handle admin chats where client can be None)
    if chat_room.room_type == "publisher_admin":
        if request.user != chat_room.publisher and not request.user.is_staff:
            return JsonResponse({"error": "Unauthorized"}, status=403)
    else:
        if request.user not in [chat_room.publisher, chat_room.client]:
            return JsonResponse({"error": "Unauthorized"}, status=403)

    # Get messages after specific time (for polling)
    after_time_str = request.GET.get("after")

    messages_query = chat_room.messages.select_related("sender").order_by("created_at")

    if after_time_str:
        try:
            # Parse datetime string (handles URL-encoded '+' in timezone offset)
            after_time = parse_datetime(after_time_str)
            if after_time is None:
                # If parsing fails, return error instead of 500
                return JsonResponse({"error": "Invalid datetime format"}, status=400)
            messages_query = messages_query.filter(created_at__gt=after_time)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid datetime format"}, status=400)

    messages = messages_query[:50]  # Limit to last 50 messages

    # Mark as read
    chat_room.mark_as_read(request.user)

    messages_data = [
        {
            "id": msg.id,
            "sender_id": msg.sender.id,
            "sender_name": msg.sender.get_full_name() or msg.sender.username,
            "message": msg.message,
            "created_at": msg.created_at.isoformat(),
            "is_read": msg.is_read,
        }
        for msg in messages
    ]

    # Build room info for header updates
    room_info = {
        "id": chat_room.id,
        "client_name": (
            f"{chat_room.client.first_name or ''} {chat_room.client.last_name or ''}".strip()
            or chat_room.client.username
            if chat_room.client else None
        ),
        "ad_title": chat_room.ad.title if chat_room.ad else None,
        "ad_url": chat_room.ad.get_absolute_url() if chat_room.ad else None,
    }

    return JsonResponse(
        {
            "success": True,
            "messages": messages_data,
            "room": room_info,
            "unread_count": chat_room.get_unread_count(request.user),
        }
    )


@login_required
@require_POST
def mark_read(request, room_id):
    """
    Mark all messages in a room as read (AJAX)
    """
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({"error": "Chat room not found.", "is_inactive": False}, status=404)
    if not chat_room.is_active:
        return JsonResponse({"success": True, "is_inactive": True})

    # Check if user is participant (handle admin chats where client can be None)
    if chat_room.room_type == "publisher_admin":
        if request.user != chat_room.publisher and not request.user.is_staff:
            return JsonResponse({"error": "Unauthorized"}, status=403)
    else:
        if request.user not in [chat_room.publisher, chat_room.client]:
            return JsonResponse({"error": "Unauthorized"}, status=403)

    chat_room.mark_as_read(request.user)

    return JsonResponse({"success": True})


@login_required
@require_POST
def archive_chat_room(request, room_id):
    """
    Archive a chat room (soft delete)
    """
    chat_room = get_object_or_404(ChatRoom, id=room_id)

    # Check if user is the publisher
    if request.user != chat_room.publisher:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Soft delete by setting is_active to False
    chat_room.is_active = False
    chat_room.save()

    return JsonResponse({"success": True})


@login_required
def admin_chat_panel(request):
    """
    Load chat panel content for admin (AJAX)
    """
    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User ID required"}, status=400)

    # Check if requester is staff
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    other_user = get_object_or_404(User, id=user_id)

    # Find or create admin chat room
    chat_room = ChatRoom.objects.filter(
        room_type="publisher_admin", publisher=other_user, is_active=True
    ).first()

    if not chat_room:
        chat_room = ChatRoom.objects.create(
            room_type="publisher_admin", publisher=other_user, client=None
        )

    # Get messages
    messages = chat_room.messages.select_related("sender").order_by("created_at")[:100]

    # Mark as read
    chat_room.mark_as_read(request.user)

    context = {
        "chat_room": chat_room,
        "other_user": other_user,
        "messages": messages,
        "is_admin_panel": True,
    }

    return render(request, "chat/partials/_chat_panel_content.html", context)


@login_required
@require_POST
def create_support_ticket(request):
    """
    Create a new support ticket (publisher to admin chat)
    """
    import json

    try:
        data = json.loads(request.body)
        subject = data.get("subject", "").strip()
        category = data.get("category", "").strip()
        message = data.get("message", "").strip()

        if not all([subject, category, message]):
            return JsonResponse(
                {"success": False, "error": "All fields are required"}, status=400
            )

        # Translate category names
        category_names = {
            "technical": "مشكلة تقنية",
            "payment": "الدفع والباقات",
            "account": "الحساب",
            "ads": "الإعلانات",
            "other": "أخرى",
        }
        category_display = category_names.get(category, category)

        # Create a new publisher_admin chat room
        chat_room = ChatRoom.objects.create(
            room_type="publisher_admin",
            publisher=request.user,
            client=None,  # Admin chats don't have a client
        )

        # Create the first message with subject and category info
        initial_message = f"[{category_display}] {subject}\n\n{message}"
        ChatMessage.objects.create(
            room=chat_room, sender=request.user, message=initial_message
        )

        return JsonResponse(
            {
                "success": True,
                "room_id": chat_room.id,
                "message": "Support ticket created successfully",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
