"""
Management command to permanently delete old ads based on retention settings
Run this command via Django-Q scheduled task daily
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import ClassifiedAd
from content.site_config import SiteConfiguration
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "حذف الإعلانات القديمة نهائياً - Permanently delete old ads based on retention settings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="عرض النتائج فقط بدون تطبيق التغييرات - Show results without applying changes",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="فرض الحذف حتى لو لم تكتمل المدة - Force delete even if retention period not met",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        # Get configuration
        config = SiteConfiguration.get_solo()
        deleted_retention_days = config.deleted_ads_retention_days
        expired_retention_days = config.expired_ads_retention_days

        now = timezone.now()

        self.stdout.write(
            self.style.WARNING(
                f"\n{'='*70}\n"
                f"🗑️  تنظيف الإعلانات القديمة - Old Ads Cleanup\n"
                f"{'='*70}\n"
            )
        )

        self.stdout.write(
            f"📋 الإعدادات - Settings:\n"
            f"   • مدة الاحتفاظ بالمحذوفة: {deleted_retention_days} يوم\n"
            f"   • مدة الاحتفاظ بالمنتهية: {expired_retention_days} يوم\n"
            f"   • وضع التجربة: {'نعم' if dry_run else 'لا'}\n"
            f"   • فرض الحذف: {'نعم' if force else 'لا'}\n\n"
        )

        # Find ads eligible for permanent deletion
        total_deleted = 0

        # 1. Soft-deleted ads past retention period
        deleted_cutoff = now - timezone.timedelta(days=deleted_retention_days)
        soft_deleted_ads = ClassifiedAd.objects.filter(
            deleted_at__isnull=False, deleted_at__lte=deleted_cutoff
        ).select_related("user", "category")

        deleted_count = soft_deleted_ads.count()

        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🗑️  الإعلانات المحذوفة - Soft-Deleted Ads:\n"
                    f"   تم العثور على {deleted_count} إعلان محذوف منذ أكثر من {deleted_retention_days} يوم\n"
                )
            )

            for ad in soft_deleted_ads[:10]:  # Show first 10
                days_since_deletion = (now - ad.deleted_at).days
                self.stdout.write(
                    f"   • ID: {ad.id} | {ad.title[:40]} | "
                    f"محذوف منذ: {days_since_deletion} يوم | "
                    f"المستخدم: {ad.user.username}"
                )

            if deleted_count > 10:
                self.stdout.write(f"   ... و {deleted_count - 10} إعلان آخر")

            if not dry_run:
                deleted_titles = [ad.title for ad in soft_deleted_ads]
                soft_deleted_ads.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ تم حذف {deleted_count} إعلان محذوف نهائياً")
                )
                logger.info(
                    f"Permanently deleted {deleted_count} soft-deleted ads: {deleted_titles[:5]}"
                )
                total_deleted += deleted_count
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  سيتم حذف {deleted_count} إعلان (وضع التجربة)"
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ لا توجد إعلانات محذوفة تحتاج للحذف النهائي")
            )

        # 2. Expired ads past retention period
        expired_cutoff = now - timezone.timedelta(days=expired_retention_days)
        expired_ads = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.EXPIRED,
            expires_at__isnull=False,
            expires_at__lte=expired_cutoff,
            deleted_at__isnull=True,  # Not already soft-deleted
        ).select_related("user", "category")

        expired_count = expired_ads.count()

        if expired_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⌛ الإعلانات المنتهية - Expired Ads:\n"
                    f"   تم العثور على {expired_count} إعلان منتهي منذ أكثر من {expired_retention_days} يوم\n"
                )
            )

            for ad in expired_ads[:10]:  # Show first 10
                days_since_expiry = (now - ad.expires_at).days
                self.stdout.write(
                    f"   • ID: {ad.id} | {ad.title[:40]} | "
                    f"منتهي منذ: {days_since_expiry} يوم | "
                    f"المستخدم: {ad.user.username}"
                )

            if expired_count > 10:
                self.stdout.write(f"   ... و {expired_count - 10} إعلان آخر")

            if not dry_run:
                expired_titles = [ad.title for ad in expired_ads]
                expired_ads.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ تم حذف {expired_count} إعلان منتهي نهائياً")
                )
                logger.info(
                    f"Permanently deleted {expired_count} expired ads: {expired_titles[:5]}"
                )
                total_deleted += expired_count
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  سيتم حذف {expired_count} إعلان (وضع التجربة)"
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ لا توجد إعلانات منتهية تحتاج للحذف النهائي")
            )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*70}\n"
                f"📊 الملخص - Summary:\n"
                f"   • إجمالي الحذف: {total_deleted if not dry_run else 0} إعلان\n"
                f"   • الإعلانات المحذوفة: {deleted_count}\n"
                f"   • الإعلانات المنتهية: {expired_count}\n"
                f"{'='*70}\n"
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  هذا وضع تجريبي. لم يتم حذف أي شيء.\n"
                    "   استخدم الأمر بدون --dry-run للحذف الفعلي.\n"
                )
            )

        return total_deleted
