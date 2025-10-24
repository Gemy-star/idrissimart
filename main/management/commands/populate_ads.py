import os
import random

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from content.models import Country
from main.models import AdFeature, AdImage, Category, ClassifiedAd, User


class Command(BaseCommand):
    """
    A custom management command to populate the database with dummy classified ads.
    This is useful for testing and development.

    Example usage:
    python manage.py populate_ads 50 --country_code EG
    """

    help = "Populates the database with dummy classified ads for a specific country."

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "total",
            type=int,
            help="Indicates the number of ads to be created.",
        )
        parser.add_argument(
            "--country_code",
            type=str,
            default="EG",
            help="The country code for which to create ads (e.g., EG, SA).",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        total = kwargs["total"]
        country_code = kwargs["country_code"].upper()

        fake = Faker("ar_SA")
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting to populate {total} ads for country: {country_code}"
            )
        )

        # --- 1. Get required objects ---
        try:
            country = Country.objects.get(code=country_code)
        except Country.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Country '{country_code}' not found."))
            return

        # Get a list of regular users to assign ads to.
        # Prioritize verified users (including verified vendors/merchants)
        verified_users = list(
            User.objects.filter(is_superuser=False, verification_status="verified")
        )
        regular_users = list(User.objects.filter(is_superuser=False))

        # Create a weighted pool: 70% verified users, 30% regular users
        if verified_users:
            # Use verified users more frequently
            users = verified_users * 7 + regular_users * 3
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(verified_users)} verified users and {len(regular_users)} total users."
                )
            )
        elif regular_users:
            users = regular_users
            self.stdout.write(
                self.style.WARNING("No verified users found. Using regular users only.")
            )
        else:
            # If no regular users, fall back to the first superuser.
            self.stdout.write(
                self.style.WARNING("No regular users found. Falling back to superuser.")
            )
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                self.stderr.write(
                    self.style.ERROR(
                        "No users found at all. Please create a superuser or run populate_users first."
                    )
                )
                return
            users = [superuser]

        # Get classified ad categories for the specified country
        categories = list(
            Category.get_by_section_and_country("classified", country_code)
        )
        if not categories:
            self.stderr.write(
                self.style.ERROR(
                    f"No 'classified' categories found for country '{country_code}'."
                )
            )
            return

        # Arabic ad titles and descriptions for different categories
        arabic_ad_templates = {
            "surveying": {
                "titles": [
                    "جهاز {item} للبيع بحالة ممتازة",
                    "للإيجار اليومي: جهاز {item} معاير وحديث",
                    "عرض خاص على جهاز {item} مع كافة الملحقات",
                    "جهاز {item} مستعمل للبيع بسعر مغري",
                ],
                "items": [
                    "توتال ستيشن لايكا TS07",
                    "جهاز GPS ترايمبل R10",
                    "محطة شاملة توبكون GT-1000",
                    "جهاز ليزر سكانر Trimble X7",
                    "درون فانتوم 4 RTK للمسح الجوي",
                    "جهاز ميزان Sokkia B40",
                ],
                "price_range": (2000, 150000),
            },
            "vehicles": {
                "titles": [
                    "سيارة {item} موديل {year} للبيع",
                    "امتلك {item} {year} بحالة ممتازة",
                    "عرض خاص على {item} {year}",
                    "للبيع: {item} {year} نظيفة جداً",
                ],
                "items": [
                    "تويوتا كامري",
                    "هونداي سوناتا",
                    "فورد تورس",
                    "نيسان باترول",
                    "شيفروليه تاهو",
                ],
                "price_range": (30000, 250000),
            },
            "electronics": {
                "titles": [
                    "جهاز {item} جديد بالكرتونة",
                    "{item} مستعمل بحالة ممتازة",
                    "للبيع {item} مع كامل الملحقات",
                    "خصم على {item} لفترة محدودة",
                ],
                "items": [
                    "آيفون 15 برو",
                    "لابتوب ديل XPS",
                    "شاشة سامسونج 4K",
                    "سماعات سوني WH-1000XM5",
                    "بلايستيشن 5",
                ],
                "price_range": (500, 8000),
            },
            "default": {
                "titles": [
                    "عرض خاص على {item}",
                    "{item} للبيع بسعر مناسب",
                    "{item} جديد وبحالة ممتازة",
                ],
                "items": [
                    "منتج عالي الجودة",
                    "خدمة احترافية",
                    "سلعة نادرة",
                    "عرض مميز",
                ],
                "price_range": (100, 50000),
            },
        }

        # Arabic city names by country
        cities_by_country = {
            "SA": [
                "الرياض",
                "جدة",
                "مكة المكرمة",
                "المدينة المنورة",
                "الدمام",
                "الخبر",
                "الطائف",
                "تبوك",
                "أبها",
                "نجران",
                "جازان",
                "حائل",
                "الجبيل",
                "الخرج",
                "القطيف",
            ],
            "EG": [
                "القاهرة",
                "الإسكندرية",
                "الجيزة",
                "الأقصر",
                "أسوان",
                "بورسعيد",
                "السويس",
                "طنطا",
                "المنصورة",
                "الزقازيق",
                "أسيوط",
                "الفيوم",
                "الإسماعيلية",
                "دمنهور",
                "بني سويف",
            ],
            "AE": [
                "دبي",
                "أبو ظبي",
                "الشارقة",
                "عجمان",
                "رأس الخيمة",
                "الفجيرة",
                "أم القيوين",
            ],
            "KW": [
                "مدينة الكويت",
                "حولي",
                "الفروانية",
                "الأحمدي",
                "الجهراء",
                "مبارك الكبير",
            ],
            "QA": ["الدوحة", "الريان", "الوكرة", "الخور", "أم صلال"],
            "BH": ["المنامة", "المحرق", "الرفاع", "مدينة حمد", "مدينة عيسى"],
            "OM": ["مسقط", "صلالة", "نزوى", "صحار", "البريمي"],
            "JO": ["عمان", "إربد", "الزرقاء", "العقبة", "السلط", "مأدبا"],
        }

        # --- 2. Create Ads ---
        # The loop variable `i` is intentionally unused.
        for i in range(total):
            category = random.choice(categories)

            # --- Smarter Template Selection ---
            template_key = "default"
            slug = category.slug.lower()
            if "vehicle" in slug:
                template_key = "vehicles"
            elif "electronic" in slug:
                template_key = "electronics"
            elif "survey" in slug or "equipment" in slug:
                template_key = "surveying"
            template_data = arabic_ad_templates.get(template_key)

            # Generate Title
            title_template = random.choice(template_data["titles"])
            item = random.choice(template_data["items"])
            if "{year}" in title_template:
                year = random.randint(2018, 2024)
                title = title_template.format(item=item, year=year)
            else:
                title = title_template.format(item=item)

            # Generate Description
            description = (
                fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
                + "\n"
                + f"المواصفات: {fake.sentence(nb_words=6)}.\n"
                + f"الحالة: {fake.word()}."
            )

            # Generate Price based on category
            price_min, price_max = template_data["price_range"]
            price = random.randint(price_min, price_max)

            # Generate Custom Fields
            custom_fields = {
                "brand": item.split(" ")[0],  # Use the first word of the item as brand
                "condition": random.choice(["new", "used", "used_good"]),
            }

            # Get city name based on country
            city = random.choice(
                cities_by_country.get(country_code, ["مدينة افتراضية"])
            )

            ad = ClassifiedAd.objects.create(
                user=random.choice(users),
                category=category,
                title=title,
                description=description,
                price=price,
                is_negotiable=random.choice([True, False]),
                country=country,
                city=city,
                custom_fields=custom_fields,
                status=ClassifiedAd.AdStatus.ACTIVE,
            )

            # Randomly add features to some ads (e.g., 20% chance)
            if random.random() < 0.2:
                feature_type = random.choice(AdFeature.FeatureType.choices)[0]
                end_date = timezone.now() + timezone.timedelta(
                    days=random.randint(7, 30)
                )
                AdFeature.objects.create(
                    ad=ad, feature_type=feature_type, end_date=end_date, is_active=True
                )
                # Feature added (suppressed output to avoid encoding errors)

            # --- Dynamic Image Selection ---
            image_filenames = [
                "mini-logo-dark-theme.png",
                "mini-logo-white-theme.png",
                "logo-dark-theme.png",
                "logo-white-theme.png",
            ]
            selected_image_name = random.choice(image_filenames)
            static_image_path = os.path.join(
                settings.BASE_DIR, "static", "images", "logos", selected_image_name
            )

            if os.path.exists(static_image_path):
                with open(static_image_path, "rb") as f:
                    # Use a unique name to avoid conflicts if the same image is used multiple times
                    image_name = f"{random.randint(1000, 9999)}_{selected_image_name}"
                    image_file = File(f, name=image_name)
                    AdImage.objects.create(ad=ad, image=image_file)
                # Avoid printing Arabic characters to prevent encoding errors on Windows
            else:
                self.stderr.write(
                    self.style.WARNING(
                        f"  - Warning: Static image not found. No image added for ad {ad.pk}."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully created {total} classified ads.")
        )
