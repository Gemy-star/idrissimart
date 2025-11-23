"""
WebSocket URL routing for Django Channels
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Publisher-Client Chat
    re_path(
        r"ws/chat/ad/(?P<ad_id>\d+)/$", consumers.PublisherClientChatConsumer.as_asgi()
    ),
    # Publisher-Admin Chat
    re_path(
        r"ws/chat/support/(?P<room_name>\w+)/$",
        consumers.PublisherAdminChatConsumer.as_asgi(),
    ),
    # General notification channel (optional)
    re_path(r"ws/notifications/$", consumers.NotificationConsumer.as_asgi()),
]
