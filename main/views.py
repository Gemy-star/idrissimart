from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models, transaction
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
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
    AboutPage,
    AdFeature,
    Category,
    ClassifiedAd,
    ContactInfo,
    AdPackage,
    CartSettings,
)
from main.templatetags.idrissimart_tags import phone_format
from main.utils import get_selected_country_from_request


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        # Fallback: If there are no featured ads, show the latest ads instead.
        if not featured_ads.exists():
            featured_ads = latest_ads

        context["selected_country"] = selected_country
        context["categories_by_section"] = categories_by_section
        context["latest_ads"] = latest_ads
        context["featured_ads"] = featured_ads
        # Add latest blogs to the context
        context["latest_blogs"] = (
            Blog.objects.filter(is_published=True)
            .order_by("-published_date")
            .select_related("author")[:3]
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

        # Apply category filtering - supports main, sub, and sub-sub categories
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

        # Get selected country
        selected_country = get_selected_country_from_request(self.request)

        # Get categories by section with content counts (generic approach)
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
            "section": self.request.GET.get("section", "all"),
            "min_price": self.request.GET.get("min_price", ""),
            "max_price": self.request.GET.get("max_price", ""),
            "sort": self.request.GET.get("sort", "-created_at"),
        }

        # Calculate statistics based on content type
        total_items = self.get_queryset().count()
        section_type_value = self._get_section_type_from_string(content_type)
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

        # Get all active categories for the category filter dropdown
        all_categories = Category.objects.filter(
            is_active=True,
            section_type=section_type_value or Category.SectionType.CLASSIFIED,
        ).order_by("name")

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

        # Optional: Store in user profile if authenticated
        if request.user.is_authenticated:
            request.user.profile.country = country
            request.user.profile.save()

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
        context = super().get_context_data(**kwargs)

        # Get about page content
        about_content = AboutPage.get_active_content()
        if not about_content:
            # Create default content if none exists
            about_content = AboutPage.objects.create(
                title="إدريسي مارت",
                tagline="تميّزك… ملموس",
                subtitle="منصتك للتجارة الإلكترونية المتكاملة",
                who_we_are_content="""
                منصة <strong>إدريسي مارت</strong> هي منصة سعودية متخصصة في التجارة الإلكترونية المتكاملة،
                تأسست لتجمع بين البائعين المعتمدين والمشترين في سوق واحد متنوع.

                نهدف إلى تسهيل تجربة التسوق والبيع من خلال منصة موحدة تضم تنوعاً كبيراً من المنتجات والخدمات،
                وتدعم البائعين المحليين للوصول إلى جمهور أوسع.

                نعتز بانطلاقنا من قلب المملكة، لنكون المنصة التي تجمع الإبداع المحلي بروح التطور العالمي
                في عالم التجارة الإلكترونية.
                """,
                vision_content="""
                أن نكون المنصة السعودية الرائدة في التجارة الإلكترونية المتكاملة،
                التي تُلهم وتُبرز التميّز في كل قطاع وخدمة.
                """,
                mission_content="""
                نحوّل أفكار التجارة والخدمات إلى تجارب رقمية متكاملة تعبّر عن الجودة،
                وتبني أقوى الروابط بين البائعين والعملاء في المملكة.
                """,
            )

        context["about_content"] = about_content
        context["page_title"] = _("من نحن - إدريسي مارت")
        context["meta_description"] = _("تعرف على منصة إدريسي مارت ورؤيتنا ورسالتنا")

        return context


