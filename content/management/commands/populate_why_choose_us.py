# management/commands/populate_why_choose_us.py
from django.core.management.base import BaseCommand

from content.models import HomePage, WhyChooseUsFeature


class Command(BaseCommand):
    help = "Populate Why Choose Us features with default data"

    def handle(self, *args, **options):
        # Get or create HomePage instance
        home_page = HomePage.get_solo()

        # Default features data
        # العناصر التي تم إزالتها:
        # - دقة عالية
        # - إعلانات مساحية متخصصة
        # - تقنية متطورة
        # - إعلانك يصل لمكانه الصحيح

        features_data = [
            {
                "title": "Specialization Makes the Difference",
                "title_ar": "لأن التخصص يصنع الفرق",
                "description": "Because general ads don't understand the surveying market needs, we created a specialized ads platform that clearly brings together opportunities and expertise.",
                "description_ar": "لأن الإعلانات العامة لا تفهم احتياجات السوق المساحي، أنشأنا منصة إعلانات متخصصة تجمع الفرص والخبرات بوضوح.",
                "icon": "fas fa-star",
                "order": 1,
            },
            {
                "title": "Platform Understood by Industry Professionals",
                "title_ar": "منصة إعلانات يفهمها أهل المجال",
                "description": "Post your surveying ad or search for the right service within a professional community that understands your field and interacts with you seriously.",
                "description_ar": "انشر إعلانك المساحي، أو ابحث عن الخدمة المناسبة، ضمن مجتمع مهني يفهم مجالك ويتفاعل معك بجدية.",
                "icon": "fas fa-users",
                "order": 2,
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
