"""
Admin configuration for Chat models
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import ChatRoom, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    """Admin interface for ChatRoom model"""

    list_display = [
        "id",
        "room_type",
        "publisher_link",
        "client_link",
        "ad_link",
        "message_count",
        "is_active",
        "created_at",
        "updated_at",
    ]

    list_filter = [
        "room_type",
        "is_active",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "publisher__username",
        "publisher__email",
        "client__username",
        "client__email",
        "ad__title",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "message_count",
    ]

    raw_id_fields = ["publisher", "client", "ad"]

    fieldsets = (
        ("Room Information", {"fields": ("room_type", "is_active")}),
        ("Participants", {"fields": ("publisher", "client")}),
        ("Related Content", {"fields": ("ad",)}),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at", "message_count"),
                "classes": ("collapse",),
            },
        ),
    )

    def publisher_link(self, obj):
        """Display publisher as clickable link"""
        if obj.publisher:
            user_url = reverse("admin:main_user_change", args=[obj.publisher.id])
            return format_html(
                '<a href="{}">{}</a>',
                user_url,
                obj.publisher.username,
            )
        return "-"

    publisher_link.short_description = "Publisher"

    def client_link(self, obj):
        """Display client as clickable link"""
        if obj.client:
            user_url = reverse("admin:main_user_change", args=[obj.client.id])
            return format_html(
                '<a href="{}">{}</a>',
                user_url,
                obj.client.username,
            )
        return "-"

    client_link.short_description = "Client"

    def ad_link(self, obj):
        """Display ad as clickable link"""
        if obj.ad:
            ad_url = reverse("admin:main_classifiedad_change", args=[obj.ad.id])
            return format_html(
                '<a href="{}">{}</a>',
                ad_url,
                obj.ad.title[:50],
            )
        return "-"

    ad_link.short_description = "Ad"

    def message_count(self, obj):
        """Display total message count"""
        return obj.messages.count()

    message_count.short_description = "Messages"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage model"""

    list_display = [
        "id",
        "room_link",
        "sender_link",
        "message_preview",
        "is_read",
        "created_at",
    ]

    list_filter = [
        "is_read",
        "created_at",
        "room__room_type",
    ]

    search_fields = [
        "message",
        "sender__username",
        "sender__email",
    ]

    readonly_fields = [
        "created_at",
        "read_at",
    ]

    raw_id_fields = ["room", "sender"]

    fieldsets = (
        ("Message Information", {"fields": ("room", "sender", "message")}),
        ("Attachment", {"fields": ("attachment",)}),
        ("Status", {"fields": ("is_read", "read_at")}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def room_link(self, obj):
        """Display room as clickable link"""
        room_url = reverse("admin:main_chatroom_change", args=[obj.room.id])
        return format_html(
            '<a href="{}">Room #{}</a>',
            room_url,
            obj.room.id,
        )

    room_link.short_description = "Room"

    def sender_link(self, obj):
        """Display sender as clickable link"""
        sender_url = reverse("admin:main_user_change", args=[obj.sender.id])
        return format_html(
            '<a href="{}">{}</a>',
            sender_url,
            obj.sender.username,
        )

    sender_link.short_description = "Sender"

    def message_preview(self, obj):
        """Display message preview"""
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message

    message_preview.short_description = "Message"

    def has_add_permission(self, request):
        """Disable add permission - messages should be created via chat interface"""
        return False
