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
    Enhanced Categories View with Classified Ads Integration and Filtering
    """

    model = ClassifiedAd
    filterset_class = ClassifiedAdFilter
    template_name = "pages/categories.html"
    context_object_name = "ads"
    paginate_by = 12

    def get_queryset(self):
        """
        Get classified ads with filtering support
        """
        # Get selected country from middleware/utility function
        selected_country = get_selected_country_from_request(self.request)

        # Start with active ads for the selected country
        queryset = (
            ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.ACTIVE,
                country__code=selected_country,
            )
            .select_related("user", "category", "country")
            .prefetch_related("images", "features")
            .order_by("-created_at")
        )

        # Apply category filtering if specified
        category_slug = self.request.GET.get("category")
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
                descendants = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=descendants)
            except Category.DoesNotExist:
                pass

        # Apply section filtering
        section = self.request.GET.get("section")
        if section and section != "all":
            queryset = queryset.filter(category__section_type=section)

        # Apply text search
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search)
                | models.Q(description__icontains=search)
                | models.Q(category__name__icontains=search)
                | models.Q(category__name_ar__icontains=search)
            )

        # Apply price range filtering
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass

        # Apply sorting
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get active section from URL parameter
        active_section = self.request.GET.get("section", "all")

        # Get selected country from middleware/utility function
        selected_country = get_selected_country_from_request(self.request)

        # Get categories by country and section with ad counts
        categories_by_section = self._get_categories_with_ad_counts(
            country_code=selected_country
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

        # Calculate statistics
        total_ads = self.get_queryset().count()
        active_categories = Category.objects.filter(
            is_active=True, section_type=Category.SectionType.CLASSIFIED
        ).count()

        context.update(
            {
                "selected_country": selected_country,
                "categories_by_section": categories_by_section,
                "active_section": active_section,
                "cart_count": cart_count,
                "wishlist_count": wishlist_count,
                "current_filters": current_filters,
                "total_ads": total_ads,
                "active_categories": active_categories,
                "page_title": _("الفئات - إدريسي مارت"),
                "meta_description": _("استكشف جميع فئات منصة إدريسي مارت المتنوعة"),
                "has_filters": any(current_filters.values()),
            }
        )

        return context

    def _get_categories_with_ad_counts(self, country_code=None):
        """
        Enhanced helper function to get categories with their subcategories and ad counts
        """
        # Get main categories (parent categories)
        main_categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True,
            section_type=Category.SectionType.CLASSIFIED,
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

            # Count active ads for this category and its descendants
            descendants = category.get_descendants(include_self=True)
            ads_count = ClassifiedAd.objects.filter(
                category__in=descendants,
                status=ClassifiedAd.AdStatus.ACTIVE,
                country__code=country_code,
            ).count()

            # Add subcategory ad counts
            subcategory_data = []
            for subcat in subcategories:
                subcat_descendants = subcat.get_descendants(include_self=True)
                subcat_ads_count = ClassifiedAd.objects.filter(
                    category__in=subcat_descendants,
                    status=ClassifiedAd.AdStatus.ACTIVE,
                    country__code=country_code,
                ).count()
                subcategory_data.append(
                    {"category": subcat, "ads_count": subcat_ads_count}
                )

            categories_by_section[section].append(
                {
                    "category": category,
                    "subcategories": subcategory_data,
                    "ads_count": ads_count,
                }
            )

        return categories_by_section


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

        # Apply phone formatting
        contact_info.formatted_phone = phone_format(contact_info.phone)
        contact_info.formatted_whatsapp = phone_format(contact_info.whatsapp)

        # Initialize contact form
        form = ContactForm(
            user=self.request.user if self.request.user.is_authenticated else None
        )

        context["contact_info"] = contact_info
        context["form"] = form
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
