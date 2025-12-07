import json
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import ListView, TemplateView
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from .decorators import SuperadminRequiredMixin, superadmin_required
from .services import MobileVerificationService
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models, transaction
from django.http import HttpResponseForbidden
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.urls import reverse_lazy, reverse
from django_filters.views import FilterView

from content.models import Blog, Country
from main.filters import ClassifiedAdFilter
from main.forms import AdImageFormSet, ClassifiedAdForm, ContactForm
from main.models import (
    AdFeature,
    AdReport,
    Category,
    ClassifiedAd,
    AdPackage,
    UserPackage,
    CartSettings,
    User,
    CustomField,
    Payment,
    Notification,
    ChatRoom,
    ChatMessage,
)
from main.templatetags.idrissimart_tags import phone_format
from main.utils import get_selected_country_from_request


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        from content.site_config import HomePage

        context = super().get_context_data(**kwargs)

        # Get HomePage content from django-solo
        home_page = HomePage.get_solo()
        context["home_page"] = home_page

        # Get selected country from middleware/utility function
        selected_country = get_selected_country_from_request(self.request)

        # Fetch categories efficiently using MPTT
        categories_by_section = {}
        for section_code, section_name in Category.SectionType.choices:
            # Get all nodes for this section, ordered correctly for MPTT.
            # We limit the depth to level 1 (root and their direct children).
            nodes = (
                Category.objects.with_ad_counts()
                .filter(
                    section_type=section_code,
                    country__code=selected_country,
                )
                .filter(level__lte=1, is_active=True)
            )

            categories_by_section[section_code] = {
                "name": section_name,
                "nodes": nodes,  # Pass the MPTT queryset to the template
            }

        # Fetch latest and featured ads based on selected country
        latest_ads = ClassifiedAd.objects.active_for_country(selected_country).order_by(
            "-created_at"
        )[:6]
        featured_ads = ClassifiedAd.objects.featured_for_country(selected_country)[:6]

        # Get cart and wishlist items from session for current user
        cart_items = self.request.session.get("cart", [])
        wishlist_items = self.request.session.get("wishlist", [])

        for ad in latest_ads:
            ad.is_in_cart = str(ad.id) in cart_items
            ad.is_in_wishlist = str(ad.id) in wishlist_items
        for ad in featured_ads:
            ad.is_in_cart = str(ad.id) in cart_items
            ad.is_in_wishlist = str(ad.id) in wishlist_items
        # Fallback: If there are no featured ads, show the latest ads instead.
        if not featured_ads.exists():
            featured_ads = latest_ads

        context["selected_country"] = selected_country
        context["categories_by_section"] = categories_by_section
        context["latest_ads"] = latest_ads
        context["featured_ads"] = featured_ads
        # Add all latest blogs to the context for slider
        context["latest_blogs"] = (
            Blog.objects.filter(is_published=True)
            .order_by("-published_date")
            .select_related("author")
        )
        context["page_title"] = _("الرئيسية - إدريسي مارت")

        return context


def _get_categories_with_subcategories(country_code=None):
    """
    Helper function to get categories with their subcategories
    """
    # Get main categories (parent categories)
    main_categories = Category.objects.filter(
        parent__isnull=True, is_active=True
    ).order_by("order", "name")

    categories_by_section = {}

    for category in main_categories:
        section = category.section_type
        if section not in categories_by_section:
            categories_by_section[section] = []

        # Get subcategories for this main category
        subcategories = (
            category.get_children().filter(is_active=True).order_by("order", "name")
        )

        categories_by_section[section].append(
            {"category": category, "subcategories": subcategories}
        )

    return categories_by_section


class CategoriesView(FilterView):
    """
    Generic Categories View with flexible content type support
    Handles main categories, subcategories, and sub-subcategories with related content
    """

    model = ClassifiedAd  # Default model, can be overridden
    filterset_class = ClassifiedAdFilter
    template_name = "pages/categories.html"
    context_object_name = "ads"
    paginate_by = 12

    # Configuration for different content types
    content_type_config = {
        "classified": {
            "model": "ClassifiedAd",
            "status_field": "status",
            "active_status": "ACTIVE",
            "category_field": "category",
            "country_field": "country__code",
            "search_fields": [
                "title",
                "description",
                "category__name",
                "category__name_ar",
            ],
            "price_fields": {"min": "price__gte", "max": "price__lte"},
            "sort_fields": [
                "price",
                "-price",
                "created_at",
                "-created_at",
                "views_count",
                "-views_count",
                "title",
                "-title",
            ],
            "related_fields": ["user", "category", "country"],
            "prefetch_fields": ["images", "features"],
        }
        # Future content types can be added here:
        # 'product': { ... },
        # 'service': { ... },
        # 'job': { ... },
    }

    def get_content_type(self):
        """Determine content type from section parameter"""
        section = self.request.GET.get("section", "classified")
        return section if section in self.content_type_config else "classified"

    def get_model_class(self):
        """Get the appropriate model class based on content type"""
        content_type = self.get_content_type()
        config = self.content_type_config[content_type]

        if content_type == "classified":
            return ClassifiedAd
        # Future model mappings can be added here
        return ClassifiedAd

    def get_queryset(self):
        """
        Generic queryset builder that works with different content types
        """
        content_type = self.get_content_type()
        config = self.content_type_config[content_type]
        model_class = self.get_model_class()

        # Get selected country
        selected_country = get_selected_country_from_request(self.request)

        # Build base queryset with proper filtering
        base_filters = {}
        if config.get("status_field") and config.get("active_status"):
            if content_type == "classified":
                base_filters[config["status_field"]] = ClassifiedAd.AdStatus.ACTIVE

        if config.get("country_field"):
            base_filters[config["country_field"]] = selected_country

        queryset = model_class.objects.filter(**base_filters)

        # Apply related and prefetch fields
        if config.get("related_fields"):
            queryset = queryset.select_related(*config["related_fields"])
        if config.get("prefetch_fields"):
            queryset = queryset.prefetch_related(*config["prefetch_fields"])

        # Apply parent category filtering (for viewing subcategories)
        parent_id = self.request.GET.get("parent")
        if parent_id:
            try:
                parent_category = Category.objects.get(id=parent_id, is_active=True)
                # Get all descendants (subcategories and sub-subcategories)
                descendants = parent_category.get_descendants(include_self=True)
                filter_field = config.get("category_field", "category")
                queryset = queryset.filter(**{f"{filter_field}__in": descendants})
            except (Category.DoesNotExist, ValueError):
                pass
        else:
            # Apply category filtering by slug - supports main, sub, and sub-sub categories
            category_slug = self.request.GET.get("category")
            if category_slug:
                try:
                    category = Category.objects.get(slug=category_slug, is_active=True)
                    # Get all descendants (subcategories and sub-subcategories)
                    descendants = category.get_descendants(include_self=True)
                    filter_field = config.get("category_field", "category")
                    queryset = queryset.filter(**{f"{filter_field}__in": descendants})
                except Category.DoesNotExist:
                    pass

        # Apply section filtering
        section = self.request.GET.get("section")
        if section and section != "all":
            section_type = self._get_section_type_from_string(section)
            if section_type:
                queryset = queryset.filter(category__section_type=section_type)

        # Apply text search
        search = self.request.GET.get("search")
        if search and config.get("search_fields"):
            search_q = models.Q()
            for field in config["search_fields"]:
                search_q |= models.Q(**{f"{field}__icontains": search})
            queryset = queryset.filter(search_q)

        # Apply price range filtering
        price_config = config.get("price_fields", {})
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")

        if min_price and price_config.get("min"):
            try:
                queryset = queryset.filter(**{price_config["min"]: float(min_price)})
            except (ValueError, TypeError):
                pass

        if max_price and price_config.get("max"):
            try:
                queryset = queryset.filter(**{price_config["max"]: float(max_price)})
            except (ValueError, TypeError):
                pass

        # Apply sorting
        sort_by = self.request.GET.get("sort", "-created_at")
        valid_sorts = config.get("sort_fields", ["-created_at"])
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def _get_section_type_from_string(self, section_string):
        """Convert URL section parameter to model section type"""
        section_mapping = {
            "classified": Category.SectionType.CLASSIFIED,
            "product": Category.SectionType.PRODUCT,
            "service": Category.SectionType.SERVICE,
            "job": Category.SectionType.JOB,
            "course": Category.SectionType.COURSE,
        }
        return section_mapping.get(section_string)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get content type and configuration
        content_type = self.get_content_type()
        active_section = self.request.GET.get("section", "all")

        # Get cart and wishlist items from session for current user
        cart_items = self.request.session.get("cart", [])
        wishlist_items = self.request.session.get("wishlist", [])
        for ad in context["ads"]:
            ad.is_in_cart = str(ad.id) in cart_items
            ad.is_in_wishlist = str(ad.id) in wishlist_items

        # Get selected country
        selected_country = get_selected_country_from_request(self.request)

        # Check if filtering by parent category
        parent_id = self.request.GET.get("parent")
        parent_category = None
        if parent_id:
            try:
                parent_category = Category.objects.get(id=parent_id, is_active=True)
            except (Category.DoesNotExist, ValueError):
                parent_category = None

        # Get categories by section with content counts (generic approach)
        # If parent is specified, get subcategories of that parent
        if parent_category:
            categories_by_section = self._get_subcategories_with_content_counts(
                parent_category, content_type, selected_country
            )
        else:
            categories_by_section = self._get_categories_with_content_counts(
                section_type=content_type, country_code=selected_country
            )

        # Get cart and wishlist counts from session
        cart_count = len(self.request.session.get("cart", []))
        wishlist_count = len(self.request.session.get("wishlist", []))

        # Get current filters for display
        current_filters = {
            "search": self.request.GET.get("search", ""),
            "category": self.request.GET.get("category", ""),
            "parent": self.request.GET.get("parent", ""),
            "section": self.request.GET.get("section", "all"),
            "min_price": self.request.GET.get("min_price", ""),
            "max_price": self.request.GET.get("max_price", ""),
            "sort": self.request.GET.get("sort", "-created_at"),
        }

        # Calculate statistics based on content type
        total_items = self.get_queryset().count()
        section_type_value = self._get_section_type_from_string(content_type)

        # Calculate active categories based on parent filter
        if parent_category:
            active_categories = (
                parent_category.get_children().filter(is_active=True).count()
            )
        else:
            active_categories = Category.objects.filter(
                is_active=True,
                section_type=section_type_value or Category.SectionType.CLASSIFIED,
            ).count()

        # Dynamic context based on content type
        context_names = {
            "classified": {
                "items_name": "ads",
                "total_items_label": "total_ads",
                "page_title": _("الإعلانات المبوبة - إدريسي مارت"),
                "meta_description": _(
                    "استكشف جميع الإعلانات المبوبة في منصة إدريسي مارت"
                ),
            }
            # Future content types can be added here
        }

        content_labels = context_names.get(content_type, context_names["classified"])

        # Get all active categories for the category filter dropdown (hierarchical)
        # If viewing subcategories of a parent, show those; otherwise show root categories
        if parent_category:
            all_categories = (
                parent_category.get_children()
                .filter(is_active=True)
                .prefetch_related("children")
                .order_by("order", "name")
            )
        else:
            all_categories = (
                Category.objects.filter(
                    is_active=True,
                    section_type=section_type_value or Category.SectionType.CLASSIFIED,
                    parent__isnull=True,
                )
                .prefetch_related("subcategories__subcategories")
                .order_by("order", "name")
            )

        context.update(
            {
                "selected_country": selected_country,
                "categories_by_section": categories_by_section,
                "active_section": active_section,
                "content_type": content_type,
                "cart_count": cart_count,
                "wishlist_count": wishlist_count,
                "current_filters": current_filters,
                content_labels["total_items_label"]: total_items,
                "total_categories": active_categories,
                "categories": all_categories,
                "active_categories": active_categories,
                "page_title": content_labels["page_title"],
                "meta_description": content_labels["meta_description"],
                "has_filters": any(current_filters.values()),
                "parent_category": parent_category,  # Add parent category to context
            }
        )

        return context

    def _get_categories_with_content_counts(
        self, section_type="classified", country_code=None
    ):
        """
        Generic helper function to get categories with their subcategories and content counts
        Works with any content type (classified ads, products, services, etc.)
        """
        # Map section type to Category enum
        section_type_value = self._get_section_type_from_string(section_type)
        if not section_type_value:
            section_type_value = Category.SectionType.CLASSIFIED

        # Get main categories (root level)
        main_categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True,
            section_type=section_type_value,
        ).order_by("order", "name")

        categories_by_section = {}
        content_type = section_type
        config = self.content_type_config.get(
            content_type, self.content_type_config["classified"]
        )

        for category in main_categories:
            section = category.section_type
            if section not in categories_by_section:
                categories_by_section[section] = []

            # Get all descendants (includes subcategories and sub-subcategories)
            descendants = category.get_descendants(include_self=True)

            # Count content items for this category tree
            content_count = self._count_content_for_categories(
                descendants, content_type, config, country_code
            )

            # Process subcategories with their own counts
            subcategory_data = []
            subcategories = (
                category.get_children().filter(is_active=True).order_by("order", "name")
            )

            for subcat in subcategories:
                subcat_descendants = subcat.get_descendants(include_self=True)
                subcat_count = self._count_content_for_categories(
                    subcat_descendants, content_type, config, country_code
                )

                # Process sub-subcategories
                sub_subcategory_data = []
                sub_subcategories = (
                    subcat.get_children()
                    .filter(is_active=True)
                    .order_by("order", "name")
                )

                for sub_subcat in sub_subcategories:
                    sub_subcat_descendants = sub_subcat.get_descendants(
                        include_self=True
                    )
                    sub_subcat_count = self._count_content_for_categories(
                        sub_subcat_descendants, content_type, config, country_code
                    )
                    sub_subcategory_data.append(
                        {
                            "category": sub_subcat,
                            "content_count": sub_subcat_count,
                        }
                    )

                subcategory_data.append(
                    {
                        "category": subcat,
                        "content_count": subcat_count,
                        "sub_subcategories": sub_subcategory_data,
                    }
                )

            categories_by_section[section].append(
                {
                    "category": category,
                    "subcategories": subcategory_data,
                    "content_count": content_count,
                }
            )

        return categories_by_section

    def _get_subcategories_with_content_counts(
        self, parent_category, content_type="classified", country_code=None
    ):
        """
        Get subcategories of a parent category with their content counts
        Similar to _get_categories_with_content_counts but for subcategories
        """
        categories_by_section = {}
        config = self.content_type_config.get(
            content_type, self.content_type_config["classified"]
        )

        section = parent_category.section_type
        if section not in categories_by_section:
            categories_by_section[section] = []

        # Get direct children (subcategories) of the parent
        subcategories = (
            parent_category.get_children()
            .filter(is_active=True)
            .order_by("order", "name")
        )

        for subcat in subcategories:
            subcat_descendants = subcat.get_descendants(include_self=True)
            subcat_count = self._count_content_for_categories(
                subcat_descendants, content_type, config, country_code
            )

            # Process sub-subcategories
            sub_subcategory_data = []
            sub_subcategories = (
                subcat.get_children().filter(is_active=True).order_by("order", "name")
            )

            for sub_subcat in sub_subcategories:
                sub_subcat_descendants = sub_subcat.get_descendants(include_self=True)
                sub_subcat_count = self._count_content_for_categories(
                    sub_subcat_descendants, content_type, config, country_code
                )
                sub_subcategory_data.append(
                    {
                        "category": sub_subcat,
                        "content_count": sub_subcat_count,
                    }
                )

            categories_by_section[section].append(
                {
                    "category": subcat,
                    "subcategories": sub_subcategory_data,
                    "content_count": subcat_count,
                }
            )

        return categories_by_section

    def _count_content_for_categories(
        self, categories, content_type, config, country_code=None
    ):
        """
        Generic method to count content items for given categories
        """
        if content_type == "classified":
            # Count classified ads
            base_filters = {
                "category__in": categories,
                "status": ClassifiedAd.AdStatus.ACTIVE,
            }
            if country_code:
                base_filters["country__code"] = country_code

            return ClassifiedAd.objects.filter(**base_filters).count()

        # Future content types can be handled here
        # elif content_type == 'product':
        #     return Product.objects.filter(category__in=categories, is_active=True).count()

        return 0


@require_POST
def set_country(request):
    """
    API endpoint to set user's selected country
    """
    try:
        country_code = request.POST.get("country_code")

        if not country_code:
            return JsonResponse(
                {"success": False, "message": _("لم يتم تحديد البلد")}, status=400
            )

        # Validate country exists and is active
        try:
            country = Country.objects.get(code=country_code, is_active=True)
        except Country.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": _("البلد المحدد غير متاح")}, status=404
            )

        # Store in session
        request.session["selected_country"] = country_code
        request.session["selected_country_name"] = country.name

        # Optional: Store in user model if authenticated
        if request.user.is_authenticated:
            request.user.country = country_code
            request.user.save(update_fields=["country"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم تغيير البلد بنجاح"),
                "country_code": country_code,
                "country_name": country.name,
            }
        )

    except Exception:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ في تغيير البلد")}, status=500
        )


class CategoryDetailView(FilterView):
    """
    عرض تفاصيل القسم مع الإعلانات والفلترة المتقدمة
    Displays a category page with ads listing and advanced filtering
    """

    model = ClassifiedAd
    filterset_class = ClassifiedAdFilter
    template_name = "pages/category_detail.html"
    context_object_name = "ads"
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        """Get the category object and add it to the instance"""
        try:
            self.category = get_object_or_404(
                Category, slug=self.kwargs["slug"], is_active=True
            )
        except Http404:
            self.category = None

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        إرجاع الإعلانات من القسم الحالي وجميع الأقسام الفرعية
        Return ads from the current category and all its descendants.
        """
        if not self.category:
            return ClassifiedAd.objects.none()

        # self.category is set in dispatch()
        descendants = self.category.get_descendants(include_self=True)
        selected_country = get_selected_country_from_request(self.request)

        queryset = (
            ClassifiedAd.objects.filter(
                category__in=descendants,
                status=ClassifiedAd.AdStatus.ACTIVE,
                country__code=selected_country,
            )
            .select_related("user", "category", "country")
            .prefetch_related("images", "features")
        )

        # تطبيق الفلاتر الإضافية
        queryset = self.apply_custom_filters(queryset)

        # تطبيق الترتيب
        queryset = self.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.category:
            context["category"] = None
            context["page_title"] = _("القسم غير موجود")
            return context

        # Get selected country
        selected_country = get_selected_country_from_request(self.request)

        # Build breadcrumbs
        breadcrumbs = []
        ancestors = self.category.get_ancestors(ascending=True)
        for ancestor in ancestors:
            breadcrumbs.append(
                {
                    "name": ancestor.name_ar if ancestor.name_ar else ancestor.name,
                    "url": f"/category/{ancestor.slug}/",
                }
            )

        # Category statistics
        descendants = self.category.get_descendants(include_self=True)
        total_ads = ClassifiedAd.objects.filter(
            category__in=descendants,
            status=ClassifiedAd.AdStatus.ACTIVE,
            country__code=selected_country,
        ).count()

        subcategories_count = (
            self.category.get_children().filter(is_active=True).count()
        )

        # Current filters for display
        current_filters = {
            "search": self.request.GET.get("search", ""),
            "min_price": self.request.GET.get("min_price", ""),
            "max_price": self.request.GET.get("max_price", ""),
            "city": self.request.GET.get("city", ""),
            "sort": self.request.GET.get("sort", "-created_at"),
            "negotiable": bool(self.request.GET.get("negotiable")),
            "delivery": bool(self.request.GET.get("delivery")),
            "verified_only": bool(self.request.GET.get("verified_only")),
        }

        context.update(
            {
                "category": self.category,
                "breadcrumbs": breadcrumbs,
                "total_ads": total_ads,
                "subcategories_count": subcategories_count,
                "current_filters": current_filters,
                "has_filters": any(v for v in current_filters.values() if v),
                "selected_country": selected_country,
                "page_title": (
                    self.category.name_ar
                    if self.category.name_ar
                    else self.category.name
                )
                + " - "
                + _("إدريسي مارت"),
                "meta_description": (
                    self.category.description_ar
                    if self.category.description_ar
                    else self.category.description
                )
                or _("تصفح إعلانات قسم {category}").format(
                    category=(
                        self.category.name_ar
                        if self.category.name_ar
                        else self.category.name
                    )
                ),
            }
        )

        return context

        # تطبيق الفلاتر الإضافية
        queryset = self.apply_custom_filters(queryset)

        # تطبيق الترتيب
        queryset = self.apply_sorting(queryset)

        return queryset

    def apply_custom_filters(self, queryset):
        """تطبيق فلاتر مخصصة إضافية"""
        # البحث النصي
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search)
                | models.Q(description__icontains=search)
            )

        # فلتر السعر
        min_price = self.request.GET.get("min_price")
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = self.request.GET.get("max_price")
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # فلتر المدينة
        city = self.request.GET.get("city")
        if city:
            queryset = queryset.filter(city__icontains=city)

        # فلتر قابل للتفاوض
        if self.request.GET.get("negotiable"):
            queryset = queryset.filter(is_negotiable=True)

        # فلتر التوصيل
        if self.request.GET.get("delivery"):
            queryset = queryset.filter(is_delivery_available=True)

        # فلتر الأعضاء الموثقين فقط
        if self.request.GET.get("verified_only"):
            queryset = queryset.filter(user__verification_status="verified")

        return queryset

    def apply_sorting(self, queryset):
        """تطبيق الترتيب"""
        sort_option = self.request.GET.get("sort", "-created_at")

        valid_sorts = [
            "-created_at",  # الأحدث
            "created_at",  # الأقدم
            "price",  # السعر الأقل
            "-price",  # السعر الأعلى
            "-views_count",  # الأكثر مشاهدة
            "title",  # العنوان أ-ي
            "-title",  # العنوان ي-أ
        ]

        if sort_option in valid_sorts:
            queryset = queryset.order_by(sort_option)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # MPTT's get_ancestors is highly efficient for breadcrumbs
        context["breadcrumbs"] = self.category.get_ancestors(include_self=True)
        context["category"] = self.category

        # Get direct subcategories for initial display
        context["subcategories"] = (
            self.category.get_children()
            .filter(is_active=True)
            .order_by("order", "name")[:12]
        )

        # إضافة قائمة المدن المتاحة للفلترة
        descendants = self.category.get_descendants(include_self=True)
        selected_country = get_selected_country_from_request(self.request)

        context["cities"] = (
            ClassifiedAd.objects.filter(
                category__in=descendants,
                status=ClassifiedAd.AdStatus.ACTIVE,
                country__code=selected_country,
            )
            .values_list("city", flat=True)
            .distinct()
            .order_by("city")
        )

        # Pass the query string to the template for pagination
        context["query_params"] = self.request.GET.urlencode()
        context["page_title"] = f"{self.category.name} - {_('إدريسي مارت')}"

        # Add category stats
        context["ads_count"] = ClassifiedAd.objects.filter(
            category__in=descendants,
            status=ClassifiedAd.AdStatus.ACTIVE,
            country__code=selected_country,
        ).count()
        context["subcategories_count"] = context["subcategories"].count()

        # إضافة قائمة الأقسام الرئيسية للفلترة
        context["categories"] = Category.objects.filter(
            parent=None, is_active=True
        ).order_by("name")

        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Get the category object from the slug and make it available to other methods.
        """
        slug = self.kwargs.get("slug")
        # Try to find category by both slug and slug_ar
        try:
            self.category = Category.objects.get(
                models.Q(slug=slug) | models.Q(slug_ar=slug), is_active=True
            )
        except Category.DoesNotExist:
            raise Http404("Category not found")

        return super().dispatch(request, *args, **kwargs)


