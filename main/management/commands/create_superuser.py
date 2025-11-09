from django.core.management.base import BaseCommand

from main.models import User


class Command(BaseCommand):
    """
    A custom management command to create a superuser with predefined credentials.

    Usage:
    python manage.py create_superuser
    """

    help = "Creates a superuser with username 'admin' and email 'info@idrissimart.com'"

    def handle(self, *args, **options):
        username = "admin"
        email = "info@idrissimart.com"
        password = "admin123456"

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  User '{username}' already exists. Skipping creation."
                )
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  User with email '{email}' already exists. Skipping creation."
                )
            )
            return

        # Create the superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name="Admin",
                last_name="Idrissimart",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Superuser created successfully!\n"
                    f"   Username: {username}\n"
                    f"   Email: {email}\n"
                    f"   Password: {password}\n"
                    f"   First Name: {user.first_name}\n"
                    f"   Last Name: {user.last_name}\n"
                    f"   Is Superuser: {user.is_superuser}\n"
                    f"   Is Staff: {user.is_staff}"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to create superuser: {str(e)}")
            )