class ContactView(TemplateView):
    """Contact page view with form handling"""

    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        from constance import config

        context = super().get_context_data(**kwargs)

        # Get contact information
        contact_info = ContactInfo.get_active_info()
        if not contact_info:
            # Create default contact info if none exists
            contact_info = ContactInfo.objects.create(
                phone="+966 11 123 4567",
                email="info@idrissimart.com",
                address="الرياض، المملكة العربية السعودية",
                whatsapp="+966 50 123 4567",
                map_embed_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3620.059022564443!2d46.71516947512605!3d24.7038092779999!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3e2f05072c84c457%3A0xf45cf328d8856bac!2z2KfZhNi52YbYqSDYp9mE2KfYsdiz2YrYp9mEINin2YTYrNix2KfYtNmK2Kkg2YTZhNmF2YrYp9ix2KfYqiDYp9mE2YXYrdmK2KfYqiDYp9mE2KfZhNiz2KfZhdi52Kkg!5e0!3m2!1sar!2ssa!4v1728780637482!5m2!1sar!2ssa",
            )

        # Initialize contact form
        form = ContactForm(
            user=self.request.user if self.request.user.is_authenticated else None
        )

        context["contact_info"] = contact_info
        context["form"] = form
        context["config"] = config
        context["page_title"] = _("اتصل بنا - إدريسي مارت")
        context["meta_description"] = _("تواصل معنا في إدريسي مارت")

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

        context = super().get_context_data(**kwargs)
        context["config"] = config
        return context


class TermsConditionsView(TemplateView):
    """Terms and conditions page view"""

    template_name = "pages/terms.html"

    def get_context_data(self, **kwargs):
        from constance import config

        context = super().get_context_data(**kwargs)
        context["config"] = config
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
                "message": _("Item added to cart"),
                "cart_count": len(cart),
            }
        )

    return JsonResponse({"success": False, "message": _("Item already in cart")})