class SubcategoryDetailView(FilterView):
    """
    عرض تفاصيل القسم الفرعي مع الإعلانات والفلترة المتقدمة
    Displays a subcategory page with ads listing and advanced filtering
    """

    model = ClassifiedAd
    filterset_class = ClassifiedAdFilter
    template_name = "pages/categories.html"
    context_object_name = "ads"
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        """Get the category object and add it to the instance"""
        try:
            self.category = get_object_or_404(
                Category, slug=self.kwargs["slug"], is_active=True
            )
        except Http404:
            self.category = None

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        إرجاع الإعلانات من القسم الفرعي الحالي
        Return ads from the current subcategory only.
        """
        if not self.category:
            return ClassifiedAd.objects.none()

        selected_country = get_selected_country_from_request(self.request)

        queryset = (
            ClassifiedAd.objects.filter(
                category=self.category,  # Only this specific subcategory
                status=ClassifiedAd.AdStatus.ACTIVE,
                country__code=selected_country,
            )
            .select_related("user", "category", "country")
            .prefetch_related("images", "features")
        )

        # تطبيق الفلاتر الإضافية
        queryset = self.apply_custom_filters(queryset)

        # تطبيق الترتيب
        queryset = self.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.category:
            context["category"] = None
            context["page_title"] = _("القسم غير موجود")
            return context

        # Get selected country
        selected_country = get_selected_country_from_request(self.request)

        # Build breadcrumbs
        breadcrumbs = []
        ancestors = self.category.get_ancestors(ascending=True)
        for ancestor in ancestors:
            breadcrumbs.append(
                {
                    "name": ancestor.name_ar if ancestor.name_ar else ancestor.name,
                    "url": f"/category/{ancestor.slug}/",
                }
            )

        # Category statistics
        total_ads = ClassifiedAd.objects.filter(
            category=self.category,
            status=ClassifiedAd.AdStatus.ACTIVE,
            country__code=selected_country,
        ).count()

        # Get subcategories
        subcategories = (
            self.category.get_children()
            .filter(is_active=True)
            .order_by("order", "name")
        )
        total_subcategories = subcategories.count()

        # Current filters for display
        current_filters = {
            "search": self.request.GET.get("search", ""),
            "min_price": self.request.GET.get("min_price", ""),
            "max_price": self.request.GET.get("max_price", ""),
            "city": self.request.GET.get("city", ""),
            "sort": self.request.GET.get("sort", "-created_at"),
            "negotiable": bool(self.request.GET.get("negotiable")),
            "delivery": bool(self.request.GET.get("delivery")),
            "verified": bool(self.request.GET.get("verified")),
        }

        context.update(
            {
                "category": self.category,
                "breadcrumbs": breadcrumbs,
                "subcategories": subcategories,
                "total_subcategories": total_subcategories,
                "total_ads": total_ads,
                "current_filters": current_filters,
                "selected_country": selected_country,
                "page_title": (
                    self.category.name_ar
                    if self.category.name_ar
                    else self.category.name
                ),
                "meta_description": (
                    self.category.description_ar
                    if self.category.description_ar
                    else self.category.description
                ),
                "has_filters": any(current_filters.values()),
            }
        )

        return context

    def apply_custom_filters(self, queryset):
        """تطبيق فلاتر مخصصة إضافية"""
        # البحث النصي
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search)
                | models.Q(description__icontains=search)
            )

        # فلتر السعر
        min_price = self.request.GET.get("min_price")
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = self.request.GET.get("max_price")
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # فلتر المدينة
        city = self.request.GET.get("city")
        if city:
            queryset = queryset.filter(city__icontains=city)

        # فلاتر منطقية
        if self.request.GET.get("negotiable"):
            queryset = queryset.filter(is_negotiable=True)

        if self.request.GET.get("delivery"):
            queryset = queryset.filter(delivery_available=True)

        if self.request.GET.get("verified"):
            queryset = queryset.filter(user__is_verified=True)

        return queryset

    def apply_sorting(self, queryset):
        """تطبيق الترتيب"""
        sort_by = self.request.GET.get("sort", "-created_at")
        valid_sorts = [
            "price",
            "-price",
            "created_at",
            "-created_at",
            "views_count",
            "-views_count",
            "title",
            "-title",
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)

        return queryset


class AboutView(TemplateView):
    """About page view"""

    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        from content.site_config import AboutPage

        context = super().get_context_data(**kwargs)

        # Get about page content from django-solo
        about_page = AboutPage.get_solo()

        context["about_page"] = about_page
        context["page_title"] = (
            about_page.title_ar if about_page.title_ar else _("من نحن - إدريسي مارت")
        )
        context["meta_description"] = _("تعرف على منصة إدريسي مارت ورؤيتنا ورسالتنا")

        return context


class ContactView(TemplateView):
    """Contact page view with form handling"""

    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        from constance import config
        from content.site_config import ContactPage

        context = super().get_context_data(**kwargs)

        # Get contact page content from django-solo
        contact_page = ContactPage.get_solo()

        # Initialize contact form
        form = ContactForm(
            user=self.request.user if self.request.user.is_authenticated else None
        )

        context["contact_page"] = contact_page
        context["form"] = form
        context["config"] = config
        context["page_title"] = (
            contact_page.title_ar
            if contact_page.title_ar
            else _("اتصل بنا - إدريسي مارت")
        )
        context["meta_description"] = (
            contact_page.description_ar
            if contact_page.description_ar
            else _("تواصل معنا في إدريسي مارت")
        )

        return context

    def post(self, request, *args, **kwargs):
        """Handle contact form submission"""
        form = ContactForm(
            request.POST, user=request.user if request.user.is_authenticated else None
        )

        if form.is_valid():
            form.save()
            messages.success(
                request, _("تم إرسال رسالتك بنجاح. سنتواصل معك في أقرب وقت ممكن.")
            )
            return redirect("main:contact")
        else:
            # If form is invalid, return the same page with errors
            context = self.get_context_data(**kwargs)
            context["form"] = form
            return self.render_to_response(context)


class SocialMediaView(TemplateView):
    """Social media page view"""

    template_name = "pages/social.html"

    def get_context_data(self, **kwargs):
        from constance import config

        context = super().get_context_data(**kwargs)
        context["config"] = config
        return context


class PrivacyPolicyView(TemplateView):
    """Privacy policy page view"""

    template_name = "pages/privacy.html"

    def get_context_data(self, **kwargs):
        from constance import config
        from content.site_config import PrivacyPage

        context = super().get_context_data(**kwargs)
        context["config"] = config
        privacy_page = PrivacyPage.get_solo()
        context["privacy_page"] = privacy_page
        context["page_title"] = (
            privacy_page.title_ar if privacy_page.title_ar else _("سياسة الخصوصية")
        )
        return context


class TermsConditionsView(TemplateView):
    """Terms and conditions page view"""

    template_name = "pages/terms.html"

    def get_context_data(self, **kwargs):
        from constance import config
        from content.site_config import TermsPage

        context = super().get_context_data(**kwargs)
        context["config"] = config
        terms_page = TermsPage.get_solo()
        context["terms_page"] = terms_page
        context["page_title"] = (
            terms_page.title_ar if terms_page.title_ar else _("الشروط والأحكام")
        )
        return context


@login_required
@require_POST
def add_to_cart(request):
    """Add item to cart"""
    item_id = request.POST.get("item_id")

    if not item_id:
        return JsonResponse(
            {"success": False, "message": _("Item ID required")}, status=400
        )

    cart = request.session.get("cart", [])

    if item_id not in cart:
        cart.append(item_id)
        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse(
            {
                "success": True,
                "message": _("تمت إضافة العنصر إلى السلة"),
                "cart_count": len(cart),
            }
        )

    return JsonResponse(
        {"success": False, "message": _("العنصر موجود بالفعل في السلة")}
    )


@login_required
@require_POST
def add_to_wishlist(request):
    """Add item to wishlist"""
    item_id = request.POST.get("item_id")

    if not item_id:
        return JsonResponse(
            {"success": False, "message": _("معرف العنصر مطلوب")}, status=400
        )

    wishlist = request.session.get("wishlist", [])

    if item_id not in wishlist:
        wishlist.append(item_id)
        request.session["wishlist"] = wishlist
        request.session.modified = True

        return JsonResponse(
            {
                "success": True,
                "message": _("تمت إضافة العنصر إلى قائمة الرغبات"),
                "wishlist_count": len(wishlist),
            }
        )

    return JsonResponse(
        {"success": False, "message": _("العنصر موجود بالفعل في قائمة الرغبات")}
    )


@login_required
@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    item_id = request.POST.get("item_id")
    cart = request.session.get("cart", [])

    if item_id in cart:
        cart.remove(item_id)
        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse(
            {
                "success": True,
                "message": _("تمت إزالة العنصر من السلة"),
                "cart_count": len(cart),
            }
        )

    return JsonResponse({"success": False, "message": _("العنصر غير موجود في السلة")})


@require_POST
def remove_from_wishlist(request):
    """Remove item from wishlist"""
    item_id = request.POST.get("item_id")
    wishlist = request.session.get("wishlist", [])

    if item_id in wishlist:
        wishlist.remove(item_id)
        request.session["wishlist"] = wishlist
        request.session.modified = True

        return JsonResponse(
            {
                "success": True,
                "message": _("تمت إزالة العنصر من قائمة الرغبات"),
                "wishlist_count": len(wishlist),
            }
        )

    return JsonResponse(
        {"success": False, "message": _("العنصر غير موجود في قائمة الرغبات")}
    )


class AdDetailView(DetailView):
    """
    View to display the details of a single classified ad.
    """

    model = ClassifiedAd
    template_name = "classifieds/ad_detail.html"
    context_object_name = "ad"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.get_object()

        # Check if ad is in user's cart or wishlist
        if self.request.user.is_authenticated:
            # For authenticated users, check database
            try:
                from main.models import Cart, Wishlist, WishlistItem, CartItem

                cart, _ = Cart.objects.get_or_create(user=self.request.user)
                wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)

                ad.is_in_cart = CartItem.objects.filter(cart=cart, ad=ad).exists()
                ad.is_in_wishlist = WishlistItem.objects.filter(
                    wishlist=wishlist, ad=ad
                ).exists()
            except Exception:
                ad.is_in_cart = False
                ad.is_in_wishlist = False
        else:
            # For guests, check session
            cart_items = self.request.session.get("cart", [])
            wishlist_items = self.request.session.get("wishlist", [])
            ad.is_in_cart = str(ad.id) in cart_items
            ad.is_in_wishlist = str(ad.id) in wishlist_items

        # Increment view count without triggering a full save/update_fields
        ClassifiedAd.objects.filter(pk=ad.pk).update(
            views_count=models.F("views_count") + 1
        )

        # Prepare custom fields with labels for clean display in the template
        custom_fields_with_labels = []
        if ad.custom_fields:
            from main.models import CategoryCustomField

            # Get custom fields for this category
            category_fields = (
                CategoryCustomField.objects.filter(category=ad.category, is_active=True)
                .select_related("custom_field")
                .order_by("order")
            )

            for cf in category_fields:
                field = cf.custom_field
                field_name = f"custom_{field.name}"
                value = ad.custom_fields.get(field_name)

                # Only show fields that have a value
                if value is not None and value != "":
                    custom_fields_with_labels.append(
                        {
                            "label": field.label_ar or field.name,
                            "value": value,
                            "type": field.field_type,
                        }
                    )
        context["custom_fields"] = custom_fields_with_labels

        # Get related ads from the same category, excluding the current one
        context["related_ads"] = (
            ClassifiedAd.objects.filter(
                category=ad.category, status=ClassifiedAd.AdStatus.ACTIVE
            )
            .exclude(pk=ad.pk)
            .select_related("user", "country")
            .prefetch_related("images")[:4]
        )

        category_name = ad.category.name
        if self.request.LANGUAGE_CODE == "ar" and ad.category.name_ar:
            category_name = ad.category.name_ar

        context["page_title"] = f"{ad.title} - {category_name}"
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    """
    View to handle the creation of a new classified ad.
    """

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:home")  # Redirect to home for now

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_country = self.request.session.get("selected_country", "EG")

        # Provide all 'classified' categories to the template
        context["ad_categories"] = Category.get_by_section_and_country(
            "classified", selected_country
        ).filter(parent__isnull=True)

        # Add the image formset to the context
        if self.request.POST:
            context["image_formset"] = AdImageFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["image_formset"] = AdImageFormSet()

        # Add mobile verification setting
        from constance import config

        context["mobile_verification_enabled"] = getattr(
            config, "ENABLE_MOBILE_VERIFICATION", True
        )

        # Add countries list
        from content.models import Country

        context["countries"] = Country.objects.filter(is_active=True).order_by(
            "order", "name"
        )

        return context

    def get_form_kwargs(self):
        """Pass the selected category and user to the form if available."""
        kwargs = super().get_form_kwargs()
        # Pass the current user to the form for mobile verification
        kwargs["user"] = self.request.user
        if "category" in self.request.GET:
            try:
                category = Category.objects.get(pk=self.request.GET["category"])
                kwargs["category"] = category
            except (Category.DoesNotExist, ValueError):
                pass
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, save the associated models.
        """
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            form.instance.user = self.request.user

            # Determine if ad needs approval
            # Skip approval if:
            # 1. User is staff, OR
            # 2. User is verified AND has an active package with remaining ads
            needs_approval = True

            if self.request.user.is_staff:
                needs_approval = False
            elif self.request.user.is_verified:
                # Check if user has an active package with remaining ads
                from main.models import UserPackage

                active_package = UserPackage.objects.filter(
                    user=self.request.user,
                    ads_remaining__gt=0,
                    expiry_date__gte=timezone.now(),
                ).first()

                if active_package:
                    needs_approval = False
                    # Deduct one ad from the package
                    active_package.use_ad()

            # Set status based on approval requirement
            if needs_approval:
                form.instance.status = ClassifiedAd.AdStatus.PENDING
            else:
                form.instance.status = ClassifiedAd.AdStatus.ACTIVE

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()

            # Show appropriate success message based on ad status
            if self.object.status == ClassifiedAd.AdStatus.ACTIVE:
                messages.success(self.request, _("تم نشر إعلانك بنجاح!"))
            else:
                messages.success(
                    self.request,
                    _("تم إرسال إعلانك للمراجعة! سيتم نشره بعد موافقة الإدارة."),
                )

            return super().form_valid(form)
        else:
            # Add formset errors to messages
            for error in image_formset.errors:
                if error:
                    messages.error(self.request, str(error))
            return self.form_invalid(form)


