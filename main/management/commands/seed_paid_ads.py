"""
Django management command to seed PaidBanner data for testing
Creates sample paid advertisements including shared advertising spaces for carousel testing
"""

import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
import requests
from io import BytesIO

User = get_user_model()


class Command(BaseCommand):
    help = "Seed PaidBanner data for testing (including shared advertising spaces)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ads",
            type=int,
            default=20,
            help="Number of paid ads to create (default: 20)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing paid banner data before seeding",
        )
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="Skip downloading placeholder images (faster but ads won't have images)",
        )

    def get_placeholder_image(self, width=1200, height=600, text="Ad"):
        """
        Get a placeholder image from a placeholder service
        """
        try:
            url = f"https://via.placeholder.com/{width}x{height}/667eea/ffffff?text={text.replace(' ', '+')}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content, name=f"ad_{text.lower().replace(' ', '_')}.jpg")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Failed to download image: {str(e)}"))
        return None

    @transaction.atomic
    def handle(self, *args, **options):
        from main.models import PaidBanner, Category
        from content.models import Country

        num_ads = options["ads"]
        clear_data = options["clear"]
        skip_images = options["no_images"]

        self.stdout.write(self.style.WARNING("\n🌱 Starting paid banner seeding...\n"))

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing paid banner data..."))
            PaidBanner.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared existing data\n"))

        # Get or create advertisers
        self.stdout.write("Creating/getting advertisers...")
        advertisers = []
        for i in range(5):  # Create 5 advertisers
            username = f"advertiser_{i + 1}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": f"Advertiser",
                    "last_name": f"{i + 1}",
                    "phone": f"+96650{random.randint(1000000, 9999999)}",
                },
            )
            if created and not user.has_usable_password():
                user.set_password("testpass123")
                user.save()
            advertisers.append(user)
            status = "Created" if created else "Found"
            self.stdout.write(self.style.SUCCESS(f"  ✓ {status} advertiser: {username}"))

        # Get countries
        countries = list(Country.objects.all()[:3])  # Get first 3 countries
        if not countries:
            self.stdout.write(self.style.ERROR("No countries found! Please run populate_countries first."))
            return

        # Get categories
        categories = list(Category.objects.filter(is_active=True, parent__isnull=False)[:10])
        if not categories:
            self.stdout.write(self.style.WARNING("No categories found. Ads will use general placement."))

        # Define advertising spaces with their configurations
        advertising_spaces = [
            {
                "space": "homepage-hero-banner",
                "ad_type": PaidBanner.AdType.BANNER,
                "placement_type": PaidBanner.PlacementType.GENERAL,
                "count": 3,  # 3 ads will share this space
            },
            {
                "space": "homepage-sidebar-top",
                "ad_type": PaidBanner.AdType.SIDEBAR,
                "placement_type": PaidBanner.PlacementType.GENERAL,
                "count": 2,  # 2 ads will share this space
            },
            {
                "space": "homepage-featured-middle",
                "ad_type": PaidBanner.AdType.FEATURED_BOX,
                "placement_type": PaidBanner.PlacementType.GENERAL,
                "count": 3,  # 3 ads will share this space
            },
            {
                "space": "category-tech-banner",
                "ad_type": PaidBanner.AdType.BANNER,
                "placement_type": PaidBanner.PlacementType.CATEGORY,
                "count": 2,  # 2 ads will share this space
            },
            {
                "space": "category-fashion-sidebar",
                "ad_type": PaidBanner.AdType.SIDEBAR,
                "placement_type": PaidBanner.PlacementType.CATEGORY,
                "count": 2,  # 2 ads will share this space
            },
        ]

        # Sample ad data templates
        ad_templates = [
            {
                "title": "Spring Sale - Up to 50% Off",
                "title_ar": "تخفيضات الربيع - خصم حتى 50%",
                "description": "Don't miss our biggest sale of the season! Amazing deals on all categories.",
                "description_ar": "لا تفوت أكبر تخفيضات الموسم! عروض مذهلة على جميع الأقسام.",
                "company": "MegaStore",
                "cta": "Shop Now",
                "cta_ar": "تسوق الآن",
            },
            {
                "title": "New Tech Arrivals",
                "title_ar": "أحدث المنتجات التقنية",
                "description": "Discover the latest gadgets and electronics at unbeatable prices.",
                "description_ar": "اكتشف أحدث الأجهزة والإلكترونيات بأسعار لا تقبل المنافسة.",
                "company": "TechHub",
                "cta": "Explore Now",
                "cta_ar": "استكشف الآن",
            },
            {
                "title": "Fashion Week Special",
                "title_ar": "عرض أسبوع الموضة",
                "description": "Trending styles and exclusive collections just for you.",
                "description_ar": "أحدث الصيحات والمجموعات الحصرية من أجلك.",
                "company": "StyleVault",
                "cta": "View Collection",
                "cta_ar": "شاهد المجموعة",
            },
            {
                "title": "Premium Services Available",
                "title_ar": "خدمات مميزة متاحة",
                "description": "Upgrade your experience with our premium features and support.",
                "description_ar": "حسّن تجربتك مع ميزاتنا المميزة والدعم الفني.",
                "company": "ProServices",
                "cta": "Learn More",
                "cta_ar": "اعرف المزيد",
            },
            {
                "title": "Limited Time Offer",
                "title_ar": "عرض لفترة محدودة",
                "description": "Exclusive deals ending soon. Act fast to get the best prices!",
                "description_ar": "عروض حصرية تنتهي قريباً. سارع للحصول على أفضل الأسعار!",
                "company": "DealMaster",
                "cta": "Get Deal",
                "cta_ar": "احصل على العرض",
            },
            {
                "title": "Free Shipping on All Orders",
                "title_ar": "توصيل مجاني على جميع الطلبات",
                "description": "Order now and enjoy free shipping to your doorstep.",
                "description_ar": "اطلب الآن واستمتع بالتوصيل المجاني حتى باب منزلك.",
                "company": "QuickShip",
                "cta": "Order Now",
                "cta_ar": "اطلب الآن",
            },
            {
                "title": "Buy 2 Get 1 Free",
                "title_ar": "اشتري 2 واحصل على 1 مجاناً",
                "description": "Triple the value with our amazing buy 2 get 1 free promotion.",
                "description_ar": "ضاعف القيمة مع عرضنا المذهل اشتري 2 واحصل على 1 مجاناً.",
                "company": "ValueMart",
                "cta": "Shop Deal",
                "cta_ar": "تسوق العرض",
            },
            {
                "title": "Summer Collection Launch",
                "title_ar": "إطلاق مجموعة الصيف",
                "description": "Fresh styles for the season. Be the first to shop our new arrivals.",
                "description_ar": "أساليب جديدة للموسم. كن أول من يتسوق من مجموعتنا الجديدة.",
                "company": "SeasonStyle",
                "cta": "Browse Collection",
                "cta_ar": "تصفح المجموعة",
            },
        ]

        created_count = 0
        now = timezone.now()

        self.stdout.write(f"\nCreating {num_ads} paid banners...")

        # Track which templates we've used for variety
        template_index = 0

        # First, create ads for defined advertising spaces
        for space_config in advertising_spaces:
            for i in range(space_config["count"]):
                template = ad_templates[template_index % len(ad_templates)]
                template_index += 1

                advertiser = random.choice(advertisers)
                country = random.choice(countries)
                category = random.choice(categories) if categories and space_config["placement_type"] == PaidBanner.PlacementType.CATEGORY else None

                # Set dates
                start_date = now - timedelta(days=random.randint(1, 10))
                end_date = now + timedelta(days=random.randint(30, 90))

                # Determine pricing based on ad type
                pricing = {
                    PaidBanner.AdType.BANNER: Decimal("200.00"),
                    PaidBanner.AdType.SIDEBAR: Decimal("150.00"),
                    PaidBanner.AdType.POPUP: Decimal("250.00"),
                    PaidBanner.AdType.FEATURED_BOX: Decimal("180.00"),
                }

                ad_data = {
                    "title": f"{template['title']} - {space_config['space']} #{i+1}",
                    "title_ar": f"{template['title_ar']} - {space_config['space']} #{i+1}",
                    "description": template["description"],
                    "description_ar": template["description_ar"],
                    "advertiser": advertiser,
                    "company_name": template["company"],
                    "contact_email": advertiser.email,
                    "contact_phone": advertiser.phone or "+966501234567",
                    "target_url": f"https://example.com/{template['company'].lower()}",
                    "cta_text": template["cta"],
                    "cta_text_ar": template["cta_ar"],
                    "open_in_new_tab": True,
                    "ad_type": space_config["ad_type"],
                    "placement_type": space_config["placement_type"],
                    "advertising_space": space_config["space"],  # Key field for grouping
                    "country": country,
                    "category": category,
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": PaidBanner.Status.ACTIVE,
                    "is_active": True,
                    "priority": random.randint(1, 10),
                    "order": i,
                    "price": pricing[space_config["ad_type"]],
                    "currency": "EGP",
                    "payment_status": "paid",
                    "payment_reference": f"PAY-{random.randint(10000, 99999)}",
                    "views_count": random.randint(100, 5000),
                    "clicks_count": random.randint(10, 500),
                }

                ad = PaidBanner.objects.create(**ad_data)

                # Add image if not skipping
                if not skip_images:
                    dimensions = {
                        PaidBanner.AdType.BANNER: (1200, 600),
                        PaidBanner.AdType.SIDEBAR: (300, 600),
                        PaidBanner.AdType.FEATURED_BOX: (800, 400),
                        PaidBanner.AdType.POPUP: (600, 400),
                    }
                    width, height = dimensions.get(space_config["ad_type"], (1200, 600))
                    image = self.get_placeholder_image(width, height, template["company"])
                    if image:
                        ad.image.save(f"ad_{ad.id}.jpg", image, save=True)

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Created {space_config['ad_type']} ad for space '{space_config['space']}' (#{i+1})"
                    )
                )

                if created_count >= num_ads:
                    break

            if created_count >= num_ads:
                break

        # Create remaining ads as unique (no shared advertising space)
        while created_count < num_ads:
            template = ad_templates[template_index % len(ad_templates)]
            template_index += 1

            advertiser = random.choice(advertisers)
            country = random.choice(countries)
            ad_type = random.choice(list(PaidBanner.AdType))
            placement_type = random.choice([
                PaidBanner.PlacementType.GENERAL,
                PaidBanner.PlacementType.CATEGORY,
            ])
            category = random.choice(categories) if categories and placement_type == PaidBanner.PlacementType.CATEGORY else None

            start_date = now - timedelta(days=random.randint(1, 10))
            end_date = now + timedelta(days=random.randint(30, 90))

            pricing = {
                PaidBanner.AdType.BANNER: Decimal("200.00"),
                PaidBanner.AdType.SIDEBAR: Decimal("150.00"),
                PaidBanner.AdType.POPUP: Decimal("250.00"),
                PaidBanner.AdType.FEATURED_BOX: Decimal("180.00"),
            }

            ad_data = {
                "title": f"{template['title']} - Unique Ad #{created_count + 1}",
                "title_ar": f"{template['title_ar']} - إعلان فريد #{created_count + 1}",
                "description": template["description"],
                "description_ar": template["description_ar"],
                "advertiser": advertiser,
                "company_name": template["company"],
                "contact_email": advertiser.email,
                "contact_phone": advertiser.phone or "+966501234567",
                "target_url": f"https://example.com/{template['company'].lower()}/{created_count}",
                "cta_text": template["cta"],
                "cta_text_ar": template["cta_ar"],
                "open_in_new_tab": True,
                "ad_type": ad_type,
                "placement_type": placement_type,
                "advertising_space": None,  # No shared space
                "country": country,
                "category": category,
                "start_date": start_date,
                "end_date": end_date,
                "status": PaidBanner.Status.ACTIVE,
                "is_active": True,
                "priority": random.randint(1, 10),
                "order": created_count,
                "price": pricing[ad_type],
                "currency": "EGP",
                "payment_status": "paid",
                "payment_reference": f"PAY-{random.randint(10000, 99999)}",
                "views_count": random.randint(100, 5000),
                "clicks_count": random.randint(10, 500),
            }

            ad = PaidBanner.objects.create(**ad_data)

            # Add image if not skipping
            if not skip_images:
                dimensions = {
                    PaidBanner.AdType.BANNER: (1200, 600),
                    PaidBanner.AdType.SIDEBAR: (300, 600),
                    PaidBanner.AdType.FEATURED_BOX: (800, 400),
                    PaidBanner.AdType.POPUP: (600, 400),
                }
                width, height = dimensions.get(ad_type, (1200, 600))
                image = self.get_placeholder_image(width, height, template["company"])
                if image:
                    ad.image.save(f"ad_{ad.id}.jpg", image, save=True)

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Created unique {ad_type} ad (#{created_count})")
            )

        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully created {created_count} paid banners!\n"))

        # Show advertising space summary
        self.stdout.write(self.style.WARNING("📊 Advertising Space Summary:"))
        for space_config in advertising_spaces:
            count = PaidBanner.objects.filter(
                advertising_space=space_config["space"]
            ).count()
            if count > 0:
                self.stdout.write(
                    f"  • {space_config['space']}: {count} ads "
                    f"({space_config['ad_type']}, {space_config['placement_type']})"
                )

        unique_count = PaidBanner.objects.filter(advertising_space__isnull=True).count()
        self.stdout.write(f"  • Unique ads (no shared space): {unique_count}")

        self.stdout.write(self.style.WARNING("\n💡 Tips:"))
        self.stdout.write("  - Ads with the same 'advertising_space' will appear in a carousel")
        self.stdout.write("  - Visit the homepage or category pages to see the carousels in action")
        self.stdout.write("  - Check Django Admin > Paid Banners to manage ads")
        self.stdout.write(self.style.SUCCESS("\n✨ Seeding complete!\n"))
