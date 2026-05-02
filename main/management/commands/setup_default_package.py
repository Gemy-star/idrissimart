from django.core.management.base import BaseCommand
from main.models import AdPackage


class Command(BaseCommand):
    help = "Create or update the default free package assigned to new users"

    def handle(self, *args, **options):
        # Unset any existing default to avoid duplicates
        AdPackage.objects.filter(is_default=True).update(is_default=False)

        package, created = AdPackage.objects.update_or_create(
            name="الباقة المجانية",
            defaults={
                "name_en": "Free Package",
                "description": (
                    "مرحبا بك معنا على منصة إدريسي مارت بمجرد تسجيل عضويتك تمتع بنشر إعلاناتك المجانية "
                    "على أول منصة متخصصة"
                ),
                "price": 0,
                "ad_count": 6,
                "ad_duration_days": 30,
                "duration_days": 365,
                "feature_highlighted_price": 0,
                "feature_pinned_price": 0,
                "feature_urgent_price": 0,
                "feature_contact_for_price": 0,
                "is_default": True,
                "is_active": True,
                "features": [
                    "عدد الإعلانات: 6",
                    "مدة ظهور الإعلان: 30 يوم",
                    "صلاحية الباقة: 365 يوم",
                    "تمييز الإعلان: مجاني",
                    "تثبيت الإعلان: مجاني",
                    "إعلان عاجل: مجاني",
                    "تواصل للسعر: مجاني",
                    "لقد خفضنا لك سعر تمييز الإعلان لتجربه هذه الميزة فلا تدعها تفوتك",
                ],
            },
        )

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} default package: '{package.name}' (id={package.pk})"
        ))
        self.stdout.write(f"  ad_count={package.ad_count}, ad_duration_days={package.ad_duration_days}, "
                         f"duration_days={package.duration_days}")
        self.stdout.write(f"  highlighted=0, pinned=0, urgent=0, contact_for_price=0")