class AdUpdateView(LoginRequiredMixin, UpdateView):
    """
    View to handle updating an existing classified ad.
    """

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:home")

    def get_queryset(self):
        """Ensure users can only edit their own ads."""
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_country = self.request.session.get("selected_country", "EG")
        context["ad_categories"] = Category.get_by_section_and_country(
            "classified", selected_country
        ).filter(parent__isnull=True)

        if self.request.POST:
            context["image_formset"] = AdImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["image_formset"] = AdImageFormSet(instance=self.object)

        # Add mobile verification setting
        from constance import config

        context["mobile_verification_enabled"] = getattr(
            config, "ENABLE_MOBILE_VERIFICATION", True
        )

        # Add countries list
        from content.models import Country

        context["countries"] = Country.objects.filter(is_active=True).order_by(
            "order", "name"
        )

        return context

    def get_form_kwargs(self):
        """Pass the user to the form for mobile verification."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]
        if image_formset.is_valid():
            # Determine if updated ad needs re-approval
            # Skip re-approval if:
            # 1. User is staff, OR
            # 2. User is verified (trusted user)
            needs_approval = False

            if not self.request.user.is_staff and not self.request.user.is_verified:
                # Non-verified users need re-approval if ad was active
                if self.object.status == ClassifiedAd.AdStatus.ACTIVE:
                    needs_approval = True

            if needs_approval:
                form.instance.status = ClassifiedAd.AdStatus.PENDING
                messages.info(
                    self.request, _("سيتم مراجعة التعديلات من قبل الإدارة قبل نشرها.")
                )

            self.object = form.save()
            image_formset.save()
            messages.success(self.request, _("تم تحديث إعلانك بنجاح!"))
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


@csrf_exempt
def get_subcategories(request):
    """AJAX endpoint to fetch subcategories for a given category"""
    if request.method == "GET":
        category_id = request.GET.get("category_id")
        selected_country = request.session.get("selected_country", "EG")

        if not category_id:
            return JsonResponse({"error": _("معرف القسم مطلوب")}, status=400)

        try:
            category = Category.objects.get(id=category_id)
            # Get direct children (subcategories) of this category
            subcategories = (
                category.get_children().filter(is_active=True).order_by("order", "name")
            )

            # Filter by country if applicable
            if selected_country:
                from content.models import Country

                try:
                    country = Country.objects.get(code=selected_country, is_active=True)
                    subcategories = subcategories.filter(
                        models.Q(country=country)
                        | models.Q(countries=country)
                        | models.Q(country__isnull=True, countries__isnull=True)
                    ).distinct()
                except Country.DoesNotExist:
                    pass

            # Serialize subcategories data
            subcategories_data = []
            for subcat in subcategories:
                subcategories_data.append(
                    {
                        "id": subcat.id,
                        "name": subcat.name_ar if subcat.name_ar else subcat.name,
                        "slug": subcat.slug_ar if subcat.slug_ar else subcat.slug,
                        "icon": subcat.icon,
                        "url": f"/category/{subcat.slug}/",
                        "has_children": subcat.get_children()
                        .filter(is_active=True)
                        .exists(),
                    }
                )

            return JsonResponse(
                {
                    "subcategories": subcategories_data,
                    "parent_category": {
                        "id": category.id,
                        "name": category.name_ar if category.name_ar else category.name,
                        "slug": category.slug_ar if category.slug_ar else category.slug,
                    },
                }
            )

        except Category.DoesNotExist:
            return JsonResponse({"error": _("القسم غير موجود")}, status=404)

    return JsonResponse({"error": _("طريقة الطلب غير صالحة")}, status=405)


@csrf_exempt
def get_category_stats(request):
    """AJAX endpoint to fetch category statistics"""
    if request.method == "GET":
        category_id = request.GET.get("category_id")

        if not category_id:
            return JsonResponse({"error": _("معرف القسم مطلوب")}, status=400)

        try:
            category = Category.objects.get(id=category_id)

            # Get all descendants including self for ads count
            descendants = category.get_descendants(include_self=True)

            # Get country from utility function for filtering
            selected_country = get_selected_country_from_request(request)

            # Count active ads in this category and its descendants
            ads_count = ClassifiedAd.objects.filter(
                category__in=descendants,
                status=ClassifiedAd.AdStatus.ACTIVE,
                country__code=selected_country,
            ).count()

            # Count direct subcategories
            subcategories_count = category.get_children().filter(is_active=True).count()

            return JsonResponse(
                {
                    "ads_count": ads_count,
                    "subcategories_count": subcategories_count,
                    "category": {
                        "id": category.id,
                        "name": category.name_ar if category.name_ar else category.name,
                        "slug": category.slug_ar if category.slug_ar else category.slug,
                    },
                }
            )

        except Category.DoesNotExist:
            return JsonResponse({"error": _("القسم غير موجود")}, status=404)

    return JsonResponse({"error": _("طريقة الطلب غير صالحة")}, status=405)


@login_required
def enhanced_ad_create_view(request):
    """Simple enhanced ad creation view with balance check"""

    # First check if user is authenticated
    if not request.user.is_authenticated:
        messages.info(
            request,
            _("يجب تسجيل الدخول أولاً لتتمكن من نشر الإعلانات."),
        )
        return redirect("main:login")

    # Check if user has any active package with remaining ads
    active_package = (
        UserPackage.objects.filter(
            user=request.user,
            expiry_date__gte=timezone.now(),
            ads_remaining__gt=0,
        )
        .order_by("expiry_date")
        .first()
    )

    if not active_package:
        # User has no balance (ads_remaining = 0) or no active package
        messages.warning(
            request,
            _("يجب الاشتراك في باقة لتتمكن من نشر إعلان. رصيدك الحالي = 0"),
        )
        return redirect("main:packages_list")

    # Store remaining ads count for display
    request.session["ads_remaining"] = active_package.ads_remaining

    if request.method == "POST":
        # استخدام النموذج المبسط
        from .forms import SimpleEnhancedAdForm

        form = SimpleEnhancedAdForm(request.POST, user=request.user)

        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.status = "pending"
            ad.save()

            messages.success(request, _("تم إنشاء الإعلان بنجاح وسيتم مراجعته قريباً"))
            return redirect("main:ad_creation_success", ad_id=ad.id)
        else:
            messages.error(request, _("يرجى تصحيح الأخطاء أدناه"))
    else:
        from .forms import SimpleEnhancedAdForm

        form = SimpleEnhancedAdForm(user=request.user)

    categories = Category.objects.filter(level=0, is_active=True)
    return render(
        request,
        "classifieds/enhanced_ad_form.html",
        {"form": form, "categories": categories},
    )


def ad_creation_success_view(request):
    """Simple success view"""
    return render(request, "classifieds/ad_create_success.html")


def get_subcategories_ajax(request, category_id):
    """Get subcategories via AJAX with Arabic support"""
    try:
        category = Category.objects.get(id=category_id)
        subcategories = category.get_children().filter(is_active=True)

        subcategories_data = [
            {
                "id": subcat.id,
                "name": subcat.name,
                "name_ar": subcat.name_ar,
                "icon": subcat.icon if subcat.icon else "fas fa-folder",
                "slug": subcat.slug,
                "url": f"/category/{subcat.slug}/",
                "has_children": subcat.get_children().exists(),
            }
            for subcat in subcategories
        ]

        return JsonResponse(
            {
                "subcategories": subcategories_data,
                "parent_category": {
                    "id": category.id,
                    "name": category.name_ar or category.name,
                    "name_ar": category.name_ar,
                    "slug": category.slug,
                },
            }
        )
    except Category.DoesNotExist:
        return JsonResponse({"error": _("القسم غير موجود")}, status=404)


def enhanced_ad_creation_success_view(request, ad_id=None):
    """Enhanced success view"""
    context = {}
    if ad_id:
        try:
            ad = ClassifiedAd.objects.get(id=ad_id, user=request.user)
            context["ad"] = ad
        except ClassifiedAd.DoesNotExist:
            pass
    return render(request, "classifieds/ad_create_success.html", context)


def get_subcategories(request, category_id):
    """AJAX view to get subcategories with Arabic support"""
    try:
        category = get_object_or_404(Category, id=category_id)
        subcategories = category.get_children().filter(is_active=True)

        subcategories_data = [
            {
                "id": subcat.id,
                "name": subcat.name,
                "name_ar": subcat.name_ar,
                "icon": subcat.icon if subcat.icon else "fas fa-folder",
                "slug": subcat.slug,
                "url": f"/category/{subcat.slug}/",
                "has_children": subcat.get_children().exists(),
            }
            for subcat in subcategories
        ]

        return JsonResponse(
            {
                "subcategories": subcategories_data,
                "parent_category": {
                    "id": category.id,
                    "name": category.name_ar or category.name,
                    "name_ar": category.name_ar,
                    "slug": category.slug,
                },
            }
        )

    except Category.DoesNotExist:
        return JsonResponse({"error": _("القسم غير موجود")}, status=404)


def check_ad_allowance(request):
    """AJAX view to check if user can post ads"""
    if not request.user.is_authenticated:
        return JsonResponse({"allowed": False, "reason": _("غير مصادق عليه")})

    # TODO: Implement email verification when needed
    # if not request.user.is_email_verified:
    #     return JsonResponse({"allowed": False, "reason": _("البريد الإلكتروني لم يتم التحقق منه")})

    # Check package limits
    # TODO: Implement user package system when needed
    # user_settings = getattr(request.user, "cart_settings", None)
    # if user_settings and user_settings.current_package:
    #     package = user_settings.current_package
    #     if user_settings.used_ads >= package.max_ads:
    #         return JsonResponse({
    #             "allowed": False,
    #             "reason": _("تم الوصول إلى حد الباقة"),
    #             "used_ads": user_settings.used_ads,
    #             "max_ads": package.max_ads,
    #         })

    return JsonResponse(
        {
            "allowed": True,
            "used_ads": 0,  # TODO: Get from user package system
            "max_ads": 3,  # TODO: Get from user package system
        }
    )


@login_required
@require_POST
def send_mobile_verification(request):
    """Send OTP verification code to mobile number"""
    mobile_number = request.POST.get("mobile_number", "").strip()

    if not mobile_number:
        return JsonResponse({"success": False, "message": _("رقم الجوال مطلوب")})

    verification_service = MobileVerificationService()

    # Check if verification is required
    required, message = verification_service.check_mobile_verification_required(
        request.user, mobile_number
    )

    if not required:
        return JsonResponse({"success": True, "verified": True, "message": message})

    # Send verification code
    success, message = verification_service.initiate_verification(
        request.user, mobile_number
    )

    return JsonResponse({"success": success, "verified": False, "message": message})


@login_required
@require_POST
def verify_mobile_otp(request):
    """Verify the OTP code for mobile number"""
    verification_code = request.POST.get("verification_code", "").strip()

    if not verification_code:
        return JsonResponse({"success": False, "message": _("رمز التحقق مطلوب")})

    verification_service = MobileVerificationService()
    success, message = verification_service.verify_mobile_for_ad(
        request.user, verification_code
    )

    return JsonResponse({"success": success, "message": message})


@csrf_exempt
def filter_categories_ajax(request):
    """
    AJAX endpoint for filtering categories and ads on categories page
    """
    if request.method == "GET":
        # Get filter parameters
        search = request.GET.get("search", "").strip()
        section = request.GET.get("section", "all")
        category_slug = request.GET.get("category", "")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        sort_by = request.GET.get("sort", "-created_at")

        # Get selected country
        selected_country = get_selected_country_from_request(request)

        try:
            # Start with active categories
            categories_queryset = Category.objects.filter(
                is_active=True,
                section_type=Category.SectionType.CLASSIFIED,
                parent__isnull=True,
            )

            # Apply search filter to categories
            if search:
                categories_queryset = categories_queryset.filter(
                    models.Q(name__icontains=search)
                    | models.Q(name_ar__icontains=search)
                    | models.Q(description__icontains=search)
                    | models.Q(description_ar__icontains=search)
                )

            # Apply section filter
            if section != "all":
                categories_queryset = categories_queryset.filter(section_type=section)

            # Get ads queryset
            ads_queryset = ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.ACTIVE,
                country__code=selected_country,
            ).select_related("category", "user")

            # Apply category filter to ads
            if category_slug:
                try:
                    category = Category.objects.get(slug=category_slug, is_active=True)
                    descendants = category.get_descendants(include_self=True)
                    ads_queryset = ads_queryset.filter(category__in=descendants)
                except Category.DoesNotExist:
                    pass

            # Apply search filter to ads
            if search:
                ads_queryset = ads_queryset.filter(
                    models.Q(title__icontains=search)
                    | models.Q(description__icontains=search)
                    | models.Q(category__name__icontains=search)
                    | models.Q(category__name_ar__icontains=search)
                )

            # Apply price filters
            if min_price:
                try:
                    ads_queryset = ads_queryset.filter(price__gte=float(min_price))
                except (ValueError, TypeError):
                    pass

            if max_price:
                try:
                    ads_queryset = ads_queryset.filter(price__lte=float(max_price))
                except (ValueError, TypeError):
                    pass

            # Apply sorting
            valid_sorts = [
                "price",
                "-price",
                "created_at",
                "-created_at",
                "views_count",
                "-views_count",
                "title",
                "-title",
            ]
            if sort_by in valid_sorts:
                ads_queryset = ads_queryset.order_by(sort_by)

            # Build response data
            filtered_categories = []
            for category in categories_queryset[:50]:  # Limit categories
                # Get ad count for this category
                descendants = category.get_descendants(include_self=True)
                category_ads_count = ads_queryset.filter(
                    category__in=descendants
                ).count()

                # Get subcategories with counts
                subcategories_data = []
                subcategories = category.get_children().filter(is_active=True)[:10]
                for subcat in subcategories:
                    subcat_descendants = subcat.get_descendants(include_self=True)
                    subcat_ads_count = ads_queryset.filter(
                        category__in=subcat_descendants
                    ).count()
                    subcategories_data.append(
                        {
                            "id": subcat.id,
                            "name": subcat.name_ar if subcat.name_ar else subcat.name,
                            "slug": subcat.slug_ar if subcat.slug_ar else subcat.slug,
                            "icon": subcat.icon or "",
                            "ads_count": subcat_ads_count,
                            "url": f"/category/{subcat.slug}/",
                        }
                    )

                filtered_categories.append(
                    {
                        "id": category.id,
                        "name": category.name_ar if category.name_ar else category.name,
                        "slug": category.slug_ar if category.slug_ar else category.slug,
                        "icon": category.icon or "",
                        "description": (
                            category.description_ar
                            if category.description_ar
                            else category.description
                        ),
                        "ads_count": category_ads_count,
                        "subcategories": subcategories_data,
                        "url": f"/category/{category.slug}/",
                    }
                )

            # Get sample ads for the current filters
            sample_ads = []
            for ad in ads_queryset[:12]:  # Limit ads
                sample_ads.append(
                    {
                        "id": ad.id,
                        "title": ad.title,
                        "price": float(ad.price) if ad.price else 0,
                        "currency": "MAD",  # or get from ad/settings
                        "category_name": (
                            ad.category.name_ar
                            if ad.category.name_ar
                            else ad.category.name
                        ),
                        "location": ad.city or "",
                        "created_at": ad.created_at.strftime("%Y-%m-%d"),
                        "image_url": (
                            ad.images.first().image.url if ad.images.exists() else ""
                        ),
                        "url": f"/classifieds/{ad.id}/",
                        "is_featured": getattr(ad, "is_featured", False),
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "categories": filtered_categories,
                    "ads": sample_ads,
                    "total_categories": len(filtered_categories),
                    "total_ads": ads_queryset.count(),
                    "filters_applied": {
                        "search": search,
                        "section": section,
                        "category": category_slug,
                        "price_range": [min_price, max_price],
                        "sort": sort_by,
                    },
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": str(e),
                    "message": _("حدث خطأ في تحديث النتائج"),
                },
                status=500,
            )

    return JsonResponse({"error": "Invalid request method"}, status=405)


class AdCardShowcaseView(TemplateView):
    """Showcase view to demonstrate the modern ad card design"""

    template_name = "test/ad_card_showcase.html"


class ComparisonView(TemplateView):
    """
    View to display a side-by-side comparison of selected ads.
    """

    template_name = "classifieds/compare_ads.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad_ids_str = self.request.GET.get("ids", "")
        ad_ids = [int(id) for id in ad_ids_str.split(",") if id.isdigit()]

        if ad_ids:
            # Fetch ads, preserving the order of IDs for display consistency
            ads = list(ClassifiedAd.objects.filter(pk__in=ad_ids))
            ads.sort(key=lambda ad: ad_ids.index(ad.pk))
            context["ads_to_compare"] = ads

            # Compute the minimum price among the compared ads (for "أقل سعر")
            # Ignore ads with null/zero prices in the min calculation
            prices = [ad.price for ad in ads if getattr(ad, "price", None)]
            if prices:
                context["min_compare_price"] = min(prices)

            # Increment view count for each ad being compared
            # Use F() expression to avoid race conditions
            from django.db.models import F

            ClassifiedAd.objects.filter(pk__in=ad_ids).update(
                views_count=F("views_count") + 1
            )
        else:
            context["ads_to_compare"] = []

        context["page_title"] = _("مقارنة الإعلانات")
        return context


# ==============================================
# PUBLISHER DASHBOARD VIEWS
# ==============================================

from .decorators import PublisherRequiredMixin, publisher_required


class PublisherDashboardView(PublisherRequiredMixin, ListView):
    """
    Publisher Dashboard - Main dashboard view with ad listing and management
    Restricted to users with publisher profile type or users who have created ads
    """

    model = ClassifiedAd
    template_name = "dashboard/publisher_dashboard.html"
    context_object_name = "ads"
    paginate_by = 20

    def get_queryset(self):
        """Get user's own ads with filtering and searching"""
        queryset = (
            ClassifiedAd.objects.filter(user=self.request.user)
            .select_related("category", "country")
            .prefetch_related("images")
        )

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search)
                | models.Q(description__icontains=search)
            )

        # Status filtering
        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Date range filtering
        date_from = self.request.GET.get("date_from")
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = self.request.GET.get("date_to")
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # Sorting
        sort_by = self.request.GET.get("sort", "-created_at")
        valid_sorts = [
            "title",
            "-title",
            "price",
            "-price",
            "created_at",
            "-created_at",
            "views_count",
            "-views_count",
            "status",
            "-status",
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            # Default: Sort by priority (pinned > urgent > highlighted > newest)
            queryset = queryset.order_by(
                "-is_pinned", "-is_urgent", "-is_highlighted", "-created_at"
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard statistics
        user_ads = ClassifiedAd.objects.filter(user=self.request.user)

        # Check and expire old upgrades
        for ad in user_ads:
            ad.check_and_expire_upgrades()

        context["dashboard_stats"] = {
            "total_ads": user_ads.count(),
            "active_ads": user_ads.filter(status=ClassifiedAd.AdStatus.ACTIVE).count(),
            "pending_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.PENDING
            ).count(),
            "expired_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.EXPIRED
            ).count(),
            "draft_ads": user_ads.filter(status=ClassifiedAd.AdStatus.DRAFT).count(),
            "total_views": user_ads.aggregate(total=models.Sum("views_count"))["total"]
            or 0,
            # Upgrade statistics
            "highlighted_ads": user_ads.filter(is_highlighted=True).count(),
            "urgent_ads": user_ads.filter(is_urgent=True).count(),
            "pinned_ads": user_ads.filter(is_pinned=True).count(),
        }

        # Ad Balance - الرصيد الإعلاني
        from main.models import UserPackage

        active_packages = UserPackage.objects.filter(
            user=self.request.user, expiry_date__gte=timezone.now(), ads_remaining__gt=0
        )

        total_ads = sum(pkg.total_ads() for pkg in active_packages)
        used_ads = sum(pkg.ads_used for pkg in active_packages)
        available_ads = sum(pkg.ads_remaining for pkg in active_packages)

        context["ad_balance"] = {
            "total": total_ads,
            "used": used_ads,
            "available": available_ads,
            "active_packages": active_packages,
        }

        # Current filters for display
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "status": self.request.GET.get("status", ""),
            "date_from": self.request.GET.get("date_from", ""),
            "date_to": self.request.GET.get("date_to", ""),
            "sort": self.request.GET.get("sort", "-created_at"),
        }

        # Status choices for filter dropdown
        context["status_choices"] = ClassifiedAd.AdStatus.choices

        # Page title
        context["page_title"] = _("لوحة التحكم - إعلاناتي")

        # Active navigation for publisher dashboard
        context["active_nav"] = "dashboard"

        return context


