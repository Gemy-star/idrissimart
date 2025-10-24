import random

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from faker import Faker

from main.models import User


class Command(BaseCommand):
    """
    A custom management command to populate the database with dummy users.
    This is useful for testing and development.

    Example usage:
    python manage.py populate_users 20
    """

    help = _("Populates the database with dummy users.")

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "total",
            type=int,
            help=_("Indicates the number of users to be created."),
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        total = kwargs["total"]
        fake = Faker("ar_EG")  # Use Arabic locale for names
        password = "admin123456"
        created_count = 0

        self.stdout.write(self.style.SUCCESS(f"Starting to populate {total} users..."))

        for _ in range(total):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = (
                f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
            )
            email = fake.unique.email()
            profile_type = random.choice(
                [choice[0] for choice in User.ProfileType.choices]
            )
            verification_status = random.choices(
                list(User.VerificationStatus), weights=[60, 10, 25, 5], k=1
            )[0]

            try:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    profile_type=profile_type,
                    verification_status=verification_status,
                )
                created_count += 1
                self.stdout.write(
                    f"  - Created user: {username} (Password: {password})"
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - Skipping duplicate user: {username} or {email}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully created {created_count} users.")
        )