@login_required
@require_POST
def add_to_wishlist(request):
    """Add item to wishlist"""
    item_id = request.POST.get("item_id")

    if not item_id:
        return JsonResponse(
            {"success": False, "message": _("Item ID required")}, status=400
        )

    wishlist = request.session.get("wishlist", [])

    if item_id not in wishlist:
        wishlist.append(item_id)
        request.session["wishlist"] = wishlist
        request.session.modified = True

        return JsonResponse(
            {
                "success": True,
                "message": _("Item added to wishlist"),
                "wishlist_count": len(wishlist),
            }
        )

    return JsonResponse({"success": False, "message": _("Item already in wishlist")})


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
                "message": _("Item removed from cart"),
                "cart_count": len(cart),
            }
        )

    return JsonResponse({"success": False, "message": _("Item not in cart")})


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
                "message": _("Item removed from wishlist"),
                "wishlist_count": len(wishlist),
            }
        )

    return JsonResponse({"success": False, "message": _("Item not in wishlist")})


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

        # Increment view count without triggering a full save/update_fields
        ClassifiedAd.objects.filter(pk=ad.pk).update(
            views_count=models.F("views_count") + 1
        )

        # Prepare custom fields with labels for clean display in the template
        custom_fields_with_labels = []
        if ad.category.custom_field_schema and ad.custom_fields:
            schema = ad.category.custom_field_schema
            for field_schema in schema:
                field_name = field_schema.get("name")
                value = ad.custom_fields.get(field_name)

                # Only show fields that have a value
                if value is not None and value != "":
                    custom_fields_with_labels.append(
                        {
                            "label": field_schema.get("label", field_name),
                            "value": value,
                            "type": field_schema.get("type", "text"),
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

        context["page_title"] = f"{ad.title} - {ad.category.name}"
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

        return context

    def get_form_kwargs(self):
        """Pass the selected category to the form if available."""
        kwargs = super().get_form_kwargs()
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
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            messages.success(self.request, _("Your ad has been submitted for review!"))
            return super().form_valid(form)
        else:
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
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.save()
            messages.success(self.request, _("Your ad has been updated successfully!"))
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
            return JsonResponse({"error": "Category ID is required"}, status=400)

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
            return JsonResponse({"error": "Category not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def get_category_stats(request):
    """AJAX endpoint to fetch category statistics"""
    if request.method == "GET":
        category_id = request.GET.get("category_id")

        if not category_id:
            return JsonResponse({"error": "Category ID is required"}, status=400)

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
            return JsonResponse({"error": "Category not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def enhanced_ad_create_view(request):
    """Simple enhanced ad creation view"""

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
    return render(request, "classifieds/ad_creation_success.html")


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
        return JsonResponse({"error": "Category not found"}, status=404)


def enhanced_ad_creation_success_view(request, ad_id=None):
    """Enhanced success view"""
    context = {}
    if ad_id:
        try:
            ad = ClassifiedAd.objects.get(id=ad_id, user=request.user)
            context["ad"] = ad
        except ClassifiedAd.DoesNotExist:
            pass
    return render(request, "classifieds/ad_creation_success.html", context)


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
        return JsonResponse({"error": "Category not found"}, status=404)


def check_ad_allowance(request):
    """AJAX view to check if user can post ads"""
    if not request.user.is_authenticated:
        return JsonResponse({"allowed": False, "reason": "not_authenticated"})

    if not request.user.is_email_verified:
        return JsonResponse({"allowed": False, "reason": "email_not_verified"})

    # Check package limits
    user_settings = getattr(request.user, "cart_settings", None)
    if user_settings and user_settings.current_package:
        package = user_settings.current_package
        if user_settings.used_ads >= package.max_ads:
            return JsonResponse(
                {
                    "allowed": False,
                    "reason": "package_limit_reached",
                    "used_ads": user_settings.used_ads,
                    "max_ads": package.max_ads,
                }
            )

    return JsonResponse(
        {
            "allowed": True,
            "used_ads": user_settings.used_ads if user_settings else 0,
            "max_ads": (
                user_settings.current_package.max_ads
                if user_settings and user_settings.current_package
                else 3
            ),
        }
    )


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
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dashboard statistics
        user_ads = ClassifiedAd.objects.filter(user=self.request.user)
        context["dashboard_stats"] = {
            "total_ads": user_ads.count(),
            "active_ads": user_ads.filter(status=ClassifiedAd.AdStatus.ACTIVE).count(),
            "pending_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.PENDING
            ).count(),
            "expired_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.EXPIRED
            ).count(),
            "total_views": user_ads.aggregate(total=models.Sum("views_count"))["total"]
            or 0,
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

        return context


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
                status_text = _("مخفي")
                action = "hidden"
            elif ad.status == ClassifiedAd.AdStatus.DRAFT:
                ad.status = ClassifiedAd.AdStatus.ACTIVE
                status_text = _("نشط")
                action = "shown"
            else:
                return JsonResponse(
                    {"success": False, "message": _("لا يمكن تغيير حالة هذا الإعلان")}
                )

            ad.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم تحديث حالة الإعلان بنجاح"),
                    "new_status": ad.status,
                    "status_text": status_text,
                    "action": action,
                }
            )

        except Exception:
            return JsonResponse(
                {"success": False, "message": _("حدث خطأ أثناء تحديث حالة الإعلان")}
            )

    return JsonResponse({"success": False, "message": _("طلب غير صحيح")})


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
                    "message": _("تم حذف الإعلان '{}' بنجاح").format(ad_title),
                }
            )

        except Exception:
            return JsonResponse(
                {"success": False, "message": _("حدث خطأ أثناء حذف الإعلان")}
            )

    return JsonResponse({"success": False, "message": _("طلب غير صحيح")})


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
            {"success": False, "message": _("حدث خطأ أثناء تحميل تفاصيل الإعلان")}
        )