class PublisherNotificationView(PublisherRequiredMixin, ListView):
    """
    Publisher notification view - Shows notifications for publisher users
    Restricted to users with publisher profile
    """

    model = Notification
    template_name = "dashboard/notifications.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        """Get notifications for the current publisher"""
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "notifications"
        context["page_title"] = _("الإشعارات")
        return context

    def get(self, request, *args, **kwargs):
        """Mark all publisher notifications as read when viewed"""
        Notification.objects.filter(user=request.user).update(is_read=True)
        return super().get(request, *args, **kwargs)


@login_required
@publisher_required
def dashboard_ad_toggle_status(request, ad_id):
    """AJAX endpoint to toggle ad status (hide/show)"""
    if request.method == "POST":
        try:
            ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)

            # Toggle between active and draft (using draft as hidden)
            if ad.status == ClassifiedAd.AdStatus.ACTIVE:
                ad.status = ClassifiedAd.AdStatus.DRAFT
                status_text = _("مخفي")  # Hidden
                action = "hidden"  # For JS
            elif ad.status == ClassifiedAd.AdStatus.DRAFT:
                ad.status = ClassifiedAd.AdStatus.ACTIVE
                status_text = _("نشط")  # Active
                action = "shown"  # For JS
            else:
                return JsonResponse(
                    {"success": False, "message": _("لا يمكن تغيير حالة هذا الإعلان")}
                )

            ad.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم تحديث حالة الإعلان بنجاح."),
                    "new_status": ad.status,
                    "status_text": status_text,
                    "action": action,
                }
            )

        except Exception:
            return JsonResponse(
                {"success": False, "message": _("حدث خطأ أثناء تحديث حالة الإعلان.")}
            )

    return JsonResponse({"success": False, "message": _("طلب غير صالح.")})


from .decorators import PublisherRequiredMixin, publisher_required


@login_required
@publisher_required
def dashboard_ad_delete(request, ad_id):
    """AJAX endpoint to delete an ad"""
    if request.method == "POST":
        try:
            ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)
            ad_title = ad.title
            ad.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم حذف الإعلان '{ad_title}' بنجاح.").format(
                        ad_title=ad_title
                    ),
                }
            )

        except Exception:
            return JsonResponse(
                {"success": False, "message": _("حدث خطأ أثناء حذف الإعلان.")}
            )

    return JsonResponse({"success": False, "message": _("طلب غير صالح.")})


@login_required
@publisher_required
def dashboard_get_ad_details(request, ad_id):
    """AJAX endpoint to get ad details for modal display"""
    try:
        ad = get_object_or_404(
            ClassifiedAd.objects.select_related("category", "country").prefetch_related(
                "images"
            ),
            id=ad_id,
            user=request.user,
        )

        return JsonResponse(
            {
                "success": True,
                "ad": {
                    "id": ad.pk,
                    "title": ad.title,
                    "description": ad.description,
                    "price": str(ad.price),
                    "category": ad.category.name if ad.category else "",
                    "city": ad.city,
                    "country": ad.country.name if ad.country else "",
                    "status": next(
                        (
                            choice[1]
                            for choice in ClassifiedAd.AdStatus.choices
                            if choice[0] == ad.status
                        ),
                        ad.status,
                    ),
                    "status_code": ad.status,
                    "views_count": ad.views_count,
                    "created_at": ad.created_at.strftime("%Y-%m-%d %H:%M"),
                    "updated_at": ad.updated_at.strftime("%Y-%m-%d %H:%M"),
                    "is_urgent": ad.is_urgent,
                    "is_highlighted": ad.is_highlighted,
                    "is_negotiable": ad.is_negotiable,
                    "is_delivery_available": ad.is_delivery_available,
                    "expires_at": (
                        ad.expires_at.strftime("%Y-%m-%d %H:%M")
                        if ad.expires_at
                        else ""
                    ),
                    "images": [
                        {"url": img.image.url if img.image else "", "alt": ad.title}
                        for img in ad.images.all()[:5]  # Limit to 5 images
                    ],
                },
            }
        )

    except Exception:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ أثناء تحميل تفاصيل الإعلان.")}
        )


# ============================================================================
# ADMIN DASHBOARD VIEWS
# ============================================================================

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Q, Avg
from datetime import datetime, timedelta
from .decorators import SuperadminRequiredMixin, superadmin_required


class AdminDashboardView(SuperadminRequiredMixin, TemplateView):
    """
    Main superadmin dashboard with comprehensive system overview
    Restricted to superusers only
    """

    template_name = "admin_dashboard/dashboard.html"
    template_name = "admin_dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard Statistics
        context["dashboard_stats"] = self.get_dashboard_stats()

        # Recent Activities
        context["recent_ads"] = self.get_recent_ads()
        context["recent_users"] = self.get_recent_users()

        # System Metrics
        context["system_metrics"] = self.get_system_metrics()

        # Chart Data
        context["chart_data"] = self.get_chart_data()

        # Chat Statistics
        context["chat_stats"] = self.get_chat_stats()

        context["active_nav"] = "dashboard"

        return context

    def get_dashboard_stats(self):
        """Get main dashboard statistics"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        stats = {
            # Ad Statistics
            "total_ads": ClassifiedAd.objects.count(),
            "active_ads": ClassifiedAd.objects.filter(status="active").count(),
            "pending_ads": ClassifiedAd.objects.filter(status="pending").count(),
            "expired_ads": ClassifiedAd.objects.filter(status="expired").count(),
            "hidden_ads": ClassifiedAd.objects.filter(status="draft").count(),
            "cart_ads": ClassifiedAd.objects.filter(
                Q(is_cart_enabled=True) | Q(allow_cart=True)
            ).count(),
            # User Statistics
            "total_users": User.objects.count(),
            "new_users_week": User.objects.filter(date_joined__gte=week_ago).count(),
            "verified_users": 0,  # TODO: Implement when userprofile model exists
            # User.objects.filter(
            #     Q(userprofile__is_person_verified=True)
            #     | Q(userprofile__is_company_verified=True)
            # ).count(),
            # Category Statistics
            "total_categories": Category.objects.filter(parent__isnull=True).count(),
            "total_subcategories": Category.objects.filter(
                parent__isnull=False
            ).count(),
            # Revenue Statistics (if payment system exists)
            "premium_members": User.objects.filter(is_premium=True).count(),
            # Today's Statistics
            "today_ads": ClassifiedAd.objects.filter(created_at__date=today).count(),
            "today_users": User.objects.filter(date_joined__date=today).count(),
        }

        # Calculate growth percentages
        stats["ads_growth"] = self.calculate_growth_percentage(
            ClassifiedAd.objects.filter(created_at__gte=month_ago).count(),
            ClassifiedAd.objects.filter(
                created_at__gte=month_ago - timedelta(days=30), created_at__lt=month_ago
            ).count(),
        )

        return stats

    def get_chat_stats(self):
        """Get chat statistics for admin dashboard"""
        from main.models import ChatRoom, ChatMessage
        from django.db.models import Q

        # Support chat statistics
        total_support_chats = ChatRoom.objects.filter(
            room_type="publisher_admin"
        ).count()
        active_support_chats = ChatRoom.objects.filter(
            room_type="publisher_admin", is_active=True
        ).count()

        # Unread messages from publishers to admin
        unread_support_messages = ChatMessage.objects.filter(
            room__room_type="publisher_admin",
            is_read=False,
            sender__is_staff=False,  # Messages from publishers
        ).count()

        # Regular chat statistics
        total_user_chats = ChatRoom.objects.filter(
            Q(room_type="user_to_user") | Q(room_type="ad_inquiry")
        ).count()

        # Recent chat activity (last 24 hours)
        from django.utils import timezone

        yesterday = timezone.now() - timedelta(hours=24)
        recent_chat_activity = ChatMessage.objects.filter(
            created_at__gte=yesterday
        ).count()

        return {
            "total_support_chats": total_support_chats,
            "active_support_chats": active_support_chats,
            "unread_support_messages": unread_support_messages,
            "total_user_chats": total_user_chats,
            "recent_activity": recent_chat_activity,
        }

    def get_recent_ads(self):
        """Get recent ads for admin review"""
        return (
            ClassifiedAd.objects.select_related("user", "category", "country")
            .prefetch_related("images")
            .order_by("-created_at")[:10]
        )

    def get_recent_users(self):
        """Get recently registered users"""
        # TODO: Add select_related("userprofile") when userprofile model exists
        return User.objects.order_by("-date_joined")[:10]

    def get_system_metrics(self):
        """Get system performance metrics"""
        return {
            "avg_ads_per_user": ClassifiedAd.objects.count()
            / max(User.objects.count(), 1),
            "most_popular_category": Category.objects.annotate(
                ad_count=Count("classified_ads")
            )
            .order_by("-ad_count")
            .first(),
            "countries_count": Country.objects.count(),
            "features_count": AdFeature.objects.count(),
        }

    def get_chart_data(self):
        """Get data for dashboard charts"""
        today = timezone.now().date()

        # Last 7 days ads data
        ads_last_7_days = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            count = ClassifiedAd.objects.filter(created_at__date=date).count()
            ads_last_7_days.append(count)

        # Last 30 days users data (weekly)
        users_last_4_weeks = []
        for i in range(3, -1, -1):
            week_start = today - timedelta(days=(i + 1) * 7)
            week_end = today - timedelta(days=i * 7)
            count = User.objects.filter(
                date_joined__date__range=[week_start, week_end]
            ).count()
            users_last_4_weeks.append(count)

        # Top categories by ad count
        top_categories = Category.objects.annotate(
            ad_count=Count("classified_ads")
        ).order_by("-ad_count")[:5]

        category_names = [cat.name_ar or cat.name for cat in top_categories]
        category_counts = [cat.ad_count for cat in top_categories]

        return {
            "ads_last_7_days": ads_last_7_days,
            "users_last_4_weeks": users_last_4_weeks,
            "category_names": category_names,
            "category_counts": category_counts,
        }

    def calculate_growth_percentage(self, current, previous):
        """Calculate growth percentage"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 2)


class AdminCategoriesView(SuperadminRequiredMixin, TemplateView):
    """
    Admin interface for managing main and subcategories
    Restricted to superusers only
    """

    template_name = "admin_dashboard/categories.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get categories organized by section
        categories_by_section = {}
        for section_code, section_name in Category.SectionType.choices:
            categories_by_section[section_code] = {
                "name": section_name,
                "categories": Category.objects.filter(
                    section_type=section_code, parent__isnull=True
                )
                .prefetch_related("subcategories")
                .annotate(
                    ad_count=Count("classified_ads"),
                    subcategory_count=Count("subcategories"),
                ),
            }

        context["categories_by_section"] = categories_by_section
        context["countries"] = Country.objects.all()
        context["section_choices"] = Category.SectionType.choices
        context["active_nav"] = "categories"

        return context


class AdminAdsManagementView(SuperadminRequiredMixin, ListView):
    """
    Admin interface for comprehensive ads management with tabs
    Restricted to superusers only
    """

    template_name = "admin_dashboard/ads_management.html"
    model = ClassifiedAd
    context_object_name = "ads"
    paginate_by = 15

    def get_queryset(self):
        """Get ads filtered by status tab and search query."""
        status = self.request.GET.get("tab", "active")
        search_query = self.request.GET.get("search", "")

        queryset = ClassifiedAd.objects.select_related(
            "user", "category", "country"
        ).prefetch_related("images")

        if status == "active":
            queryset = queryset.filter(status="active")
        elif status == "pending":
            queryset = queryset.filter(status="pending")
        elif status == "expired":
            queryset = queryset.filter(status="expired")
        elif status == "hidden":
            queryset = queryset.filter(is_hidden=True)
        elif status == "cart":
            queryset = queryset.filter(
                Q(allow_cart=True) & Q(cart_enabled_by_admin=True)
            )

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(user__username__icontains=search_query)
            )

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get ad counts for each tab
        context["tab_counts"] = {
            "active": ClassifiedAd.objects.filter(status="active").count(),
            "pending": ClassifiedAd.objects.filter(status="pending").count(),
            "expired": ClassifiedAd.objects.filter(status="expired").count(),
            "hidden": ClassifiedAd.objects.filter(is_hidden=True).count(),
            "cart": ClassifiedAd.objects.filter(
                Q(allow_cart=True) & Q(cart_enabled_by_admin=True)
            ).count(),
        }
        context["current_tab"] = self.request.GET.get("tab", "active")
        context["search_query"] = self.request.GET.get("search", "")
        context["active_nav"] = "ads"
        return context


class AdminCategoryCustomFieldsView(SuperadminRequiredMixin, View):
    """
    API endpoint to get and save custom fields for a specific category.
    """

    def get(self, request, category_id):
        try:
            from main.models import CategoryCustomField, CustomFieldOption

            category = Category.objects.get(id=category_id)
            category_fields = (
                CategoryCustomField.objects.filter(category=category)
                .select_related("custom_field")
                .prefetch_related("custom_field__field_options")
                .order_by("order")
            )

            fields_data = []
            for cf in category_fields:
                field = cf.custom_field
                # Get options for this field
                options = []
                if field.field_type in ["select", "radio", "checkbox"]:
                    options = list(
                        field.field_options.filter(is_active=True)
                        .values_list("value", flat=True)
                        .order_by("order")
                    )

                fields_data.append(
                    {
                        "id": field.id,
                        "name": field.name,
                        "label_ar": field.label_ar,
                        "label_en": field.label_en,
                        "field_type": field.field_type,
                        "is_required": cf.is_required,  # From CategoryCustomField
                        "options": (
                            ",".join(options) if options else ""
                        ),  # Join for compatibility
                        "order": cf.order,  # From CategoryCustomField
                        "show_on_card": cf.show_on_card,  # Show on ad card
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "category_name": category.name,
                    "fields": fields_data,
                }
            )
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Category not found"}, status=404
            )

    def post(self, request, category_id):
        """Save custom fields for a category"""
        try:
            import json
            from main.models import CategoryCustomField, CustomFieldOption

            category = Category.objects.get(id=category_id)
            data = json.loads(request.body)
            fields_data = data.get("fields", [])

            # Delete existing CategoryCustomField relationships for this category
            CategoryCustomField.objects.filter(category=category).delete()

            # Create or update fields and their relationships
            for index, field_data in enumerate(fields_data):
                field_name = field_data.get("name", "")
                if not field_name:
                    continue

                # Get or create the CustomField
                field, created = CustomField.objects.get_or_create(
                    name=field_name,
                    defaults={
                        "label_ar": field_data.get("name", ""),
                        "label_en": field_data.get("name", ""),
                        "field_type": field_data.get("type", "text"),
                    },
                )

                # If field already exists, update it
                if not created:
                    field.label_ar = field_data.get("name", field.label_ar)
                    field.field_type = field_data.get("type", field.field_type)
                    field.save()

                # Create CategoryCustomField relationship
                CategoryCustomField.objects.create(
                    category=category,
                    custom_field=field,
                    is_required=field_data.get("required", False),
                    order=index,
                    is_active=True,
                    show_on_card=field_data.get("show_on_card", False),
                )

                # Handle options for select/radio/checkbox fields
                options_str = field_data.get("options", "")
                if options_str and field.field_type in ["select", "radio", "checkbox"]:
                    # Delete existing options for this field
                    CustomFieldOption.objects.filter(custom_field=field).delete()

                    # Create new options
                    options_list = [
                        opt.strip() for opt in options_str.split(",") if opt.strip()
                    ]
                    for opt_index, option_value in enumerate(options_list):
                        CustomFieldOption.objects.create(
                            custom_field=field,
                            label_ar=option_value,
                            label_en=option_value,
                            value=option_value,
                            order=opt_index,
                            is_active=True,
                        )

            return JsonResponse(
                {"success": True, "message": _("تم حفظ الحقول المخصصة بنجاح")}
            )

        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Category not found"}, status=404
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": f"Error: {str(e)}"}, status=400
            )


class AdminCustomFieldsView(SuperadminRequiredMixin, ListView):
    """
    Admin interface for managing custom fields.
    Restricted to superusers only.
    """

    template_name = "admin_dashboard/custom_fields.html"
    model = CustomField
    context_object_name = "fields"

    def get_queryset(self):
        queryset = CustomField.objects.prefetch_related(
            "categories", "field_options"
        ).order_by("name")
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(label_ar__icontains=search_query)
                | Q(categories__name__icontains=search_query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "custom_fields"
        context["search_query"] = self.request.GET.get("search", "")

        # Add field type choices for the modal
        context["field_type_choices"] = CustomField.FieldType.choices

        # Get all categories hierarchically (main -> sub -> sub-sub)
        context["all_categories"] = (
            Category.objects.filter(parent__isnull=True)
            .prefetch_related("subcategories__subcategories")
            .order_by("order", "name_ar")
        )

        # Get all fields with their category relationships
        from main.models import CategoryCustomField

        context["category_fields"] = (
            CategoryCustomField.objects.select_related("category", "custom_field")
            .prefetch_related("custom_field__field_options")
            .order_by("category__name", "order")
        )
        return context


class AdminCustomFieldGetView(SuperadminRequiredMixin, View):
    """AJAX view to get data for a single custom field."""

    def get(self, request, field_id):
        try:
            from main.models import CustomFieldOption

            field = get_object_or_404(CustomField, pk=field_id)

            # Get options for select/radio/checkbox fields
            options_list = []
            if field.field_type in ["select", "radio", "checkbox"]:
                options_list = list(
                    field.field_options.filter(is_active=True)
                    .values_list("value", flat=True)
                    .order_by("order")
                )

            # Get categories this field is associated with
            category_ids = list(field.categories.values_list("id", flat=True))

            data = {
                "id": field.id,
                "name": field.name,
                "label_ar": field.label_ar,
                "label_en": field.label_en,
                "field_type": field.field_type,
                "is_required": field.is_required,
                "help_text": field.help_text,
                "placeholder": field.placeholder,
                "default_value": field.default_value,
                "options": ",".join(options_list),  # Join for backward compatibility
                "is_active": field.is_active,
                "category_ids": category_ids,  # Multiple categories now
            }
            return JsonResponse({"success": True, "field": data})
        except Http404:
            return JsonResponse(
                {"success": False, "message": _("Field not found.")}, status=404
            )


class AdminCustomFieldSaveView(SuperadminRequiredMixin, View):
    """AJAX view to save/update a single custom field."""

    def post(self, request):
        try:
            from main.models import CategoryCustomField, CustomFieldOption

            field_id = request.POST.get("field_id")
            if field_id:
                field = get_object_or_404(CustomField, pk=field_id)
                message = _("تم تحديث الحقل بنجاح.")
            else:
                field = CustomField()
                message = _("تم إنشاء الحقل بنجاح.")

            # Update field data
            field.name = request.POST.get("name", field.name)
            field.label_ar = request.POST.get("label_ar", field.label_ar)
            field.label_en = request.POST.get("label_en", field.label_en)
            field.field_type = request.POST.get("field_type", field.field_type)
            field.is_required = request.POST.get("is_required") == "on"
            field.is_active = request.POST.get("is_active") == "on"
            field.help_text = request.POST.get("help_text", field.help_text or "")
            field.placeholder = request.POST.get("placeholder", field.placeholder or "")
            field.default_value = request.POST.get(
                "default_value", field.default_value or ""
            )
            field.save()

            # Handle category association
            category_id = request.POST.get("category")
            if category_id:
                category = get_object_or_404(Category, pk=category_id)
                # Create or update CategoryCustomField relationship
                CategoryCustomField.objects.update_or_create(
                    category=category,
                    custom_field=field,
                    defaults={
                        "is_required": field.is_required,
                        "order": int(request.POST.get("order", 0)),
                        "is_active": True,
                    },
                )

            # Handle options for select/radio/checkbox fields
            options_str = request.POST.get("options", "")
            if options_str and field.field_type in ["select", "radio", "checkbox"]:
                # Delete existing options
                CustomFieldOption.objects.filter(custom_field=field).delete()

                # Create new options
                options_list = [
                    opt.strip() for opt in options_str.split(",") if opt.strip()
                ]
                for index, option_value in enumerate(options_list):
                    CustomFieldOption.objects.create(
                        custom_field=field,
                        label_ar=option_value,
                        label_en=option_value,
                        value=option_value,
                        order=index,
                        is_active=True,
                    )

            return JsonResponse({"success": True, "message": message})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


class AdminCustomFieldDeleteView(SuperadminRequiredMixin, View):
    """AJAX view to delete a custom field."""

    def post(self, request, field_id):
        try:
            field = get_object_or_404(CustomField, pk=field_id)
            field_name = field.label_ar or field.name
            field.delete()
            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم حذف الحقل '%(name)s' بنجاح.")
                    % {"name": field_name},
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("حدث خطأ أثناء حذف الحقل: %(error)s")
                    % {"error": str(e)},
                },
                status=500,
            )


class AdminUsersManagementView(SuperadminRequiredMixin, ListView):
    """
    Admin interface for comprehensive user management.
    Restricted to superusers only.
    """

    template_name = "admin_dashboard/users_management.html"
    model = User
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        """Get users with filtering and searching."""
        queryset = User.objects.order_by("-date_joined")
        search_query = self.request.GET.get("search", "")
        role_filter = self.request.GET.get("role", "")

        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )

        if role_filter:
            queryset = queryset.filter(profile_type=role_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["role_filter"] = self.request.GET.get("role", "")
        context["profile_type_choices"] = User.ProfileType.choices
        context["total_users"] = User.objects.count()
        context["verified_users"] = User.objects.filter(
            verification_status=User.VerificationStatus.VERIFIED
        ).count()
        context["publisher_users"] = User.objects.filter(
            profile_type__in=["publisher", "merchant", "service", "educational"]
        ).count()
        context["active_nav"] = "users"

        return context


class AdminSettingsView(SuperadminRequiredMixin, View):
    """
    Admin system settings and configurations with form handling
    Restricted to superusers only
    """

    def get(self, request):
        from constance import config

        # Get current system settings from Constance
        context = {
            "system_settings": {
                "publishing_mode": getattr(config, "PUBLISHING_MODE", "direct"),
                "allow_guest_viewing": getattr(config, "ALLOW_GUEST_VIEWING", True),
                "allow_guest_contact": getattr(config, "ALLOW_GUEST_CONTACT", False),
                "delivery_service_enabled": getattr(
                    config, "DELIVERY_SERVICE_ENABLED", True
                ),
                "cart_system_enabled": getattr(config, "CART_SYSTEM_ENABLED", True),
                "auto_approval_verified_users": getattr(
                    config, "VERIFIED_AUTO_PUBLISH", True
                ),
                "verified_auto_publish": getattr(config, "VERIFIED_AUTO_PUBLISH", True),
                "members_only_contact": getattr(config, "MEMBERS_ONLY_CONTACT", True),
                "members_only_messaging": getattr(
                    config, "MEMBERS_ONLY_MESSAGING", True
                ),
                "delivery_requires_approval": getattr(
                    config, "DELIVERY_REQUIRES_APPROVAL", True
                ),
                "cart_by_main_category": getattr(
                    config, "CART_BY_MAIN_CATEGORY", False
                ),
                "cart_by_subcategory": getattr(config, "CART_BY_SUBCATEGORY", True),
                "cart_per_ad": getattr(config, "CART_PER_AD", True),
                "default_reservation_percentage": getattr(
                    config, "DEFAULT_RESERVATION_PERCENTAGE", 20
                ),
                "min_reservation_amount": getattr(config, "MIN_RESERVATION_AMOUNT", 50),
                "max_reservation_amount": getattr(
                    config, "MAX_RESERVATION_AMOUNT", 5000
                ),
                "delivery_fee_percentage": getattr(
                    config, "DELIVERY_FEE_PERCENTAGE", 5
                ),
                "delivery_fee_min": getattr(config, "DELIVERY_FEE_MIN", 10),
                "delivery_fee_max": getattr(config, "DELIVERY_FEE_MAX", 500),
                "notify_admin_new_ads": getattr(config, "NOTIFY_ADMIN_NEW_ADS", True),
                "notify_admin_pending_review": getattr(
                    config, "NOTIFY_ADMIN_PENDING_REVIEW", True
                ),
                "notify_admin_new_users": getattr(
                    config, "NOTIFY_ADMIN_NEW_USERS", True
                ),
                "notify_admin_payments": getattr(config, "NOTIFY_ADMIN_PAYMENTS", True),
                "admin_notification_email": getattr(
                    config, "ADMIN_NOTIFICATION_EMAIL", request.user.email
                ),
                "site_name_in_emails": getattr(
                    config, "SITE_NAME_IN_EMAILS", "إدريسي مارت"
                ),
                "ads_notification_frequency": getattr(
                    config, "ADS_NOTIFICATION_FREQUENCY", "hourly"
                ),
                "stats_report_frequency": getattr(
                    config, "STATS_REPORT_FREQUENCY", "daily"
                ),
            },
            "delivery_terms": {
                "arabic": "شروط التوصيل والتحصيل باللغة العربية",
                "english": "Delivery and collection terms in English",
            },
            "active_nav": "settings",
        }

        return render(request, "admin_dashboard/settings.html", context)

    def post(self, request):
        # Handle settings form submission (placeholder)
        # TODO: Implement actual settings storage
        return JsonResponse({"success": True, "message": "تم حفظ الإعدادات بنجاح"})


class AdminPaymentsView(SuperadminRequiredMixin, TemplateView):
    """
    Admin interface for payment operations and premium members
    Restricted to superusers only
    """

    template_name = "admin_dashboard/payments.html"

    def get_context_data(self, **kwargs):
        from django.db.models import Sum, Count, Q
        from django.utils import timezone
        from datetime import datetime, timedelta

        context = super().get_context_data(**kwargs)

        # Payment statistics
        completed_payments = Payment.objects.filter(
            status=Payment.PaymentStatus.COMPLETED
        )
        total_payments = Payment.objects.count()
        total_revenue = completed_payments.aggregate(total=Sum("amount"))["total"] or 0
        pending_payments = Payment.objects.filter(
            status=Payment.PaymentStatus.PENDING
        ).count()

        # Debug: Print payment counts
        print(f"DEBUG - Total payments: {total_payments}")
        print(f"DEBUG - Completed payments: {completed_payments.count()}")
        print(f"DEBUG - Total revenue: {total_revenue}")
        print(f"DEBUG - Pending payments: {pending_payments}")

        # Calculate monthly revenue (current month)
        current_month_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        monthly_revenue = (
            completed_payments.filter(completed_at__gte=current_month_start).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        # Premium members statistics
        total_premium_members = User.objects.filter(is_premium=True).count()
        today = timezone.now().date()
        active_premium_members = User.objects.filter(
            is_premium=True, subscription_end__gte=today
        ).count()

        context["payment_stats"] = {
            "total_transactions": total_payments,
            "total_revenue": total_revenue,
            "premium_members": total_premium_members,
            "pending_payments": pending_payments,
            "active_premium_members": active_premium_members,
        }

        # Recent transactions
        context["recent_transactions"] = Payment.objects.select_related(
            "user"
        ).order_by("-created_at")[:10]

        # Monthly revenue chart data (last 6 months)
        monthly_data = []
        for i in range(5, -1, -1):  # Reversed to show oldest to newest
            month_date = timezone.now() - timedelta(days=30 * i)
            month_start = month_date.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            # Calculate next month start
            if month_start.month == 12:
                next_month_start = month_start.replace(
                    year=month_start.year + 1, month=1
                )
            else:
                next_month_start = month_start.replace(month=month_start.month + 1)

            # Get revenue for this month
            month_revenue = (
                completed_payments.filter(
                    completed_at__gte=month_start, completed_at__lt=next_month_start
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )

            monthly_data.append(
                {
                    "month": month_start.strftime("%Y-%m"),
                    "revenue": float(month_revenue),
                }
            )

        import json

        context["monthly_data"] = json.dumps(monthly_data)

        # Premium membership packages - Get actual package counts
        gold_subscribers = (
            completed_payments.filter(description__icontains="الباقة الذهبية")
            .values("user")
            .distinct()
            .count()
        )

        platinum_subscribers = (
            completed_payments.filter(description__icontains="الباقة البلاتينية")
            .values("user")
            .distinct()
            .count()
        )

        context["membership_packages"] = [
            {
                "id": 1,
                "name": "الباقة الذهبية",
                "price": 99,
                "duration": 30,
                "features": ["إعلانات مميزة", "دعم فوري", "إحصائيات متقدمة"],
                "subscribers": gold_subscribers,
                "is_active": True,
            },
            {
                "id": 2,
                "name": "الباقة البلاتينية",
                "price": 199,
                "duration": 30,
                "features": [
                    "جميع ميزات الذهبية",
                    "إعلانات غير محدودة",
                    "مدير حساب مخصص",
                ],
                "subscribers": platinum_subscribers,
                "is_active": True,
            },
        ]

        # Premium members - Get actual premium members with active subscriptions
        context["premium_members"] = User.objects.filter(is_premium=True).order_by(
            "-date_joined"
        )[:20]

        # Don't load packages/subscriptions data directly - will be loaded via AJAX
        context["user_packages"] = None  # Load via AJAX
        context["user_subscriptions"] = None  # Load via AJAX

        # Get currency from selected country
        selected_country = self.request.session.get("selected_country", "EG")
        try:
            from content.models import Country
            country = Country.objects.get(code=selected_country, is_active=True)
            context["currency"] = country.currency or "SAR"
        except:
            context["currency"] = "SAR"

        context["active_nav"] = "payments"

        return context


@login_required
def admin_payment_transaction_detail(request, transaction_id):
    """Get payment transaction details for admin view"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        transaction = get_object_or_404(
            Payment.objects.select_related("user"), id=transaction_id
        )

        return JsonResponse(
            {
                "success": True,
                "transaction": {
                    "id": transaction.id,
                    "user_name": transaction.user.get_full_name()
                    or transaction.user.username,
                    "user_email": transaction.user.email,
                    "package_name": transaction.description or "غير محدد",
                    "amount": str(transaction.amount),
                    "currency": transaction.currency or "SAR",
                    "payment_method": (
                        transaction.get_provider_display()
                        if transaction.provider
                        else "غير محدد"
                    ),
                    "status": transaction.status,
                    "status_display": transaction.get_status_display(),
                    "transaction_id": transaction.provider_transaction_id
                    or "غير متوفر",
                    "created_at": transaction.created_at.strftime("%Y-%m-%d %H:%M"),
                    "completed_at": (
                        transaction.completed_at.strftime("%Y-%m-%d %H:%M")
                        if transaction.completed_at
                        else None
                    ),
                    "notes": (
                        transaction.metadata.get("notes", "")
                        if transaction.metadata
                        else ""
                    ),
                },
            }
        )
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error loading transaction {transaction_id}: {str(e)}")
        return JsonResponse(
            {"success": False, "error": "حدث خطأ في تحميل تفاصيل المعاملة"},
            status=500,
        )
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error loading transaction {transaction_id}: {str(e)}")
        return JsonResponse(
            {"success": False, "error": "حدث خطأ في تحميل تفاصيل المعاملة"}, status=500
        )


