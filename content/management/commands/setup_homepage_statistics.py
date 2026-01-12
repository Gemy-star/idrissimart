"""
Management command to setup homepage statistics
"""

from django.core.management.base import BaseCommand
from content.site_config import HomePage


class Command(BaseCommand):
    help = "Setup homepage statistics with default values"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Setting up homepage statistics..."))

        try:
            home_page = HomePage.get_solo()

            # Enable statistics section
            home_page.show_statistics = True

            # Statistic 1: معلنين نشطين (Active Advertisers)
            home_page.stat1_value = 15
            home_page.stat1_title = "Active Advertisers"
            home_page.stat1_title_ar = "معلنين نشطين"
            home_page.stat1_subtitle = "Offices, Engineers & Companies"
            home_page.stat1_subtitle_ar = "مكاتب، مهندسين، وشركات"
            home_page.stat1_icon = "fas fa-user-friends"

            # Statistic 2: إعلانات منشورة (Published Ads)
            home_page.stat2_value = 150
            home_page.stat2_title = "Published Ads"
            home_page.stat2_title_ar = "إعلانات منشورة"
            home_page.stat2_subtitle = "Services, Equipment & Job Opportunities"
            home_page.stat2_subtitle_ar = "خدمات، معدات، وفرص عمل"
            home_page.stat2_icon = "fas fa-bullhorn"

            # Statistic 3: زيارات شهرية (Monthly Visits)
            home_page.stat3_value = 500
            home_page.stat3_title = "Monthly Visits"
            home_page.stat3_title_ar = "زيارات شهرية"
            home_page.stat3_subtitle = "Interested in Surveying Field"
            home_page.stat3_subtitle_ar = "مهتمون بالمجال المساحي"
            home_page.stat3_icon = "fas fa-chart-line"

            # Statistic 4: تخصصات مدعومة (Supported Specializations)
            home_page.stat4_value = 250
            home_page.stat4_title = "Supported Specializations"
            home_page.stat4_title_ar = "تخصصات مدعومة"
            home_page.stat4_subtitle = "Surveying - Engineering - GIS"
            home_page.stat4_subtitle_ar = "مساحة – هندسة – GIS"
            home_page.stat4_icon = "fas fa-th-large"

            home_page.save()

            self.stdout.write(self.style.SUCCESS("\n✅ Homepage statistics setup completed successfully!\n"))
            self.stdout.write(self.style.SUCCESS("Statistics configured:"))
            self.stdout.write(f"  📊 Stat 1: {home_page.stat1_value} - {home_page.stat1_title_ar}")
            self.stdout.write(f"     └─ {home_page.stat1_subtitle_ar}")
            self.stdout.write(f"  📊 Stat 2: {home_page.stat2_value} - {home_page.stat2_title_ar}")
            self.stdout.write(f"     └─ {home_page.stat2_subtitle_ar}")
            self.stdout.write(f"  📊 Stat 3: {home_page.stat3_value} - {home_page.stat3_title_ar}")
            self.stdout.write(f"     └─ {home_page.stat3_subtitle_ar}")
            self.stdout.write(f"  📊 Stat 4: {home_page.stat4_value} - {home_page.stat4_title_ar}")
            self.stdout.write(f"     └─ {home_page.stat4_subtitle_ar}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error setting up statistics: {str(e)}"))
            raise