# ============================================================================
# ADMIN DASHBOARD VIEWS
# ============================================================================

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User as DjangoUser
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
                Q(is_in_cart=True) | Q(cart_settings__isnull=False)
            ).count(),
            # User Statistics
            "total_users": User.objects.count(),
            "new_users_week": User.objects.filter(date_joined__gte=week_ago).count(),
            "verified_users": User.objects.filter(
                Q(userprofile__is_person_verified=True)
                | Q(userprofile__is_company_verified=True)
            ).count(),
            # Category Statistics
            "total_categories": Category.objects.filter(parent__isnull=True).count(),
            "total_subcategories": Category.objects.filter(
                parent__isnull=False
            ).count(),
            # Revenue Statistics (if payment system exists)
            "premium_members": User.objects.filter(
                # Assuming premium membership field exists
                # userprofile__is_premium=True
            ).count(),
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

    def get_recent_ads(self):
        """Get recent ads for admin review"""
        return (
            ClassifiedAd.objects.select_related("user", "category", "country")
            .prefetch_related("images")
            .order_by("-created_at")[:10]
        )

    def get_recent_users(self):
        """Get recently registered users"""
        return User.objects.select_related("userprofile").order_by("-date_joined")[:10]

    def get_system_metrics(self):
        """Get system performance metrics"""
        return {
            "avg_ads_per_user": ClassifiedAd.objects.count()
            / max(User.objects.count(), 1),
            "most_popular_category": Category.objects.annotate(ad_count=Count("ads"))
            .order_by("-ad_count")
            .first(),
            "countries_count": Country.objects.count(),
            "features_count": AdFeature.objects.count(),
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
                .prefetch_related("children")
                .annotate(ad_count=Count("ads"), subcategory_count=Count("children")),
            }

        context["categories_by_section"] = categories_by_section
        context["countries"] = Country.objects.all()

        return context


class AdminAdsManagementView(SuperadminRequiredMixin, TemplateView):
    """
    Admin interface for comprehensive ads management with tabs
    Restricted to superusers only
    """

    template_name = "admin_dashboard/ads_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get ad counts for each tab
        context["tab_counts"] = {
            "active": ClassifiedAd.objects.filter(status="active").count(),
            "pending": ClassifiedAd.objects.filter(status="pending").count(),
            "expired": ClassifiedAd.objects.filter(status="expired").count(),
            "hidden": ClassifiedAd.objects.filter(status="draft").count(),
            "cart": ClassifiedAd.objects.filter(
                Q(is_in_cart=True) | Q(cart_settings__isnull=False)
            ).count(),
        }

        # Get default tab data (active ads)
        context["ads"] = self.get_ads_by_status("active")
        context["current_tab"] = "active"
        context["categories"] = Category.objects.filter(parent__isnull=True)
        context["countries"] = Country.objects.all()

        return context

    def get_ads_by_status(self, status):
        """Get ads filtered by status"""
        queryset = ClassifiedAd.objects.select_related(
            "user", "category", "country"
        ).prefetch_related("images")

        if status == "active":
            return queryset.filter(status="active")
        elif status == "pending":
            return queryset.filter(status="pending")
        elif status == "expired":
            return queryset.filter(status="expired")
        elif status == "hidden":
            return queryset.filter(status="draft")
        elif status == "cart":
            return queryset.filter(Q(is_in_cart=True) | Q(cart_settings__isnull=False))

        return queryset.none()