class AdminNotificationView(SuperadminRequiredMixin, ListView):
    """
    Admin notification view - Shows all notifications for admin users
    Restricted to superusers only
    """

    model = Notification
    template_name = "admin_dashboard/notifications.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        """Get all notifications (admin sees all)"""
        return Notification.objects.all().select_related("user").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "notifications"
        return context

    # Removed auto-mark-as-read functionality
    # Admin viewing all notifications shouldn't mark them as read
    # Individual notifications can be marked as read by their owners


@login_required
def admin_get_user_packages(request):
    """Get user packages data via AJAX"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        status_filter = request.GET.get('status', 'all')
        page = int(request.GET.get('page', 1))
        per_page = 50

        # Base queryset
        packages = UserPackage.objects.select_related("user", "package").order_by("-purchase_date")

        # Apply status filter
        if status_filter == 'active':
            packages = packages.filter(expiry_date__gte=timezone.now(), ads_remaining__gt=0)
        elif status_filter == 'expired':
            packages = packages.filter(Q(expiry_date__lt=timezone.now()) | Q(ads_remaining=0))

        # Pagination
        paginator = Paginator(packages, per_page)
        packages_page = paginator.get_page(page)

        # Serialize data
        packages_data = []
        for pkg in packages_page:
            is_active = pkg.expiry_date >= timezone.now() and pkg.ads_remaining > 0
            packages_data.append({
                'id': pkg.id,
                'user_username': pkg.user.username if pkg.user else 'N/A',
                'user_email': pkg.user.email if pkg.user else 'N/A',
                'package_name': pkg.package.name if pkg.package else 'إعلان مجاني',
                'package_type': pkg.package.name if pkg.package else 'free',
                'purchase_date': pkg.purchase_date.strftime('%d/%m/%Y %H:%M') if pkg.purchase_date else 'N/A',
                'expiry_date': pkg.expiry_date.strftime('%d/%m/%Y %H:%M') if pkg.expiry_date else 'N/A',
                'ads_remaining': pkg.ads_remaining,
                'status': 'active' if is_active else 'expired',
                'status_label': 'نشط' if is_active else 'منتهي',
            })

        return JsonResponse({
            'success': True,
            'packages': packages_data,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
            'has_next': packages_page.has_next(),
            'has_previous': packages_page.has_previous(),
        })

    except Exception as e:
        import traceback
        return JsonResponse({"error": str(e), "traceback": traceback.format_exc()}, status=500)


@login_required
def admin_get_user_subscriptions(request):
    """Get user subscriptions data via AJAX"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        from main.models import UserSubscription

        status_filter = request.GET.get('status', 'all')
        page = int(request.GET.get('page', 1))
        per_page = 50

        # Base queryset
        subscriptions = UserSubscription.objects.select_related("user").order_by("-created_at")

        # Apply status filter
        if status_filter == 'active':
            subscriptions = subscriptions.filter(end_date__gte=timezone.now(), is_active=True)
        elif status_filter == 'expired':
            subscriptions = subscriptions.filter(Q(end_date__lt=timezone.now()) | Q(is_active=False))

        # Pagination
        paginator = Paginator(subscriptions, per_page)
        subscriptions_page = paginator.get_page(page)

        # Serialize data
        subscriptions_data = []
        for sub in subscriptions_page:
            is_active = sub.end_date >= timezone.now() and sub.is_active
            subscriptions_data.append({
                'id': sub.id,
                'user_username': sub.user.username if sub.user else 'N/A',
                'user_email': sub.user.email if sub.user else 'N/A',
                'package_type': sub.subscription_type,
                'price': float(sub.price) if sub.price else 0,
                'start_date': sub.start_date.strftime('%d/%m/%Y %H:%M') if sub.start_date else '',
                'end_date': sub.end_date.strftime('%d/%m/%Y %H:%M') if sub.end_date else '',
                'auto_renew': sub.auto_renew if hasattr(sub, 'auto_renew') else False,
                'status': 'active' if is_active else 'expired',
                'status_label': 'نشط' if is_active else 'منتهي',
            })

        return JsonResponse({
            'success': True,
            'subscriptions': subscriptions_data,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
            'has_next': subscriptions_page.has_next(),
            'has_previous': subscriptions_page.has_previous(),
        })

    except Exception as e:
        import traceback
        return JsonResponse({"error": str(e), "traceback": traceback.format_exc()}, status=500)


class AdminTranslationsView(SuperadminRequiredMixin, TemplateView):
    """
    Admin interface for translation management using Django Rosetta
    Restricted to superusers only
    """

    template_name = "admin_dashboard/translations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "translations"

        # You can add additional context here if needed
        # For example, translation statistics, available languages, etc.

        return context


# AJAX Views for Admin Dashboard


@superadmin_required
@require_POST
def admin_ad_status_change(request, ad_id):
    """Change ad status from admin panel"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        new_status = request.POST.get("status")

        if new_status in [choice[0] for choice in ClassifiedAd.AdStatus.choices]:
            old_status = ad.status
            ad.status = new_status
            ad.save()

            # Log the action
            # Add logging here if needed

            return JsonResponse(
                {
                    "success": True,
                    "message": f"تم تغيير حالة الإعلان من {old_status} إلى {new_status}",
                    "new_status": new_status,
                    "new_status_display": ad.get_status_display(),
                }
            )
        else:
            return JsonResponse({"success": False, "message": "حالة غير صالحة"})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"حدث خطأ: {str(e)}"})


@superadmin_required
def admin_category_get(request, category_id):
    """
    Get category data for editing via AJAX.
    """
    try:
        category = get_object_or_404(Category, pk=category_id)

        return JsonResponse(
            {
                "success": True,
                "id": category.id,
                "name": category.name,
                "name_en": category.name,  # English name
                "name_ar": category.name_ar,
                "slug": category.slug,
                "section_type": category.section_type,
                "description": category.description or "",
                "description_ar": category.description or "",  # Arabic description
                "description_en": category.description
                or "",  # English description (same for now)
                "icon": category.icon or "",
                "color": getattr(category, "color", "") or "",
                "order": getattr(category, "order", 0),
                "is_active": getattr(category, "is_active", True),
                "allow_cart": category.allow_cart,
                "parent_id": category.parent.id if category.parent else None,
            }
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"حدث خطأ: {str(e)}"}, status=500
        )


@superadmin_required
@require_POST
def admin_category_save(request):
    """
    Create or update a category via AJAX.
    """
    try:
        from django.utils.text import slugify

        category_id = request.POST.get("category_id")

        # Get or create category
        if category_id:
            category = get_object_or_404(Category, pk=category_id)
        else:
            category = Category()

        # Update category fields
        name_en = request.POST.get("name_en", "")
        name_ar = request.POST.get("name_ar", "")

        category.name = (
            name_en or name_ar
        )  # Use English name as primary, fallback to Arabic
        category.name_ar = name_ar

        # Auto-generate slug if not provided or on new category
        provided_slug = request.POST.get("slug", "")
        if provided_slug:
            category.slug = provided_slug
        elif not category.id:  # New category
            # Generate unique slug
            base_slug = (
                slugify(name_en) if name_en else slugify(name_ar, allow_unicode=True)
            )
            slug = base_slug
            counter = 1
            while (
                Category.objects.filter(slug=slug)
                .exclude(pk=category.id if category.id else None)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1
            category.slug = slug

        category.section_type = request.POST.get("section_type", "classified")

        # Handle description - prefer description_ar if provided
        description_ar = request.POST.get("description_ar", "")
        description_en = request.POST.get("description_en", "")
        category.description = (
            description_ar or description_en or request.POST.get("description", "")
        )

        category.icon = request.POST.get("icon", "")

        # Handle optional fields with getattr/setattr for compatibility
        if hasattr(category, "color"):
            category.color = request.POST.get("color", "")
        if hasattr(category, "order"):
            category.order = int(request.POST.get("order", 0))
        if hasattr(category, "is_active"):
            category.is_active = (
                request.POST.get("is_active") == "on"
                or request.POST.get("is_active") == "true"
            )

        category.allow_cart = (
            request.POST.get("allow_cart") == "on"
            or request.POST.get("allow_cart") == "true"
        )

        # Handle parent category
        parent_id = request.POST.get("parent")
        if parent_id:
            category.parent = Category.objects.get(pk=parent_id)
        else:
            category.parent = None

        # Handle country
        country_code = request.POST.get("country")
        if country_code:
            from content.models import Country

            category.country = Country.objects.get(code=country_code)
        else:
            category.country = None

        category.save()

        return JsonResponse(
            {
                "success": True,
                "message": _("تم حفظ القسم بنجاح"),
                "category_id": category.id,
            }
        )

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error saving category: {error_trace}")  # For debugging
        return JsonResponse(
            {"success": False, "message": f"حدث خطأ: {str(e)}"}, status=500
        )


@superadmin_required
@require_POST
def admin_category_delete(request, category_id):
    """
    Delete a category from the admin panel.
    Ensures the category has no children or associated ads before deletion.
    """
    try:
        category = get_object_or_404(Category, pk=category_id)

        # Prevent deletion if category has children or associated ads
        if category.get_children().exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": _(
                        "Cannot delete category because it has subcategories."
                    ),
                },
                status=400,
            )
        if category.classified_ads.exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": _("Cannot delete category because it contains ads."),
                },
                status=400,
            )

        category_name = category.name
        category.delete()

        return JsonResponse(
            {
                "success": True,
                "message": _("Category '{}' was deleted successfully.").format(
                    category_name
                ),
            }
        )
    except Exception as e:
        # It's good practice to log the error 'e' here
        return JsonResponse(
            {
                "success": False,
                "message": _("An error occurred while deleting the category."),
            },
            status=500,
        )


@superadmin_required
@require_POST
def admin_category_reorder(request):
    """
    AJAX endpoint to handle reordering of categories via drag-and-drop.
    """
    try:
        data = json.loads(request.body)
        category_ids = data.get("ordered_ids", [])

        with transaction.atomic():
            for index, category_id in enumerate(category_ids):
                Category.objects.filter(pk=category_id).update(order=index)

        return JsonResponse(
            {
                "success": True,
                "message": _("Category order has been updated successfully."),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@superadmin_required
def admin_user_detail(request, user_id):
    """
    Admin view to see detailed information about a specific user.
    """
    user_obj = get_object_or_404(
        User.objects.prefetch_related("classified_ads", "classified_ads__images"),
        pk=user_id,
    )

    # Get user's ad statistics
    user_ads = user_obj.classified_ads.all()
    user_ad_stats = {
        "total": user_ads.count(),
        "active": user_ads.filter(status=ClassifiedAd.AdStatus.ACTIVE).count(),
        "pending": user_ads.filter(status=ClassifiedAd.AdStatus.PENDING).count(),
        "expired": user_ads.filter(status=ClassifiedAd.AdStatus.EXPIRED).count(),
        "rejected": user_ads.filter(status=ClassifiedAd.AdStatus.REJECTED).count(),
        "draft": user_ads.filter(status=ClassifiedAd.AdStatus.DRAFT).count(),
    }

    # Get recent ads
    recent_ads = (
        user_ads.select_related("category", "country")
        .prefetch_related("images")
        .order_by("-created_at")[:10]
    )

    context = {
        "user_obj": user_obj,
        "user_ad_stats": user_ad_stats,
        "recent_ads": recent_ads,
        "page_title": _("تفاصيل المستخدم") + f" - {user_obj.username}",
        "active_nav": "users",
    }
    return render(request, "admin_dashboard/user_detail.html", context)


@superadmin_required
@require_POST
def admin_user_update(request, user_id):
    """
    Update user information from admin panel.
    """
    try:
        user_to_update = get_object_or_404(User, pk=user_id)

        # Get form data
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        whatsapp = request.POST.get("whatsapp", "").strip()
        username = request.POST.get("username", "").strip()
        new_password = request.POST.get("new_password", "").strip()

        # Additional fields
        country = request.POST.get("country", "").strip()
        city = request.POST.get("city", "").strip()
        language = request.POST.get("language", "").strip()
        is_company = request.POST.get("is_company") == "true"
        is_verified = request.POST.get("is_verified") == "verified"
        is_active = request.POST.get("is_active") == "true"
        user_role = request.POST.get("user_role", "member").strip()

        # Validate email uniqueness
        if email and email != user_to_update.email:
            if User.objects.filter(email=email).exclude(pk=user_id).exists():
                return JsonResponse(
                    {"success": False, "message": _("البريد الإلكتروني مستخدم بالفعل.")}
                )

        # Validate username uniqueness
        if username and username != user_to_update.username:
            if User.objects.filter(username=username).exclude(pk=user_id).exists():
                return JsonResponse(
                    {"success": False, "message": _("اسم المستخدم مستخدم بالفعل.")}
                )

        # Update user basic info
        user_to_update.first_name = first_name
        user_to_update.last_name = last_name
        user_to_update.email = email
        user_to_update.phone = phone
        user_to_update.whatsapp = whatsapp

        if username:
            user_to_update.username = username

        # Update additional fields
        if country:
            user_to_update.country = country
        if city:
            user_to_update.city = city
        if language:
            user_to_update.language = language

        user_to_update.is_company = is_company
        user_to_update.is_active = is_active

        # Update verification status
        if is_verified:
            user_to_update.verification_status = User.VerificationStatus.VERIFIED
            if not user_to_update.verified_at:
                user_to_update.verified_at = timezone.now()
        else:
            user_to_update.verification_status = User.VerificationStatus.UNVERIFIED
            user_to_update.verified_at = None

        # Update user role (only superadmin can change this)
        if request.user.is_superuser:
            if user_role == "staff":
                user_to_update.is_staff = True
                user_to_update.is_superuser = False
            elif user_role == "superuser":
                user_to_update.is_staff = True
                user_to_update.is_superuser = True
            else:  # member
                user_to_update.is_staff = False
                user_to_update.is_superuser = False

        # Update password if provided
        if new_password:
            if len(new_password) < 8:
                return JsonResponse(
                    {
                        "success": False,
                        "message": _("كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل."),
                    }
                )
            user_to_update.set_password(new_password)

        user_to_update.save()

        return JsonResponse(
            {"success": True, "message": _("تم تحديث معلومات المستخدم بنجاح.")}
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("حدث خطأ أثناء تحديث المعلومات: {}").format(str(e)),
            }
        )


@superadmin_required
@require_POST
def admin_user_action(request, user_id):
    """
    Handle admin actions on a user like suspend, unsuspend, or verify.
    """
    try:
        user_to_act_on = get_object_or_404(User, pk=user_id)
        data = json.loads(request.body)
        action = data.get("action")

        if action == "suspend":
            user_to_act_on.is_suspended = True
            user_to_act_on.save(update_fields=["is_suspended"])
            message = _("تم تعليق المستخدم '{}'.").format(user_to_act_on.username)
        elif action == "unsuspend":
            user_to_act_on.is_suspended = False
            user_to_act_on.save(update_fields=["is_suspended"])
            message = _("تم إلغاء تعليق المستخدم '{}'.").format(user_to_act_on.username)
        elif action == "verify":
            user_to_act_on.verification_status = User.VerificationStatus.VERIFIED
            user_to_act_on.verified_at = timezone.now()
            user_to_act_on.save(update_fields=["verification_status", "verified_at"])
            message = _("تم توثيق المستخدم '{}'.").format(user_to_act_on.username)
        else:
            return JsonResponse(
                {"success": False, "message": _("إجراء غير صالح.")}, status=400
            )

        return JsonResponse({"success": True, "message": message})

    except User.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("المستخدم غير موجود.")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": str(e)}, status=500
        )  # Developer-facing


