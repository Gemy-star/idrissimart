"""
Management command to seed dummy admin support chats for testing
Usage: python manage.py seed_admin_chats
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import ChatRoom, ChatMessage
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed dummy admin support chats for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of chat rooms to create (default: 5)",
        )
        parser.add_argument(
            "--messages",
            type=int,
            default=10,
            help="Number of messages per chat (default: 10)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        messages_per_chat = options["messages"]

        self.stdout.write("Creating admin support chats...")

        # Get admin user
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            self.stdout.write(
                self.style.ERROR("No admin user found. Please create an admin first.")
            )
            return

        # Get or create test users (publishers)
        publishers = []
        for i in range(count):
            username = f"publisher_{i + 1}"
            email = f"publisher{i + 1}@test.com"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": f"Publisher",
                    "last_name": f"{i + 1}",
                },
            )
            if created:
                user.set_password("testpass123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created publisher: {username}"))
            publishers.append(user)

        # Sample messages
        publisher_messages = [
            "مرحباً، لدي مشكلة في نشر الإعلان",
            "هل يمكنني تغيير فئة الإعلان؟",
            "كم من الوقت يستغرق الموافقة على الإعلان؟",
            "لا أستطيع تحميل الصور",
            "كيف يمكنني ترقية باقتي؟",
            "أحتاج مساعدة في الدفع",
            "إعلاني لا يظهر في النتائج",
            "هل يمكن استرداد الأموال؟",
            "كيف أحذف حسابي؟",
            "لدي سؤال عن الأسعار",
        ]

        admin_messages = [
            "مرحباً! كيف يمكنني مساعدتك؟",
            "دعني أتحقق من ذلك لك",
            "تم حل المشكلة، يرجى المحاولة الآن",
            "سأحيل هذا إلى الفريق الفني",
            "شكراً على تواصلك معنا",
            "هل هناك أي شيء آخر يمكنني مساعدتك به؟",
            "تم الموافقة على طلبك",
            "يرجى التحقق من بريدك الإلكتروني",
            "سيتم معالجة طلبك خلال 24 ساعة",
            "هل حُلت مشكلتك؟",
        ]

        # Create chat rooms with messages
        for publisher in publishers:
            # Create chat room
            room, created = ChatRoom.objects.get_or_create(
                room_type="publisher_admin",
                publisher=publisher,
                defaults={"is_active": random.choice([True, True, False])},
            )

            if created:
                self.stdout.write(
                    f"Created chat room for {publisher.username} (ID: {room.id})"
                )
            else:
                # Clear existing messages if room already exists
                room.messages.all().delete()
                self.stdout.write(
                    f"Using existing chat room for {publisher.username} (ID: {room.id})"
                )

            # Create messages
            start_time = timezone.now() - timedelta(days=random.randint(1, 7))

            for i in range(messages_per_chat):
                # Alternate between publisher and admin
                is_from_publisher = i % 2 == 0
                sender = publisher if is_from_publisher else admin
                message_list = (
                    publisher_messages if is_from_publisher else admin_messages
                )
                message_text = random.choice(message_list)

                # Create message with incrementing timestamps
                created_at = start_time + timedelta(minutes=i * 30)
                is_read = random.choice([True, False]) if is_from_publisher else True

                ChatMessage.objects.create(
                    room=room,
                    sender=sender,
                    message=message_text,
                    is_read=is_read,
                    created_at=created_at,
                )

            # Update room timestamp
            room.updated_at = start_time + timedelta(
                minutes=(messages_per_chat - 1) * 30
            )
            room.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"  Added {messages_per_chat} messages to room {room.id}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Successfully created {count} chat rooms with {messages_per_chat} messages each!"
            )
        )
        self.stdout.write(f"Total messages created: {count * messages_per_chat}")
        self.stdout.write(f"\nAdmin user: {admin.username}")
        self.stdout.write(f"Publishers: {', '.join([p.username for p in publishers])}")
