# management/commands/populate_why_choose_us.py
from django.core.management.base import BaseCommand

from content.models import HomePage, WhyChooseUsFeature


class Command(BaseCommand):
    help = "Populate Why Choose Us features with default data"

    def handle(self, *args, **options):
        # Get or create HomePage instance
        home_page = HomePage.get_solo()

        # Default features data
        features_data = [
            {
                "title": "High Accuracy",
                "title_ar": "دقة عالية",
                "description": "We ensure the highest standards of accuracy in all surveying and measurement work",
                "description_ar": "نضمن أعلى معايير الدقة في جميع أعمال المساحة والقياس",
                "icon": "fas fa-crosshairs",
                "order": 1,
            },
            {
                "title": "Advanced Technology",
                "title_ar": "تقنية متطورة",
                "description": "We use the latest surveying equipment and geodetic technologies",
                "description_ar": "نستخدم أحدث أجهزة المساحة والتقنيات الجيوديسية",
                "icon": "fas fa-satellite",
                "order": 2,
            },
            {
                "title": "Certified Expertise",
                "title_ar": "خبرة معتمدة",
                "description": "A team of certified and experienced surveying engineers",
                "description_ar": "فريق من المهندسين المساحين المعتمدين وذوي الخبرة",
                "icon": "fas fa-certificate",
                "order": 3,
            },
            {
                "title": "Fast Delivery",
                "title_ar": "تسليم سريع",
                "description": "Commitment to deadlines and delivering projects on time",
                "description_ar": "التزام بالمواعيد المحددة وتسليم المشاريع في الوقت",
                "icon": "fas fa-clock",
                "order": 4,
            },
        ]

        created_count = 0
        updated_count = 0

        for feature_data in features_data:
            feature, created = WhyChooseUsFeature.objects.update_or_create(
                home_page=home_page,
                title_ar=feature_data["title_ar"],
                defaults={
                    "title": feature_data["title"],
                    "description": feature_data["description"],
                    "description_ar": feature_data["description_ar"],
                    "icon": feature_data["icon"],
                    "order": feature_data["order"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                try:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created: {feature.title_ar}")
                    )
                except UnicodeEncodeError:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created feature: order {feature.order}")
                    )
            else:
                updated_count += 1
                try:
                    self.stdout.write(
                        self.style.WARNING(f"Updated: {feature.title_ar}")
                    )
                except UnicodeEncodeError:
                    self.stdout.write(
                        self.style.WARNING(f"Updated feature: order {feature.order}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {created_count} created, {updated_count} updated"
            )
        )