class AdminSettingsView(SuperadminRequiredMixin, View):
    """
    Admin system settings and configurations with form handling
    Restricted to superusers only
    """

    def get(self, request):
        # Get current system settings
        context = {
            "system_settings": {
                "publishing_mode": "direct",  # or 'review' - from settings
                "allow_guest_viewing": True,
                "allow_guest_contact": False,
                "delivery_service_enabled": True,
                "cart_system_enabled": True,
                "auto_approval_verified_users": True,
                "verified_auto_publish": True,
                "members_only_contact": True,
                "members_only_messaging": True,
                "delivery_requires_approval": True,
                "cart_by_main_category": False,
                "cart_by_subcategory": True,
                "cart_per_ad": True,
                "default_reservation_percentage": 20,
                "min_reservation_amount": 50,
                "max_reservation_amount": 5000,
                "delivery_fee_percentage": 5,
                "delivery_fee_min": 10,
                "delivery_fee_max": 500,
                "notify_admin_new_ads": True,
                "notify_admin_pending_review": True,
                "notify_admin_new_users": True,
                "notify_admin_payments": True,
                "admin_notification_email": request.user.email,
                "site_name_in_emails": "إدريسي مارت",
                "ads_notification_frequency": "hourly",
                "stats_report_frequency": "daily",
            },
            "delivery_terms": {
                "arabic": "شروط التوصيل والتحصيل باللغة العربية",
                "english": "Delivery and collection terms in English",
            },
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
    template_name = "admin_dashboard/payments.html"

    def get_context_data(self, **kwargs):
        from django.db.models import Sum, Count, Q
        from django.utils import timezone
        from datetime import datetime, timedelta

        context = super().get_context_data(**kwargs)

        # Payment statistics
        total_payments = 0  # TODO: Get from payment model
        monthly_revenue = 0  # TODO: Calculate monthly revenue
        pending_payments = 0  # TODO: Count pending payments

        # Premium members statistics
        total_premium_members = User.objects.filter(
            # userprofile__is_premium=True  # Uncomment when userprofile exists
        ).count()
        active_premium_members = (
            total_premium_members  # TODO: Filter active memberships
        )

        context["payment_stats"] = {
            "total_transactions": total_payments,
            "total_revenue": monthly_revenue,
            "premium_members": total_premium_members,
            "pending_payments": pending_payments,
            "active_premium_members": active_premium_members,
        }

        # Recent transactions (mock data for now)
        context["recent_transactions"] = []  # TODO: Get from payment model

        # Monthly revenue chart data
        monthly_data = []
        for i in range(6):
            month = timezone.now() - timedelta(days=30 * i)
            monthly_data.append(
                {
                    "month": month.strftime("%Y-%m"),
                    "revenue": 0,  # TODO: Calculate actual revenue
                }
            )
        context["monthly_data"] = monthly_data

        # Premium membership packages
        context["membership_packages"] = [
            {
                "id": 1,
                "name": "الباقة الذهبية",
                "price": 99,
                "duration": 30,
                "features": ["إعلانات مميزة", "دعم فوري", "إحصائيات متقدمة"],
                "subscribers": 0,
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
                "subscribers": 0,
                "is_active": True,
            },
        ]

        # Premium members
        context["premium_members"] = User.objects.select_related(
            # 'userprofile'  # Uncomment when userprofile exists
        ).filter(
            # userprofile__is_premium=True  # Uncomment when userprofile exists
        )[
            :20
        ]

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
@require_POST
def admin_ad_delete(request, ad_id):
    """Delete ad from admin panel"""
    try:
        ad = get_object_or_404(ClassifiedAd, pk=ad_id)
        ad_title = ad.title
        ad.delete()

        return JsonResponse(
            {"success": True, "message": f'تم حذف الإعلان "{ad_title}" بنجاح'}
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"حدث خطأ أثناء حذف الإعلان: {str(e)}"}
        )


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
                Q(is_in_cart=True) | Q(cart_settings__isnull=False)
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
        return JsonResponse({"success": False, "message": f"حدث خطأ: {str(e)}"})


# Settings AJAX Endpoints


@superadmin_required
@require_POST
def admin_settings_get(request):
    """Get current system settings"""
    try:
        # TODO: Get actual settings from database
        settings = {
            "publishing_mode": "direct",
            "verified_auto_publish": True,
            "allow_guest_viewing": True,
            "allow_guest_contact": False,
            "members_only_contact": True,
            "members_only_messaging": True,
            "delivery_service_enabled": True,
            "delivery_requires_approval": True,
            "cart_system_enabled": True,
        }

        return JsonResponse({"success": True, "settings": settings})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"حدث خطأ: {str(e)}"})


