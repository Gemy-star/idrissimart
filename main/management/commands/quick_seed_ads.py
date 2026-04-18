"""
Quick seed command for PaidBanner - creates ads with simple local images (no internet required)
"""

import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

User = get_user_model()


class Command(BaseCommand):
    help = "Quick seed for PaidBanner with locally generated images"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of ads to create (default: 20)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing ads first",
        )

    def create_simple_image(self, width, height, text, bg_color, text_color):
        """Create a simple colored image with text"""
        # Create image
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw text
        draw.text((x, y), text, fill=text_color, font=font)

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        return SimpleUploadedFile(
            f"{text.lower().replace(' ', '_')}.jpg",
            buffer.read(),
            content_type='image/jpeg'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from main.models import PaidBanner, Category
        from content.models import Country

        count = options["count"]
        clear = options["clear"]

        self.stdout.write(self.style.WARNING("\n🚀 Quick seeding paid banners...\n"))

        if clear:
            self.stdout.write("Clearing existing ads...")
            PaidBanner.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared\n"))

        # Get/create advertiser
        advertiser, created = User.objects.get_or_create(
            username="demo_advertiser",
            defaults={
                "email": "advertiser@example.com",
                "first_name": "Demo",
                "last_name": "Advertiser",
            }
        )
        if created:
            advertiser.set_password("demo123")
            advertiser.save()

        # Get necessary objects
        countries = list(Country.objects.all()[:1])
        if not countries:
            self.stdout.write(self.style.ERROR("No countries found!"))
            return

        categories = list(Category.objects.filter(is_active=True, parent__isnull=False)[:5])

        # Ad space configurations with carousel grouping
        spaces = [
            {
                "name": "homepage-main-banner",
                "type": PaidBanner.AdType.BANNER,
                "placement": PaidBanner.PlacementType.GENERAL,
                "count": 3,
                "colors": [
                    ('#667eea', '#ffffff'),
                    ('#764ba2', '#ffffff'),
                    ('#f093fb', '#ffffff'),
                ]
            },
            {
                "name": "homepage-sidebar",
                "type": PaidBanner.AdType.SIDEBAR,
                "placement": PaidBanner.PlacementType.GENERAL,
                "count": 2,
                "colors": [
                    ('#43e97b', '#ffffff'),
                    ('#38f9d7', '#000000'),
                ]
            },
            {
                "name": "homepage-featured",
                "type": PaidBanner.AdType.FEATURED_BOX,
                "placement": PaidBanner.PlacementType.GENERAL,
                "count": 3,
                "colors": [
                    ('#fa709a', '#ffffff'),
                    ('#fee140', '#000000'),
                    ('#30cfd0', '#ffffff'),
                ]
            },
        ]

        if categories:
            spaces.append({
                "name": "category-banner",
                "type": PaidBanner.AdType.BANNER,
                "placement": PaidBanner.PlacementType.CATEGORY,
                "count": 2,
                "colors": [
                    ('#a8edea', '#000000'),
                    ('#fed6e3', '#000000'),
                ]
            })

        titles = [
            ("Spring Sale", "تخفيضات الربيع"),
            ("Tech Deals", "عروض التقنية"),
            ("Fashion Week", "أسبوع الموضة"),
            ("New Arrivals", "وصل حديثاً"),
            ("Limited Offer", "عرض محدود"),
            ("Premium Services", "خدمات مميزة"),
            ("Free Shipping", "توصيل مجاني"),
            ("Best Sellers", "الأكثر مبيعاً"),
        ]

        companies = ["MegaStore", "TechHub", "StyleVault", "ProShop", "DealMaster"]

        created = 0
        now = timezone.now()

        self.stdout.write("Creating ads with local images...")

        # Create ads for each space
        title_idx = 0
        for space_config in spaces:
            for i in range(space_config["count"]):
                if created >= count:
                    break

                title_en, title_ar = titles[title_idx % len(titles)]
                company = companies[title_idx % len(companies)]
                bg_color, text_color = space_config["colors"][i]

                # Dimensions based on ad type
                dimensions = {
                    PaidBanner.AdType.BANNER: (1200, 600),
                    PaidBanner.AdType.SIDEBAR: (300, 600),
                    PaidBanner.AdType.FEATURED_BOX: (800, 400),
                }
                width, height = dimensions.get(space_config["type"], (1200, 600))

                ad = PaidBanner.objects.create(
                    title=f"{title_en} - {company} #{i+1}",
                    title_ar=f"{title_ar} - {company} #{i+1}",
                    description=f"Amazing deals and offers from {company}. Don't miss out!",
                    description_ar=f"عروض وصفقات مذهلة من {company}. لا تفوتها!",
                    advertiser=advertiser,
                    company_name=company,
                    contact_email=advertiser.email,
                    contact_phone="+966501234567",
                    target_url=f"https://example.com/{company.lower()}",
                    cta_text="Shop Now",
                    cta_text_ar="تسوق الآن",
                    ad_type=space_config["type"],
                    placement_type=space_config["placement"],
                    advertising_space=space_config["name"],
                    country=countries[0],
                    category=random.choice(categories) if categories and space_config["placement"] == PaidBanner.PlacementType.CATEGORY else None,
                    start_date=now - timedelta(days=5),
                    end_date=now + timedelta(days=60),
                    status=PaidBanner.Status.ACTIVE,
                    is_active=True,
                    priority=random.randint(1, 10),
                    price=Decimal("200.00"),
                    currency="EGP",
                    payment_status="paid",
                    views_count=random.randint(500, 3000),
                    clicks_count=random.randint(50, 300),
                )

                # Create and attach image
                image = self.create_simple_image(
                    width, height,
                    f"{company}\n{title_en}",
                    bg_color, text_color
                )
                ad.image.save(f"ad_{ad.id}.jpg", image, save=True)

                created += 1
                title_idx += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ {space_config['type']} - {space_config['name']} #{i+1}"
                ))

        # Fill remaining with unique ads
        while created < count:
            title_en, title_ar = titles[title_idx % len(titles)]
            company = companies[title_idx % len(companies)]

            ad_type = random.choice(list(PaidBanner.AdType.choices))[0]
            dimensions = {
                'banner': (1200, 600),
                'sidebar': (300, 600),
                'featured_box': (800, 400),
                'popup': (600, 400),
            }
            width, height = dimensions.get(ad_type, (1200, 600))

            ad = PaidBanner.objects.create(
                title=f"{title_en} - {company} (Unique #{created+1})",
                title_ar=f"{title_ar} - {company} (فريد #{created+1})",
                description=f"Exclusive offer from {company}",
                description_ar=f"عرض حصري من {company}",
                advertiser=advertiser,
                company_name=company,
                contact_email=advertiser.email,
                contact_phone="+966501234567",
                target_url=f"https://example.com/{company.lower()}/{created}",
                cta_text="View Offer",
                cta_text_ar="شاهد العرض",
                ad_type=ad_type,
                placement_type=PaidBanner.PlacementType.GENERAL,
                advertising_space=None,
                country=countries[0],
                start_date=now - timedelta(days=5),
                end_date=now + timedelta(days=60),
                status=PaidBanner.Status.ACTIVE,
                is_active=True,
                priority=random.randint(1, 10),
                price=Decimal("150.00"),
                currency="EGP",
                payment_status="paid",
                views_count=random.randint(200, 1000),
                clicks_count=random.randint(20, 100),
            )

            # Create and attach image
            image = self.create_simple_image(
                width, height,
                f"{company}\n{title_en}",
                '#667eea', '#ffffff'
            )
            ad.image.save(f"ad_{ad.id}.jpg", image, save=True)

            created += 1
            title_idx += 1
            self.stdout.write(self.style.SUCCESS(f"  ✓ Unique ad #{created}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Created {created} ads!"))

        # Summary
        self.stdout.write(self.style.WARNING("\n📊 Summary:"))
        for space in spaces:
            ads = PaidBanner.objects.filter(advertising_space=space["name"])
            if ads.exists():
                self.stdout.write(f"  • {space['name']}: {ads.count()} ads (carousel)")

        unique = PaidBanner.objects.filter(advertising_space__isnull=True).count()
        self.stdout.write(f"  • Unique (non-carousel): {unique} ads")

        self.stdout.write(self.style.SUCCESS("\n✨ Done!\n"))
