"""
WebSocket Consumers for Real-time Chat
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatMessage, ChatRoom, Ad

User = get_user_model()


class PublisherClientChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat between publisher and client about a specific ad
    """

    async def connect(self):
        self.ad_id = self.scope["url_route"]["kwargs"]["ad_id"]
        self.user = self.scope["user"]

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Get or create chat room
        self.room = await self.get_or_create_room()
        if not self.room:
            await self.close()
            return

        self.room_group_name = f"chat_ad_{self.ad_id}_{self.room.id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send chat history
        await self.send_chat_history()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "message")

            if message_type == "message":
                message = data.get("message", "").strip()

                if message:
                    # Save message to database
                    chat_message = await self.save_message(message)

                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "message": message,
                            "sender_id": self.user.id,
                            "sender_name": self.user.get_full_name()
                            or self.user.username,
                            "timestamp": chat_message.created_at.isoformat(),
                            "message_id": chat_message.id,
                        },
                    )

            elif message_type == "typing":
                # Broadcast typing indicator
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_typing",
                        "user_id": self.user.id,
                        "user_name": self.user.get_full_name() or self.user.username,
                    },
                )

        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def chat_message(self, event):
        """
        Receive message from room group
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "sender_id": event["sender_id"],
                    "sender_name": event["sender_name"],
                    "timestamp": event["timestamp"],
                    "message_id": event["message_id"],
                }
            )
        )

    async def user_typing(self, event):
        """
        Receive typing indicator from room group
        """
        # Don't send typing indicator to self
        if event["user_id"] != self.user.id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing",
                        "user_id": event["user_id"],
                        "user_name": event["user_name"],
                    }
                )
            )

    @database_sync_to_async
    def get_or_create_room(self):
        """
        Get or create chat room for this ad and user
        """
        try:
            ad = Ad.objects.select_related("user").get(id=self.ad_id)

            # Determine publisher and client
            if self.user == ad.user:
                # User is the publisher
                publisher = ad.user
                client = None  # Will be set when client joins
            else:
                # User is the client
                publisher = ad.user
                client = self.user

            # Get or create chat room
            room, created = ChatRoom.objects.get_or_create(
                ad=ad,
                client=client,
                defaults={"publisher": publisher, "room_type": "publisher_client"},
            )

            return room

        except Ad.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, message):
        """
        Save message to database
        """
        return ChatMessage.objects.create(
            room=self.room, sender=self.user, message=message
        )

    async def send_chat_history(self):
        """
        Send recent chat history to newly connected user
        """
        messages = await self.get_recent_messages()

        await self.send(text_data=json.dumps({"type": "history", "messages": messages}))

    @database_sync_to_async
    def get_recent_messages(self, limit=50):
        """
        Get recent messages from database
        """
        messages = (
            ChatMessage.objects.filter(room=self.room)
            .select_related("sender")
            .order_by("-created_at")[:limit]
        )

        return [
            {
                "id": msg.id,
                "message": msg.message,
                "sender_id": msg.sender.id,
                "sender_name": msg.sender.get_full_name() or msg.sender.username,
                "timestamp": msg.created_at.isoformat(),
                "is_read": msg.is_read,
            }
            for msg in reversed(messages)
        ]


class PublisherAdminChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat between publisher and admin
    """

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = self.scope["user"]

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user is publisher or admin
        is_allowed = await self.check_permission()
        if not is_allowed:
            await self.close()
            return

        # Get or create chat room
        self.room = await self.get_or_create_support_room()
        if not self.room:
            await self.close()
            return

        self.room_group_name = f"chat_support_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send chat history
        await self.send_chat_history()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "message")

            if message_type == "message":
                message = data.get("message", "").strip()

                if message:
                    # Save message to database
                    chat_message = await self.save_message(message)

                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "message": message,
                            "sender_id": self.user.id,
                            "sender_name": self.user.get_full_name()
                            or self.user.username,
                            "sender_role": (
                                "admin" if self.user.is_staff else "publisher"
                            ),
                            "timestamp": chat_message.created_at.isoformat(),
                            "message_id": chat_message.id,
                        },
                    )

            elif message_type == "typing":
                # Broadcast typing indicator
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_typing",
                        "user_id": self.user.id,
                        "user_name": self.user.get_full_name() or self.user.username,
                    },
                )

        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def chat_message(self, event):
        """
        Receive message from room group
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "sender_id": event["sender_id"],
                    "sender_name": event["sender_name"],
                    "sender_role": event["sender_role"],
                    "timestamp": event["timestamp"],
                    "message_id": event["message_id"],
                }
            )
        )

    async def user_typing(self, event):
        """
        Receive typing indicator from room group
        """
        # Don't send typing indicator to self
        if event["user_id"] != self.user.id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing",
                        "user_id": event["user_id"],
                        "user_name": event["user_name"],
                    }
                )
            )

    @database_sync_to_async
    def check_permission(self):
        """
        Check if user is allowed to access this chat
        """
        return self.user.is_publisher() or self.user.is_staff

    @database_sync_to_async
    def get_or_create_support_room(self):
        """
        Get or create support chat room
        """
        # Extract publisher ID from room name (format: publisher_123)
        try:
            publisher_id = int(self.room_name.split("_")[-1])
            publisher = User.objects.get(id=publisher_id)

            # Get or create support room
            room, created = ChatRoom.objects.get_or_create(
                publisher=publisher,
                room_type="publisher_admin",
                defaults={
                    "client": None,
                    "ad": None,
                },
            )

            return room

        except (ValueError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def save_message(self, message):
        """
        Save message to database
        """
        return ChatMessage.objects.create(
            room=self.room, sender=self.user, message=message
        )

    async def send_chat_history(self):
        """
        Send recent chat history to newly connected user
        """
        messages = await self.get_recent_messages()

        await self.send(text_data=json.dumps({"type": "history", "messages": messages}))

    @database_sync_to_async
    def get_recent_messages(self, limit=100):
        """
        Get recent messages from database
        """
        messages = (
            ChatMessage.objects.filter(room=self.room)
            .select_related("sender")
            .order_by("-created_at")[:limit]
        )

        return [
            {
                "id": msg.id,
                "message": msg.message,
                "sender_id": msg.sender.id,
                "sender_name": msg.sender.get_full_name() or msg.sender.username,
                "sender_role": "admin" if msg.sender.is_staff else "publisher",
                "timestamp": msg.created_at.isoformat(),
                "is_read": msg.is_read,
            }
            for msg in reversed(messages)
        ]


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f"notifications_{self.user.id}"

        # Join user's notification group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data):
        # Handle ping/pong for connection keep-alive
        data = json.loads(text_data)
        if data.get("type") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def notification_message(self, event):
        """
        Send notification to user
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "notification": event["notification"],
                }
            )
        )
