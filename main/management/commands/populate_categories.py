from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from content.models import Country
from main.models import Category


class Command(BaseCommand):
    help = "Populate categories with default data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--country",
            type=str,
            default="EG",
            help="Country code to associate categories with (default: EG)",
        )

    def handle(self, *args, **options):
        country_code = options["country"]

        try:
            country = Country.objects.get(code=country_code, is_active=True)
            self.stdout.write(f"Using country: {country.name} ({country.code})")
        except Country.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Country with code '{country_code}' not found. "
                    f"Please run 'python manage.py populate_countries' first."
                )
            )
            return

        self.created_count = 0
        self.updated_count = 0
        self.country = country

        categories_data = self.get_default_categories()

        with transaction.atomic():
            for section_type, section_categories in categories_data.items():
                self.stdout.write(f"\n--- Processing {section_type} categories ---")
                for cat_data in section_categories:
                    self.create_category(cat_data, section_type)

        # Rebuild the MPTT tree after all categories are created/updated
        self.stdout.write(self.style.NOTICE("\nRebuilding category tree..."))
        Category.objects.rebuild()
        self.stdout.write(self.style.SUCCESS("Category tree rebuilt successfully."))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! {self.created_count} created, {self.updated_count} updated"
            )
        )

    def create_category(self, cat_data, section_type, parent=None):
        """Recursively create categories and subcategories."""
        base_slug = slugify(cat_data["name"])

        # Build slug based on hierarchy (keeping it short)
        if parent:
            # For subcategories, just use parent slug + base slug
            slug = f"{parent.slug}-{base_slug}"
        else:
            # For root categories, use section abbreviation + base slug
            section_abbr = {
                "classified": "cl",
                "product": "pr",
                "service": "sv",
                "course": "co",
                "job": "jb",
            }.get(section_type, section_type[:2])
            slug = f"{section_abbr}-{base_slug}"

        # Ensure slug doesn't exceed 50 characters (SlugField default max_length)
        if len(slug) > 50:
            # Truncate and add country code for uniqueness
            slug = slug[:44] + f"-{self.country.code.lower()}"

        category_defaults = {
            "name": cat_data["name"],
            "name_ar": cat_data["name_ar"],
            "section_type": section_type,
            "parent": parent,
            "description": cat_data.get("description", ""),
            "icon": cat_data.get("icon", ""),
            "country": self.country,
            "order": cat_data.get("order", 0),
            "custom_field_schema": cat_data.get("custom_field_schema", []),
            "allow_cart": cat_data.get("allow_cart", False),
            "default_reservation_percentage": cat_data.get(
                "default_reservation_percentage", 10
            ),
            "require_admin_approval": cat_data.get("require_admin_approval", True),
        }

        # Try to find existing category by slug first
        try:
            category = Category.objects.get(slug=slug)
            # Update existing category
            for key, value in category_defaults.items():
                setattr(category, key, value)
            category.save()
            created = False
        except Category.DoesNotExist:
            # Create new category
            category = Category.objects.create(slug=slug, **category_defaults)
            created = True

        indent = "  " * (category.get_level() + 1)
        if created:
            self.created_count += 1
            self.stdout.write(self.style.SUCCESS(f"{indent}Created: {category.name}"))
        else:
            self.updated_count += 1
            self.stdout.write(self.style.WARNING(f"{indent}Updated: {category.name}"))

        # Create subcategories if they exist
        if "subcategories" in cat_data:
            for sub_data in cat_data["subcategories"]:
                self.create_category(sub_data, section_type, parent=category)

        return category

    def get_default_categories(self):
        """Returns default categories structure"""
        return {
            "classified": [
                {
                    "name": "Classified Ads",
                    "name_ar": "إعلانات مبوبة",
                    "description": "General classified ads",
                    "icon": "fas fa-bullhorn",
                    "order": 1,
                    "subcategories": [
                        {
                            "name": "Used",
                            "name_ar": "مستعمل",
                            "order": 1,
                            "icon": "fas fa-recycle",
                            "custom_field_schema": [
                                {
                                    "name": "brand",
                                    "label": "Brand",
                                    "type": "text",
                                    "required": True,
                                    "validation": {"min_length": 2, "max_length": 50},
                                },
                                {
                                    "name": "model_year",
                                    "label": "Model Year",
                                    "type": "number",
                                    "validation": {
                                        "min_value": 1980,
                                        "max_value": 2025,
                                    },
                                },
                                {
                                    "name": "condition",
                                    "label": "Condition",
                                    "type": "select",
                                    "options": ["New-like", "Good", "Fair"],
                                    "required": True,
                                },
                                {
                                    "name": "warranty_included",
                                    "label": "Warranty Included",
                                    "type": "checkbox",
                                },
                                {
                                    "name": "purchase_date",
                                    "label": "Purchase Date",
                                    "type": "date",
                                },
                            ],
                        },
                        {
                            "name": "Equipment Rental",
                            "name_ar": "ايجار أجهزة",
                            "order": 2,
                            "icon": "fas fa-exchange-alt",
                        },
                        {
                            "name": "Maintenance and Calibration",
                            "name_ar": "الصيانة والمعايرة",
                            "order": 3,
                            "icon": "fas fa-wrench",
                        },
                        {
                            "name": "Books and Programs",
                            "name_ar": "كتب وبرامج",
                            "order": 4,
                            "icon": "fas fa-book",
                        },
                    ],
                }
            ],
            "product": [
                {
                    "name": "Real Estate",
                    "name_ar": "العقارات",
                    "description": "Properties for rent and sale",
                    "icon": "fas fa-building",
                    "order": 1,
                    "subcategories": [
                        {
                            "name": "Apartments for Rent",
                            "name_ar": "شقق للإيجار",
                            "order": 1,
                        },
                        {
                            "name": "Houses for Sale",
                            "name_ar": "منازل للبيع",
                            "order": 2,
                        },
                        {"name": "Commercial", "name_ar": "تجاري", "order": 3},
                        {"name": "Land", "name_ar": "أراضي", "order": 4},
                    ],
                },
                {
                    "name": "Vehicles",
                    "name_ar": "المركبات",
                    "description": "Cars, motorcycles and vehicles",
                    "icon": "fas fa-car",
                    "order": 2,
                    "subcategories": [
                        {"name": "Cars", "name_ar": "السيارات", "order": 1},
                        {
                            "name": "Motorcycles",
                            "name_ar": "الدراجات النارية",
                            "order": 2,
                        },
                        {"name": "Trucks", "name_ar": "الشاحنات", "order": 3},
                        {"name": "Spare Parts", "name_ar": "قطع الغيار", "order": 4},
                    ],
                },
                {
                    "name": "Electronics",
                    "name_ar": "الإلكترونيات",
                    "description": "Electronic devices and gadgets",
                    "icon": "fas fa-mobile-alt",
                    "order": 3,
                    "subcategories": [
                        {
                            "name": "Smartphones",
                            "name_ar": "الهواتف الذكية",
                            "order": 1,
                        },
                        {
                            "name": "Laptops",
                            "name_ar": "أجهزة الكمبيوتر المحمولة",
                            "order": 2,
                        },
                        {"name": "Tablets", "name_ar": "الأجهزة اللوحية", "order": 3},
                        {"name": "Accessories", "name_ar": "الإكسسوارات", "order": 4},
                    ],
                },
            ],
            "service": [
                {
                    "name": "Fashion",
                    "name_ar": "الأزياء",
                    "description": "Clothing and fashion items",
                    "icon": "fas fa-tshirt",
                    "order": 1,
                    "subcategories": [
                        {
                            "name": "Mens Clothing",
                            "name_ar": "ملابس رجالية",
                            "order": 1,
                        },
                        {
                            "name": "Womens Clothing",
                            "name_ar": "ملابس نسائية",
                            "order": 2,
                        },
                        {"name": "Shoes", "name_ar": "الأحذية", "order": 3},
                        {"name": "Bags", "name_ar": "الحقائب", "order": 4},
                    ],
                },
                {
                    "name": "Home & Garden",
                    "name_ar": "المنزل والحديقة",
                    "description": "Home and garden products",
                    "icon": "fas fa-home",
                    "order": 2,
                    "subcategories": [
                        {"name": "Furniture", "name_ar": "الأثاث", "order": 1},
                        {"name": "Decor", "name_ar": "الديكور", "order": 2},
                        {"name": "Kitchen", "name_ar": "المطبخ", "order": 3},
                        {"name": "Garden", "name_ar": "الحديقة", "order": 4},
                    ],
                },
                {
                    "name": "Sports & Leisure",
                    "name_ar": "الرياضة والترفيه",
                    "description": "Sports and leisure products",
                    "icon": "fas fa-futbol",
                    "order": 3,
                    "subcategories": [
                        {
                            "name": "Sports Equipment",
                            "name_ar": "معدات رياضية",
                            "order": 1,
                        },
                        {"name": "Outdoor", "name_ar": "الأنشطة الخارجية", "order": 2},
                        {"name": "Fitness", "name_ar": "اللياقة البدنية", "order": 3},
                        {"name": "Games", "name_ar": "الألعاب", "order": 4},
                    ],
                },
                {
                    "name": "Home Services",
                    "name_ar": "خدمات منزلية",
                    "description": "Home maintenance and repair services",
                    "icon": "fas fa-tools",
                    "order": 4,
                    "subcategories": [
                        {"name": "Plumbing", "name_ar": "السباكة", "order": 1},
                        {"name": "Electrical", "name_ar": "الكهرباء", "order": 2},
                        {"name": "Cleaning", "name_ar": "التنظيف", "order": 3},
                        {"name": "Gardening", "name_ar": "البستنة", "order": 4},
                    ],
                },
                {
                    "name": "Professional Services",
                    "name_ar": "خدمات مهنية",
                    "description": "Professional and business services",
                    "icon": "fas fa-briefcase",
                    "order": 5,
                    "subcategories": [
                        {
                            "name": "Legal Services",
                            "name_ar": "الخدمات القانونية",
                            "order": 1,
                        },
                        {"name": "Accounting", "name_ar": "المحاسبة", "order": 2},
                        {"name": "Consulting", "name_ar": "الاستشارات", "order": 3},
                        {"name": "Translation", "name_ar": "الترجمة", "order": 4},
                    ],
                },
                {
                    "name": "Technical Services",
                    "name_ar": "خدمات تقنية",
                    "description": "Technical and IT services",
                    "icon": "fas fa-laptop-code",
                    "order": 6,
                    "subcategories": [
                        {
                            "name": "Computer Repair",
                            "name_ar": "إصلاح الكمبيوتر",
                            "order": 1,
                        },
                        {
                            "name": "Software Installation",
                            "name_ar": "تثبيت البرامج",
                            "order": 2,
                        },
                        {
                            "name": "Network Setup",
                            "name_ar": "إعداد الشبكات",
                            "order": 3,
                        },
                        {
                            "name": "Data Recovery",
                            "name_ar": "استرداد البيانات",
                            "order": 4,
                        },
                    ],
                },
            ],
            "course": [
                {
                    "name": "Technology Courses",
                    "name_ar": "دورات تكنولوجيا",
                    "description": "Technology and programming courses",
                    "icon": "fas fa-laptop",
                    "order": 1,
                    "subcategories": [
                        {"name": "Programming", "name_ar": "البرمجة", "order": 1},
                        {"name": "Web Design", "name_ar": "تصميم المواقع", "order": 2},
                        {
                            "name": "Digital Marketing",
                            "name_ar": "التسويق الرقمي",
                            "order": 3,
                        },
                        {
                            "name": "Data Analysis",
                            "name_ar": "تحليل البيانات",
                            "order": 4,
                        },
                    ],
                },
                {
                    "name": "Business Courses",
                    "name_ar": "دورات الأعمال",
                    "description": "Business and management courses",
                    "icon": "fas fa-chart-line",
                    "order": 2,
                    "subcategories": [
                        {
                            "name": "Project Management",
                            "name_ar": "إدارة المشاريع",
                            "order": 1,
                        },
                        {"name": "Leadership", "name_ar": "القيادة", "order": 2},
                        {
                            "name": "Entrepreneurship",
                            "name_ar": "ريادة الأعمال",
                            "order": 3,
                        },
                        {"name": "Finance", "name_ar": "المالية", "order": 4},
                    ],
                },
                {
                    "name": "Language Courses",
                    "name_ar": "دورات اللغات",
                    "description": "Language learning courses",
                    "icon": "fas fa-language",
                    "order": 3,
                    "subcategories": [
                        {"name": "English", "name_ar": "الإنجليزية", "order": 1},
                        {"name": "Arabic", "name_ar": "العربية", "order": 2},
                        {"name": "French", "name_ar": "الفرنسية", "order": 3},
                        {"name": "German", "name_ar": "الألمانية", "order": 4},
                    ],
                },
            ],
            "job": [
                {
                    "name": "Information Technology",
                    "name_ar": "تكنولوجيا المعلومات",
                    "description": "IT jobs and technology positions",
                    "icon": "fas fa-code",
                    "order": 1,
                    "subcategories": [
                        {
                            "name": "Software Development",
                            "name_ar": "تطوير البرمجيات",
                            "order": 1,
                        },
                        {
                            "name": "Web Development",
                            "name_ar": "تطوير المواقع",
                            "order": 2,
                        },
                        {
                            "name": "Mobile Development",
                            "name_ar": "تطوير التطبيقات",
                            "order": 3,
                        },
                        {
                            "name": "Data Science",
                            "name_ar": "علوم البيانات",
                            "order": 4,
                        },
                    ],
                },
                {
                    "name": "Engineering",
                    "name_ar": "الهندسة",
                    "description": "Engineering positions and technical roles",
                    "icon": "fas fa-cogs",
                    "order": 2,
                    "subcategories": [
                        {
                            "name": "Civil Engineering",
                            "name_ar": "الهندسة المدنية",
                            "order": 1,
                        },
                        {
                            "name": "Mechanical Engineering",
                            "name_ar": "الهندسة الميكانيكية",
                            "order": 2,
                        },
                        {
                            "name": "Electrical Engineering",
                            "name_ar": "الهندسة الكهربائية",
                            "order": 3,
                        },
                        {
                            "name": "Chemical Engineering",
                            "name_ar": "الهندسة الكيميائية",
                            "order": 4,
                        },
                    ],
                },
                {
                    "name": "Business & Finance",
                    "name_ar": "الأعمال والمالية",
                    "description": "Business and finance positions",
                    "icon": "fas fa-chart-bar",
                    "order": 3,
                    "subcategories": [
                        {"name": "Accounting", "name_ar": "المحاسبة", "order": 1},
                        {"name": "Marketing", "name_ar": "التسويق", "order": 2},
                        {"name": "Sales", "name_ar": "المبيعات", "order": 3},
                        {"name": "Management", "name_ar": "الإدارة", "order": 4},
                    ],
                },
            ],
        }
