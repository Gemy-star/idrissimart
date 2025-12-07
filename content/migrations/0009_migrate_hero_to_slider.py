# Migration to transfer hero data from HomePage to HomeSlider

from django.db import migrations


def migrate_hero_to_slider(apps, schema_editor):
    """Migrate existing hero section data to HomeSlider"""
    HomePage = apps.get_model("content", "HomePage")
    HomeSlider = apps.get_model("content", "HomeSlider")

    try:
        homepage = HomePage.objects.first()
        if homepage and homepage.hero_title:
            # Create a slider from the hero section
            slider = HomeSlider.objects.create(
                title=homepage.hero_title or "Welcome to Idrissimart",
                title_ar=homepage.hero_title_ar or "مرحباً بك في إدريسي مارت",
                subtitle=str(homepage.hero_subtitle or ""),
                subtitle_ar=str(homepage.hero_subtitle_ar or ""),
                description="",
                description_ar="",
                button_text=homepage.hero_button_text or "Get Started",
                button_text_ar=homepage.hero_button_text_ar or "ابدأ الآن",
                button_url=homepage.hero_button_url or "/classifieds/",
                background_color="#4B315E",
                text_color="#FFFFFF",
                is_active=True,
                order=1,
            )

            # Copy hero image if exists
            if homepage.hero_image:
                slider.image = homepage.hero_image
                slider.save()

            print(f"✅ Successfully migrated hero data to slider: {slider.title}")
        else:
            print("⚠️  No HomePage or hero data found, creating default slider")
            # Create a default slider
            HomeSlider.objects.create(
                title="Welcome to Idrissimart",
                title_ar="مرحباً بك في إدريسي مارت",
                subtitle="Your trusted marketplace for classified ads",
                subtitle_ar="سوقك الموثوق للإعلانات المبوبة",
                button_text="Browse Ads",
                button_text_ar="تصفح الإعلانات",
                button_url="/classifieds/",
                background_color="#4B315E",
                text_color="#FFFFFF",
                is_active=True,
                order=1,
            )

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        # Continue anyway to not block migration


def reverse_migration(apps, schema_editor):
    """Reverse migration - delete all sliders"""
    HomeSlider = apps.get_model("content", "HomeSlider")
    HomeSlider.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0008_homeslider"),
    ]

    operations = [
        migrations.RunPython(migrate_hero_to_slider, reverse_migration),
    ]
