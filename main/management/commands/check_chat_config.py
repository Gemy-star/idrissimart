"""
Django management command to check chat/Channels configuration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import sys


class Command(BaseCommand):
    help = "Check Django Channels and chat configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed information",
        )

    def handle(self, *args, **options):
        verbose = options.get("verbose", False)

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(
            self.style.SUCCESS("DJANGO CHANNELS CHAT CONFIGURATION CHECK")
        )
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        all_passed = True

        # 1. Check if Channels is installed
        all_passed &= self._check_channels_installed(verbose)

        # 2. Check ASGI application
        all_passed &= self._check_asgi_application(verbose)

        # 3. Check Channel Layers
        all_passed &= self._check_channel_layers(verbose)

        # 4. Check Redis connection
        all_passed &= self._check_redis_connection(verbose)

        # 5. Check Chat models
        all_passed &= self._check_chat_models(verbose)

        # 6. Check routing configuration
        all_passed &= self._check_routing(verbose)

        # 7. Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        if all_passed:
            self.stdout.write(self.style.SUCCESS("✓ ALL CHECKS PASSED"))
            self.stdout.write(self.style.SUCCESS("Chat system is properly configured!"))
        else:
            self.stdout.write(self.style.ERROR("✗ SOME CHECKS FAILED"))
            self.stdout.write(self.style.WARNING("Please fix the issues above."))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        return 0 if all_passed else 1

    def _check_channels_installed(self, verbose):
        """Check if Django Channels is installed"""
        self.stdout.write(
            self.style.HTTP_INFO("1. Checking Django Channels installation...")
        )

        try:
            import channels
            import daphne

            self.stdout.write(
                self.style.SUCCESS(f"   ✓ Channels version: {channels.__version__}")
            )
            self.stdout.write(
                self.style.SUCCESS(f"   ✓ Daphne version: {daphne.__version__}")
            )

            # Check if in INSTALLED_APPS
            if "channels" in settings.INSTALLED_APPS:
                self.stdout.write(self.style.SUCCESS("   ✓ Channels in INSTALLED_APPS"))
            else:
                self.stdout.write(
                    self.style.ERROR("   ✗ Channels NOT in INSTALLED_APPS")
                )
                return False

            if "daphne" in settings.INSTALLED_APPS:
                self.stdout.write(self.style.SUCCESS("   ✓ Daphne in INSTALLED_APPS"))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "   ⚠ Daphne NOT in INSTALLED_APPS (should be first)"
                    )
                )

            return True

        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Channels not installed: {e}"))
            self.stdout.write(
                self.style.WARNING("   Run: pip install channels daphne channels-redis")
            )
            return False

    def _check_asgi_application(self, verbose):
        """Check ASGI application configuration"""
        self.stdout.write(self.style.HTTP_INFO("2. Checking ASGI application..."))

        if hasattr(settings, "ASGI_APPLICATION"):
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✓ ASGI_APPLICATION: {settings.ASGI_APPLICATION}"
                )
            )

            # Try to import ASGI application
            try:
                app_path = settings.ASGI_APPLICATION
                module_path, app_name = app_path.rsplit(".", 1)

                from importlib import import_module

                module = import_module(module_path)
                app = getattr(module, app_name)

                self.stdout.write(
                    self.style.SUCCESS("   ✓ ASGI application imports successfully")
                )

                if verbose:
                    self.stdout.write(f"   Application: {app}")

                return True
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ Failed to import ASGI application: {e}")
                )
                return False
        else:
            self.stdout.write(
                self.style.ERROR("   ✗ ASGI_APPLICATION not configured in settings")
            )
            self.stdout.write(
                self.style.WARNING(
                    '   Add: ASGI_APPLICATION = "idrissimart.asgi.application"'
                )
            )
            return False

    def _check_channel_layers(self, verbose):
        """Check Channel Layers configuration"""
        self.stdout.write(self.style.HTTP_INFO("3. Checking Channel Layers..."))

        if hasattr(settings, "CHANNEL_LAYERS"):
            config = settings.CHANNEL_LAYERS.get("default", {})
            backend = config.get("BACKEND", "Not set")

            self.stdout.write(self.style.SUCCESS(f"   ✓ Channel Layers configured"))
            self.stdout.write(f"   Backend: {backend}")

            if verbose:
                self.stdout.write(f'   Config: {config.get("CONFIG", {})}')

            # Check if using Redis
            if "redis" in backend.lower():
                self.stdout.write(self.style.SUCCESS("   ✓ Using Redis channel layer"))
                return True
            elif "InMemoryChannelLayer" in backend:
                self.stdout.write(
                    self.style.WARNING(
                        "   ⚠ Using InMemory channel layer (not for production)"
                    )
                )
                return True
            else:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠ Unknown channel layer: {backend}")
                )
                return True
        else:
            self.stdout.write(self.style.ERROR("   ✗ CHANNEL_LAYERS not configured"))
            self.stdout.write(
                self.style.WARNING("   Configure CHANNEL_LAYERS in settings")
            )
            return False

    def _check_redis_connection(self, verbose):
        """Check Redis connection"""
        self.stdout.write(self.style.HTTP_INFO("4. Checking Redis connection..."))

        try:
            import redis

            self.stdout.write(
                self.style.SUCCESS(f"   ✓ Redis library installed: {redis.__version__}")
            )
        except ImportError:
            self.stdout.write(self.style.WARNING("   ⚠ Redis library not installed"))
            self.stdout.write(self.style.WARNING("   Run: pip install redis hiredis"))
            return True  # Not critical if using InMemory

        # Test channel layer
        try:
            channel_layer = get_channel_layer()

            if channel_layer is None:
                self.stdout.write(self.style.ERROR("   ✗ Channel layer is None"))
                return False

            # Test send/receive
            test_channel = "test_channel"
            test_message = {"type": "test.message", "text": "Hello"}

            async_to_sync(channel_layer.send)(test_channel, test_message)
            received = async_to_sync(channel_layer.receive)(test_channel)

            if received == test_message:
                self.stdout.write(
                    self.style.SUCCESS("   ✓ Redis connection successful")
                )
                self.stdout.write(
                    self.style.SUCCESS("   ✓ Channel layer send/receive working")
                )
                return True
            else:
                self.stdout.write(self.style.ERROR("   ✗ Message send/receive failed"))
                return False

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Redis connection failed: {e}"))
            self.stdout.write(
                self.style.WARNING("   Make sure Redis server is running:")
            )
            self.stdout.write(self.style.WARNING("   - sudo systemctl start redis"))
            self.stdout.write(self.style.WARNING("   - redis-cli ping"))
            return False

    def _check_chat_models(self, verbose):
        """Check if chat models exist"""
        self.stdout.write(self.style.HTTP_INFO("5. Checking Chat models..."))

        try:
            from main.models import ChatRoom, ChatMessage

            self.stdout.write(self.style.SUCCESS("   ✓ ChatRoom model found"))
            self.stdout.write(self.style.SUCCESS("   ✓ ChatMessage model found"))

            # Check if tables exist
            try:
                room_count = ChatRoom.objects.count()
                message_count = ChatMessage.objects.count()

                self.stdout.write(self.style.SUCCESS(f"   ✓ Database tables exist"))
                self.stdout.write(f"   ChatRooms: {room_count}")
                self.stdout.write(f"   ChatMessages: {message_count}")

                return True
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ Database tables not found: {e}")
                )
                self.stdout.write(
                    self.style.WARNING("   Run: python manage.py migrate")
                )
                return False

        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Chat models not found: {e}"))
            self.stdout.write(
                self.style.WARNING(
                    "   Make sure chat models are defined in main/models.py"
                )
            )
            return False

    def _check_routing(self, verbose):
        """Check WebSocket routing configuration"""
        self.stdout.write(self.style.HTTP_INFO("6. Checking WebSocket routing..."))

        try:
            from main import routing

            if hasattr(routing, "websocket_urlpatterns"):
                patterns = routing.websocket_urlpatterns
                self.stdout.write(
                    self.style.SUCCESS(
                        f"   ✓ WebSocket URL patterns found ({len(patterns)} routes)"
                    )
                )

                if verbose:
                    for pattern in patterns:
                        self.stdout.write(f"   - {pattern.pattern}")

                # Check consumers
                try:
                    from main import consumers

                    consumer_classes = [
                        "PublisherClientChatConsumer",
                        "PublisherAdminChatConsumer",
                        "NotificationConsumer",
                    ]

                    for consumer_name in consumer_classes:
                        if hasattr(consumers, consumer_name):
                            self.stdout.write(
                                self.style.SUCCESS(f"   ✓ {consumer_name} found")
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f"   ⚠ {consumer_name} not found")
                            )

                    return True

                except ImportError as e:
                    self.stdout.write(
                        self.style.ERROR(f"   ✗ Consumers not found: {e}")
                    )
                    return False
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "   ✗ websocket_urlpatterns not found in routing.py"
                    )
                )
                return False

        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Routing module not found: {e}"))
            self.stdout.write(
                self.style.WARNING(
                    "   Create main/routing.py with WebSocket URL patterns"
                )
            )
            return False