@superadmin_required
@require_POST
def admin_reset_user_password(request, user_id):
    """
    Reset user password from admin panel with optional email notification.
    """
    try:
        user_to_update = get_object_or_404(User, pk=user_id)
        data = json.loads(request.body)
        new_password = data.get("new_password", "").strip()
        send_email = data.get("send_email", False)

        if not new_password:
            return JsonResponse(
                {"success": False, "message": _("كلمة المرور مطلوبة.")}, status=400
            )

        if len(new_password) < 8:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل."),
                },
                status=400,
            )

        # Update password
        user_to_update.set_password(new_password)
        user_to_update.save()

        # Send email if requested
        if send_email and user_to_update.email:
            try:
                from django.core.mail import send_mail
                from django.conf import settings

                subject = _("تم إعادة تعيين كلمة المرور الخاصة بك")
                message = _(
                    """
مرحباً {username},

تم إعادة تعيين كلمة المرور الخاصة بك من قبل الإدارة.

كلمة المرور الجديدة: {password}

يرجى تسجيل الدخول وتغيير كلمة المرور الخاصة بك من الإعدادات.

مع تحياتنا،
فريق الإدارة
                """
                ).format(username=user_to_update.username, password=new_password)

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user_to_update.email],
                    fail_silently=False,
                )
            except Exception as email_error:
                # Password changed but email failed
                return JsonResponse(
                    {
                        "success": True,
                        "message": _(
                            "تم إعادة تعيين كلمة المرور ولكن فشل إرسال البريد الإلكتروني."
                        ),
                    }
                )

        return JsonResponse(
            {
                "success": True,
                "message": _("تم إعادة تعيين كلمة المرور بنجاح.")
                + (_(" وتم إرسال بريد إلكتروني للمستخدم.") if send_email else ""),
            }
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("المستخدم غير موجود.")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@superadmin_required
@require_POST
def admin_send_user_notification(request, user_id):
    """
    Send notification to user via email and/or SMS.
    """
    try:
        user = get_object_or_404(User, pk=user_id)
        data = json.loads(request.body)

        title = data.get("title", "").strip()
        message = data.get("message", "").strip()
        send_email_flag = data.get("send_email", False)
        send_sms = data.get("send_sms", False)

        if not title or not message:
            return JsonResponse(
                {"success": False, "message": _("العنوان والرسالة مطلوبان.")},
                status=400,
            )

        if not send_email_flag and not send_sms:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("يجب اختيار طريقة إرسال واحدة على الأقل."),
                },
                status=400,
            )

        success_methods = []
        failed_methods = []

        # Send Email
        if send_email_flag and user.email:
            try:
                from django.core.mail import send_mail
                from django.conf import settings

                email_message = f"""
مرحباً {user.get_full_name() or user.username},

{message}

مع تحياتنا،
فريق الإدارة
                """

                send_mail(
                    title,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                success_methods.append(_("البريد الإلكتروني"))
            except Exception as e:
                failed_methods.append(_("البريد الإلكتروني"))

        # Send SMS (placeholder - integrate with your SMS provider)
        if send_sms and user.phone:
            try:
                # TODO: Integrate with SMS provider (Twilio, etc.)
                # For now, we'll just mark it as sent
                # sms_provider.send(user.phone, f"{title}: {message}")
                success_methods.append(_("الرسائل النصية"))
            except Exception as e:
                failed_methods.append(_("الرسائل النصية"))

        if success_methods:
            methods_str = _(" و ").join(success_methods)
            response_message = _("تم إرسال الإشعار عبر {}").format(methods_str)

            if failed_methods:
                failed_str = _(" و ").join(failed_methods)
                response_message += _(". فشل الإرسال عبر {}").format(failed_str)

            return JsonResponse({"success": True, "message": response_message})
        else:
            return JsonResponse(
                {"success": False, "message": _("فشل إرسال الإشعار عبر جميع الطرق.")}
            )

    except User.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("المستخدم غير موجود.")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@superadmin_required
@require_POST
def admin_delete_user(request, user_id):
    """
    Delete user with option to also delete all their ads.
    """
    try:
        user_to_delete = get_object_or_404(User, pk=user_id)

        # Prevent deleting yourself
        if user_to_delete.id == request.user.id:
            return JsonResponse(
                {"success": False, "message": _("لا يمكنك حذف حسابك الخاص.")},
                status=400,
            )

        # Prevent deleting other superusers
        if user_to_delete.is_superuser:
            return JsonResponse(
                {"success": False, "message": _("لا يمكن حذف مدير رئيسي.")}, status=403
            )

        data = json.loads(request.body)
        delete_ads = data.get("delete_ads", False)
        username = user_to_delete.username

        # Delete user's ads if requested
        if delete_ads:
            ads_count = user_to_delete.classifiedads.count()
            user_to_delete.classifiedads.all().delete()
            message = _("تم حذف المستخدم '{}' و {} إعلان.").format(username, ads_count)
        else:
            # Reassign ads to a default "deleted user" or mark as orphaned
            # For now, we'll just delete the user and let CASCADE handle it
            message = _("تم حذف المستخدم '{}'.").format(username)

        user_to_delete.delete()

        return JsonResponse({"success": True, "message": message})

    except User.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("المستخدم غير موجود.")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@superadmin_required
@require_POST
def admin_create_user(request):
    """
    Create new user from admin panel.
    """
    try:
        data = json.loads(request.body)

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        user_type = data.get('user_type', 'member')
        is_verified = data.get('is_verified', False)
        is_mobile_verified = data.get('is_mobile_verified', False)

        # Validation
        if not username or not email or not password:
            return JsonResponse({
                "success": False,
                "message": _("اسم المستخدم والبريد الإلكتروني وكلمة المرور مطلوبة")
            }, status=400)

        # Check uniqueness
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "success": False,
                "message": _("اسم المستخدم مستخدم بالفعل")
            }, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": _("البريد الإلكتروني مستخدم بالفعل")
            }, status=400)

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )

        # Set user type
        if user_type == 'staff':
            user.is_staff = True
        elif user_type == 'superuser':
            user.is_staff = True
            user.is_superuser = True

        # Set verification
        if is_verified:
            user.verification_status = User.VerificationStatus.VERIFIED
            user.verified_at = timezone.now()

        if is_mobile_verified:
            user.is_mobile_verified = True

        user.save()

        return JsonResponse({
            "success": True,
            "message": _("تم إنشاء المستخدم '{}' بنجاح").format(username),
            "user_id": user.id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {}").format(str(e))
        }, status=500)


