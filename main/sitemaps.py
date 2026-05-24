from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from content.models import Blog, BlogCategory
from main.models import Category, ClassifiedAd


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"
    i18n = True

    def items(self):
        return ["home", "ad_list", "categories"]

    def location(self, item):
        return reverse(f"main:{item}")


class CategorySitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"
    i18n = True

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("main:categories_by_slug", kwargs={"category_slug": obj.slug})

    def lastmod(self, obj):
        return obj.updated_at


class ClassifiedAdSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"
    i18n = True

    def items(self):
        return ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE
        ).order_by("-updated_at")

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"
    i18n = True

    def items(self):
        return Blog.objects.filter(is_published=True).order_by("-published_date")

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.published_date


class BlogCategorySitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"
    i18n = True

    def items(self):
        return BlogCategory.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("content:blog_list_by_category", kwargs={"category_slug": obj.slug})


sitemaps = {
    "static": StaticViewSitemap,
    "categories": CategorySitemap,
    "ads": ClassifiedAdSitemap,
    "blog": BlogSitemap,
    "blog_categories": BlogCategorySitemap,
}
