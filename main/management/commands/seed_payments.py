"""
Management command to seed initial payment and premium user data for testing.

Usage:
    python manage.py seed_payments
    python manage.py seed_payments --clear  # Clear existing data first
    python manage.py seed_payments --count 50  # Create 50 payments
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import random
from decimal import Decimal

from main.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial payment and premium user data for testing the payments dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing payment data before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of payments to create (default: 30)',
        )
        parser.add_argument(
            '--premium-users',
            type=int,
            default=10,
            help='Number of premium users to create (default: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        premium_count = options['premium_users']
        clear = options['clear']

        self.stdout.write(self.style.WARNING('Starting payment data seeding...'))

        # Clear existing data if requested
        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing payment data...'))
            Payment.objects.all().delete()
            User.objects.filter(is_premium=True).update(
                is_premium=False,
                subscription_start=None,
                subscription_end=None,
                subscription_type=''
            )
            self.stdout.write(self.style.SUCCESS(' Cleared existing data'))

        # Get or create test users
        users = self._get_or_create_users(premium_count + 5)

        # Create premium users
        premium_users = self._create_premium_users(users[:premium_count])

        # Create payments
        payments = self._create_payments(users, count)

        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(' Payment Data Seeding Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Premium Users Created: {self.style.SUCCESS(len(premium_users))}')
        self.stdout.write(f'  Payments Created: {self.style.SUCCESS(len(payments))}')

        # Statistics
        completed = Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED).count()
        pending = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()
        failed = Payment.objects.filter(status=Payment.PaymentStatus.FAILED).count()
        from django.db.models import Sum
        total_revenue = Payment.objects.filter(
            status=Payment.PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0

        self.stdout.write(f'\n  Payment Statistics:')
        self.stdout.write(f'    - Completed: {self.style.SUCCESS(completed)}')
        self.stdout.write(f'    - Pending: {self.style.WARNING(pending)}')
        self.stdout.write(f'    - Failed: {self.style.ERROR(failed)}')
        self.stdout.write(f'    - Total Revenue: {self.style.SUCCESS(f"{total_revenue} SAR")}')

        self.stdout.write(self.style.SUCCESS('\n You can now view the data at /admin/payments/'))

    def _get_or_create_users(self, count):
        """Get or create test users"""
        self.stdout.write('Creating test users...')
        users = []

        for i in range(count):
            username = f'test_user_{i+1}'
            email = f'test_user_{i+1}@example.com'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test',
                    'last_name': f'User {i+1}',
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()

            users.append(user)

        self.stdout.write(self.style.SUCCESS(f' Created/found {len(users)} test users'))
        return users

    def _create_premium_users(self, users):
        """Create premium users with active subscriptions"""
        self.stdout.write('Creating premium users...')
        premium_users = []

        today = timezone.now().date()

        for i, user in enumerate(users):
            # Vary subscription types
            if i % 3 == 0:
                # Active monthly subscription
                subscription_start = today - timedelta(days=random.randint(1, 25))
                subscription_end = subscription_start + timedelta(days=30)
                subscription_type = 'monthly'
            elif i % 3 == 1:
                # Active yearly subscription
                subscription_start = today - timedelta(days=random.randint(1, 300))
                subscription_end = subscription_start + timedelta(days=365)
                subscription_type = 'yearly'
            else:
                # Expired subscription (for testing)
                subscription_start = today - timedelta(days=random.randint(40, 90))
                subscription_end = today - timedelta(days=random.randint(1, 10))
                subscription_type = 'monthly'

            user.is_premium = True
            user.subscription_start = subscription_start
            user.subscription_end = subscription_end
            user.subscription_type = subscription_type
            user.save()

            premium_users.append(user)

        active_count = User.objects.filter(
            is_premium=True,
            subscription_end__gte=today
        ).count()

        self.stdout.write(self.style.SUCCESS(
            f' Created {len(premium_users)} premium users ({active_count} active)'
        ))
        return premium_users

    def _create_payments(self, users, count):
        """Create test payments with various statuses and dates"""
        self.stdout.write('Creating payments...')
        payments = []

        # Package options
        packages = [
            {
                'name': 'Gold Package',
                'price': Decimal('99.00'),
                'description': 'Monthly subscription - Gold Package - Featured ads and instant support'
            },
            {
                'name': 'Platinum Package',
                'price': Decimal('199.00'),
                'description': 'Monthly subscription - Platinum Package - All features unlimited'
            },
            {
                'name': 'Featured Ad',
                'price': Decimal('49.00'),
                'description': 'Featured ad for 7 days'
            },
            {
                'name': 'Urgent Ad',
                'price': Decimal('29.00'),
                'description': 'Urgent ad for 3 days'
            },
        ]

        # Payment providers
        providers = [
            Payment.PaymentProvider.PAYPAL,
            Payment.PaymentProvider.PAYMOB,
            Payment.PaymentProvider.BANK_TRANSFER,
        ]

        # Payment statuses (weighted towards completed)
        statuses = [
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.PENDING,
            Payment.PaymentStatus.FAILED,
        ]

        # Create payments over the last 6 months
        now = timezone.now()

        for i in range(count):
            # Random date within last 6 months
            days_ago = random.randint(0, 180)
            created_at = now - timedelta(days=days_ago)

            # Select random package
            package = random.choice(packages)

            # Select random user
            user = random.choice(users)

            # Select random provider
            provider = random.choice(providers)

            # Select random status
            status = random.choice(statuses)

            # Determine completed_at based on status
            if status == Payment.PaymentStatus.COMPLETED:
                completed_at = created_at + timedelta(minutes=random.randint(1, 30))
            else:
                completed_at = None

            # Create payment
            payment = Payment.objects.create(
                user=user,
                provider=provider,
                provider_transaction_id=f'TXN_{random.randint(100000, 999999)}',
                amount=package['price'],
                currency='SAR',
                status=status,
                description=package['description'],
                metadata={
                    'package_name': package['name'],
                    'package_price': str(package['price']),
                },
                created_at=created_at,
                completed_at=completed_at,
            )

            payments.append(payment)

        self.stdout.write(self.style.SUCCESS(f' Created {len(payments)} payments'))
        return payments