@superadmin_required
@require_POST
def admin_settings_publishing(request):
    """Save publishing settings"""
    try:
        # TODO: Save actual settings to database
        publishing_mode = request.POST.get("publishing_mode")
        verified_auto_publish = request.POST.get("verified_auto_publish") == "on"
        allow_guest_viewing = request.POST.get("allow_guest_viewing") == "on"
        allow_guest_contact = request.POST.get("allow_guest_contact") == "on"
        members_only_contact = request.POST.get("members_only_contact") == "on"
        members_only_messaging = request.POST.get("members_only_messaging") == "on"

        # Here you would save to database/settings

        return JsonResponse({"success": True, "message": "تم حفظ إعدادات النشر بنجاح"})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"حدث خطأ: {str(e)}"})


@superadmin_required
@require_POST
def admin_settings_delivery(request):
    """Save delivery settings"""
    try:
        # TODO: Save actual settings to database
        delivery_service_enabled = request.POST.get("delivery_service_enabled") == "on"
        delivery_requires_approval = (
            request.POST.get("delivery_requires_approval") == "on"
        )
        delivery_terms_ar = request.POST.get("delivery_terms_ar")
        delivery_terms_en = request.POST.get("delivery_terms_en")
        delivery_fee_percentage = request.POST.get("delivery_fee_percentage")
        delivery_fee_min = request.POST.get("delivery_fee_min")
        delivery_fee_max = request.POST.get("delivery_fee_max")

        # Here you would save to database/settings

        return JsonResponse(
            {"success": True, "message": "تم حفظ إعدادات التوصيل بنجاح"}
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": f"حدث خطأ: {str(e)}"})


@superadmin_required
@require_POST
def admin_settings_cart(request):
    """Save cart settings"""
    try:
        # TODO: Save actual settings to database
        cart_system_enabled = request.POST.get("cart_system_enabled") == "on"
        cart_by_main_category = request.POST.get("cart_by_main_category") == "on"
        cart_by_subcategory = request.POST.get("cart_by_subcategory") == "on"
        cart_per_ad = request.POST.get("cart_per_ad") == "on"
        default_reservation_percentage = request.POST.get(
            "default_reservation_percentage"
        )
        min_reservation_amount = request.POST.get("min_reservation_amount")
        max_reservation_amount = request.POST.get("max_reservation_amount")

        # Here you would save to database/settings

        return JsonResponse({"success": True, "message": "تم حفظ إعدادات السلة بنجاح"})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"حدث خطأ: {str(e)}"})


@superadmin_required
@require_POST
def admin_settings_notifications(request):
    """Save notification settings"""
    try:
        # TODO: Save actual settings to database
        notify_admin_new_ads = request.POST.get("notify_admin_new_ads") == "on"
        notify_admin_pending_review = (
            request.POST.get("notify_admin_pending_review") == "on"
        )
        notify_admin_new_users = request.POST.get("notify_admin_new_users") == "on"
        notify_admin_payments = request.POST.get("notify_admin_payments") == "on"
        admin_notification_email = request.POST.get("admin_notification_email")
        site_name_in_emails = request.POST.get("site_name_in_emails")
        ads_notification_frequency = request.POST.get("ads_notification_frequency")
        stats_report_frequency = request.POST.get("stats_report_frequency")

        # Here you would save to database/settings

        return JsonResponse(
            {"success": True, "message": "تم حفظ إعدادات الإشعارات بنجاح"}
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": f"حدث خطأ: {str(e)}"})


@login_required
def dashboard_redirect(request):
    """
    Smart dashboard redirect based on user role:
    - Superusers/Staff -> Admin Dashboard
    - Users with ads -> Publisher Dashboard (My Ads)
    - Regular users -> Home page
    """
    user = request.user

    # Redirect admins to admin dashboard
    if user.is_superuser or user.is_staff:
        return redirect("main:admin_dashboard")

    # Check if user has posted any ads
    user_has_ads = ClassifiedAd.objects.filter(user=user).exists()

    if user_has_ads:
        # Redirect to publisher dashboard (their ads list)
        return redirect("main:my_ads")

    # Default redirect for users without ads
    return redirect("main:home")
