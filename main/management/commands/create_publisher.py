from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from main.models import User, ClassifiedAd, Category, ChatRoom, ChatMessage
from content.models import Country


class Command(BaseCommand):
    """
    Custom management command to create a publisher user for development/testing.

    This command creates a user with a 'publisher' profile type.
    Email: publisher@admin.com
    Password: admin123456
    Username: publisher

    If the user already exists, it will report it and exit gracefully.
    """

    help = _("Creates a publisher user with predefined credentials.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--num_ads",
            type=int,
            default=3,
            help=_("The number of sample ads to create for the publisher."),
        )
        parser.add_argument(
            "--country_code",
            type=str,
            default=None,
            help=_("The country code (e.g., 'EG', 'SA') for the ads."),
        )
        parser.add_argument(
            "--city",
            type=str,
            default="Riyadh",
            help=_("The city for the ads."),
        )

    def handle(self, *args, **options):
        email = "publisher@admin.com"
        password = "admin123456"
        username = "publisher"

        user = User.objects.filter(email=email).first()

        if user:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found existing publisher '{username}' with email '{email}'."
                )
            )
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                profile_type="publisher",
                verification_status="verified",
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created publisher '{username}' with email '{email}'."
                )
            )

        # --- Create sample ads for the new publisher ---
        num_ads_to_create = options["num_ads"]
        country_code = options["country_code"]
        city = options["city"]
        if num_ads_to_create <= 0:
            self.stdout.write(
                self.style.HTTP_INFO("Skipping ad creation as num_ads is not positive.")
            )
            return

        self.stdout.write(
            self.style.HTTP_INFO(
                f"Attempting to create {num_ads_to_create} sample ads..."
            )
        )

        try:
            # Get the country
            country = None
            if country_code:
                try:
                    country = Country.objects.get(
                        code__iexact=country_code, is_active=True
                    )
                    self.stdout.write(
                        self.style.HTTP_INFO(
                            f"Using specified country: {country.name} ({country_code})"
                        )
                    )
                except Country.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Country with code '{country_code}' not found or is not active. Aborting ad creation."
                        )
                    )
                    return
            else:
                country = Country.objects.filter(is_active=True).first()
                if country:
                    self.stdout.write(
                        self.style.HTTP_INFO(
                            f"Using first available country: {country.name}"
                        )
                    )

            # Get the first available classified category
            category = Category.objects.filter(
                section_type="classified", is_active=True
            ).first()

            if not country or not category:
                self.stdout.write(
                    self.style.WARNING(
                        "Could not find an active country or classified category. Skipping ad creation."
                    )
                )
                return

            for i in range(1, num_ads_to_create + 1):
                ClassifiedAd.objects.create(
                    user=user,
                    category=category,
                    country=country,
                    title=f"Sample Ad {i} by {username}",
                    description=f"This is a detailed description for sample ad number {i}.",
                    price=100 + (i * 20),
                    city=city,
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {num_ads_to_create} sample ads for {username}."
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"An error occurred while creating sample ads: {e}")
            )

        # --- Create a sample chat conversation ---
        self.stdout.write(self.style.HTTP_INFO("Attempting to create a sample chat..."))
        try:
            # 1. Get or create a customer to chat with
            customer_username = "chat_customer"
            customer_user, created = User.objects.get_or_create(
                username=customer_username,
                defaults={
                    "email": "customer@example.com",
                    "profile_type": "customer",
                    "verification_status": "verified",
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created sample user '{customer_username}' for chat."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found existing user '{customer_username}' for chat."
                    )
                )

            # 2. Get or create a chat room between the publisher and the customer
            chat_room, chat_created = ChatRoom.objects.get_or_create(
                publisher=user,
                client=customer_user,
                defaults={"room_type": "publisher_client"},
            )

            # 3. Add some messages to the chat
            ChatMessage.objects.create(
                room=chat_room,
                sender=customer_user,
                message="مرحباً، هل هذا المنتج ما زال متوفراً؟",
            )
            ChatMessage.objects.create(
                room=chat_room, sender=user, message="نعم، ما زال متوفراً!"
            )
            ChatMessage.objects.create(
                room=chat_room,
                sender=customer_user,
                message="رائع، هل يمكنك إخباري المزيد عنه؟",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created a sample chat for '{username}'."
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"An error occurred while creating the sample chat: {e}"
                )
            )

        # --- Create sample support chat room ---
        self.stdout.write(
            self.style.HTTP_INFO("Attempting to create sample support tickets...")
        )
        try:
            # Get or create admin user for support
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                self.stdout.write(
                    self.style.WARNING(
                        "No admin user found. Skipping support chat creation."
                    )
                )
            else:
                # Create publisher-admin support chat room
                support_room, support_created = ChatRoom.objects.get_or_create(
                    publisher=user,
                    client=None,  # Admin chats have no client
                    room_type="publisher_admin",
                    defaults={"is_active": True},
                )

                if support_created:
                    # Add sample support messages
                    ChatMessage.objects.create(
                        room=support_room,
                        sender=user,
                        message="مرحباً، لدي مشكلة في نشر إعلاني الجديد.",
                    )
                    ChatMessage.objects.create(
                        room=support_room,
                        sender=admin_user,
                        message="مرحباً! سأساعدك في حل هذه المشكلة. هل يمكنك إخباري بالتفاصيل؟",
                    )
                    ChatMessage.objects.create(
                        room=support_room,
                        sender=user,
                        message="عند محاولة رفع الصور، أحصل على رسالة خطأ.",
                    )
                    ChatMessage.objects.create(
                        room=support_room,
                        sender=admin_user,
                        message="تأكد من أن حجم الصور لا يتجاوز 5 ميجابايت وأنها بصيغة JPG أو PNG.",
                        is_read=False,
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully created support chat room for '{username}'."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Found existing support chat room for '{username}'."
                        )
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"An error occurred while creating support chat: {e}")
            )
