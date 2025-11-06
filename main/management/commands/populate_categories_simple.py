from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from content.models import Country
from main.models import Category


class Command(BaseCommand):
    help = "Populate surveying engineering classified ads categories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--country",
            type=str,
            default="EG",
            help="Country code (default: EG)",
        )

    def handle(self, *args, **options):
        country_code = options["country"]

        try:
            country = Country.objects.get(code=country_code)
            self.stdout.write(f"Using country: {country.name} ({country.code})")
        except Country.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Country {country_code} not found. Run populate_countries first."
                )
            )
            return

        self.country = country
        self.created_count = 0

        with transaction.atomic():
            # Create main category
            main_category = self.create_main_category()

            # Create subcategories
            self.create_subcategories(main_category)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Created {self.created_count} categories successfully!"
            )
        )

    def create_main_category(self):
        """Create main surveying engineering classified ads category"""
        category = Category.objects.create(
            name="Surveying Engineering Classified Ads",
            name_ar="إعلانات مبوبة - هندسة المساحة",
            slug="surveying-engineering-classified-ads",
            section_type="classified",
            description="إعلانات مبوبة متخصصة في معدات وخدمات هندسة المساحة",
            icon="fas fa-ruler-combined",
            country=self.country,
            parent=None,
            is_active=True,
            order=1,
            custom_field_schema=["brand", "condition", "model", "year"],
        )

        self.created_count += 1
        self.stdout.write(f"✅ Created main category: {category.name_ar}")
        return category

    def create_subcategories(self, parent):
        """Create surveying equipment subcategories"""
        subcategories = [
            {
                "name": "Used Equipment",
                "name_ar": "مستعمل",
                "slug": f"{parent.slug}-used-equipment",
                "description": "معدات مساحة مستعملة بحالة جيدة",
                "icon": "fas fa-recycle",
                "order": 1,
            },
            {
                "name": "Equipment Rental",
                "name_ar": "إيجار أجهزة",
                "slug": f"{parent.slug}-equipment-rental",
                "description": "تأجير معدات المساحة بالساعة أو اليوم أو الشهر",
                "icon": "fas fa-exchange-alt",
                "order": 2,
            },
            {
                "name": "Maintenance and Calibration",
                "name_ar": "الصيانة والمعايرة",
                "slug": f"{parent.slug}-maintenance-calibration",
                "description": "خدمات صيانة ومعايرة أجهزة المساحة",
                "icon": "fas fa-wrench",
                "order": 3,
            },
            {
                "name": "Books and Software",
                "name_ar": "كتب وبرامج",
                "slug": f"{parent.slug}-books-software",
                "description": "كتب مراجع وبرامج متخصصة في هندسة المساحة",
                "icon": "fas fa-book",
                "order": 4,
            },
        ]

        for subcat_data in subcategories:
            category = Category.objects.create(
                name=subcat_data["name"],
                name_ar=subcat_data["name_ar"],
                slug=subcat_data["slug"],
                section_type="classified",
                description=subcat_data["description"],
                icon=subcat_data["icon"],
                country=self.country,
                parent=parent,
                is_active=True,
                order=subcat_data["order"],
                custom_field_schema=["brand", "condition", "model"],
            )

            self.created_count += 1
            self.stdout.write(f"  ✅ Created subcategory: {category.name_ar}")
