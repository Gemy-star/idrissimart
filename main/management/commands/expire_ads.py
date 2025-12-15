"""
Management command to automatically expire ads that have passed their expiration date
Run this command via cron job daily
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import ClassifiedAd
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "تحديث حالة الإعلانات المنتهية - Update status of expired ads"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="عرض النتائج فقط بدون تطبيق التغييرات - Show results without applying changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        now = timezone.now()

        # Find active ads that have expired
        expired_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE,
            expires_at__isnull=False,
            expires_at__lte=now,
        ).select_related("user", "category")

        count = expired_ads.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("✅ لا توجد إعلانات منتهية - No expired ads found")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"⚠️  تم العثور على {count} إعلان منتهي - Found {count} expired ads"
            )
        )

        # Display details
        for ad in expired_ads:
            days_expired = (now - ad.expires_at).days
            self.stdout.write(
                f"  - [{ad.id}] {ad.title[:50]} "
                f"(انتهى منذ {days_expired} يوم - expired {days_expired} days ago)"
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n🔍 وضع التجربة فعّال - لم يتم تطبيق أي تغييرات"
                    "\n🔍 Dry run mode - No changes applied"
                )
            )
            return

        # Update ads to expired status
        updated = expired_ads.update(status=ClassifiedAd.AdStatus.EXPIRED)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ تم تحديث {updated} إعلان إلى حالة "منتهي"'
                f"\n✅ Updated {updated} ads to EXPIRED status"
            )
        )

        # Log the action
        logger.info(f"Expired {updated} ads automatically")
