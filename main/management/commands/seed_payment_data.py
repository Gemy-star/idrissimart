"""
Django management command to seed payment data for testing
"""

import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from main.models import User, Payment, AdPackage, UserPackage


class Command(BaseCommand):
    help = "Seed payment data for testing the admin payments dashboard"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Number of users to create (default: 10)",
        )
        parser.add_argument(
            "--payments",
            type=int,
            default=50,
            help="Number of payments to create (default: 50)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing payment data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        num_users = options["users"]
        num_payments = options["payments"]
        clear_data = options["clear"]

        self.stdout.write(self.style.WARNING("\n🌱 Starting payment data seeding...\n"))

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing payment data..."))
            Payment.objects.all().delete()
            UserPackage.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared existing data\n"))

        # Create or get users
        self.stdout.write("Creating users...")
        users = []
        for i in range(num_users):
            username = f"test_user_{i + 1}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": f"User",
                    "last_name": f"{i + 1}",
                    "phone": f"+96650{random.randint(1000000, 9999999)}",
                    "is_premium": random.choice([True, False]),
                },
            )
            if not user.has_usable_password():
                user.set_password("testpass123")
                user.save()

            # Set random subscription end date for premium users
            if user.is_premium and not user.subscription_end:
                days_ahead = random.randint(1, 365)
                user.subscription_end = timezone.now().date() + timedelta(
                    days=days_ahead
                )
                user.save()

            users.append(user)

            if created:
                self.stdout.write(f"  ✓ Created user: {username}")

        self.stdout.write(self.style.SUCCESS(f"✓ Total users: {len(users)}\n"))

        # Create or get ad packages
        self.stdout.write("Creating ad packages...")
        packages = []
        package_data = [
            {
                "name": "الباقة الذهبية",
                "name_en": "Gold Package",
                "price": Decimal("99.00"),
                "duration_days": 30,
                "ad_count": 10,
                "ad_duration_days": 30,
                "description": "باقة مميزة للإعلانات",
                "description_en": "Premium package for advertisements",
            },
            {
                "name": "الباقة البلاتينية",
                "name_en": "Platinum Package",
                "price": Decimal("199.00"),
                "duration_days": 30,
                "ad_count": 50,
                "ad_duration_days": 60,
                "description": "أفضل باقة لرجال الأعمال",
                "description_en": "Best package for business professionals",
            },
            {
                "name": "الباقة الفضية",
                "name_en": "Silver Package",
                "price": Decimal("49.00"),
                "duration_days": 15,
                "ad_count": 5,
                "ad_duration_days": 15,
                "description": "باقة اقتصادية للمبتدئين",
                "description_en": "Economic package for beginners",
            },
        ]

        for pkg_data in package_data:
            package, created = AdPackage.objects.get_or_create(
                name=pkg_data["name"], defaults=pkg_data
            )
            packages.append(package)
            if created:
                self.stdout.write(f'  ✓ Created package: {pkg_data["name"]}')

        self.stdout.write(self.style.SUCCESS(f"✓ Total packages: {len(packages)}\n"))

        # Create payments
        self.stdout.write(f"Creating {num_payments} payments...")

        payment_statuses = [
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.PENDING,
            Payment.PaymentStatus.FAILED,
        ]

        payment_providers = [
            Payment.PaymentProvider.PAYPAL,
            Payment.PaymentProvider.PAYMOB,
            Payment.PaymentProvider.BANK_TRANSFER,
        ]

        payments_created = 0
        for i in range(num_payments):
            user = random.choice(users)
            package = random.choice(packages)
            status = random.choice(payment_statuses)
            provider = random.choice(payment_providers)

            # Create payment date within last 6 months
            days_ago = random.randint(1, 180)
            payment_date = timezone.now() - timedelta(days=days_ago)

            payment = Payment.objects.create(
                user=user,
                provider=provider,
                provider_transaction_id=f"TXN-{random.randint(100000, 999999)}",
                amount=package.price,
                currency="SAR",
                status=status,
                description=f"شراء {package.name}",
                metadata={
                    "package_id": package.id,
                    "package_name": package.name,
                    "ip_address": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
                },
                created_at=payment_date,
            )

            # Set completion date for completed payments
            if status == Payment.PaymentStatus.COMPLETED:
                payment.completed_at = payment_date + timedelta(
                    minutes=random.randint(1, 30)
                )
                payment.save()

                # Create user package for completed payments
                UserPackage.objects.create(
                    user=user,
                    payment=payment,
                    package=package,
                    ads_remaining=package.ad_count,
                    expiry_date=payment.completed_at
                    + timedelta(days=package.duration_days),
                )

            payments_created += 1

            if payments_created % 10 == 0:
                self.stdout.write(
                    f"  Created {payments_created}/{num_payments} payments..."
                )

        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {payments_created} payments\n")
        )

        # Display summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("🎉 Seeding completed successfully!"))
        self.stdout.write(self.style.SUCCESS("=" * 60 + "\n"))

        total_payments = Payment.objects.count()
        completed = Payment.objects.filter(
            status=Payment.PaymentStatus.COMPLETED
        ).count()
        pending = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()
        failed = Payment.objects.filter(status=Payment.PaymentStatus.FAILED).count()
        total_revenue = Payment.objects.filter(
            status=Payment.PaymentStatus.COMPLETED
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

        self.stdout.write(f"📊 Summary:")
        self.stdout.write(f"  • Total Users: {User.objects.count()}")
        self.stdout.write(
            f"  • Premium Users: {User.objects.filter(is_premium=True).count()}"
        )
        self.stdout.write(f"  • Total Payments: {total_payments}")
        self.stdout.write(f"    - Completed: {completed}")
        self.stdout.write(f"    - Pending: {pending}")
        self.stdout.write(f"    - Failed: {failed}")
        self.stdout.write(f"  • Total Revenue: {total_revenue} SAR")
        self.stdout.write(f"  • Ad Packages: {AdPackage.objects.count()}")
        self.stdout.write(f"  • User Packages: {UserPackage.objects.count()}")

        self.stdout.write(
            self.style.SUCCESS("\n✅ You can now view the data at /admin/payments/")
        )
        self.stdout.write(
            self.style.WARNING(
                '\n💡 Run "python manage.py seed_payment_data --clear" to reset the data\n'
            )
        )


# Import models for aggregate
from django.db import models
