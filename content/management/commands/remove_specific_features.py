# management/commands/remove_specific_features.py
from django.core.management.base import BaseCommand
from content.models import WhyChooseUsFeature


class Command(BaseCommand):
    help = "Remove specific Why Choose Us features"

    def handle(self, *args, **options):
        # العناوين المطلوب حذفها
        titles_to_remove = [
            "دقة عالية",
            "إعلانات مساحية متخصصة",
            "تقنية متطورة",
            "إعلانك يصل لمكانه الصحيح",
        ]

        deleted_count = 0

        for title in titles_to_remove:
            # حذف العناصر التي تطابق العنوان العربي
            features = WhyChooseUsFeature.objects.filter(title_ar=title)
            count = features.count()

            if count > 0:
                features.delete()
                deleted_count += count
                try:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ تم حذف: {title}")
                    )
                except UnicodeEncodeError:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Deleted: {title}")
                    )
            else:
                try:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ لم يتم العثور على: {title}")
                    )
                except UnicodeEncodeError:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Not found: {title}")
                    )

        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ تم حذف {deleted_count} عنصر بنجاح"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠ لم يتم حذف أي عناصر"
                )
            )
