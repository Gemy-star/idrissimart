"""
Chat Views for User-to-User Communication
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q, Max, Count
from django.utils import timezone
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

        # Check if user is participant
        if user not in [chat_room.publisher, chat_room.client]:
            return redirect("main:chat_list")

        # Mark messages as read
        chat_room.mark_as_read(user)

        # Determine other user
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

            # Create new room
            chat_room = ChatRoom.objects.create(
                room_type="publisher_client",
                publisher=user,
                client=other_user,
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
    chat_room = get_object_or_404(ChatRoom, id=room_id, is_active=True)

    # Check if user is participant
    if request.user not in [chat_room.publisher, chat_room.client]:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    message_text = request.POST.get("message", "").strip()

    if not message_text:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    # Create message
    message = ChatMessage.objects.create(
        room=chat_room, sender=request.user, message=message_text
    )

    # Update room timestamp
    chat_room.updated_at = timezone.now()
    chat_room.save(update_fields=["updated_at"])

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
    chat_room = get_object_or_404(ChatRoom, id=room_id, is_active=True)

    # Check if user is participant
    if request.user not in [chat_room.publisher, chat_room.client]:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Get messages after specific time (for polling)
    after_time = request.GET.get("after")

    messages_query = chat_room.messages.select_related("sender").order_by("created_at")

    if after_time:
        messages_query = messages_query.filter(created_at__gt=after_time)

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

    return JsonResponse(
        {
            "messages": messages_data,
            "unread_count": chat_room.get_unread_count(request.user),
        }
    )


@login_required
@require_POST
def mark_read(request, room_id):
    """
    Mark all messages in a room as read (AJAX)
    """
    chat_room = get_object_or_404(ChatRoom, id=room_id, is_active=True)

    # Check if user is participant
    if request.user not in [chat_room.publisher, chat_room.client]:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    chat_room.mark_as_read(request.user)

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