@superadmin_required
@require_POST
def admin_verify_user_email(request, user_id):
    """Toggle user's email verification status."""
    try:
        user = get_object_or_404(User, pk=user_id)

        # Toggle verification status based on current state
        if user.verification_status == User.VerificationStatus.VERIFIED:
            user.verification_status = User.VerificationStatus.UNVERIFIED
            user.verified_at = None
            message = _("تم إلغاء توثيق البريد الإلكتروني للمستخدم '{}'").format(user.username)
            verified = False
        else:
            user.verification_status = User.VerificationStatus.VERIFIED
            user.verified_at = timezone.now()
            message = _("تم توثيق البريد الإلكتروني للمستخدم '{}'").format(user.username)
            verified = True

        user.save(update_fields=['verification_status', 'verified_at'])

        return JsonResponse({"success": True, "message": message, "verified": verified})

    except Exception as e:
        return JsonResponse({"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500)


@superadmin_required
@require_POST
def admin_verify_user_phone(request, user_id):
    """Toggle user's mobile verification status."""
    try:
        user = get_object_or_404(User, pk=user_id)

        # Toggle mobile verification (the actual field name in User model)
        user.is_mobile_verified = not user.is_mobile_verified

        if user.is_mobile_verified:
            message = _("تم توثيق رقم الهاتف للمستخدم '{}'").format(user.username)
        else:
            message = _("تم إلغاء توثيق رقم الهاتف للمستخدم '{}'").format(user.username)

        user.save(update_fields=['is_mobile_verified'])

        return JsonResponse({"success": True, "message": message, "phone_verified": user.is_mobile_verified})

    except Exception as e:
        return JsonResponse({"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500)


@superadmin_required
@require_POST
def admin_add_user_ad_balance(request, user_id):
    """Add ad balance (credits) to user's active package."""
    try:
        user = get_object_or_404(User, pk=user_id)
        data = json.loads(request.body)

        amount = data.get('amount', 0)
        note = data.get('note', '').strip()

        if amount <= 0:
            return JsonResponse({"success": False, "message": _("يجب أن يكون المبلغ أكبر من صفر")}, status=400)

        # Get or create user's active package
        from main.models import UserPackage

        # Try to get active package
        active_package = user.ad_packages.filter(
            expiry_date__gte=timezone.now()
        ).order_by('-purchase_date').first()

        if active_package:
            # Add to existing package
            old_balance = active_package.ads_remaining
            active_package.ads_remaining += amount
            active_package.save(update_fields=['ads_remaining'])
            new_balance = active_package.ads_remaining
        else:
            # Create a new free package for the user
            from main.models import AdPackage
            expiry_date = timezone.now() + timezone.timedelta(days=365)  # 1 year validity

            active_package = UserPackage.objects.create(
                user=user,
                package=None,  # Free package
                ads_remaining=amount,
                expiry_date=expiry_date
            )
            old_balance = 0
            new_balance = amount

        return JsonResponse({
            "success": True,
            "message": _("تم إضافة {} إعلان إلى رصيد '{}'").format(amount, user.username),
            "old_balance": old_balance,
            "new_balance": new_balance
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500)


@superadmin_required
@require_POST
def admin_toggle_user_active(request, user_id):
    """Activate or deactivate user account."""
    try:
        user = get_object_or_404(User, pk=user_id)

        if user.id == request.user.id:
            return JsonResponse({"success": False, "message": _("لا يمكنك تعطيل حسابك الخاص")}, status=400)

        if user.is_superuser and user.id != request.user.id:
            return JsonResponse({"success": False, "message": _("لا يمكن تعطيل مدير رئيسي آخر")}, status=403)

        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

        status_text = _("تم تفعيل") if user.is_active else _("تم تعطيل")
        message = _("{} حساب المستخدم '{}'").format(status_text, user.username)

        return JsonResponse({"success": True, "message": message, "is_active": user.is_active})

    except Exception as e:
        return JsonResponse({"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500)


@superadmin_required
@require_POST
def admin_change_user_role(request, user_id):
    """Change user's role (member, staff, superuser)."""
    try:
        user = get_object_or_404(User, pk=user_id)
        data = json.loads(request.body)

        new_role = data.get('role', 'member')

        if user.id == request.user.id:
            return JsonResponse({"success": False, "message": _("لا يمكنك تغيير دورك الخاص")}, status=400)

        if new_role == 'superuser':
            user.is_staff = True
            user.is_superuser = True
            role_name = _("مدير رئيسي")
        elif new_role == 'staff':
            user.is_staff = True
            user.is_superuser = False
            role_name = _("موظف")
        else:
            user.is_staff = False
            user.is_superuser = False
            role_name = _("عضو")

        user.save(update_fields=['is_staff', 'is_superuser'])

        return JsonResponse({"success": True, "message": _("تم تغيير دور '{}' إلى {}").format(user.username, role_name), "role": new_role})

    except Exception as e:
        return JsonResponse({"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500)


@superadmin_required
@require_POST
def admin_ad_delete(request, ad_id):
    """Delete ad from admin panel"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        ad_title = ad.title
        ad.delete()

        return JsonResponse(
            {
                "success": True,
                "message": _("تم حذف الإعلان '{ad_title}' بنجاح.").format(
                    ad_title=ad_title
                ),
            },
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("حدث خطأ أثناء حذف الإعلان: {error}").format(error=str(e)),
            }
        )


@superadmin_required
@require_POST
def admin_ad_toggle_cart(request, ad_id):
    """Toggle cart enabled status for ad"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        ad.cart_enabled_by_admin = not ad.cart_enabled_by_admin
        ad.save(update_fields=['cart_enabled_by_admin'])

        status_text = _("تم تفعيل السلة") if ad.cart_enabled_by_admin else _("تم إيقاف السلة")

        return JsonResponse({
            "success": True,
            "message": status_text,
            "cart_enabled": ad.cart_enabled_by_admin
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_ad_mark_sold(request, ad_id):
    """Mark ad as sold or unsold"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)

        if ad.status == 'SOLD':
            ad.status = 'ACTIVE'
            message = _("تم إلغاء وضع 'مباع'")
        else:
            ad.status = 'SOLD'
            message = _("تم تحديد الإعلان كمباع")

        ad.save(update_fields=['status'])

        return JsonResponse({
            "success": True,
            "message": message,
            "status": ad.status
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_ad_suspend(request, ad_id):
    """Suspend or unsuspend ad"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)

        if ad.status == 'SUSPENDED':
            ad.status = 'ACTIVE'
            message = _("تم إلغاء تعليق الإعلان")
        else:
            ad.status = 'SUSPENDED'
            message = _("تم تعليق الإعلان")

        ad.save(update_fields=['status'])

        return JsonResponse({
            "success": True,
            "message": message,
            "status": ad.status
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_ad_boost(request, ad_id):
    """Boost ad by updating created_at to move it to top"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        ad.created_at = timezone.now()
        ad.save(update_fields=['created_at'])

        return JsonResponse({
            "success": True,
            "message": _("تم ترويج الإعلان بنجاح")
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_ad_duplicate(request, ad_id):
    """Duplicate ad with all details"""
    try:
        original_ad = get_object_or_404(ClassifiedAd, pk=ad_id)

        # Create duplicate
        new_ad = ClassifiedAd.objects.create(
            user=original_ad.user,
            category=original_ad.category,
            country=original_ad.country,
            title=f"{original_ad.title} (نسخة)",
            description=original_ad.description,
            price=original_ad.price,
            location=original_ad.location,
            contact_phone=original_ad.contact_phone,
            contact_email=original_ad.contact_email,
            status='PENDING'
        )

        # Copy images
        for image in original_ad.images.all():
            from main.models import AdImage
            AdImage.objects.create(
                ad=new_ad,
                image=image.image,
                caption=image.caption
            )

        return JsonResponse({
            "success": True,
            "message": _("تم نسخ الإعلان بنجاح"),
            "new_ad_id": new_ad.id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_ad_ban(request, ad_id):
    """Permanently ban ad"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        ad.status = 'BANNED'
        ad.is_hidden = True
        ad.save(update_fields=['status', 'is_hidden'])

        return JsonResponse({
            "success": True,
            "message": _("تم حظر الإعلان نهائياً")
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_ad_change_category(request, ad_id):
    """Change ad category and section"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        data = json.loads(request.body)

        category_id = data.get('category_id')
        if not category_id:
            return JsonResponse({
                "success": False,
                "message": _("يرجى اختيار فئة")
            })

        category = get_object_or_404(Category, pk=category_id)
        ad.category = category
        ad.save(update_fields=['category'])

        return JsonResponse({
            "success": True,
            "message": _("تم تغيير القسم والفئة بنجاح")
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_ad_extend(request, ad_id):
    """Extend ad expiration date"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        data = json.loads(request.body)

        days = data.get('days', 30)
        if not isinstance(days, int) or days < 1 or days > 365:
            return JsonResponse({
                "success": False,
                "message": _("عدد الأيام يجب أن يكون بين 1 و 365")
            })

        if ad.expires_at:
            ad.expires_at = ad.expires_at + timedelta(days=days)
        else:
            ad.expires_at = timezone.now() + timedelta(days=days)

        ad.save(update_fields=['expires_at'])

        return JsonResponse({
            "success": True,
            "message": _("تم تمديد الإعلان لمدة {days} يوم").format(days=days)
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
@require_POST
def admin_contact_publisher(request, ad_id):
    """Send message to ad publisher"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        data = json.loads(request.body)

        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        if not subject or not message:
            return JsonResponse({
                "success": False,
                "message": _("الموضوع والرسالة مطلوبان")
            })

        # Send email if user has email
        if ad.user.email:
            from django.core.mail import send_mail
            from django.conf import settings

            full_message = f"""
مرحباً {ad.user.get_full_name() or ad.user.username},

بخصوص إعلانك: {ad.title}

{message}

مع تحياتنا،
فريق الإدارة
            """

            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [ad.user.email],
                fail_silently=False,
            )

            return JsonResponse({
                "success": True,
                "message": _("تم إرسال الرسالة بنجاح")
            })
        else:
            return JsonResponse({
                "success": False,
                "message": _("المستخدم ليس لديه بريد إلكتروني")
            })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": _("حدث خطأ: {error}").format(error=str(e))
        })


@superadmin_required
def admin_get_ads_by_tab(request, tab):
    """Get ads for specific tab via AJAX"""
    try:
        ads_data = []

        if tab == "active":
            ads = ClassifiedAd.objects.filter(status="active")
        elif tab == "pending":
            ads = ClassifiedAd.objects.filter(status="pending")
        elif tab == "expired":
            ads = ClassifiedAd.objects.filter(status="expired")
        elif tab == "hidden":
            ads = ClassifiedAd.objects.filter(status="draft")
        elif tab == "cart":
            ads = ClassifiedAd.objects.filter(
                Q(is_cart_enabled=True) | Q(allow_cart=True)
            )
        else:
            ads = ClassifiedAd.objects.none()

        ads = ads.select_related("user", "category", "country").prefetch_related(
            "images"
        )

        for ad in ads[:50]:  # Limit to 50 for performance
            ads_data.append(
                {
                    "id": ad.pk,
                    "title": ad.title,
                    "user": ad.user.username,
                    "category": ad.category.name,
                    "status": ad.status,
                    "status_display": ad.get_status_display(),
                    "price": str(ad.price),
                    "created_at": ad.created_at.strftime("%Y-%m-%d %H:%M"),
                    "image": ad.images.first().image.url if ad.images.first() else "",
                }
            )

        return JsonResponse({"success": True, "ads": ads_data, "count": ads.count()})

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {error}").format(error=str(e))}
        )


@superadmin_required
@require_POST
def admin_settings_constance_get(request):
    """Return all django-constance config keys with values and inferred types."""
    try:
        from constance import config as constance_config
        from django.conf import settings as dj_settings

        result = []
        const_cfg = getattr(dj_settings, "CONSTANCE_CONFIG", {})
        for key, meta in const_cfg.items():
            default = None
            help_text = ""
            field_type = None
            try:
                # CONSTANCE_CONFIG can be (default,) or (default, help) or (default, help, type)
                if isinstance(meta, (list, tuple)):
                    if len(meta) > 0:
                        default = meta[0]
                    if len(meta) > 1:
                        help_text = meta[1] or ""
                    if len(meta) > 2:
                        field_type = meta[2]
            except Exception:
                pass

            value = getattr(constance_config, key, default)
            # Infer simple type if not provided
            py_type = type(value).__name__
            result.append(
                {
                    "key": key,
                    "value": value,
                    "default": default,
                    "help": help_text,
                    "type": (
                        field_type.__name__
                        if hasattr(field_type, "__name__")
                        else py_type
                    ),
                }
            )

        return JsonResponse({"success": True, "config": result})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@superadmin_required
@require_POST
def admin_settings_constance_save(request):
    """Save posted django-constance key/value pairs."""
    try:
        from constance import config as constance_config
        from django.conf import settings as dj_settings

        data = json.loads(request.body or "{}")
        updates = data.get("updates", {})

        const_cfg = getattr(dj_settings, "CONSTANCE_CONFIG", {})

        def cast_value(key, val):
            meta = const_cfg.get(key)
            if (
                isinstance(meta, (list, tuple))
                and len(meta) > 2
                and meta[2] is not None
            ):
                target = meta[2]
                try:
                    # Handle booleans explicitly as JSON may send true/false or strings
                    if target is bool:
                        if isinstance(val, bool):
                            return val
                        if isinstance(val, str):
                            return val.lower() in ("1", "true", "yes", "on")
                        return bool(val)
                    return target(val)
                except Exception:
                    return val
            return val

        for key, val in updates.items():
            try:
                setattr(constance_config, key, cast_value(key, val))
            except Exception:
                # continue best-effort updates
                continue

        return JsonResponse({"success": True, "message": _("تم حفظ إعدادات النظام")})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@superadmin_required
def admin_translations_stats(request):
    """Get translation statistics from .po files"""
    try:
        import os
        from django.conf import settings

        try:
            import polib
        except ImportError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "polib is not installed. Please install it with: pip install polib",
                },
                status=500,
            )

        stats = {
            "languages": [],
            "total_strings": 0,
            "translated_strings": 0,
            "completion_rate": 0,
        }

        # Get locale directory
        locale_path = os.path.join(settings.BASE_DIR, "locale")

        if not os.path.exists(locale_path):
            return JsonResponse({"success": True, "stats": stats})

        language_stats = []
        # Use the first language to get the total count (all languages have same source strings)
        base_total = 0
        total_translated = 0
        lang_count = 0

        # Iterate through language directories
        for lang_code in os.listdir(locale_path):
            lang_dir = os.path.join(locale_path, lang_code)
            if not os.path.isdir(lang_dir):
                continue

            po_file = os.path.join(lang_dir, "LC_MESSAGES", "django.po")

            if os.path.exists(po_file):
                try:
                    po = polib.pofile(po_file)
                    total = len(po)
                    translated = len(po.translated_entries())
                    untranslated = len(po.untranslated_entries())
                    fuzzy = len(po.fuzzy_entries())
                    percent = po.percent_translated()

                    language_stats.append(
                        {
                            "code": lang_code,
                            "total": total,
                            "translated": translated,
                            "untranslated": untranslated,
                            "fuzzy": fuzzy,
                            "percent": round(percent, 1),
                        }
                    )

                    # Use the first language's total as the base (all have same source strings)
                    if base_total == 0:
                        base_total = total

                    total_translated += translated
                    lang_count += 1

                except Exception as e:
                    print(f"Error reading {po_file}: {e}")
                    import traceback

                    print(traceback.format_exc())
                    continue

        stats["languages"] = language_stats
        stats["total_strings"] = base_total  # Total unique strings (from one language)
        stats["translated_strings"] = (
            total_translated // lang_count if lang_count > 0 else 0
        )  # Average across languages
        stats["completion_rate"] = round(
            (stats["translated_strings"] / base_total * 100) if base_total > 0 else 0,
            1,
        )

        return JsonResponse({"success": True, "stats": stats})

    except Exception as e:
        import traceback

        print(f"Translation stats error: {traceback.format_exc()}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@superadmin_required
def admin_translations_get(request, lang):
    """Get translations from .po file for editing"""
    try:
        import os
        from django.conf import settings

        try:
            import polib
        except ImportError:
            return JsonResponse(
                {"success": False, "message": "polib is not installed"}, status=500
            )

        locale_path = os.path.join(
            settings.BASE_DIR, "locale", lang, "LC_MESSAGES", "django.po"
        )

        if not os.path.exists(locale_path):
            return JsonResponse(
                {"success": False, "message": f"Translation file for {lang} not found"},
                status=404,
            )

        po = polib.pofile(locale_path)
        translations = []

        for entry in po:
            if not entry.obsolete:  # Skip obsolete entries
                translations.append(
                    {
                        "msgid": entry.msgid,
                        "msgstr": entry.msgstr,
                        "fuzzy": entry.fuzzy if hasattr(entry, "fuzzy") else False,
                    }
                )

        return JsonResponse(
            {"success": True, "translations": translations, "total": len(translations)}
        )

    except Exception as e:
        import traceback

        print(f"Translation get error: {traceback.format_exc()}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@superadmin_required
@require_POST
def admin_translations_save(request, lang):
    """Save translations to .po file"""
    try:
        import os
        import json
        from django.conf import settings

        try:
            import polib
        except ImportError:
            return JsonResponse(
                {"success": False, "message": "polib is not installed"}, status=500
            )

        locale_path = os.path.join(
            settings.BASE_DIR, "locale", lang, "LC_MESSAGES", "django.po"
        )

        if not os.path.exists(locale_path):
            return JsonResponse(
                {"success": False, "message": f"Translation file for {lang} not found"},
                status=404,
            )

        data = json.loads(request.body)
        updates = data.get("updates", [])

        if not updates:
            return JsonResponse(
                {"success": False, "message": "No updates provided"}, status=400
            )

        # Load the .po file
        po = polib.pofile(locale_path)
        updated_count = 0

        # Update translations
        for update in updates:
            msgid = update.get("msgid")
            msgstr = update.get("msgstr")

            if not msgid:
                continue

            # Find the entry in the .po file
            entry = po.find(msgid)
            if entry:
                entry.msgstr = msgstr
                # Remove fuzzy flag if translation is provided
                if msgstr and "fuzzy" in entry.flags:
                    entry.flags.remove("fuzzy")
                updated_count += 1

        # Save the .po file
        po.save(locale_path)

        # Compile to .mo file
        mo_path = os.path.join(
            settings.BASE_DIR, "locale", lang, "LC_MESSAGES", "django.mo"
        )
        po.save_as_mofile(mo_path)

        return JsonResponse(
            {
                "success": True,
                "message": f"Updated {updated_count} translations",
                "updated_count": updated_count,
            }
        )

    except Exception as e:
        import traceback

        print(f"Translation save error: {traceback.format_exc()}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# Settings AJAX Endpoints


@superadmin_required
@require_POST
def admin_settings_get(request):
    """Get current system settings from Constance"""
    try:
        from constance import config

        settings = {
            "publishing_mode": getattr(config, "PUBLISHING_MODE", "direct"),
            "verified_auto_publish": getattr(config, "VERIFIED_AUTO_PUBLISH", True),
            "allow_guest_viewing": getattr(config, "ALLOW_GUEST_VIEWING", True),
            "allow_guest_contact": getattr(config, "ALLOW_GUEST_CONTACT", False),
            "members_only_contact": getattr(config, "MEMBERS_ONLY_CONTACT", True),
            "members_only_messaging": getattr(config, "MEMBERS_ONLY_MESSAGING", True),
            "delivery_service_enabled": getattr(
                config, "DELIVERY_SERVICE_ENABLED", True
            ),
            "delivery_requires_approval": getattr(
                config, "DELIVERY_REQUIRES_APPROVAL", True
            ),
            "cart_system_enabled": getattr(config, "CART_SYSTEM_ENABLED", True),
            "cart_by_main_category": getattr(config, "CART_BY_MAIN_CATEGORY", False),
            "cart_by_subcategory": getattr(config, "CART_BY_SUBCATEGORY", True),
            "cart_per_ad": getattr(config, "CART_PER_AD", True),
            "default_reservation_percentage": getattr(
                config, "DEFAULT_RESERVATION_PERCENTAGE", 20
            ),
            "min_reservation_amount": getattr(config, "MIN_RESERVATION_AMOUNT", 50),
            "max_reservation_amount": getattr(config, "MAX_RESERVATION_AMOUNT", 5000),
            "delivery_fee_percentage": getattr(config, "DELIVERY_FEE_PERCENTAGE", 5),
            "delivery_fee_min": getattr(config, "DELIVERY_FEE_MIN", 10),
            "delivery_fee_max": getattr(config, "DELIVERY_FEE_MAX", 500),
            "notify_admin_new_ads": getattr(config, "NOTIFY_ADMIN_NEW_ADS", True),
            "notify_admin_pending_review": getattr(
                config, "NOTIFY_ADMIN_PENDING_REVIEW", True
            ),
            "notify_admin_new_users": getattr(config, "NOTIFY_ADMIN_NEW_USERS", True),
            "notify_admin_payments": getattr(config, "NOTIFY_ADMIN_PAYMENTS", True),
            "admin_notification_email": getattr(
                config,
                "ADMIN_NOTIFICATION_EMAIL",
                request.user.email if request.user.is_authenticated else "",
            ),
            "site_name_in_emails": getattr(
                config, "SITE_NAME_IN_EMAILS", "إدريسي مارت"
            ),
            "ads_notification_frequency": getattr(
                config, "ADS_NOTIFICATION_FREQUENCY", "hourly"
            ),
            "stats_report_frequency": getattr(
                config, "STATS_REPORT_FREQUENCY", "daily"
            ),
        }

        return JsonResponse({"success": True, "settings": settings})

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {error}").format(error=str(e))}
        )


@superadmin_required
@require_POST
def admin_settings_publishing(request):
    """Save publishing settings to Constance"""
    try:
        from constance import config

        # Get values from POST
        publishing_mode = request.POST.get("publishing_mode", "direct")
        verified_auto_publish = request.POST.get("verified_auto_publish") == "on"
        allow_guest_viewing = request.POST.get("allow_guest_viewing") == "on"
        allow_guest_contact = request.POST.get("allow_guest_contact") == "on"
        members_only_contact = request.POST.get("members_only_contact") == "on"
        members_only_messaging = request.POST.get("members_only_messaging") == "on"

        # Save to Constance
        config.PUBLISHING_MODE = publishing_mode
        config.VERIFIED_AUTO_PUBLISH = verified_auto_publish
        config.ALLOW_GUEST_VIEWING = allow_guest_viewing
        config.ALLOW_GUEST_CONTACT = allow_guest_contact
        config.MEMBERS_ONLY_CONTACT = members_only_contact
        config.MEMBERS_ONLY_MESSAGING = members_only_messaging

        return JsonResponse(
            {"success": True, "message": _("تم حفظ إعدادات النشر بنجاح.")}
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {error}").format(error=str(e))}
        )


@superadmin_required
@require_POST
def admin_settings_delivery(request):
    """Save delivery settings to Constance"""
    try:
        from constance import config

        # Get values from POST
        delivery_service_enabled = request.POST.get("delivery_service_enabled") == "on"
        delivery_requires_approval = (
            request.POST.get("delivery_requires_approval") == "on"
        )
        delivery_terms_ar = request.POST.get("delivery_terms_ar", "")
        delivery_terms_en = request.POST.get("delivery_terms_en", "")
        delivery_fee_percentage = int(request.POST.get("delivery_fee_percentage", 5))
        delivery_fee_min = int(request.POST.get("delivery_fee_min", 10))
        delivery_fee_max = int(request.POST.get("delivery_fee_max", 500))

        # Save to Constance
        config.DELIVERY_SERVICE_ENABLED = delivery_service_enabled
        config.DELIVERY_REQUIRES_APPROVAL = delivery_requires_approval
        config.DELIVERY_FEE_PERCENTAGE = delivery_fee_percentage
        config.DELIVERY_FEE_MIN = delivery_fee_min
        config.DELIVERY_FEE_MAX = delivery_fee_max

        return JsonResponse(
            {"success": True, "message": _("تم حفظ إعدادات التوصيل بنجاح.")}
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {error}").format(error=str(e))}
        )


@superadmin_required
@require_POST
def admin_settings_cart(request):
    """Save cart settings to Constance"""
    try:
        from constance import config

        # Get values from POST
        cart_system_enabled = request.POST.get("cart_system_enabled") == "on"
        cart_by_main_category = request.POST.get("cart_by_main_category") == "on"
        cart_by_subcategory = request.POST.get("cart_by_subcategory") == "on"
        cart_per_ad = request.POST.get("cart_per_ad") == "on"
        default_reservation_percentage = int(
            request.POST.get("default_reservation_percentage", 20)
        )
        min_reservation_amount = int(request.POST.get("min_reservation_amount", 50))
        max_reservation_amount = int(request.POST.get("max_reservation_amount", 5000))

        # Save to Constance
        config.CART_SYSTEM_ENABLED = cart_system_enabled
        config.CART_BY_MAIN_CATEGORY = cart_by_main_category
        config.CART_BY_SUBCATEGORY = cart_by_subcategory
        config.CART_PER_AD = cart_per_ad
        config.DEFAULT_RESERVATION_PERCENTAGE = default_reservation_percentage
        config.MIN_RESERVATION_AMOUNT = min_reservation_amount
        config.MAX_RESERVATION_AMOUNT = max_reservation_amount

        return JsonResponse(
            {"success": True, "message": _("تم حفظ إعدادات السلة بنجاح.")}
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {error}").format(error=str(e))}
        )


@superadmin_required
@require_POST
def admin_settings_notifications(request):
    """Save notification settings to Constance"""
    try:
        from constance import config

        # Get values from POST
        notify_admin_new_ads = request.POST.get("notify_admin_new_ads") == "on"
        notify_admin_pending_review = (
            request.POST.get("notify_admin_pending_review") == "on"
        )
        notify_admin_new_users = request.POST.get("notify_admin_new_users") == "on"
        notify_admin_payments = request.POST.get("notify_admin_payments") == "on"
        admin_notification_email = request.POST.get("admin_notification_email", "")
        site_name_in_emails = request.POST.get("site_name_in_emails", "")
        ads_notification_frequency = request.POST.get(
            "ads_notification_frequency", "hourly"
        )
        stats_report_frequency = request.POST.get("stats_report_frequency", "daily")

        # Save to Constance
        config.NOTIFY_ADMIN_NEW_ADS = notify_admin_new_ads
        config.NOTIFY_ADMIN_PENDING_REVIEW = notify_admin_pending_review
        config.NOTIFY_ADMIN_NEW_USERS = notify_admin_new_users
        config.NOTIFY_ADMIN_PAYMENTS = notify_admin_payments
        config.ADMIN_NOTIFICATION_EMAIL = admin_notification_email
        config.SITE_NAME_IN_EMAILS = site_name_in_emails
        config.ADS_NOTIFICATION_FREQUENCY = ads_notification_frequency
        config.STATS_REPORT_FREQUENCY = stats_report_frequency

        return JsonResponse(
            {"success": True, "message": _("تم حفظ إعدادات الإشعارات بنجاح.")}
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {error}").format(error=str(e))}
        )


@superadmin_required
def ad_publisher_detail(request, ad_id):
    """
    Admin view to see the full details of an ad from a publisher's perspective.
    """
    ad = get_object_or_404(
        ClassifiedAd.objects.select_related(
            "user", "category", "country", "category__parent"
        ).prefetch_related("images", "features"),
        pk=ad_id,
    )

    # Get other active ads by the same user, excluding the current one
    other_ads_by_user = (
        ClassifiedAd.objects.filter(user=ad.user, status=ClassifiedAd.AdStatus.ACTIVE)
        .exclude(pk=ad.pk)
        .select_related("category", "country")
        .prefetch_related("images")
        .order_by("-created_at")[:8]
    )

    # Get user's ad status counts for the chart
    user_ad_stats = ad.user.classified_ads.aggregate(
        active=Count("pk", filter=Q(status=ClassifiedAd.AdStatus.ACTIVE)),
        pending=Count("pk", filter=Q(status=ClassifiedAd.AdStatus.PENDING)),
        expired=Count("pk", filter=Q(status=ClassifiedAd.AdStatus.EXPIRED)),
        rejected=Count("pk", filter=Q(status=ClassifiedAd.AdStatus.REJECTED)),
        draft=Count("pk", filter=Q(status=ClassifiedAd.AdStatus.DRAFT)),
    )

    # Get all active categories for the Change Category modal
    categories = Category.objects.filter(is_active=True).order_by('name')

    context = {
        "ad": ad,
        "page_title": _("معاينة الإعلان") + f" - {ad.title}",
        "other_ads_by_user": other_ads_by_user,
        "user_ad_stats": json.dumps(user_ad_stats),
        "categories": categories,
        "active_nav": "ads",
    }
    return render(request, "classifieds/ad_publisher_detail.html", context)


@login_required
def dashboard_redirect(request):
    """
    Smart dashboard redirect based on user role:
    - Superusers/Staff -> Admin Dashboard
    - Publisher profile -> Publisher Dashboard (My Ads)
    - Users with ads -> Publisher Dashboard (My Ads)
    - Regular users -> Home page
    """
    user = request.user

    # Redirect admins to admin dashboard
    if user.is_superuser or user.is_staff:
        return redirect("main:admin_dashboard")

    # Both DEFAULT and PUBLISHER users go to publisher dashboard
    try:
        if getattr(user, "profile_type", None) in ["default", "publisher"]:
            return redirect("main:my_ads")
    except Exception:
        pass

    # Fallback for other cases
    return redirect("main:home")


# ========== Chat Views (Django Channels) ==========


class PublisherChatsView(LoginRequiredMixin, TemplateView):
    """Publisher chat list view - shows all chats with clients"""

    template_name = "chat/publisher_chats.html"

    def get_context_data(self, **kwargs):
        from django.db.models import Count, Q

        context = super().get_context_data(**kwargs)
        context["active_nav"] = "chats"

        # Get all chat rooms for the publisher
        chat_rooms = (
            ChatRoom.objects.filter(
                publisher=self.request.user, room_type="publisher_client"
            )
            .select_related("client", "ad")
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

        # Add unread count for each room
        rooms_with_unread = []
        for room in chat_rooms:
            room.unread_count = room.get_unread_count(self.request.user)
            rooms_with_unread.append(room)

        context["chat_rooms"] = rooms_with_unread

        # Calculate statistics
        total_chats = len(rooms_with_unread)
        active_chats = (
            ChatRoom.objects.filter(
                publisher=self.request.user,
                is_active=True,
                room_type="publisher_client",
                messages__created_at__gte=timezone.now() - timezone.timedelta(days=7),
            )
            .distinct()
            .count()
        )

        unread_messages = (
            ChatMessage.objects.filter(room__publisher=self.request.user, is_read=False)
            .exclude(sender=self.request.user)
            .count()
        )

        active_ads = (
            ChatRoom.objects.filter(
                publisher=self.request.user, room_type="publisher_client"
            )
            .values("ad")
            .distinct()
            .count()
        )

        context["chat_stats"] = {
            "total_chats": total_chats,
            "active_chats": active_chats,
            "unread_messages": unread_messages,
            "active_ads": active_ads,
        }

        return context


class PublisherSupportChatView(LoginRequiredMixin, TemplateView):
    """Publisher support chat view - chat with admin"""

    template_name = "chat/publisher_support.html"

    def get_context_data(self, **kwargs):
        from django.db.models import Count, Q

        context = super().get_context_data(**kwargs)
        context["active_nav"] = "support"

        # Get all support chat rooms for the publisher
        support_rooms = (
            ChatRoom.objects.filter(
                publisher=self.request.user, room_type="publisher_admin"
            )
            .select_related("publisher")
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

        context["support_rooms"] = support_rooms

        # Calculate statistics
        total_tickets = support_rooms.count()
        pending_tickets = support_rooms.filter(is_active=True).count()
        resolved_tickets = support_rooms.filter(is_active=False).count()

        # Count unread messages from admin (messages where sender is staff and not read by publisher)
        unread_messages = (
            ChatMessage.objects.filter(
                room__in=support_rooms, sender__is_staff=True, is_read=False
            )
            .exclude(sender=self.request.user)
            .count()
        )

        context["support_stats"] = {
            "total_tickets": total_tickets,
            "pending_tickets": pending_tickets,
            "resolved_tickets": resolved_tickets,
            "unread_messages": unread_messages,
        }

        return context


class AdminSupportChatsView(SuperadminRequiredMixin, TemplateView):
    """Admin support chats view - shows all publisher support requests"""

    template_name = "chat/admin_support_chats.html"

    def get_context_data(self, **kwargs):
        from main.models import ChatRoom, ChatMessage
        from django.db.models import Count, Q

        context = super().get_context_data(**kwargs)
        context["active_nav"] = "support_chats"

        # Get all support chat rooms (publisher-admin type)
        chat_rooms = (
            ChatRoom.objects.filter(room_type="publisher_admin")
            .select_related("publisher")
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

        context["chat_rooms"] = chat_rooms

        # Calculate statistics
        total_chats = chat_rooms.count()
        active_chats = chat_rooms.filter(is_active=True).count()

        # Count unread messages (messages from publishers not read by admin)
        unread_messages = ChatMessage.objects.filter(
            room__room_type="publisher_admin",
            is_read=False,
            sender__is_staff=False,  # Messages from publishers
        ).count()

        # Count resolved chats today
        from django.utils import timezone

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        resolved_today = chat_rooms.filter(
            is_active=False, updated_at__gte=today_start
        ).count()

        # Count total resolved chats
        resolved_chats = chat_rooms.filter(is_active=False).count()

        context["chat_stats"] = {
            "total_chats": total_chats,
            "active_chats": active_chats,
            "unread_messages": unread_messages,
            "resolved_today": resolved_today,
            "resolved_chats": resolved_chats,
        }

        return context


# ==============================================
# ADMIN SUPPORT CHAT AJAX ENDPOINTS
# ==============================================


@login_required
def admin_chat_get_messages(request, room_id):
    """Get chat messages for a specific room via AJAX"""
    import logging

    logger = logging.getLogger(__name__)

    # Check if user is staff
    if not request.user.is_staff:
        logger.warning(
            f"Unauthorized access attempt to chat room {room_id} by user {request.user}"
        )
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    try:
        from main.models import ChatRoom
        from django.template.loader import render_to_string
        from django.core.exceptions import ObjectDoesNotExist

        logger.info(f"Fetching chat room {room_id}")

        try:
            room = (
                ChatRoom.objects.select_related("publisher")
                .prefetch_related("messages__sender")
                .get(
                    id=room_id,
                    room_type="publisher_admin",
                )
            )
        except ObjectDoesNotExist:
            logger.error(f"Chat room {room_id} not found")
            return JsonResponse(
                {"success": False, "error": "Chat room not found"}, status=404
            )

        logger.info(f"Chat room {room_id} found with {room.messages.count()} messages")

        # Mark messages as read
        unread_count = room.messages.filter(
            is_read=False, sender__is_staff=False
        ).count()
        room.messages.filter(is_read=False, sender__is_staff=False).update(
            is_read=True, read_at=timezone.now()
        )
        logger.info(f"Marked {unread_count} messages as read in room {room_id}")

        # Render chat HTML
        try:
            html = render_to_string(
                "chat/partials/_chat_messages.html", {"room": room, "request": request}
            )
            logger.info(f"Successfully rendered template for room {room_id}")
        except Exception as template_error:
            logger.error(
                f"Template rendering error for room {room_id}: {str(template_error)}"
            )
            raise

        return JsonResponse({"success": True, "html": html, "room_id": room.id})

    except Exception as e:
        logger.error(
            f"Error getting messages for room {room_id}: {str(e)}", exc_info=True
        )
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_POST
def admin_chat_send_message(request, room_id):
    """Send a message in support chat via AJAX"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    try:
        import json
        from main.models import ChatRoom, ChatMessage

        data = json.loads(request.body)
        message_text = data.get("message", "").strip()

        if not message_text:
            return JsonResponse(
                {"success": False, "error": _("الرسالة فارغة")}, status=400
            )

        room = get_object_or_404(ChatRoom, id=room_id, room_type="publisher_admin")

        # Create message
        message = ChatMessage.objects.create(
            room=room, sender=request.user, message=message_text
        )

        # Update room timestamp
        room.save(update_fields=["updated_at"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم إرسال الرسالة"),
                "message_id": message.id,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error sending message: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@superadmin_required
@require_POST
def admin_chat_resolve(request, room_id):
    """Mark chat as resolved"""
    try:
        from main.models import ChatRoom

        room = get_object_or_404(ChatRoom, id=room_id, room_type="publisher_admin")

        room.is_active = False
        room.save(update_fields=["is_active", "updated_at"])

        return JsonResponse({"success": True, "message": _("تم وضع المحادثة كمحلولة")})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@superadmin_required
@require_POST
def admin_chat_reopen(request, room_id):
    """Reopen a resolved chat"""
    try:
        from main.models import ChatRoom

        room = get_object_or_404(ChatRoom, id=room_id, room_type="publisher_admin")

        room.is_active = True
        room.save(update_fields=["is_active", "updated_at"])

        return JsonResponse({"success": True, "message": _("تم إعادة فتح المحادثة")})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def admin_chat_notifications(request):
    """Get chat notification counts for admin dashboard"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        from main.models import ChatRoom, ChatMessage
        from django.db.models import Q

        # Support chat statistics
        unread_support_messages = ChatMessage.objects.filter(
            room__room_type="publisher_admin",
            is_read=False,
            sender__is_staff=False,  # Messages from publishers
        ).count()

        # Regular chat statistics
        total_user_chats = ChatRoom.objects.filter(
            Q(room_type="user_to_user") | Q(room_type="ad_inquiry")
        ).count()

        # Support chat totals
        total_support_chats = ChatRoom.objects.filter(
            room_type="publisher_admin"
        ).count()
        active_support_chats = ChatRoom.objects.filter(
            room_type="publisher_admin", is_active=True
        ).count()
        resolved_support_chats = total_support_chats - active_support_chats

        # Recent activity (last 24 hours)
        yesterday = timezone.now() - timedelta(hours=24)
        recent_activity = ChatMessage.objects.filter(created_at__gte=yesterday).count()

        return JsonResponse(
            {
                "unread_support_messages": unread_support_messages,
                "total_user_chats": total_user_chats,
                "recent_activity": recent_activity,
                "total_support_chats": total_support_chats,
                "active_support_chats": active_support_chats,
                "resolved_support_chats": resolved_support_chats,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "unread_support_messages": 0,
                "total_user_chats": 0,
                "recent_activity": 0,
                "total_support_chats": 0,
                "active_support_chats": 0,
                "resolved_support_chats": 0,
                "error": str(e),
            },
            status=200,
        )


@superadmin_required
def admin_chat_history_data(request):
    """Get chat history data for admin dashboard"""
    from main.models import ChatRoom, ChatMessage
    from django.db.models import Q, Max
    from django.utils import timezone

    # Get chat room statistics
    total_chats = ChatRoom.objects.count()
    active_chats = ChatRoom.objects.filter(is_active=True).count()

    # Recent activity (last 24 hours)
    yesterday = timezone.now() - timedelta(hours=24)
    recent_activity = ChatMessage.objects.filter(created_at__gte=yesterday).count()

    # Get recent chats with last messages
    recent_chat_rooms = ChatRoom.objects.annotate(
        last_message_time=Max("messages__created_at")
    ).order_by("-last_message_time")[:10]

    recent_chats = []
    for room in recent_chat_rooms:
        last_message = room.messages.order_by("-created_at").first()
        participant = getattr(room, "publisher", None) or getattr(room, "client", None)

        if participant and last_message:
            recent_chats.append(
                {
                    "participant": participant.get_full_name() or participant.username,
                    "last_message": (
                        last_message.content[:50]
                        + ("..." if len(last_message.content) > 50 else "")
                        if hasattr(last_message, "content")
                        else last_message.message[:50]
                        + ("..." if len(last_message.message) > 50 else "")
                    ),
                    "status": "active" if room.is_active else "inactive",
                    "last_activity": last_message.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            )

    return JsonResponse(
        {
            "total_chats": total_chats,
            "active_chats": active_chats,
            "recent_activity": recent_activity,
            "recent_chats": recent_chats,
        }
    )


@superadmin_required
def admin_notifications_breakdown(request):
    """Get detailed breakdown of notifications by user type"""
    from main.models import Notification
    from django.db.models import Q

    # Customer notifications (regular users)
    customer_notifications = (
        Notification.objects.filter(user__is_staff=False, user__groups__isnull=True)
        .select_related("user")
        .order_by("-created_at")[:20]
    )

    # Publisher notifications (users with ads)
    publisher_notifications = (
        Notification.objects.filter(
            Q(
                notification_type__in=[
                    "ad_approved",
                    "ad_rejected",
                    "ad_expired",
                    "package_expired",
                ]
            )
            | Q(user__classifiedad__isnull=False)
        )
        .distinct()
        .select_related("user")
        .order_by("-created_at")[:20]
    )

    # Format notifications for JSON response
    def format_notifications(notifications):
        return [
            {
                "id": notif.id,
                "title": notif.title,
                "message": notif.message,
                "user_name": notif.user.get_full_name() or notif.user.username,
                "is_read": notif.is_read,
                "created_at": notif.created_at.strftime("%Y-%m-%d %H:%M"),
                "notification_type": notif.notification_type,
            }
            for notif in notifications
        ]

    return JsonResponse(
        {
            "customer_notifications": format_notifications(customer_notifications),
            "publisher_notifications": format_notifications(publisher_notifications),
        }
    )


@login_required
def admin_notification_counts_update(request):
    """Update notification counts for real-time dashboard updates"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        from main.models import Notification
        from django.db.models import Q

        # Get updated counts
        total_notifications = Notification.objects.count()
        unread_notifications = Notification.objects.filter(is_read=False).count()

        # Customer notifications (regular users without staff status and no special groups)
        unread_customer_notifications = Notification.objects.filter(
            user__is_staff=False, user__groups__isnull=True, is_read=False
        ).count()

        # Publisher notifications (users with published ads)
        from main.models import ClassifiedAd

        publisher_user_ids = ClassifiedAd.objects.values_list(
            "user_id", flat=True
        ).distinct()
        unread_publisher_notifications = Notification.objects.filter(
            user_id__in=publisher_user_ids, is_read=False
        ).count()

        # Admin notifications - general or for staff users
        unread_admin_notifications = Notification.objects.filter(
            Q(notification_type="general") | Q(user__is_staff=True), is_read=False
        ).count()

        return JsonResponse(
            {
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "unread_admin_notifications": unread_admin_notifications,
                "unread_customer_notifications": unread_customer_notifications,
                "unread_publisher_notifications": unread_publisher_notifications,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "total_notifications": 0,
                "unread_notifications": 0,
                "unread_admin_notifications": 0,
                "unread_customer_notifications": 0,
                "unread_publisher_notifications": 0,
                "error": str(e),
            },
            status=200,
        )


@login_required
def user_notification_counts(request):
    """Get notification counts for authenticated users (publisher dashboard)"""
    from main.models import Notification, ChatMessage
    from django.db.models import Q

    context = {
        "user_unread_notifications": 0,
        "unread_chat_messages": 0,
        "unread_support_messages": 0,
    }

    try:
        # User's personal notifications
        context["user_unread_notifications"] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()

        # Chat messages for publishers
        if (
            hasattr(request.user, "classifiedad_set")
            and request.user.classifiedad_set.exists()
        ):
            context["unread_chat_messages"] = (
                ChatMessage.objects.filter(room__publisher=request.user, is_read=False)
                .exclude(sender=request.user)
                .count()
            )

        # Support messages for publishers (messages from admin to this user)
        context["unread_support_messages"] = ChatMessage.objects.filter(
            room__room_type="publisher_admin",
            room__publisher=request.user,
            is_read=False,
            sender__is_staff=True,  # Messages from admin
        ).count()

    except Exception as e:
        # Return default values on error
        pass

    return JsonResponse(context)


class ChatWithPublisherView(LoginRequiredMixin, TemplateView):
    """Client chat with publisher view"""

    template_name = "chat/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad_id = self.kwargs.get("ad_id")

        # Get the ad
        ad = get_object_or_404(ClassifiedAd, id=ad_id)
        context["ad"] = ad

        # Prevent publisher from chatting with themselves
        if self.request.user == ad.user:
            messages.warning(
                self.request, _("You cannot chat with yourself about your own ad.")
            )
            return redirect("main:ad_detail", pk=ad_id)

        # TODO: Get or create chat room
        # from .models import ChatRoom, AdReport
        # context['chat_room'], created = ChatRoom.objects.get_or_create(
        #     ad=ad,
        #     client=self.request.user,
        #     defaults={
        #         'publisher': ad.user,
        #         'room_type': 'publisher_client'
        #     }
        # )

        return context


# ==============================================
# ADMIN PACKAGE & SUBSCRIPTION MANAGEMENT VIEWS
# ==============================================


@superadmin_required
@require_POST
def admin_user_package_extend(request, package_id):
    """Extend user package expiry date"""
    try:
        import json

        data = json.loads(request.body)
        days = int(data.get("days", 0))

        if days <= 0:
            return JsonResponse({"success": False, "error": _("عدد الأيام غير صحيح")})

        user_package = get_object_or_404(UserPackage, id=package_id)
        user_package.expiry_date = user_package.expiry_date + timedelta(days=days)
        user_package.save(update_fields=["expiry_date"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم تمديد الباقة بنجاح"),
                "new_expiry": user_package.expiry_date.strftime("%Y-%m-%d %H:%M"),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@superadmin_required
@require_POST
def admin_user_package_add_ads(request, package_id):
    """Add more ads to user package"""
    try:
        import json

        data = json.loads(request.body)
        ads_count = int(data.get("ads_count", 0))

        if ads_count <= 0:
            return JsonResponse(
                {"success": False, "error": _("عدد الإعلانات غير صحيح")}
            )

        user_package = get_object_or_404(UserPackage, id=package_id)
        user_package.ads_remaining += ads_count
        user_package.save(update_fields=["ads_remaining"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم إضافة الإعلانات بنجاح"),
                "new_ads_remaining": user_package.ads_remaining,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@superadmin_required
@require_POST
def admin_subscription_extend(request, subscription_id):
    """Extend user subscription end date"""
    try:
        import json
        from main.models import UserSubscription

        data = json.loads(request.body)
        days = int(data.get("days", 0))

        if days <= 0:
            return JsonResponse({"success": False, "error": _("عدد الأيام غير صحيح")})

        subscription = get_object_or_404(UserSubscription, id=subscription_id)

        # Convert date to datetime for addition
        from datetime import datetime, date

        if isinstance(subscription.end_date, date):
            end_datetime = datetime.combine(subscription.end_date, datetime.min.time())
        else:
            end_datetime = subscription.end_date

        new_end_date = (end_datetime + timedelta(days=days)).date()
        subscription.end_date = new_end_date
        subscription.save(update_fields=["end_date"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم تمديد الاشتراك بنجاح"),
                "new_end_date": subscription.end_date.strftime("%Y-%m-%d"),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@superadmin_required
@require_POST
def admin_subscription_cancel(request, subscription_id):
    """Cancel user subscription"""
    try:
        from main.models import UserSubscription

        subscription = get_object_or_404(UserSubscription, id=subscription_id)
        subscription.is_active = False
        subscription.auto_renew = False
        subscription.save(update_fields=["is_active", "auto_renew"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم إلغاء الاشتراك بنجاح"),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@superadmin_required
@require_POST
def admin_subscription_toggle_auto_renew(request, subscription_id):
    """Toggle subscription auto-renew setting"""
    try:
        from main.models import UserSubscription

        subscription = get_object_or_404(UserSubscription, id=subscription_id)
        subscription.auto_renew = not subscription.auto_renew
        subscription.save(update_fields=["auto_renew"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم تحديث إعدادات التجديد التلقائي"),
                "auto_renew": subscription.auto_renew,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@superadmin_required
@require_POST
def admin_package_toggle(request, package_id):
    """Toggle package active status"""
    try:
        from main.models import Package as AdPackage

        package = get_object_or_404(AdPackage, id=package_id)

        # If trying to activate the package, check if it has associated payments
        if not package.is_active:  # Will be activated
            # Check if any users have purchased this package
            user_packages_count = UserPackage.objects.filter(package=package).count()

            if user_packages_count == 0:
                # No purchases yet - allow activation (it's a new package being made available)
                package.is_active = True
                message = _("تم تفعيل الباقة")
            else:
                # Has purchases - verify at least one payment exists
                paid_packages = UserPackage.objects.filter(
                    package=package,
                    payment__isnull=False,
                    payment__status=Payment.PaymentStatus.COMPLETED,
                ).exists()

                if paid_packages or user_packages_count > 0:
                    # Has paid users or assigned packages - allow activation
                    package.is_active = True
                    message = _("تم تفعيل الباقة")
                else:
                    # Has users but no completed payments - warning
                    package.is_active = True
                    message = _(
                        "تم تفعيل الباقة - تنبيه: لا توجد مدفوعات مكتملة لهذه الباقة"
                    )
        else:
            # Deactivating package
            package.is_active = False
            message = _("تم تعطيل الباقة")

        package.save(update_fields=["is_active"])

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "is_active": package.is_active,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@superadmin_required
@require_POST
def admin_member_cancel(request, member_id):
    """Cancel a premium membership"""
    try:
        from main.models import UserSubscription

        # Assuming member_id refers to a UserSubscription
        subscription = get_object_or_404(UserSubscription, id=member_id)
        subscription.is_active = False
        subscription.auto_renew = False
        subscription.save(update_fields=["is_active", "auto_renew"])

        return JsonResponse(
            {
                "success": True,
                "message": _("تم إلغاء العضوية المميزة بنجاح"),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ========== Custom Error Handlers ==========


def custom_404(request, exception=None):
    """Custom 404 error page"""
    import logging

    logger = logging.getLogger(__name__)

    # Log the 404 error for debugging
    path = request.get_full_path()
    logger.info(
        f"404 error for path: {path}, exception: {exception}, IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
    )

    # Check if this is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse

        return JsonResponse({"error": "Page not found"}, status=404)

    return render(request, "404.html", status=404)


def custom_500(request):
    """Custom 500 error page"""
    import logging
    import traceback

    logger = logging.getLogger(__name__)

    # Log the 500 error with full traceback
    path = request.get_full_path() if hasattr(request, "get_full_path") else "unknown"
    logger.error(
        f"500 error for path: {path}, IP: {request.META.get('REMOTE_ADDR', 'unknown') if hasattr(request, 'META') else 'unknown'}"
    )
    logger.error(f"500 error traceback: {traceback.format_exc()}")

    # Check if this is an AJAX request
    if (
        hasattr(request, "headers")
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        from django.http import JsonResponse

        return JsonResponse({"error": "Internal server error"}, status=500)

    return render(request, "500.html", status=500)


class AdminReportsView(SuperadminRequiredMixin, TemplateView):
    """
    Admin reports view with comprehensive statistics.
    Includes visitor stats, user stats, ad stats, revenue, etc.
    """

    template_name = "admin_dashboard/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "reports"

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        year_ago = now - timedelta(days=365)

        # Visitor Statistics (using Visitor model)
        from .models import Visitor

        online_threshold = now - timedelta(minutes=15)
        context["online_now"] = Visitor.objects.filter(
            last_activity__gte=online_threshold
        ).count()
        context["visitors_today"] = Visitor.objects.filter(
            first_visit__gte=today_start
        ).count()
        context["visitors_week"] = Visitor.objects.filter(
            first_visit__gte=week_ago
        ).count()
        context["visitors_month"] = Visitor.objects.filter(
            first_visit__gte=month_ago
        ).count()
        context["visitors_year"] = Visitor.objects.filter(
            first_visit__gte=year_ago
        ).count()
        context["visitors_total"] = Visitor.objects.count()

        # User Statistics
        context["total_users"] = User.objects.count()
        context["verified_users"] = User.objects.filter(is_mobile_verified=True).count()
        context["new_users_today"] = User.objects.filter(
            date_joined__gte=today_start
        ).count()
        context["new_users_week"] = User.objects.filter(
            date_joined__gte=week_ago
        ).count()

        # Ads Statistics
        context["total_ads"] = ClassifiedAd.objects.count()
        context["active_ads"] = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.ACTIVE
        ).count()
        context["pending_ads"] = ClassifiedAd.objects.filter(
            status=ClassifiedAd.AdStatus.PENDING
        ).count()
        context["ads_today"] = ClassifiedAd.objects.filter(
            created_at__gte=today_start
        ).count()

        # Categories Statistics with ads count
        total_ads_count = context["total_ads"] or 1  # Avoid division by zero
        categories_stats = []
        for category in Category.objects.filter(parent__isnull=True):
            ads_count = ClassifiedAd.objects.filter(
                Q(category=category)
                | Q(category__parent=category)
                | Q(category__parent__parent=category)
            ).count()
            total_views = (
                ClassifiedAd.objects.filter(
                    Q(category=category)
                    | Q(category__parent=category)
                    | Q(category__parent__parent=category)
                ).aggregate(total=Sum("views_count"))["total"]
                or 0
            )

            categories_stats.append(
                {
                    "name": category.name_ar if category.name_ar else category.name,
                    "ads_count": ads_count,
                    "total_views": total_views,
                    "percentage": (
                        (ads_count / total_ads_count) * 100
                        if total_ads_count > 0
                        else 0
                    ),
                }
            )

        context["categories_stats"] = sorted(
            categories_stats, key=lambda x: x["ads_count"], reverse=True
        )[
            :10
        ]  # Top 10 categories

        # Revenue Statistics (from payments)
        context["revenue_today"] = (
            Payment.objects.filter(
                status="completed", created_at__gte=today_start
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        context["revenue_week"] = (
            Payment.objects.filter(
                status="completed", created_at__gte=week_ago
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        context["revenue_month"] = (
            Payment.objects.filter(
                status="completed", created_at__gte=month_ago
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        context["revenue_total"] = (
            Payment.objects.filter(status="completed").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        return context


@require_POST
def newsletter_subscribe(request):
    """Handle newsletter subscription requests"""
    from .models import NewsletterSubscriber

    email = request.POST.get("email", "").strip().lower()

    if not email:
        return JsonResponse(
            {"success": False, "message": _("يرجى إدخال البريد الإلكتروني")}, status=400
        )

    # Validate email format
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse(
            {"success": False, "message": _("البريد الإلكتروني غير صالح")}, status=400
        )

    # Get client IP and user agent
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    ip_address = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    # Check if already subscribed
    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={
            "ip_address": ip_address,
            "user_agent": user_agent,
        },
    )

    if created:
        return JsonResponse(
            {"success": True, "message": _("تم الاشتراك بنجاح! شكراً لك")}
        )
    else:
        if subscriber.is_active:
            return JsonResponse(
                {"success": False, "message": _("أنت مشترك بالفعل في نشرتنا البريدية")},
                status=400,
            )
        else:
            # Reactivate subscription
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
            subscriber.save()
            return JsonResponse(
                {"success": True, "message": _("تم إعادة تفعيل اشتراكك بنجاح!")}
            )


@require_http_methods(["GET"])
def newsletter_unsubscribe(request, email):
    """Handle newsletter unsubscribe requests"""
    from .models import NewsletterSubscriber

    try:
        subscriber = NewsletterSubscriber.objects.get(email=email, is_active=True)
        subscriber.unsubscribe()
        messages.success(request, _("تم إلغاء الاشتراك بنجاح"))
    except NewsletterSubscriber.DoesNotExist:
        messages.info(request, _("هذا البريد الإلكتروني غير مشترك"))

    return redirect("home")


class PublisherSettingsView(LoginRequiredMixin, TemplateView):
    """Publisher settings page with profile, notifications, and security settings"""

    template_name = "dashboard/publisher_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "settings"
        context["page_title"] = _("الإعدادات")
        context["user"] = self.request.user
        return context


@login_required
@require_POST
def publisher_update_profile(request):
    """Update publisher profile information"""
    user = request.user

    try:
        # Update basic profile info
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.phone = request.POST.get("phone", "").strip()
        user.mobile = request.POST.get("mobile", "").strip()
        user.whatsapp = request.POST.get("whatsapp", "").strip()
        user.bio = request.POST.get("bio", "").strip()
        user.bio_ar = request.POST.get("bio_ar", "").strip()
        user.city = request.POST.get("city", "").strip()
        user.country = request.POST.get("country", "").strip()
        user.address = request.POST.get("address", "").strip()

        # Update company info if provided
        user.company_name = request.POST.get("company_name", "").strip()
        user.company_name_ar = request.POST.get("company_name_ar", "").strip()

        # Handle avatar upload
        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]

        user.save()

        return JsonResponse(
            {"success": True, "message": _("تم تحديث الملف الشخصي بنجاح")}
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ أثناء تحديث الملف الشخصي")},
            status=400,
        )


@login_required
@require_POST
def publisher_update_notifications(request):
    """Update publisher notification preferences"""
    user = request.user

    try:
        user.email_notifications = request.POST.get("email_notifications") == "true"
        user.save()

        return JsonResponse(
            {"success": True, "message": _("تم تحديث إعدادات الإشعارات بنجاح")}
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ أثناء تحديث إعدادات الإشعارات")},
            status=400,
        )


@login_required
@require_POST
def publisher_change_password(request):
    """Change publisher password"""
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    user = request.user
    current_password = request.POST.get("current_password", "")
    new_password = request.POST.get("new_password", "")
    confirm_password = request.POST.get("confirm_password", "")

    # Verify current password
    if not user.check_password(current_password):
        return JsonResponse(
            {"success": False, "message": _("كلمة المرور الحالية غير صحيحة")},
            status=400,
        )

    # Check if new passwords match
    if new_password != confirm_password:
        return JsonResponse(
            {"success": False, "message": _("كلمات المرور الجديدة غير متطابقة")},
            status=400,
        )

    # Validate new password
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return JsonResponse(
            {"success": False, "message": ", ".join(e.messages)}, status=400
        )

    # Update password
    user.set_password(new_password)
    user.save()

    # Keep the user logged in after password change
    update_session_auth_hash(request, user)

    return JsonResponse({"success": True, "message": _("تم تغيير كلمة المرور بنجاح")})


@login_required
@require_POST
def publisher_update_email(request):
    """Update publisher email address"""
    user = request.user
    new_email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")

    # Verify password
    if not user.check_password(password):
        return JsonResponse(
            {"success": False, "message": _("كلمة المرور غير صحيحة")}, status=400
        )

    # Validate email
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(new_email)
    except ValidationError:
        return JsonResponse(
            {"success": False, "message": _("البريد الإلكتروني غير صالح")}, status=400
        )

    # Check if email already exists
    if User.objects.filter(email=new_email).exclude(id=user.id).exists():
        return JsonResponse(
            {"success": False, "message": _("هذا البريد الإلكتروني مستخدم بالفعل")},
            status=400,
        )

    user.email = new_email
    user.save()

    return JsonResponse(
        {"success": True, "message": _("تم تحديث البريد الإلكتروني بنجاح")}
    )


@login_required
@require_POST
def publisher_delete_account(request):
    """Delete publisher account (soft delete)"""
    user = request.user
    password = request.POST.get("password", "")

    # Verify password
    if not user.check_password(password):
        return JsonResponse(
            {"success": False, "message": _("كلمة المرور غير صحيحة")}, status=400
        )

    # Deactivate user account
    user.is_active = False
    user.save()

    # Log out the user
    from django.contrib.auth import logout

    logout(request)

    return JsonResponse(
        {
            "success": True,
            "message": _("تم حذف الحساب بنجاح"),
            "redirect": reverse("main:home"),
        }
    )


class AdminReportsManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view for managing user reports"""

    model = AdReport
    template_name = "admin_dashboard/user_reports.html"
    context_object_name = "reports"
    paginate_by = 20

    def test_func(self):
        """Only superusers can access"""
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = (
            AdReport.objects.all()
            .select_related("reporter", "reported_ad", "reported_user", "reviewed_by")
            .order_by("-created_at")
        )

        # Filter by status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Filter by report type
        report_type = self.request.GET.get("report_type")
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        # Search in description
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(description__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add statistics
        context["pending_count"] = AdReport.objects.filter(status="pending").count()
        context["reviewing_count"] = AdReport.objects.filter(status="reviewing").count()
        context["resolved_count"] = AdReport.objects.filter(status="resolved").count()
        context["rejected_count"] = AdReport.objects.filter(status="rejected").count()

        return context
