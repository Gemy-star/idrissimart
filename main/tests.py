from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from content.models import Country
from main.models import AdFeature, Category, ClassifiedAd, User


class HomeViewTests(TestCase):
    """
    Tests for the HomeView to ensure it displays categories and ads correctly.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        # Create users
        cls.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )

        # Create countries
        cls.country_eg = Country.objects.create(
            name="Egypt", code="EG", flag_emoji="🇪🇬"
        )
        cls.country_sa = Country.objects.create(
            name="Saudi Arabia", code="SA", flag_emoji="🇸🇦"
        )

        # Create categories
        cls.cat_classified_eg = Category.objects.create(
            name="Electronics EG",
            section_type=Category.SectionType.CLASSIFIED,
            country=cls.country_eg,
            slug="electronics-eg",
        )
        cls.cat_classified_sa = Category.objects.create(
            name="Cars SA",
            section_type=Category.SectionType.CLASSIFIED,
            country=cls.country_sa,
            slug="cars-sa",
        )

        # Create Ads
        cls.ad_latest_eg = ClassifiedAd.objects.create(
            user=cls.user,
            category=cls.cat_classified_eg,
            title="Latest Ad in EG",
            price=1000,
            country=cls.country_eg,
            city="Cairo",
            status=ClassifiedAd.AdStatus.ACTIVE,
        )
        cls.ad_featured_eg = ClassifiedAd.objects.create(
            user=cls.user,
            category=cls.cat_classified_eg,
            title="Featured Ad in EG",
            price=2000,
            country=cls.country_eg,
            city="Alexandria",
            status=ClassifiedAd.AdStatus.ACTIVE,
        )
        cls.ad_sa = ClassifiedAd.objects.create(
            user=cls.user,
            category=cls.cat_classified_sa,
            title="Ad in SA",
            price=5000,
            country=cls.country_sa,
            city="Riyadh",
            status=ClassifiedAd.AdStatus.ACTIVE,
        )

        # Make one ad featured
        AdFeature.objects.create(
            ad=cls.ad_featured_eg,
            feature_type=AdFeature.FeatureType.FEATURED_SECTION,
            end_date=timezone.now() + timezone.timedelta(days=7),
        )

    def test_home_view_loads_successfully(self):
        """Test that the home page returns a 200 status code and uses the correct template."""
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")

    def test_home_view_context_data(self):
        """Test that the correct ads and categories are present in the context for the default country (EG)."""
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)

        # Check that the context variables exist
        self.assertIn("latest_ads", response.context)
        self.assertIn("featured_ads", response.context)
        self.assertIn("categories_by_section", response.context)

        # Check that the correct ads for Egypt are displayed
        self.assertIn(self.ad_latest_eg, response.context["latest_ads"])
        self.assertIn(self.ad_featured_eg, response.context["featured_ads"])

        # Ensure ads from other countries are not present
        self.assertNotIn(self.ad_sa, response.context["latest_ads"])
        self.assertNotIn(self.ad_sa, response.context["featured_ads"])

        # Check that the correct category for Egypt is displayed
        classified_categories = response.context["categories_by_section"]["classified"][
            "categories"
        ]
        self.assertTrue(
            any(c["category"] == self.cat_classified_eg for c in classified_categories)
        )
        self.assertFalse(
            any(c["category"] == self.cat_classified_sa for c in classified_categories)
        )
