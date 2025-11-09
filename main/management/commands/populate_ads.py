from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.core.files import File
from decimal import Decimal
from faker import Faker
import random
import os
from pathlib import Path

from content.models import Country
from main.models import Category, ClassifiedAd, User, AdImage


class Command(BaseCommand):
    """
    A custom management command to populate the database with surveying engineering classified ads.
    """

    help = "Populates the database with surveying engineering classified ads for a specific country."

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
        parser.add_argument(
            "--update_existing",
            action="store_true",
            help="Update existing ads without images to add images.",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        total = kwargs["total"]
        country_code = kwargs["country_code"].upper()
        update_existing = kwargs.get("update_existing", False)

        fake = Faker("ar_EG")

        # Check if update_existing flag is set
        if update_existing:
            self.update_existing_ads()
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting to populate {total} surveying engineering ads for country: {country_code}"
            )
        )

        # --- 1. Get required objects ---
        try:
            country = Country.objects.get(code=country_code)
        except Country.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Country {country_code} not found. Please run populate_countries first."
                )
            )
            return

        # Get users to assign ads to
        users = list(User.objects.filter(is_superuser=False))
        if not users:
            self.stdout.write(
                self.style.ERROR("No users found. Please run populate_users first.")
            )
            return

        # Get surveying categories
        categories = list(
            Category.objects.filter(
                section_type=Category.SectionType.CLASSIFIED,
                country=country,
                parent__isnull=False,  # Get subcategories only
            )
        )
        if not categories:
            self.stdout.write(
                self.style.ERROR(
                    "No classified categories found. Please run populate_categories first."
                )
            )
            return

        # Define surveying equipment data per category
        surveying_data = self.get_surveying_equipment_data()

        created_count = 0
        for i in range(total):
            category = random.choice(categories)
            user = random.choice(users)

            # Get specific data for this category
            category_name = category.name_ar
            if "مستعمل" in category_name:
                ads_data = surveying_data["used_equipment"]
            elif "إيجار" in category_name:
                ads_data = surveying_data["rental"]
            elif "صيانة" in category_name:
                ads_data = surveying_data["maintenance"]
            elif "كتب" in category_name:
                ads_data = surveying_data["books"]
            else:
                ads_data = surveying_data["used_equipment"]  # default

            ad_data = random.choice(ads_data)

            # Create the classified ad
            try:
                ad = ClassifiedAd.objects.create(
                    user=user,
                    category=category,
                    title=ad_data["title"],
                    description=ad_data["description"],
                    price=Decimal(str(ad_data["price"])),
                    is_negotiable=ad_data.get("is_negotiable", True),
                    country=country,
                    city=random.choice(
                        [
                            "القاهرة",
                            "الجيزة",
                            "الإسكندرية",
                            "المنصورة",
                            "طنطا",
                            "أسوان",
                            "الأقصر",
                            "بورسعيد",
                            "السويس",
                            "شرم الشيخ",
                        ]
                    ),
                    custom_fields=ad_data.get("custom_fields", {}),
                    status=random.choices(
                        [ClassifiedAd.AdStatus.ACTIVE, ClassifiedAd.AdStatus.PENDING],
                        weights=[85, 15],
                        k=1,
                    )[0],
                    visibility_type="public",
                    require_login_for_contact=(
                        random.choice([True, False]) if random.random() < 0.3 else False
                    ),
                    is_hidden=False,
                    allow_cart=(
                        random.choice([True, False]) if random.random() < 0.2 else False
                    ),
                    cart_enabled_by_admin=False,
                    is_urgent=(
                        random.choice([True, False]) if random.random() < 0.2 else False
                    ),
                    is_highlighted=(
                        random.choice([True, False])
                        if random.random() < 0.15
                        else False
                    ),
                    views_count=random.randint(0, 200),
                    created_at=fake.date_time_between(
                        start_date="-30d",
                        end_date="now",
                        tzinfo=timezone.get_current_timezone(),
                    ),
                )

                created_count += 1
                if created_count % 10 == 0:
                    self.stdout.write(f"  Created {created_count}/{total} ads...")

                # Add images to the ad
                self.add_images_to_ad(ad)

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to create ad {i+1}: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully created {created_count} surveying engineering ads!"
            )
        )

    def add_images_to_ad(self, ad):
        """Add images to a classified ad from static/images/ads directory"""
        try:
            # Get the path to static/images/ads
            # From: main/management/commands/populate_ads.py
            # To: static/images/ads
            # Go up 4 levels: commands -> management -> main -> idrissimart (project root)
            static_images_path = (
                Path(__file__).resolve().parent.parent.parent.parent
                / "static"
                / "images"
                / "ads"
            )

            if not static_images_path.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Images directory not found: {static_images_path}"
                    )
                )
                return

            # Get all image files in the directory
            image_files = list(static_images_path.glob("*.jpg")) + list(
                static_images_path.glob("*.png")
            )

            if not image_files:
                self.stdout.write(
                    self.style.WARNING("No image files found in ads directory")
                )
                return

            # Randomly select 1-2 images (we only have 2 images)
            num_images = random.randint(1, min(2, len(image_files)))
            selected_images = random.sample(image_files, num_images)

            # Add images to the ad
            for order, image_path in enumerate(selected_images, start=1):
                # Create a new File object with unique name
                file_obj = File(
                    open(image_path, "rb"),
                    name=f"ad_{ad.id}_{order}_{image_path.name}",
                )

                # Create the AdImage object
                ad_image = AdImage(
                    ad=ad,
                    order=order,
                )
                ad_image.image.save(
                    f"ad_{ad.id}_{order}_{image_path.name}", file_obj, save=True
                )

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Failed to add images to ad {ad.id}: {e}")
            )

    def update_existing_ads(self):
        """Update all existing ads to have images from static/images/ads"""
        self.stdout.write(
            self.style.SUCCESS("Updating all existing ads to add/update images...")
        )

        # Get ALL classified ads
        all_ads = ClassifiedAd.objects.all()
        total_ads = all_ads.count()

        if total_ads == 0:
            self.stdout.write(self.style.WARNING("No ads found in database."))
            return

        self.stdout.write(f"Found {total_ads} ads to update.")

        updated_count = 0
        skipped_count = 0

        for ad in all_ads:
            try:
                # Check if ad already has images
                existing_images_count = ad.images.count()

                if existing_images_count > 0:
                    # Delete existing images and add new ones
                    ad.images.all().delete()
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Deleted {existing_images_count} existing images for ad {ad.id}"
                        )
                    )

                # Add new images
                self.add_images_to_ad(ad)
                updated_count += 1

                if updated_count % 10 == 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Updated {updated_count}/{total_ads} ads..."
                        )
                    )

            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Failed to update ad {ad.id}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully updated {updated_count} ads with images!"
            )
        )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Skipped {skipped_count} ads due to errors.")
            )

    def get_surveying_equipment_data(self):
        """Returns realistic surveying equipment data for different categories"""
        return {
            "used_equipment": [
                {
                    "title": "توتال ستيشن لايكا TC407 للبيع",
                    "description": "جهاز توتال ستيشن لايكا TC407 حالة ممتازة، تم استخدامه لمدة سنتين فقط في مشاريع صغيرة. يأتي مع حقيبة النقل الأصلية وجميع الملحقات. دقة القياس ±2 ثانية. مناسب للمساحين المبتدئين والمتوسطين.",
                    "price": 45000,
                    "custom_fields": {
                        "brand": "Leica",
                        "model": "TC407",
                        "condition": "ممتاز",
                        "year_purchased": "2022",
                        "usage_hours": "800 ساعة",
                        "warranty_remaining": "سنة واحدة",
                    },
                },
                {
                    "title": "جهاز GPS تريمبل R8s مستعمل",
                    "description": "جهاز استقبال GPS/GNSS تريمبل R8s، دقة RTK تصل إلى 1 سم. مناسب للمسح الجيوديسي والمشاريع الهندسية الكبيرة. يأتي مع قاعدة البيانات والشاحن ومجموعة من العواكس.",
                    "price": 85000,
                    "custom_fields": {
                        "brand": "Trimble",
                        "model": "R8s",
                        "condition": "جيد جداً",
                        "year_purchased": "2021",
                        "usage_hours": "1200 ساعة",
                        "warranty_remaining": "منتهية",
                    },
                },
                {
                    "title": "مستوى ليزر روتيو RL-H5A",
                    "description": "مستوى ليزر دوار روتيو RL-H5A للأعمال الإنشائية. مداه 500 متر، مقاوم للماء والغبار. تم استخدامه في مشروع واحد فقط. حالة كالجديد مع جميع الملحقات الأصلية.",
                    "price": 28000,
                    "custom_fields": {
                        "brand": "Roteo",
                        "model": "RL-H5A",
                        "condition": "كالجديد",
                        "year_purchased": "2023",
                        "usage_hours": "200 ساعة",
                        "warranty_remaining": "سنتين",
                    },
                },
                {
                    "title": "نيكون نيفو C5 توتال ستيشن مستعمل",
                    "description": "جهاز توتال ستيشن نيكون نيفو C5 بحالة جيدة. دقة ±5 ثواني، مناسب للأعمال الطبوغرافية والهندسية. يحتوي على ذاكرة داخلية 4 جيجا ونظام تشغيل Windows المدمج.",
                    "price": 55000,
                    "custom_fields": {
                        "brand": "Nikon",
                        "model": "Nivo C5",
                        "condition": "جيد",
                        "year_purchased": "2020",
                        "usage_hours": "1500 ساعة",
                        "warranty_remaining": "منتهية",
                    },
                },
                {
                    "title": "ثيودوليت وايلد T16 كلاسيكي",
                    "description": "ثيودوليت وايلد T16 كلاسيكي، حالة ممتازة. دقة قراءة 20 ثانية. مناسب للتدريب والأعمال التقليدية. تم صيانته مؤخراً ومعاير بالكامل.",
                    "price": 12000,
                    "custom_fields": {
                        "brand": "Wild",
                        "model": "T16",
                        "condition": "ممتاز",
                        "year_purchased": "1995",
                        "usage_hours": "غير محدد",
                        "warranty_remaining": "بدون ضمان",
                    },
                },
            ],
            "rental": [
                {
                    "title": "تأجير توتال ستيشن لايكا TS16 بالشهر",
                    "description": "تأجير جهاز توتال ستيشن لايكا TS16 أحدث إصدار مع تقنية ATRplus للتتبع التلقائي. مناسب للمشاريع الكبيرة والمسح التفصيلي. يأتي مع جميع الملحقات والبرمجيات.",
                    "price": 8000,
                    "is_negotiable": False,
                    "custom_fields": {
                        "rental_period": "شهري",
                        "hourly_rate": "غير متاح",
                        "daily_rate": "300",
                        "monthly_rate": "8000",
                        "deposit_required": "5000",
                        "delivery_available": "نعم",
                    },
                },
                {
                    "title": "إيجار ماسح ليزر ثلاثي الأبعاد FARO",
                    "description": "تأجير ماسح ليزر FARO Focus3D X130 للمسح ثلاثي الأبعاد. مناسب لتوثيق المباني والآثار وإنشاء نماذج ثلاثية الأبعاد دقيقة. متاح للإيجار بالأسبوع أو الشهر.",
                    "price": 15000,
                    "custom_fields": {
                        "rental_period": "أسبوعي",
                        "hourly_rate": "غير متاح",
                        "daily_rate": "2500",
                        "monthly_rate": "15000",
                        "deposit_required": "20000",
                        "delivery_available": "نعم مع تدريب",
                    },
                },
                {
                    "title": "تأجير طائرة مسح DJI Phantom 4 RTK",
                    "description": "طائرة مسح جوي DJI Phantom 4 RTK للفوتوغراميتري والمسح الجوي. تحتوي على GPS RTK مدمج لدقة سنتيمترية. مناسبة لمسح المساحات الكبيرة وإنتاج الخرائط الطبوغرافية.",
                    "price": 3000,
                    "custom_fields": {
                        "rental_period": "أسبوعي",
                        "hourly_rate": "500",
                        "daily_rate": "800",
                        "monthly_rate": "3000",
                        "deposit_required": "10000",
                        "delivery_available": "نعم",
                    },
                },
            ],
            "maintenance": [
                {
                    "title": "صيانة ومعايرة أجهزة التوتال ستيشن",
                    "description": "نقدم خدمات صيانة ومعايرة شاملة لجميع أجهزة التوتال ستيشن من جميع الماركات. فريق فنيين معتمدين مع خبرة أكثر من 10 سنوات. نوفر شهادات معايرة معتمدة وضمان على الخدمة.",
                    "price": 2500,
                    "custom_fields": {
                        "service_type": "صيانة ومعايرة",
                        "brands_supported": "Leica, Trimble, Topcon, Nikon",
                        "turnaround_time": "3-5 أيام عمل",
                        "certification_provided": "شهادة معايرة معتمدة",
                        "warranty_period": "6 شهور",
                        "pickup_delivery": "متاح",
                    },
                },
                {
                    "title": "خدمة معايرة أجهزة GPS وGNSS",
                    "description": "معايرة متخصصة لأجهزة استقبال GPS وGNSS لضمان أعلى دقة في القياسات. نستخدم محطات مرجعية معتمدة ومعايير دولية. خدمة سريعة مع تقرير تفصيلي عن حالة الجهاز.",
                    "price": 3500,
                    "custom_fields": {
                        "service_type": "معايرة GPS/GNSS",
                        "brands_supported": "Trimble, Leica, Topcon, Septentrio",
                        "turnaround_time": "2-3 أيام عمل",
                        "certification_provided": "تقرير معايرة مفصل",
                        "warranty_period": "3 شهور",
                        "pickup_delivery": "متاح مع التأمين",
                    },
                },
                {
                    "title": "إصلاح وتجديد أجهزة المساحة القديمة",
                    "description": "نتخصص في إصلاح وتجديد أجهزة المساحة الكلاسيكية والقديمة. لدينا قطع غيار أصلية ومطورين مهرة. نعيد الحياة لأجهزتك القديمة بمعايير الجودة الحديثة.",
                    "price": 1800,
                    "custom_fields": {
                        "service_type": "إصلاح وتجديد",
                        "brands_supported": "جميع الماركات الكلاسيكية",
                        "turnaround_time": "1-2 أسبوع",
                        "certification_provided": "ضمان على الإصلاح",
                        "warranty_period": "سنة واحدة",
                        "pickup_delivery": "متاح",
                    },
                },
            ],
            "books": [
                {
                    "title": "كتاب المساحة الهندسية الحديثة - الطبعة الثالثة",
                    "description": "كتاب شامل في المساحة الهندسية يغطي جميع الموضوعات من الأساسيات إلى التقنيات المتقدمة. يشمل أمثلة تطبيقية وتمارين محلولة. مناسب للطلاب والممارسين المحترفين.",
                    "price": 180,
                    "custom_fields": {
                        "type": "كتاب مطبوع",
                        "language": "العربية",
                        "edition": "الطبعة الثالثة 2023",
                        "publisher": "دار المعرفة للنشر",
                        "format": "غلاف مقوى",
                        "license_type": "غير متاح",
                    },
                },
                {
                    "title": "برنامج AutoCAD Civil 3D 2024 مع الترخيص",
                    "description": "برنامج AutoCAD Civil 3D 2024 الأحدث للتصميم المدني والمساحي. يأتي مع ترخيص كامل لمدة سنة واحدة. مناسب للمكاتب الهندسية وشركات المساحة.",
                    "price": 12000,
                    "custom_fields": {
                        "type": "برنامج",
                        "language": "الإنجليزية مع واجهة عربية",
                        "edition": "2024",
                        "publisher": "Autodesk",
                        "format": "رقمي",
                        "license_type": "ترخيص سنوي",
                    },
                },
                {
                    "title": "كتاب الفوتوغراميتري والاستشعار عن بعد",
                    "description": "مرجع متخصص في تقنيات الفوتوغراميتري والاستشعار عن بعد. يغطي النظرية والتطبيق العملي باستخدام أحدث البرمجيات والتقنيات.",
                    "price": 220,
                    "custom_fields": {
                        "type": "كتاب مطبوع",
                        "language": "العربية والإنجليزية",
                        "edition": "الطبعة الثانية 2023",
                        "publisher": "دار الفكر الجامعي",
                        "format": "غلاف عادي",
                        "license_type": "غير متاح",
                    },
                },
                {
                    "title": "مجموعة برامج المساحة المتكاملة Trimble Business Center",
                    "description": "مجموعة شاملة من برامج Trimble Business Center لمعالجة بيانات المساحة وإدارة المشاريع. تشمل معالجة بيانات GPS والتوتال ستيشن وإنتاج الخرائط.",
                    "price": 25000,
                    "custom_fields": {
                        "type": "مجموعة برامج",
                        "language": "الإنجليزية",
                        "edition": "أحدث إصدار",
                        "publisher": "Trimble Inc.",
                        "format": "رقمي",
                        "license_type": "ترخيص دائم",
                    },
                },
            ],
        }
