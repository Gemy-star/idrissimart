"""
Management command to seed saved searches for different user types.

Usage:
    python manage.py seed_saved_searches
    python manage.py seed_saved_searches --clear
    python manage.py seed_saved_searches --count 10
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import uuid

from main.models import SavedSearch

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed saved searches for admin, publisher, and client users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing saved searches before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of saved searches per user type (default: 5)',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        self.stdout.write(self.style.WARNING('Starting saved searches seeding...'))

        # Clear existing data if requested
        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing saved searches...'))
            SavedSearch.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(' Cleared existing data'))

        # Get or create users
        admin_user = self._get_or_create_admin()
        publisher_user = self._get_or_create_publisher()
        client_user = self._get_or_create_client()

        # Create saved searches for each user type
        admin_searches = self._create_admin_searches(admin_user, count)
        publisher_searches = self._create_publisher_searches(publisher_user, count)
        client_searches = self._create_client_searches(client_user, count)

        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(' Saved Searches Seeding Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Admin Searches Created: {self.style.SUCCESS(len(admin_searches))}')
        self.stdout.write(f'  Publisher Searches Created: {self.style.SUCCESS(len(publisher_searches))}')
        self.stdout.write(f'  Client Searches Created: {self.style.SUCCESS(len(client_searches))}')
        self.stdout.write(f'  Total: {self.style.SUCCESS(len(admin_searches) + len(publisher_searches) + len(client_searches))}')

        self.stdout.write(self.style.SUCCESS('\n You can now view saved searches at /classifieds/saved-searches/'))

    def _get_or_create_admin(self):
        """Get or create admin user"""
        self.stdout.write('Getting/creating admin user...')
        user, created = User.objects.get_or_create(
            username='admin_user',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(' Created admin user'))
        else:
            self.stdout.write(self.style.SUCCESS(' Found existing admin user'))
        return user

    def _get_or_create_publisher(self):
        """Get or create publisher user"""
        self.stdout.write('Getting/creating publisher user...')
        user, created = User.objects.get_or_create(
            username='publisher_user',
            defaults={
                'email': 'publisher@example.com',
                'first_name': 'Publisher',
                'last_name': 'User',
            }
        )
        if created:
            user.set_password('publisher123')
            user.save()
            self.stdout.write(self.style.SUCCESS(' Created publisher user'))
        else:
            self.stdout.write(self.style.SUCCESS(' Found existing publisher user'))
        return user

    def _get_or_create_client(self):
        """Get or create client user"""
        self.stdout.write('Getting/creating client user...')
        user, created = User.objects.get_or_create(
            username='client_user',
            defaults={
                'email': 'client@example.com',
                'first_name': 'Client',
                'last_name': 'User',
            }
        )
        if created:
            user.set_password('client123')
            user.save()
            self.stdout.write(self.style.SUCCESS(' Created client user'))
        else:
            self.stdout.write(self.style.SUCCESS(' Found existing client user'))
        return user

    def _create_admin_searches(self, user, count):
        """Create saved searches for admin user"""
        self.stdout.write('Creating admin saved searches...')
        searches = []

        admin_queries = [
            ('Pending Ads Review', 'status=pending&sort=-created_at'),
            ('Flagged Content', 'is_flagged=true&sort=-updated_at'),
            ('High Value Listings', 'min_price=10000&sort=-price'),
            ('New Users Ads', 'days=7&sort=-created_at'),
            ('Premium Listings', 'is_premium=true&sort=-views'),
            ('Expired Ads', 'status=expired&sort=-expires_at'),
            ('Most Reported', 'sort=-reports_count'),
            ('Verification Needed', 'verification_status=pending'),
        ]

        for i in range(min(count, len(admin_queries))):
            name, query = admin_queries[i]
            search, created = SavedSearch.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'query_params': query,
                    'email_notifications': i % 2 == 0,
                    'unsubscribe_token': uuid.uuid4(),
                }
            )
            if created:
                searches.append(search)

        self.stdout.write(self.style.SUCCESS(f' Created {len(searches)} admin searches'))
        return searches

    def _create_publisher_searches(self, user, count):
        """Create saved searches for publisher user"""
        self.stdout.write('Creating publisher saved searches...')
        searches = []

        publisher_queries = [
            ('My Active Listings', 'status=active&user=me&sort=-views'),
            ('Electronics Deals', 'category=electronics&condition=new&sort=-created_at'),
            ('Real Estate Listings', 'category=real-estate&sort=-price'),
            ('Vehicles Under 50k', 'category=vehicles&max_price=50000&sort=-created_at'),
            ('Furniture in My City', 'category=furniture&location=my_city&sort=-price'),
            ('Jobs in Tech', 'category=jobs&keywords=technology,software&sort=-created_at'),
            ('Services Near Me', 'category=services&radius=10km&sort=-rating'),
            ('Fashion & Accessories', 'category=fashion&condition=new&sort=-created_at'),
        ]

        for i in range(min(count, len(publisher_queries))):
            name, query = publisher_queries[i]
            search, created = SavedSearch.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'query_params': query,
                    'email_notifications': i < 3,
                    'unsubscribe_token': uuid.uuid4(),
                }
            )
            if created:
                searches.append(search)

        self.stdout.write(self.style.SUCCESS(f' Created {len(searches)} publisher searches'))
        return searches

    def _create_client_searches(self, user, count):
        """Create saved searches for client user"""
        self.stdout.write('Creating client saved searches...')
        searches = []

        client_queries = [
            ('Affordable Electronics', 'category=electronics&max_price=1000&sort=price'),
            ('Apartments for Rent', 'category=real-estate&listing_type=rent&sort=-created_at'),
            ('Used Cars', 'category=vehicles&condition=used&max_price=30000&sort=price'),
            ('Home Appliances', 'category=appliances&condition=new&sort=-created_at'),
            ('Remote Jobs', 'category=jobs&keywords=remote,work-from-home&sort=-created_at'),
            ('Gaming Consoles', 'category=electronics&keywords=playstation,xbox,nintendo&sort=price'),
            ('Books & Textbooks', 'category=books&sort=price'),
            ('Sports Equipment', 'category=sports&condition=new&sort=-created_at'),
        ]

        for i in range(min(count, len(client_queries))):
            name, query = client_queries[i]
            search, created = SavedSearch.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'query_params': query,
                    'email_notifications': i % 3 == 0,
                    'unsubscribe_token': uuid.uuid4(),
                }
            )
            if created:
                searches.append(search)

        self.stdout.write(self.style.SUCCESS(f' Created {len(searches)} client searches'))
        return searches
