from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, F, IntegerField, Value, When
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_filters.views import FilterView

from .filters import ClassifiedAdFilter
from .forms import AdImageFormSet, ClassifiedAdForm
from .models import (
    AdImage,
    AdPackage,
    AdReview,
    Category,
    ClassifiedAd,
    Notification,
    SavedSearch,
    User,
    UserPackage,
)
from .utils import get_selected_country_from_request


class ClassifiedAdListView(FilterView):
    """
    A view for listing and filtering classified ads.
    """

    model = ClassifiedAd
    filterset_class = ClassifiedAdFilter
    template_name = "classifieds/ad_list.html"
    context_object_name = "ads"
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        """Check if guests are allowed to view ads."""
        from constance import config

        # If user is not authenticated and guest viewing is disabled
        if not request.user.is_authenticated and not getattr(
            config, "ALLOW_GUEST_VIEWING", True
        ):
            from django.contrib import messages
            from django.utils.translation import gettext as _

            messages.warning(request, _("يجب عليك تسجيل الدخول لمشاهدة الإعلانات"))
            from django.shortcuts import redirect

            return redirect("main:login")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Start with only active ads for the selected country
        selected_country = get_selected_country_from_request(self.request)
        queryset = ClassifiedAd.objects.active_for_country(selected_country)

        # Apply custom field filters if provided
        for key, value in self.request.GET.items():
            if key.startswith('cf_') and value:
                field_name = key[3:]  # Remove 'cf_' prefix
                queryset = queryset.filter(**{f'custom_fields__{field_name}__icontains': value})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get custom fields for filtering if category is selected
        category_id = self.request.GET.get('category') or self.request.GET.get('subcategory')
        if category_id:
            from .models import CategoryCustomField

            try:
                category = Category.objects.get(pk=int(category_id))
                # Get all custom fields that should show in filters
                filter_fields = (
                    CategoryCustomField.objects.filter(
                        category=category,
                        show_in_filters=True,
                        is_active=True
                    )
                    .select_related('custom_field')
                    .order_by('order')
                )

                context['category_filter_fields'] = filter_fields
                context['selected_category'] = category
            except (Category.DoesNotExist, ValueError, TypeError):
                pass

        # ── Search context ────────────────────────────────────────────
        from django.utils.translation import gettext as _
        from content.models import Country as ContentCountry

        search_term = self.request.GET.get('search', '').strip()
        context['search_term'] = search_term

        # Build human-readable active-filter chips
        active_filters = []
        params = self.request.GET

        if search_term:
            active_filters.append({'label': _('بحث'), 'value': search_term, 'key': 'search'})

        city_val = params.get('city', '').strip()
        if city_val:
            active_filters.append({'label': _('المدينة'), 'value': city_val, 'key': 'city'})

        country_val = params.get('country', '').strip()
        if country_val:
            try:
                c = ContentCountry.objects.get(pk=country_val)
                active_filters.append({'label': _('الدولة'), 'value': c.name, 'key': 'country'})
            except Exception:
                active_filters.append({'label': _('الدولة'), 'value': country_val, 'key': 'country'})

        if category_id:
            try:
                cat = Category.objects.get(pk=category_id)
                active_filters.append({'label': _('القسم'), 'value': cat.name, 'key': 'category'})
            except Exception:
                pass

        min_price = params.get('min_price', '').strip()
        max_price = params.get('max_price', '').strip()
        if min_price:
            active_filters.append({'label': _('السعر من'), 'value': min_price, 'key': 'min_price'})
        if max_price:
            active_filters.append({'label': _('السعر إلى'), 'value': max_price, 'key': 'max_price'})

        brand_val = params.get('brand', '').strip()
        if brand_val:
            active_filters.append({'label': _('الماركة'), 'value': brand_val, 'key': 'brand'})

        for key, value in params.items():
            if key.startswith('cf_') and value.strip():
                active_filters.append({'label': key[3:].replace('_', ' '), 'value': value, 'key': key})

        context['active_filters'] = active_filters
        context['has_active_filters'] = bool(active_filters)

        # Total count of filtered results (before pagination)
        context['total_results'] = self.object_list.count() if hasattr(self, 'object_list') else 0

        # Pass all root categories for "search by category" quick pick
        context['root_categories'] = Category.objects.filter(
            section_type=Category.SectionType.CLASSIFIED,
            parent__isnull=True,
            is_active=True,
        ).order_by('order', 'name')

        return context


class MyClassifiedAdsView(LoginRequiredMixin, ListView):
    """View to list the current user's classified ads."""

    model = ClassifiedAd
    template_name = "classifieds/my_ads_list.html"
    context_object_name = "ads"
    paginate_by = 20  # 20 ads per page

    def get_queryset(self):
        return ClassifiedAd.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "my_ads"

        # Add statistics
        user_ads = ClassifiedAd.objects.filter(user=self.request.user)
        context["stats"] = {
            "total_ads": user_ads.count(),
            "active_ads": user_ads.filter(status=ClassifiedAd.AdStatus.ACTIVE).count(),
            "pending_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.PENDING
            ).count(),
            "rejected_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.REJECTED
            ).count(),
            "expired_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.EXPIRED
            ).count(),
            "total_views": sum(ad.views_count for ad in user_ads),
            "highlighted_ads": user_ads.filter(is_highlighted=True).count(),
            "pinned_ads": user_ads.filter(is_pinned=True).count(),
            "urgent_ads": user_ads.filter(is_urgent=True).count(),
        }

        # Add user package information
        from django.utils import timezone

        active_packages = (
            UserPackage.objects.filter(
                user=self.request.user, expiry_date__gt=timezone.now()
            )
            .select_related("package")
            .order_by("-expiry_date")
        )

        # Calculate total ads remaining from all active packages
        total_ads_remaining = sum(pkg.ads_remaining for pkg in active_packages)

        context["package_info"] = {
            "total_ads_remaining": total_ads_remaining,
            "active_packages": active_packages,
            "has_active_package": active_packages.exists(),
        }

        return context


class ExpiredAdsView(LoginRequiredMixin, ListView):
    """View to list user's expired classified ads."""

    model = ClassifiedAd
    template_name = "classifieds/expired_ads_list.html"
    context_object_name = "ads"
    paginate_by = 20

    def get_queryset(self):
        return ClassifiedAd.objects.expired_ads(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "expired_ads"
        context["page_title"] = _("إعلاناتي المنتهية")

        # Add expiring soon ads
        context["expiring_soon"] = ClassifiedAd.objects.expiring_soon(
            days=3, user=self.request.user
        )[:5]

        return context


class PublisherReportsView(LoginRequiredMixin, ListView):
    """View to display publisher reports and analytics."""

    model = ClassifiedAd
    template_name = "classifieds/publisher_reports.html"
    context_object_name = "ads"

    def get_queryset(self):
        return ClassifiedAd.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        from django.db.models import Avg, Count, Max, Min, Sum
        from datetime import timedelta

        context = super().get_context_data(**kwargs)
        context["active_nav"] = "statistics"

        user_ads = ClassifiedAd.objects.filter(user=self.request.user)
        now = timezone.now()

        # Overall Statistics
        context["stats"] = {
            "total_ads": user_ads.count(),
            "active_ads": user_ads.filter(status=ClassifiedAd.AdStatus.ACTIVE).count(),
            "pending_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.PENDING
            ).count(),
            "rejected_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.REJECTED
            ).count(),
            "expired_ads": user_ads.filter(
                status=ClassifiedAd.AdStatus.EXPIRED
            ).count(),
            "total_views": user_ads.aggregate(Sum("views_count"))["views_count__sum"]
            or 0,
            "avg_views": user_ads.aggregate(Avg("views_count"))["views_count__avg"]
            or 0,
            "highlighted_ads": user_ads.filter(is_highlighted=True).count(),
            "pinned_ads": user_ads.filter(is_pinned=True).count(),
            "urgent_ads": user_ads.filter(is_urgent=True).count(),
        }

        # This Month Statistics
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_ads = user_ads.filter(created_at__gte=month_start)
        context["month_stats"] = {
            "new_ads": month_ads.count(),
            "views": month_ads.aggregate(Sum("views_count"))["views_count__sum"] or 0,
        }

        # This Week Statistics
        week_start = now - timedelta(days=now.weekday())
        week_ads = user_ads.filter(created_at__gte=week_start)
        context["week_stats"] = {
            "new_ads": week_ads.count(),
            "views": week_ads.aggregate(Sum("views_count"))["views_count__sum"] or 0,
        }

        # Top Performing Ads
        context["top_ads"] = user_ads.order_by("-views_count")[:5]

        # Ads by Category
        context["category_stats"] = (
            user_ads.values("category__name")
            .annotate(count=Count("id"), total_views=Sum("views_count"))
            .order_by("-count")[:10]
        )

        # Ads by Status
        context["status_stats"] = (
            user_ads.values("status").annotate(count=Count("id")).order_by("-count")
        )

        # Recent Activity (last 7 days)
        last_7_days = now - timedelta(days=7)
        context["recent_ads"] = user_ads.filter(created_at__gte=last_7_days).order_by(
            "-created_at"
        )[:10]

        return context


class ClassifiedAdCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new classified ad."""

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:my_ads")

    def dispatch(self, request, *args, **kwargs):
        """
        Allow all authenticated users to create ads.
        Payment will be handled at the end based on:
        1. Whether they have free ads remaining in a package
        2. The category's ad_creation_price
        3. Site default ad_base_fee
        """
        # First check if user is authenticated
        if not request.user.is_authenticated:
            # Add toast message for guest users
            messages.info(
                request,
                _("يجب تسجيل الدخول أولاً لتتمكن من نشر الإعلانات."),
            )
            # Let LoginRequiredMixin handle the redirect
            return super().dispatch(request, *args, **kwargs)

        # Check phone verification requirement
        from constance import config
        from content.site_config import SiteConfiguration

        # Check if phone verification is enabled from constance or site_config
        constance_enabled = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)
        site_config = SiteConfiguration.get_solo()
        site_config_enabled = site_config.require_phone_verification

        # If phone verification required, let the form handle it inline
        # (no redirect — the form will show the verification UI)

        # Check if user has any active package with remaining ads (for display purposes)
        active_package = (
            UserPackage.objects.filter(
                user=request.user,
                expiry_date__gte=timezone.now(),
                ads_remaining__gt=0,
            )
            .order_by("expiry_date")
            .first()
        )

        # Store remaining ads count in session for display (if available)
        if active_package:
            request.session["ads_remaining"] = active_package.ads_remaining
        else:
            request.session["ads_remaining"] = 0

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pass user to form for mobile verification"""
        kwargs = super().get_form_kwargs()
        # Only pass user if authenticated
        if self.request.user.is_authenticated:
            kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = AdImageFormSet(
                self.request.POST,
                self.request.FILES,
                prefix="images",
                form_kwargs={"request": self.request},
            )
        else:
            # Limit extra forms to 5 as requested
            AdImageFormSet.extra = 5
            context["image_formset"] = AdImageFormSet(
                prefix="images",
                queryset=AdImage.objects.none(),
                form_kwargs={"request": self.request},
            )

        from django.db.models import Prefetch

        context["ad_categories"] = (
            Category.objects.filter(
                section_type=Category.SectionType.CLASSIFIED,
                is_active=True,
                parent__isnull=True,  # Only root categories
            )
            .defer(
                "default_reservation_percentage",
                "min_reservation_amount",
                "max_reservation_amount",
                # DO NOT defer ad_creation_price - it's needed for template rendering
            )
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=Category.objects.filter(is_active=True).defer(
                        "default_reservation_percentage",
                        "min_reservation_amount",
                        "max_reservation_amount",
                        # DO NOT defer ad_creation_price - it's needed for template rendering
                    ),
                )
            )
        )
        context["active_nav"] = "create_ad"

        # Prepare categories data with pricing for JavaScript (all levels)
        # Use effective prices with inheritance
        import json
        from django.core.serializers.json import DjangoJSONEncoder

        categories_data = {}
        # Fetch ALL active categories regardless of section_type.
        # The subcategory prefetch in ad_categories has no section_type filter, so
        # subcategories of CLASSIFIED roots may have any section_type value.
        # Excluding them from raw_cats would leave them out of categoriesPricing,
        # causing the JS to fall back to siteDefaultBaseFee (0) instead of the set price.
        raw_cats = list(Category.objects.filter(
            is_active=True,
        ).values('id', 'name', 'parent_id', 'ad_creation_price'))

        # Build lookups
        own_price_map = {c['id']: float(c['ad_creation_price'] or 0) for c in raw_cats}
        parent_map    = {c['id']: c['parent_id'] for c in raw_cats}

        def _effective_price(cat_id, depth=0):
            if depth > 5:
                return 0.0
            p = own_price_map.get(cat_id, 0.0)
            if p > 0:
                return p
            pid = parent_map.get(cat_id)
            if pid:
                return _effective_price(pid, depth + 1)
            return 0.0

        for c in raw_cats:
            own_p = own_price_map[c['id']]
            eff_p = _effective_price(c['id'])
            categories_data[c['id']] = {
                "ad_creation_price": eff_p,
                "name": c['name'],
                "parent_id": c['parent_id'],
                "has_own_price": own_p > 0,
                "is_price_inherited": own_p == 0 and c['parent_id'] is not None,
            }
        # Convert to JSON to ensure proper null handling
        context["categories_pricing"] = json.dumps(
            categories_data, cls=DjangoJSONEncoder
        )
        context["categories_pricing_safe"] = True  # Flag to indicate it's already JSON

        # Set country from session (header selection) or user profile
        selected_country = self.request.session.get("selected_country")
        if not selected_country and self.request.user.is_authenticated:
            # Fall back to user's profile country
            if hasattr(self.request.user, "country") and self.request.user.country:
                selected_country = self.request.user.country.code

        # Pass selected_country to template for country field default
        if selected_country:
            context["selected_country"] = selected_country

        # Get site configuration for pricing (local use only, not passed to template)
        from content.models import SiteConfiguration

        site_config = SiteConfiguration.get_solo()

        # Add only needed site config values (converted to avoid Decimal serialization issues)
        context["ad_base_fee"] = (
            float(site_config.ad_base_fee) if site_config.ad_base_fee else 0.0
        )
        context["cart_service_instructions"] = (
            site_config.cart_service_instructions
            or "عند تفعيل السلة، سيتم خصم رسوم خدمة من ثمن المنتج عند البيع. يجب أن يكون السعر شاملاً لهذه الرسوم ورسوم التوصيل."
        )

        # Add mobile verification setting for form validation
        context["mobile_verification_enabled"] = site_config.require_phone_verification

        # Inline phone verification: flag if the user still needs to verify
        from constance import config as constance_config
        constance_phone_enabled = getattr(constance_config, "ENABLE_MOBILE_VERIFICATION", True)
        phone_verification_needed = (
            (constance_phone_enabled or site_config.require_phone_verification)
            and self.request.user.is_authenticated
            and not self.request.user.is_mobile_verified
        )
        context["phone_verification_needed"] = phone_verification_needed

        # Get user's active package to determine feature prices
        if self.request.user.is_authenticated:
            # Only use package pricing when the user still has free ads remaining
            active_package = (
                UserPackage.objects.filter(
                    user=self.request.user,
                    expiry_date__gte=timezone.now(),
                    ads_remaining__gt=0,
                )
                .order_by("expiry_date")
                .first()
            )

            # Get all active packages for ads remaining count
            active_packages = UserPackage.objects.filter(
                user=self.request.user,
                expiry_date__gte=timezone.now(),
                ads_remaining__gt=0,
            )
            total_ads_remaining = sum(pkg.ads_remaining for pkg in active_packages)

            context["has_free_ads"] = total_ads_remaining > 0
            context["free_ads_remaining"] = total_ads_remaining

            # Pass feature prices based on package or site defaults
            if active_package and active_package.package:
                package = active_package.package
                context["feature_prices"] = {
                    "highlighted": (
                        float(package.feature_highlighted_price)
                        if package.feature_highlighted_price
                        else 0.0
                    ),
                    "urgent": (
                        float(package.feature_urgent_price)
                        if package.feature_urgent_price
                        else 0.0
                    ),
                    "pinned": (
                        float(package.feature_pinned_price)
                        if package.feature_pinned_price
                        else 0.0
                    ),
                    "contact_for_price": (
                        float(package.feature_contact_for_price)
                        if package.feature_contact_for_price
                        else 0.0
                    ),
                    "auto_refresh": (
                        float(package.feature_auto_refresh_price)
                        if package.feature_auto_refresh_price
                        else 0.0
                    ),
                    "add_video": (
                        float(package.feature_add_video_price)
                        if package.feature_add_video_price
                        else 0.0
                    ),
                }
                context["pricing_source"] = "package"
                # Don't pass the active_package object itself, just its data
                context["active_package_id"] = active_package.pk
                context["active_package_name"] = (
                    active_package.package.name if active_package.package else None
                )
            else:
                # No free ads remaining — use constance prices
                context["feature_prices"] = {
                    "highlighted": float(
                        getattr(constance_config, "FEATURE_HIGHLIGHTED_PRICE", 50.0)
                    ),
                    "urgent": float(
                        getattr(constance_config, "FEATURE_URGENT_PRICE", 30.0)
                    ),
                    "pinned": float(
                        getattr(constance_config, "FEATURE_PINNED_PRICE", 75.0)
                    ),
                    "contact_for_price": float(
                        getattr(constance_config, "FEATURE_CONTACT_FOR_PRICE", 0.0)
                    ),
                    "auto_refresh": float(
                        getattr(constance_config, "FEATURE_AUTO_REFRESH_PRICE", 35.0)
                    ),
                    "add_video": float(
                        getattr(constance_config, "FEATURE_ADD_VIDEO_PRICE", 25.0)
                    ),
                }
                context["pricing_source"] = "constance"
                context["active_package_id"] = None
                context["active_package_name"] = None
        else:
            # Guest user — use constance prices
            context["has_free_ads"] = False
            context["free_ads_remaining"] = 0
            context["feature_prices"] = {
                "highlighted": float(
                    getattr(constance_config, "FEATURE_HIGHLIGHTED_PRICE", 50.0)
                ),
                "urgent": float(
                    getattr(constance_config, "FEATURE_URGENT_PRICE", 30.0)
                ),
                "pinned": float(
                    getattr(constance_config, "FEATURE_PINNED_PRICE", 75.0)
                ),
                "contact_for_price": float(
                    getattr(constance_config, "FEATURE_CONTACT_FOR_PRICE", 0.0)
                ),
                "auto_refresh": float(
                    getattr(constance_config, "FEATURE_AUTO_REFRESH_PRICE", 35.0)
                ),
                "add_video": float(
                    getattr(constance_config, "FEATURE_ADD_VIDEO_PRICE", 25.0)
                ),
            }
            context["pricing_source"] = "constance"
            context["active_package_id"] = None
            context["active_package_name"] = None

        return context

    def form_invalid(self, form):
        """Handle form validation errors and preserve data"""
        messages.error(
            self.request,
            _("يوجد أخطاء في النموذج. يرجى مراجعة الحقول وتصحيح الأخطاء."),
        )
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        from content.models import SiteConfiguration
        from decimal import Decimal

        site_config = SiteConfiguration.get_solo()
        form.instance.user = self.request.user

        # Get selected features from POST data
        feature_highlighted = self.request.POST.get("feature_highlighted") == "on"
        feature_urgent = self.request.POST.get("feature_urgent") == "on"
        feature_pinned = self.request.POST.get("feature_pinned") == "on"
        feature_contact_for_price = (
            self.request.POST.get("feature_contact_for_price") == "on"
        )
        feature_auto_refresh = self.request.POST.get("feature_auto_refresh") == "on"
        feature_add_video = self.request.POST.get("feature_add_video") == "on"
        publisher_cart_enabled = self.request.POST.get("publisher_cart_enabled") == "on"

        # Set cart flags
        if publisher_cart_enabled:
            form.instance.publisher_cart_enabled = True
            # Check if category allows cart
            if form.instance.category and form.instance.category.allow_cart:
                form.instance.allow_cart = (
                    False  # Will be enabled by admin after receiving product
                )
            else:
                form.instance.publisher_cart_enabled = (
                    False  # Reset if category doesn't support cart
                )

        # Check if user has active package with remaining ads (for pricing)
        active_package = (
            UserPackage.objects.filter(
                user=self.request.user,
                expiry_date__gte=timezone.now(),
                ads_remaining__gt=0,
            )
            .order_by("expiry_date")
            .first()
        )

        # Get all active packages with remaining ads to check total free ads
        active_packages_with_ads = UserPackage.objects.filter(
            user=self.request.user,
            expiry_date__gte=timezone.now(),
            ads_remaining__gt=0,
        )
        total_free_ads_remaining = sum(
            pkg.ads_remaining for pkg in active_packages_with_ads
        )
        has_free_ads = total_free_ads_remaining > 0

        # Calculate features cost based on package-specific pricing
        features_cost = Decimal("0.00")

        # Determine which pricing to use (package or site default)
        if active_package and active_package.package:
            # Use package-specific pricing
            package = active_package.package
            if feature_highlighted:
                features_cost += Decimal(str(package.feature_highlighted_price))
            if feature_urgent:
                features_cost += Decimal(str(package.feature_urgent_price))
            if feature_pinned:
                features_cost += Decimal(str(package.feature_pinned_price))
            if feature_contact_for_price:
                features_cost += Decimal(str(package.feature_contact_for_price))
            if feature_auto_refresh:
                features_cost += Decimal(str(package.feature_auto_refresh_price))
            if feature_add_video:
                features_cost += Decimal(str(package.feature_add_video_price))
        else:
            # No free ads remaining — use constance pricing
            from constance import config as constance_cfg
            if feature_highlighted:
                features_cost += Decimal(
                    str(getattr(constance_cfg, "FEATURE_HIGHLIGHTED_PRICE", 50.0))
                )
            if feature_urgent:
                features_cost += Decimal(
                    str(getattr(constance_cfg, "FEATURE_URGENT_PRICE", 30.0))
                )
            if feature_pinned:
                features_cost += Decimal(
                    str(getattr(constance_cfg, "FEATURE_PINNED_PRICE", 75.0))
                )
            if feature_contact_for_price:
                features_cost += Decimal(
                    str(getattr(constance_cfg, "FEATURE_CONTACT_FOR_PRICE", 0.0))
                )
            if feature_auto_refresh:
                features_cost += Decimal(
                    str(getattr(constance_cfg, "FEATURE_AUTO_REFRESH_PRICE", 35.0))
                )
            if feature_add_video:
                features_cost += Decimal(
                    str(getattr(constance_cfg, "FEATURE_ADD_VIDEO_PRICE", 25.0))
                )

        # Determine base fee (publishing cost)
        base_fee = Decimal("0.00")
        # Check if user has free ads remaining in ANY package
        if not has_free_ads:
            # No free ads remaining, user must pay base fee
            # Use effective price with inheritance from parent categories
            if form.instance.category:
                effective_price = form.instance.category.get_effective_ad_creation_price()
                if effective_price > 0:
                    base_fee = effective_price
                else:
                    # If effective price is 0, use site default as fallback
                    base_fee = Decimal(str(site_config.ad_base_fee))
            else:
                # No category selected, use site default
                base_fee = Decimal(str(site_config.ad_base_fee))

        # Total cost = base publishing fee + features cost
        total_cost = base_fee + features_cost

        # Always save ad as DRAFT first
        form.instance.status = ClassifiedAd.AdStatus.DRAFT

        context = self.get_context_data()
        image_formset = context["image_formset"]

        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()

            features_dict = {
                "highlighted": feature_highlighted,
                "urgent": feature_urgent,
                "pinned": feature_pinned,
                "contact_for_price": feature_contact_for_price,
                "auto_refresh": feature_auto_refresh,
                "add_video": feature_add_video,
            }

            # Store ad ID and features in session
            self.request.session["pending_ad_id"] = self.object.pk
            self.request.session["ad_features"] = features_dict
            self.request.session["ad_payment_amount"] = str(total_cost)
            self.request.session["ad_base_fee"] = str(base_fee)
            self.request.session["ad_features_cost"] = str(features_cost)
            self.request.session["has_active_package"] = active_package is not None
            self.request.session["has_free_ads"] = has_free_ads
            self.request.session.modified = True  # force session save

            # Always route through payment page — handles both free/package and paid cases
            return redirect("main:ad_payment", ad_id=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ClassifiedAdUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing classified ad."""

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:my_ads")

    def get_queryset(self):
        # Ensure users can only edit their own ads (excluding deleted ones)
        return ClassifiedAd.objects.filter(
            user=self.request.user, deleted_at__isnull=True
        )

    def get_form_kwargs(self):
        """Pass user and editing flag to form"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["is_editing"] = True
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = AdImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                form_kwargs={"request": self.request},
            )
        else:
            context["image_formset"] = AdImageFormSet(
                instance=self.object,
                queryset=self.object.images.all(),
                form_kwargs={"request": self.request},
            )

        from django.db.models import Prefetch

        context["ad_categories"] = (
            Category.objects.filter(
                section_type=Category.SectionType.CLASSIFIED,
                is_active=True,
                parent__isnull=True,  # Only root categories
            )
            .defer(
                "default_reservation_percentage",
                "min_reservation_amount",
                "max_reservation_amount",
                # DO NOT defer ad_creation_price - it's needed for template rendering
            )
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=Category.objects.filter(is_active=True).defer(
                        "default_reservation_percentage",
                        "min_reservation_amount",
                        "max_reservation_amount",
                        # DO NOT defer ad_creation_price - it's needed for template rendering
                    ),
                )
            )
        )
        context["is_editing"] = True
        context["original_category"] = self.object.category

        # Prepare categories data with pricing for JavaScript (all levels)
        import json
        from django.core.serializers.json import DjangoJSONEncoder

        categories_data = {}
        raw_cats = list(Category.objects.filter(
            is_active=True,
        ).values('id', 'name', 'parent_id', 'ad_creation_price'))

        # Build lookups
        own_price_map = {c['id']: float(c['ad_creation_price'] or 0) for c in raw_cats}
        parent_map    = {c['id']: c['parent_id'] for c in raw_cats}

        def _effective_price(cat_id, depth=0):
            if depth > 5:
                return 0.0
            p = own_price_map.get(cat_id, 0.0)
            if p > 0:
                return p
            pid = parent_map.get(cat_id)
            if pid:
                return _effective_price(pid, depth + 1)
            return 0.0

        for c in raw_cats:
            own_p = own_price_map[c['id']]
            eff_p = _effective_price(c['id'])
            categories_data[c['id']] = {
                "ad_creation_price": eff_p,
                "name": c['name'],
                "parent_id": c['parent_id'],
                "has_own_price": own_p > 0,
                "is_price_inherited": own_p == 0 and c['parent_id'] is not None,
            }
        context["categories_pricing"] = json.dumps(
            categories_data, cls=DjangoJSONEncoder
        )
        context["categories_pricing_safe"] = True

        # Add mobile verification setting
        from content.models import SiteConfiguration

        site_config = SiteConfiguration.get_solo()
        context["mobile_verification_enabled"] = site_config.require_phone_verification
        context["ad_base_fee"] = (
            float(site_config.ad_base_fee) if site_config.ad_base_fee else 0.0
        )

        # Add feature prices (for consistency with create view)
        if self.request.user.is_authenticated:
            active_packages = UserPackage.objects.filter(
                user=self.request.user,
                expiry_date__gte=timezone.now(),
                ads_remaining__gt=0,
            )
            total_ads_remaining = sum(pkg.ads_remaining for pkg in active_packages)
            context["has_free_ads"] = total_ads_remaining > 0
            context["free_ads_remaining"] = total_ads_remaining

            active_package = (
                UserPackage.objects.filter(
                    user=self.request.user,
                    expiry_date__gte=timezone.now(),
                )
                .order_by("expiry_date")
                .first()
            )

            if active_package and active_package.package:
                package = active_package.package
                context["feature_prices"] = {
                    "highlighted": (
                        float(package.feature_highlighted_price)
                        if package.feature_highlighted_price
                        else 0.0
                    ),
                    "pinned": (
                        float(package.feature_pinned_price)
                        if package.feature_pinned_price
                        else 0.0
                    ),
                }
            else:
                context["feature_prices"] = {
                    "highlighted": (
                        float(site_config.featured_ad_price)
                        if site_config.featured_ad_price
                        else 50.0
                    ),
                    "pinned": (
                        float(site_config.pinned_ad_price)
                        if site_config.pinned_ad_price
                        else 100.0
                    ),
                }

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        # Prevent category changes
        if form.instance.category != self.object.category:
            messages.error(
                self.request,
                _(
                    "لا يمكن تغيير القسم بعد نشر الإعلان. لتغيير القسم، يرجى حذف الإعلان وإنشاء إعلان جديد."
                ),
            )
            return self.render_to_response(self.get_context_data(form=form))

        if form.is_valid() and image_formset.is_valid():
            # Determine if updated ad needs re-approval
            needs_approval = False
            original_status = self.object.status

            # Check if content has changed (title, description, or price)
            # Get original values from database (before form changes)
            original_ad = ClassifiedAd.objects.get(pk=self.object.pk)
            content_changed = (
                form.cleaned_data.get("title") != original_ad.title
                or form.cleaned_data.get("description") != original_ad.description
                or form.cleaned_data.get("price") != original_ad.price
            )

            # Check if images were added or changed
            images_changed = False
            for img_form in image_formset:
                if img_form.has_changed() and img_form.cleaned_data.get("image"):
                    images_changed = True
                    break

            if not self.request.user.is_staff:
                # If content or images changed, require admin approval
                if (
                    content_changed or images_changed
                ) and original_status == ClassifiedAd.AdStatus.ACTIVE:
                    needs_approval = True
                    form.instance.status = ClassifiedAd.AdStatus.PENDING
                    form.instance.is_resubmitted = True

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()

            if needs_approval:
                messages.info(
                    self.request,
                    _(
                        "تم تقديم التعديلات للمراجعة. سيتم نشر إعلانك بعد موافقة الإدارة على التغييرات."
                    ),
                )
            else:
                messages.success(self.request, _("تم تحديث إعلانك بنجاح!"))

            return redirect(self.get_success_url())
        else:
            # Add formset errors to messages for debugging
            if not image_formset.is_valid():
                for error in image_formset.errors:
                    if error:
                        messages.error(self.request, str(error))
                for error in image_formset.non_form_errors():
                    messages.error(self.request, str(error))
            return self.render_to_response(self.get_context_data(form=form))


class ClassifiedAdCreateSuccessView(LoginRequiredMixin, DetailView):
    """
    Shows a success message after creating an ad and suggests upgrades.
    """

    model = ClassifiedAd
    template_name = "classifieds/ad_create_success.html"
    context_object_name = "ad"

    def get_queryset(self):
        return ClassifiedAd.objects.filter(user=self.request.user)


def classifieds_id_redirect(request, pk):
    """Redirect old numeric-ID ad URLs to the correct slug URL (permanent 301)."""
    from django.http import Http404
    from django.shortcuts import redirect
    ad = ClassifiedAd.objects.filter(pk=pk).values("slug").first()
    if not ad:
        raise Http404
    return redirect("main:ad_detail", slug=ad["slug"], permanent=True)


class ClassifiedAdDetailView(DetailView):
    """
    Public view for a single classified ad.
    """

    model = ClassifiedAd
    template_name = "classifieds/ad_detail.html"
    context_object_name = "ad"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to handle inactive ads gracefully and check guest permissions."""
        from constance import config
        from django.contrib import messages
        from django.utils.translation import gettext as _
        from django.shortcuts import redirect

        # Check if guests are allowed to view ads
        if not request.user.is_authenticated and not getattr(
            config, "ALLOW_GUEST_VIEWING", True
        ):
            messages.warning(request, _("يجب عليك تسجيل الدخول لمشاهدة الإعلانات"))
            return redirect("main:login")

        ad_slug = self.kwargs.get(self.slug_url_kwarg)

        try:
            # First check if ad exists at all (including inactive ones)
            from .models import ClassifiedAd

            ad = ClassifiedAd.objects.select_related("user", "category").get(
                slug=ad_slug
            )

            # If ad is not active, show it with disabled actions
            if ad.status != ClassifiedAd.AdStatus.ACTIVE:
                import logging

                logger = logging.getLogger(__name__)
                logger.info(
                    f"ClassifiedAd '{ad_slug}' is {ad.get_status_display()} - showing with disabled actions. IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
                )

                # Set the object and render with inactive template
                self.object = ad
                context = self.get_context_data(object=ad)
                context["ad_inactive"] = True
                context["ad_status"] = ad.status
                context["ad_status_display"] = ad.get_status_display()
                return self.render_to_response(context)

            # Ad is active, proceed normally
            return super().dispatch(request, *args, **kwargs)

        except ClassifiedAd.DoesNotExist:
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                f"ClassifiedAd '{ad_slug}' does not exist in database. IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
            raise Http404(f"Classified ad '{ad_slug}' does not exist.")
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Error checking ClassifiedAd '{ad_slug}': {str(e)}", exc_info=True
            )
            raise Http404(f"Unable to access classified ad '{ad_slug}'.")

    def get_queryset(self):
        # We handle inactive ads in dispatch, so include all ads here
        # Optimize query with prefetch_related for images
        return ClassifiedAd.objects.select_related(
            "user", "category", "country"
        ).prefetch_related("images", "features", "reviews")

    def get_object(self, queryset=None):
        """Get the classified ad object with proper error handling and logging."""
        try:
            obj = super().get_object(queryset)
            # Increment view count without causing a race condition
            ClassifiedAd.objects.filter(pk=obj.pk).update(
                views_count=F("views_count") + 1
            )
            # obj.refresh_from_db() # The template will display the updated count
            return obj
        except ClassifiedAd.DoesNotExist:
            import logging

            logger = logging.getLogger(__name__)
            ad_slug = self.kwargs.get(self.slug_url_kwarg)
            logger.info(
                f"ClassifiedAd '{ad_slug}' does not exist or is not active. IP: {self.request.META.get('REMOTE_ADDR', 'unknown')}"
            )
            raise Http404(f"ClassifiedAd '{ad_slug}' does not exist or is not active.")
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            ad_id = self.kwargs.get(self.pk_url_kwarg)
            logger.error(
                f"Unexpected error accessing ClassifiedAd {ad_id}: {str(e)}",
                exc_info=True,
            )
            raise

    def get_context_data(self, **kwargs):
        """
        Add related ads to the context.
        """
        from constance import config

        context = super().get_context_data(**kwargs)
        # Use the already-fetched object to avoid incrementing views_count twice
        ad = context.get("ad") or getattr(self, "object", None)

        # Define a price range (e.g., +/- 25%)
        price_range_min = ad.price * Decimal("0.75")
        price_range_max = ad.price * Decimal("1.25")

        # Build a relevance score using annotations
        related_ads = (
            ClassifiedAd.objects.filter(
                category=ad.category, status=ClassifiedAd.AdStatus.ACTIVE
            )
            .exclude(pk=ad.pk)
            .annotate(
                relevance_score=Case(
                    When(city__iexact=ad.city, then=Value(2)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(
                        price__range=(price_range_min, price_range_max), then=Value(1)
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .select_related("user")
            .prefetch_related("images", "features")
            .order_by("-relevance_score", "-created_at")[:12]
        )

        context["related_ads"] = related_ads

        # Add reviews for this ad (only approved reviews)
        context["reviews"] = (
            ad.reviews.filter(is_approved=True)
            .select_related("user")
            .order_by("-created_at")[:10]
        )

        # Check if current user has already reviewed
        if self.request.user.is_authenticated:
            user_review = ad.reviews.filter(user=self.request.user).first()
            context["user_has_reviewed"] = user_review is not None
            # Check if user has pending review
            context["user_has_pending_review"] = (
                user_review is not None and not user_review.is_approved
            )
        else:
            context["user_has_reviewed"] = False
            context["user_has_pending_review"] = False

        # Determine if contact information should be shown based on settings
        show_contact_info = True
        can_send_message = True

        if not self.request.user.is_authenticated:
            # Guest user
            allow_guest_contact = getattr(config, "ALLOW_GUEST_CONTACT", False)
            show_contact_info = allow_guest_contact
            can_send_message = False  # Guests can't send messages
        else:
            # Authenticated user
            members_only_contact = getattr(config, "MEMBERS_ONLY_CONTACT", True)
            members_only_messaging = getattr(config, "MEMBERS_ONLY_MESSAGING", True)

            # For registered users, check if contact is members-only
            if members_only_contact:
                show_contact_info = True  # Registered users can see contact info
            else:
                show_contact_info = (
                    True  # Not members-only, so everyone (including guests) can see
                )

            # For messaging, check if it's members-only
            if members_only_messaging:
                can_send_message = True  # Registered users can send messages
            else:
                can_send_message = True  # Not members-only, so everyone can send

        context["show_contact_info"] = show_contact_info
        context["can_send_message"] = can_send_message

        # Add custom fields for display
        context["custom_fields"] = ad.get_custom_fields_for_detail()

        # Add buyer safety tips
        from main.models import SafetyTip
        context["safety_tips"] = SafetyTip.get_tips_for_category(ad.category)

        return context


class SaveSearchView(LoginRequiredMixin, View):
    """View to save a user's search query via POST request."""

    def post(self, request, *args, **kwargs):
        search_name = request.POST.get("name")
        query_params = request.POST.get("query_params")

        if not search_name or not query_params:
            return JsonResponse(
                {"success": False, "message": _("اسم البحث ومعاييره مطلوبان.")},
                status=400,
            )

        if SavedSearch.objects.filter(user=request.user, name=search_name).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": _("لديك بحث محفوظ بهذا الاسم بالفعل."),
                },
                status=400,
            )

        SavedSearch.objects.create(
            user=request.user, name=search_name, query_params=query_params
        )

        return JsonResponse({"success": True, "message": _("تم حفظ البحث بنجاح!")})


class UserSavedSearchesView(LoginRequiredMixin, ListView):
    """View to list the current user's saved searches."""

    model = SavedSearch
    template_name = "classifieds/saved_searches.html"
    context_object_name = "saved_searches"

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "saved_searches"
        return context

    def post(self, request, *args, **kwargs):
        search_id = request.POST.get("search_id")
        if search_id:
            search = get_object_or_404(SavedSearch, pk=search_id, user=request.user)

            # Check if email_notifications checkbox is checked
            # If checkbox is checked, it will be in POST data with value "on"
            # If checkbox is unchecked, it won't be in POST data at all
            email_notifications_enabled = "email_notifications" in request.POST

            # Save the updated preference
            search.email_notifications = email_notifications_enabled
            search.save(update_fields=["email_notifications"])

            # Log for debugging
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                f"SavedSearch {search_id} email_notifications updated to: {email_notifications_enabled}"
            )

            status_text = _("مفعلة") if email_notifications_enabled else _("معطلة")
            messages.success(
                request,
                _("تم تحديث تفضيلات الإشعارات بنجاح. الإشعارات الآن: {}").format(
                    status_text
                ),
            )
        return redirect("main:saved_searches")


class DeleteSavedSearchView(LoginRequiredMixin, View):
    """View to delete a saved search."""

    def post(self, request, *args, **kwargs):
        search_id = self.kwargs.get("pk")
        search = get_object_or_404(SavedSearch, pk=search_id, user=request.user)
        search.delete()
        messages.success(request, _("تم حذف البحث المحفوظ بنجاح."))
        return redirect("main:saved_searches")


class UnsubscribeFromSearchView(View):
    """Handles unsubscribing from a saved search via a tokenized link."""

    def get(self, request, *args, **kwargs):
        token = self.kwargs.get("token")
        search = get_object_or_404(SavedSearch, unsubscribe_token=token)
        search.email_notifications = False
        search.save(update_fields=["email_notifications"])

        messages.success(request, _("تم إلغاء اشتراكك في إشعارات هذا البحث بنجاح."))
        return redirect("main:home")


class NotificationListView(LoginRequiredMixin, ListView):
    """Displays a list of notifications for the current user."""

    model = Notification
    template_name = "pages/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        # Get notifications for the current user
        queryset = Notification.objects.filter(user=self.request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Mark all unread notifications as read once the user views the page
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return response


class PackageListView(ListView):
    """
    عرض قائمة الباقات المتاحة
    Display available ad packages
    """

    model = AdPackage
    template_name = "classifieds/packages_list_modern.html"
    context_object_name = "packages"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all active packages
        all_packages = AdPackage.objects.filter(is_active=True).select_related(
            "category"
        )

        # Separate general packages (no category) from category-specific ones
        general_packages = all_packages.filter(category__isnull=True).order_by(
            "display_order", "-is_recommended", "price"
        )

        # Get category-specific packages grouped by category
        category_packages = {}
        for package in all_packages.filter(category__isnull=False).order_by(
            "category", "display_order", "price"
        ):
            if package.category not in category_packages:
                category_packages[package.category] = []
            category_packages[package.category].append(package)

        context["general_packages"] = general_packages
        context["category_packages"] = category_packages

        # If user is authenticated, get their active packages
        if self.request.user.is_authenticated:
            context["active_packages"] = (
                UserPackage.objects.filter(
                    user=self.request.user,
                    expiry_date__gte=timezone.now(),
                    ads_remaining__gt=0,
                )
                .select_related("package", "package__category")
                .order_by("-purchase_date")
            )

        return context


class PackagePurchaseView(LoginRequiredMixin, View):
    """
    معالجة شراء/تفعيل الباقة
    Handle package purchase/activation
    """

    def post(self, request, package_id):
        package = get_object_or_404(AdPackage, id=package_id, is_active=True)

        # Check if it's a free package or default package
        if package.price == 0 or package.is_default:
            # Check if user already activated this free package before
            already_activated = UserPackage.objects.filter(
                user=request.user, package=package
            ).exists()

            if already_activated:
                messages.warning(
                    request,
                    _(
                        "لقد قمت بتفعيل هذه الباقة المجانية من قبل. الباقات المجانية يمكن تفعيلها مرة واحدة فقط."
                    ),
                )
                return redirect("main:packages_list")

            # Create user package immediately
            user_package = UserPackage.objects.create(
                user=request.user, package=package
            )
            messages.success(
                request,
                _("تم تفعيل الباقة بنجاح! لديك الآن {} إعلانات متاحة.").format(
                    package.ad_count
                ),
            )
            return redirect("main:my_ads")
        else:
            # Store package info in session and redirect to checkout
            request.session["package_checkout_id"] = package.id
            request.session["package_checkout_amount"] = str(package.price)
            return redirect("main:package_checkout", package_id=package.id)

    def get(self, request, package_id):
        # Show package purchase confirmation page
        package = get_object_or_404(AdPackage, id=package_id, is_active=True)
        return redirect("main:packages_list")


class AdminDashboardView(LoginRequiredMixin, ListView):
    """Admin dashboard for managing all advertisements"""

    model = ClassifiedAd
    template_name = "admin/dashboard_main.html"
    context_object_name = "ads"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers
        if not request.user.is_superuser:
            messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
            return redirect("main:home")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = (
            ClassifiedAd.objects.select_related("user", "category", "country")
            .prefetch_related("images")
            .order_by("-created_at")
        )

        # Filter by status
        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(
                status=ClassifiedAd.AdStatus.ACTIVE, is_hidden=False
            )
        elif status == "pending":
            queryset = queryset.filter(status=ClassifiedAd.AdStatus.PENDING)
        elif status == "expired":
            queryset = queryset.filter(status=ClassifiedAd.AdStatus.EXPIRED)
        elif status == "hidden":
            queryset = queryset.filter(is_hidden=True)

        # Filter by approval
        approval = self.request.GET.get("approval")
        if approval:
            if approval == "active":
                queryset = queryset.filter(status=ClassifiedAd.AdStatus.ACTIVE)
            elif approval == "pending":
                queryset = queryset.filter(status=ClassifiedAd.AdStatus.PENDING)
            elif approval == "expired":
                queryset = queryset.filter(status=ClassifiedAd.AdStatus.EXPIRED)
            elif approval == "hidden":
                queryset = queryset.filter(is_hidden=True)

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = (
                queryset.filter(title__icontains=search)
                | queryset.filter(user__username__icontains=search)
                | queryset.filter(category__name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate statistics
        context["stats"] = {
            "active_count": ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.ACTIVE, is_hidden=False
            ).count(),
            "pending_count": ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.PENDING
            ).count(),
            "hidden_count": ClassifiedAd.objects.filter(is_hidden=True).count(),
            "expired_count": ClassifiedAd.objects.filter(
                status=ClassifiedAd.AdStatus.EXPIRED
            ).count(),
        }

        return context


class ToggleAdHideView(LoginRequiredMixin, View):
    """AJAX view to toggle ad visibility"""

    def post(self, request, ad_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        try:
            ad = get_object_or_404(ClassifiedAd, id=ad_id)

            # Try to parse JSON data, fallback to POST data
            try:
                import json

                data = json.loads(request.body)
                hide_value = data.get("hide", False)
            except (json.JSONDecodeError, ValueError):
                # Fallback to POST data
                hide_value = request.POST.get("hide", "false").lower() == "true"

            ad.is_hidden = hide_value
            ad.save()

            # Send notification to user
            Notification.objects.create(
                user=ad.user,
                title=_("تغيير حالة الإعلان"),
                message=_("تم {} إعلانك '{}'. يمكنك مشاهدته في صفحة إعلاناتك.").format(
                    _("إخفاء") if ad.is_hidden else _("إظهار"), ad.title
                ),
                notification_type="general",
            )

            return JsonResponse({"success": True, "is_hidden": ad.is_hidden})
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error toggling ad hide {ad_id}: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class EnableAdCartView(LoginRequiredMixin, View):
    """AJAX view to enable cart for an ad"""

    def post(self, request, ad_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        try:
            ad = get_object_or_404(ClassifiedAd, id=ad_id)

            # Admin can enable cart regardless of category settings
            # This is the whole point of cart_enabled_by_admin field
            ad.cart_enabled_by_admin = True
            ad.save()

            # Send notification to user
            Notification.objects.create(
                user=ad.user,
                title=_("تفعيل السلة"),
                message=_(
                    "تم تفعيل السلة لإعلانك '{}'. يمكنك مشاهدته في صفحة إعلاناتك."
                ).format(ad.title),
                notification_type="general",
            )

            return JsonResponse({"success": True})
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error enabling cart for ad {ad_id}: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class DeleteAdView(LoginRequiredMixin, View):
    """AJAX view to delete an ad"""

    def post(self, request, ad_id):
        try:
            if not request.user.is_superuser:
                return JsonResponse(
                    {"success": False, "message": _("ليس لديك صلاحية لحذف الإعلانات")},
                    status=403,
                )

            ad = get_object_or_404(ClassifiedAd, id=ad_id)
            ad_title = ad.title
            ad_user = ad.user

            # Send notification before deleting
            Notification.objects.create(
                user=ad_user,
                title=_("حذف إعلان"),
                message=_("تم حذف إعلانك '{}' من قبل الإدارة").format(ad_title),
            )

            ad.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم حذف الإعلان '{}' بنجاح.").format(ad_title),
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("حدث خطأ أثناء حذف الإعلان: {}").format(str(e)),
                },
                status=500,
            )


class PublisherDeleteAdView(LoginRequiredMixin, View):
    """AJAX view for publishers to delete their own ads"""

    def post(self, request, ad_id):
        try:
            # Get the ad and verify ownership
            ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)
            ad_title = ad.title

            # Delete the ad
            ad.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم حذف الإعلان '{}' بنجاح.").format(ad_title),
                }
            )
        except ClassifiedAd.DoesNotExist:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("الإعلان غير موجود أو ليس لديك صلاحية لحذفه"),
                },
                status=404,
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("حدث خطأ أثناء حذف الإعلان: {}").format(str(e)),
                },
                status=500,
            )


class AdminChangeAdStatusView(LoginRequiredMixin, View):
    """AJAX view to approve or reject an ad"""

    def post(self, request, ad_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        ad = get_object_or_404(ClassifiedAd, id=ad_id)

        import json

        data = json.loads(request.body)
        action = data.get("action")
        reason = data.get("reason", "")

        if action == "approve":
            ad.status = "ACTIVE"
            ad.save()

            # Send notification to user
            Notification.objects.create(
                user=ad.user,
                title=_("تم قبول إعلانك"),
                message=_(
                    "تم قبول إعلانك '{}' ونشره بنجاح. يمكنك مشاهدته في صفحة إعلاناتك."
                ).format(ad.title),
                notification_type="ad_approved",
            )

            return JsonResponse(
                {"success": True, "message": _("تم قبول الإعلان بنجاح")}
            )

        elif action == "reject":
            ad.status = "REJECTED"
            ad.save()

            # Send notification to user with reason
            message = _("تم رفض إعلانك '{}'").format(ad.title)
            if reason:
                message += "\n" + _("السبب: {}").format(reason)

            Notification.objects.create(
                user=ad.user,
                title=_("تم رفض إعلانك"),
                message=message,
                notification_type="ad_rejected",
            )

            return JsonResponse({"success": True, "message": _("تم رفض الإعلان بنجاح")})

        return JsonResponse({"success": False, "error": "Invalid action"}, status=400)


class AdminToggleAdFeatureView(LoginRequiredMixin, View):
    """AJAX view to toggle ad features (highlight, urgent)"""

    def post(self, request, ad_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        ad = get_object_or_404(ClassifiedAd, id=ad_id)

        import json

        data = json.loads(request.body)
        feature = data.get("feature")
        state = data.get("state", False)

        if feature == "highlight":
            ad.is_highlighted = state
            feature_name = _("التمييز")
        elif feature == "urgent":
            ad.is_urgent = state
            feature_name = _("العاجل")
        else:
            return JsonResponse(
                {"success": False, "error": "Invalid feature"}, status=400
            )

        ad.save()

        # Send notification to user
        action = _("تم تفعيل") if state else _("تم إلغاء")
        Notification.objects.create(
            user=ad.user,
            title=_("تحديث ميزة الإعلان"),
            message=_("{} {} لإعلانك '{}'. يمكنك مشاهدته في صفحة إعلاناتك.").format(
                action, feature_name, ad.title
            ),
            notification_type="general",
        )

        message = _("تم {} {} بنجاح").format(
            _("تفعيل") if state else _("إلغاء"), feature_name
        )

        return JsonResponse({"success": True, "message": message})


class AdminCategoriesView(LoginRequiredMixin, ListView):
    """Admin view for managing categories"""

    model = Category
    template_name = "admin/categories.html"
    context_object_name = "categories"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
            return redirect("main:home")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Category.objects.filter(level=0).order_by("order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_categories"] = Category.objects.filter(
            parent__isnull=True
        ).prefetch_related("subcategories")
        return context


class CategorySaveView(LoginRequiredMixin, View):
    """Save (create/update) category"""

    def post(self, request):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"}, status=403
            )

        category_id = request.POST.get("category_id")
        name = request.POST.get("name")
        name_ar = request.POST.get("name_ar")
        name_en = request.POST.get("name_en")
        slug = request.POST.get("slug")
        slug_ar = request.POST.get("slug_ar")
        parent_id = request.POST.get("parent")
        section_type = request.POST.get("section_type")
        description = request.POST.get("description", "")
        description_ar = request.POST.get("description_ar", "")
        description_en = request.POST.get("description_en", "")
        allow_cart = request.POST.get("allow_cart") == "on"
        require_admin_approval = request.POST.get("require_admin_approval") == "on"
        is_active = request.POST.get("is_active") == "on"
        order = request.POST.get("order")
        icon = request.POST.get("icon", "")
        color = request.POST.get("color", "")
        country_code = request.POST.get("country")  # optional
        ad_creation_price = request.POST.get("ad_creation_price", "0")

        try:
            # Use slugify to auto-generate slugs if not provided
            from django.utils.text import slugify
            import uuid

            if category_id:
                # Update existing category
                category = Category.objects.get(id=category_id)
            else:
                # Create new category
                category = Category()

            # Basic required fields
            # Use name_en as 'name' if available, otherwise use name_ar
            category.name = name_en or name_ar or name
            category.name_ar = name_ar or name

            # Auto-generate slugs if not provided
            if not slug:
                base_slug = slugify(name_en or name_ar or name, allow_unicode=True)
                # Ensure uniqueness for new categories
                if not category_id:
                    slug = base_slug
                    counter = 1
                    while Category.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                else:
                    # For updates, check if slug conflicts with other categories
                    slug = base_slug
                    counter = 1
                    while (
                        Category.objects.filter(slug=slug)
                        .exclude(id=category_id)
                        .exists()
                    ):
                        slug = f"{base_slug}-{counter}"
                        counter += 1

            if not slug_ar:
                # For Arabic, use Arabic name or fallback to regular slug
                base_slug_ar = slugify(name_ar or name_en or name, allow_unicode=True)
                if not category_id:
                    slug_ar = base_slug_ar if base_slug_ar else slug
                    counter = 1
                    while Category.objects.filter(slug_ar=slug_ar).exists():
                        slug_ar = (
                            f"{base_slug_ar}-{counter}"
                            if base_slug_ar
                            else f"{slug}-{counter}"
                        )
                        counter += 1
                else:
                    slug_ar = base_slug_ar if base_slug_ar else slug
                    counter = 1
                    while (
                        Category.objects.filter(slug_ar=slug_ar)
                        .exclude(id=category_id)
                        .exists()
                    ):
                        slug_ar = (
                            f"{base_slug_ar}-{counter}"
                            if base_slug_ar
                            else f"{slug}-{counter}"
                        )
                        counter += 1

            category.slug = slug
            category.slug_ar = slug_ar
            # Inherit section_type from parent if not explicitly provided (e.g. when adding subcategory)
            if section_type:
                category.section_type = section_type
            elif parent_id and not category.pk:
                # New subcategory: inherit section_type from parent
                try:
                    parent_cat = Category.objects.get(id=parent_id)
                    category.section_type = parent_cat.section_type
                except Category.DoesNotExist:
                    pass
            # If editing existing category and no section_type provided, keep existing value
            category.description = description

            # Save bilingual descriptions if model supports them
            if hasattr(category, "description_ar"):
                category.description_ar = description_ar
            if hasattr(category, "description_en"):
                category.description_en = description_en

            category.icon = icon
            if order is not None:
                category.order = int(order) if str(order).isdigit() else 0
            # Optional color stored in meta or dedicated field if exists
            if hasattr(category, "color"):
                setattr(category, "color", color)
            category.allow_cart = allow_cart
            category.require_admin_approval = require_admin_approval
            category.is_active = is_active

            if parent_id:
                category.parent = Category.objects.get(id=parent_id)
            else:
                category.parent = None

            # Optional: country by code
            if country_code:
                from content.models import Country

                try:
                    category.country = Country.objects.get(code=country_code)
                except Country.DoesNotExist:
                    category.country = None

            # Handle pricing fields
            from decimal import Decimal
            try:
                category.ad_creation_price = Decimal(ad_creation_price) if ad_creation_price else Decimal('0')
            except:
                category.ad_creation_price = Decimal('0')

            category.save()

            # AJAX-friendly response
            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم حفظ القسم بنجاح"),
                    "category": {
                        "id": category.id,
                        "name": category.name,
                        "name_ar": category.name_ar,
                        "slug": category.slug,
                        "slug_ar": category.slug_ar,
                        "section_type": category.section_type,
                        "description": category.description,
                        "is_active": category.is_active,
                        "order": category.order,
                        "parent": category.parent_id,
                    },
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("حدث خطأ أثناء حفظ القسم"),
                    "error": str(e),
                },
                status=400,
            )


class CategoryGetView(LoginRequiredMixin, View):
    """Get category data for editing"""

    def get(self, request, category_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"}, status=403
            )

        category = get_object_or_404(Category, id=category_id)

        # Get effective prices (with inheritance)
        effective_ad_creation_price = category.get_effective_ad_creation_price()

        # Get price sources for inheritance info
        ad_creation_source = category.get_price_source('ad_creation')

        return JsonResponse(
            {
                "id": category.id,
                "name": category.name,
                "name_ar": category.name_ar,
                "name_en": category.name,  # Add name_en for the form
                "slug": category.slug,
                "slug_ar": category.slug_ar,
                "parent_id": category.parent_id if category.parent else None,
                "section_type": category.section_type,
                "description": category.description,
                "description_ar": getattr(category, "description_ar", ""),
                "description_en": getattr(category, "description_en", ""),
                "allow_cart": getattr(category, "allow_cart", False),
                "require_admin_approval": getattr(
                    category, "require_admin_approval", True
                ),
                "is_active": category.is_active,
                "order": getattr(category, "order", 0),
                "icon": getattr(category, "icon", ""),
                "color": getattr(category, "color", ""),
                "country": (
                    getattr(category.country, "code", None)
                    if category.country
                    else None
                ),
                "ad_creation_price": float(getattr(category, "ad_creation_price", 0)),
                # Effective prices (with inheritance)
                "effective_ad_creation_price": float(effective_ad_creation_price),
                # Inheritance information
                "ad_creation_inherited": category.is_price_inherited('ad_creation'),
                "ad_creation_source": ad_creation_source.name if ad_creation_source and ad_creation_source.id != category.id else None,
            }
        )


class CategoryDeleteView(LoginRequiredMixin, View):
    """Delete category"""

    def post(self, request, category_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        try:
            category = get_object_or_404(Category, id=category_id)

            # Check if category has children
            if category.get_children().exists():
                return JsonResponse(
                    {
                        "success": False,
                        "error": _("لا يمكن حذف القسم لأنه يحتوي على أقسام فرعية"),
                    }
                )

            # Check if category has ads
            if category.classified_ads.exists():
                return JsonResponse(
                    {
                        "success": False,
                        "error": _("لا يمكن حذف القسم لأنه يحتوي على إعلانات"),
                    }
                )

            category.delete()
            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class AdUpgradeCheckoutView(LoginRequiredMixin, DetailView):
    """
    Checkout page for ad upgrades (featured, pinned, urgent)
    """

    model = ClassifiedAd
    template_name = "classifieds/ad_upgrade_checkout.html"
    context_object_name = "ad"

    def dispatch(self, request, *args, **kwargs):
        """Check phone verification before allowing ad upgrades"""
        # First check if user is authenticated (LoginRequiredMixin handles this)
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        # Check phone verification requirement
        from constance import config
        from content.site_config import SiteConfiguration

        # Check if phone verification is enabled from constance or site_config
        constance_enabled = getattr(config, "ENABLE_MOBILE_VERIFICATION", True)
        site_config = SiteConfiguration.get_solo()
        site_config_enabled = site_config.require_phone_verification

        # Phone verification is handled inline in the form

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Only allow users to upgrade their own ads
        return ClassifiedAd.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from constance import config

        # Get pricing from constance or use defaults
        # 7 days pricing
        context["featured_price"] = getattr(
            config, "FEATURED_AD_PRICE_7DAYS", Decimal("50.00")
        )
        context["pinned_price"] = getattr(
            config, "PINNED_AD_PRICE_7DAYS", Decimal("75.00")
        )
        context["urgent_price"] = getattr(
            config, "URGENT_AD_PRICE_7DAYS", Decimal("30.00")
        )

        # 14 days pricing (usually ~80% of double)
        context["featured_price_14"] = getattr(
            config, "FEATURED_AD_PRICE_14DAYS", Decimal("80.00")
        )
        context["pinned_price_14"] = getattr(
            config, "PINNED_AD_PRICE_14DAYS", Decimal("120.00")
        )
        context["urgent_price_14"] = getattr(
            config, "URGENT_AD_PRICE_14DAYS", Decimal("48.00")
        )

        # 30 days pricing (best value - ~150% of 7 days)
        context["featured_price_30"] = getattr(
            config, "FEATURED_AD_PRICE_30DAYS", Decimal("100.00")
        )
        context["pinned_price_30"] = getattr(
            config, "PINNED_AD_PRICE_30DAYS", Decimal("150.00")
        )
        context["urgent_price_30"] = getattr(
            config, "URGENT_AD_PRICE_30DAYS", Decimal("60.00")
        )

        # Top Search pricing
        context["top_search_price"] = getattr(
            config, "TOP_SEARCH_AD_PRICE_7DAYS", Decimal("60.00")
        )
        context["top_search_price_14"] = getattr(
            config, "TOP_SEARCH_AD_PRICE_14DAYS", Decimal("96.00")
        )
        context["top_search_price_30"] = getattr(
            config, "TOP_SEARCH_AD_PRICE_30DAYS", Decimal("120.00")
        )

        # Contact for Price pricing
        context["contact_price_price"] = getattr(
            config, "CONTACT_PRICE_AD_PRICE_7DAYS", Decimal("25.00")
        )
        context["contact_price_price_14"] = getattr(
            config, "CONTACT_PRICE_AD_PRICE_14DAYS", Decimal("40.00")
        )
        context["contact_price_price_30"] = getattr(
            config, "CONTACT_PRICE_AD_PRICE_30DAYS", Decimal("50.00")
        )

        # Facebook Share pricing (one-time)
        context["facebook_share_price"] = getattr(
            config, "FACEBOOK_SHARE_AD_PRICE", Decimal("35.00")
        )

        # Video feature pricing (one-time)
        context["video_price"] = getattr(config, "VIDEO_AD_PRICE", Decimal("45.00"))

        return context


class AdUpgradeProcessView(LoginRequiredMixin, View):
    """
    Process ad upgrade selections and redirect to payment
    """

    def post(self, request, pk):
        ad = get_object_or_404(ClassifiedAd, pk=pk, user=request.user)

        # Get selected upgrades
        upgrade_featured = request.POST.get("upgrade_featured") == "1"
        upgrade_pinned = request.POST.get("upgrade_pinned") == "1"
        upgrade_urgent = request.POST.get("upgrade_urgent") == "1"

        # Get durations (handle empty strings)
        featured_duration = int(request.POST.get("featured_duration") or 0)
        pinned_duration = int(request.POST.get("pinned_duration") or 0)
        urgent_duration = int(request.POST.get("urgent_duration") or 0)

        # Calculate total amount
        total_amount = Decimal("0.00")
        upgrades = []

        from constance import config

        if upgrade_featured and featured_duration > 0:
            if featured_duration == 7:
                price = Decimal(str(getattr(config, "FEATURED_AD_PRICE_7DAYS", 50.00)))
            elif featured_duration == 14:
                price = Decimal(str(getattr(config, "FEATURED_AD_PRICE_14DAYS", 80.00)))
            else:  # 30
                price = Decimal(
                    str(getattr(config, "FEATURED_AD_PRICE_30DAYS", 100.00))
                )

            total_amount += price
            upgrades.append(
                {
                    "type": "featured",
                    "duration": featured_duration,
                    "price": str(price),
                    "name": _("إعلان مميز"),
                }
            )

        if upgrade_pinned and pinned_duration > 0:
            if pinned_duration == 7:
                price = Decimal(str(getattr(config, "PINNED_AD_PRICE_7DAYS", 75.00)))
            elif pinned_duration == 14:
                price = Decimal(str(getattr(config, "PINNED_AD_PRICE_14DAYS", 120.00)))
            else:  # 30
                price = Decimal(str(getattr(config, "PINNED_AD_PRICE_30DAYS", 150.00)))

            total_amount += price
            upgrades.append(
                {
                    "type": "pinned",
                    "duration": pinned_duration,
                    "price": str(price),
                    "name": _("تثبيت في الأعلى"),
                }
            )

        if upgrade_urgent and urgent_duration > 0:
            if urgent_duration == 7:
                price = Decimal(str(getattr(config, "URGENT_AD_PRICE_7DAYS", 30.00)))
            elif urgent_duration == 14:
                price = Decimal(str(getattr(config, "URGENT_AD_PRICE_14DAYS", 48.00)))
            else:  # 30
                price = Decimal(str(getattr(config, "URGENT_AD_PRICE_30DAYS", 60.00)))

            total_amount += price
            upgrades.append(
                {
                    "type": "urgent",
                    "duration": urgent_duration,
                    "price": str(price),
                    "name": _("إعلان عاجل"),
                }
            )

        # Top Search feature
        upgrade_top_search = request.POST.get("upgrade_top_search") == "1"
        top_search_duration = int(request.POST.get("top_search_duration") or 0)

        if upgrade_top_search and top_search_duration > 0:
            if top_search_duration == 7:
                price = Decimal(
                    str(getattr(config, "TOP_SEARCH_AD_PRICE_7DAYS", 60.00))
                )
            elif top_search_duration == 14:
                price = Decimal(
                    str(getattr(config, "TOP_SEARCH_AD_PRICE_14DAYS", 96.00))
                )
            else:  # 30
                price = Decimal(
                    str(getattr(config, "TOP_SEARCH_AD_PRICE_30DAYS", 120.00))
                )

            total_amount += price
            upgrades.append(
                {
                    "type": "top_search",
                    "duration": top_search_duration,
                    "price": str(price),
                    "name": _("أعلى نتائج البحث"),
                }
            )

        # Contact for Price feature
        upgrade_contact_price = request.POST.get("upgrade_contact_price") == "1"
        contact_price_duration = int(request.POST.get("contact_price_duration") or 0)

        if upgrade_contact_price and contact_price_duration > 0:
            if contact_price_duration == 7:
                price = Decimal(
                    str(getattr(config, "CONTACT_PRICE_AD_PRICE_7DAYS", 25.00))
                )
            elif contact_price_duration == 14:
                price = Decimal(
                    str(getattr(config, "CONTACT_PRICE_AD_PRICE_14DAYS", 40.00))
                )
            else:  # 30
                price = Decimal(
                    str(getattr(config, "CONTACT_PRICE_AD_PRICE_30DAYS", 50.00))
                )

            total_amount += price
            upgrades.append(
                {
                    "type": "contact_for_price",
                    "duration": contact_price_duration,
                    "price": str(price),
                    "name": _("تواصل ليصلك عرض سعر"),
                }
            )

        # Facebook Share feature (one-time, no duration)
        upgrade_facebook_share = request.POST.get("upgrade_facebook_share") == "1"

        if upgrade_facebook_share:
            price = Decimal(str(getattr(config, "FACEBOOK_SHARE_AD_PRICE", 35.00)))
            total_amount += price
            upgrades.append(
                {
                    "type": "facebook_share",
                    "duration": 0,  # One-time
                    "price": str(price),
                    "name": _("نشر على فيسبوك"),
                }
            )

        # Video feature (one-time, no duration)
        upgrade_video = request.POST.get("upgrade_video") == "1"
        video_type = request.POST.get("video_type", "url")
        video_url = request.POST.get("video_url", "").strip()
        video_file = request.FILES.get("video_file")

        if upgrade_video:
            price = Decimal(str(getattr(config, "VIDEO_AD_PRICE", 45.00)))
            total_amount += price

            video_data = {
                "type": "video",
                "duration": 0,  # One-time
                "price": str(price),
                "name": _("إضافة فيديو"),
                "video_type": video_type,
            }

            if video_type == "url" and video_url:
                video_data["video_url"] = video_url
            elif video_type == "file" and video_file:
                # Store video file temporarily in session or handle it differently
                # For now, we'll save it directly to the ad after payment
                video_data["has_video_file"] = True

            upgrades.append(video_data)

            # Store video file in session for later processing
            if video_file:
                # Save the uploaded file temporarily
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                import uuid

                temp_filename = f"temp_videos/{uuid.uuid4()}_{video_file.name}"
                saved_path = default_storage.save(
                    temp_filename, ContentFile(video_file.read())
                )
                request.session["pending_video_file"] = saved_path

        if not upgrades:
            messages.warning(request, _("يرجى اختيار خيار ترقية واحد على الأقل"))
            return redirect("main:ad_upgrade_checkout", pk=ad.pk)

        # Store upgrade data in session for payment processing
        request.session["ad_upgrade"] = {
            "ad_id": ad.pk,
            "upgrades": upgrades,
            "total_amount": str(total_amount),
        }

        # Create payment record
        from .models import Payment

        payment = Payment.objects.create(
            user=request.user,
            provider="pending",  # Will be set when user selects payment method
            amount=total_amount,
            currency="EGP",
            status=Payment.PaymentStatus.PENDING,
            description=_("ترقية إعلان: {}").format(ad.title),
            metadata={"ad_id": ad.pk, "upgrades": upgrades},
        )

        # Redirect to payment page with payment ID
        return redirect("main:payment_page_upgrade", payment_id=payment.pk)


@require_http_methods(["GET"])
def get_category_custom_fields(request, category_id):
    """
    AJAX endpoint to fetch custom fields for a specific category.
    Returns HTML for the custom fields to be injected into the form.
    """
    from django.template.loader import render_to_string
    from .models import CategoryCustomField, Category

    try:
        # Don't filter by is_active here — the dropdown already only shows active
        # categories. Filtering by is_active caused fields to vanish when a category
        # was accidentally deactivated (e.g. by the admin edit bug).
        category = Category.objects.get(pk=category_id)

        # Get all active custom fields for this category
        category_fields = (
            CategoryCustomField.objects.filter(category=category, is_active=True)
            .select_related("custom_field")
            .order_by("order")
        )

        if not category_fields.exists():
            return JsonResponse({"success": True, "html": "", "has_fields": False})

        # Build form fields dynamically
        import re as _re
        fields_html = []
        for cf in category_fields:
            field = cf.custom_field
            safe_name = _re.sub(r'[^\w]', '_', field.name)
            field_name = f"custom_{safe_name}"
            field_label = field.label
            field_type = field.field_type
            is_required = cf.is_required

            # Create field HTML based on type
            field_html = render_to_string(
                "classifieds/partials/custom_field.html",
                {
                    "field_name": field_name,
                    "field_label": field_label,
                    "field_type": field_type,
                    "is_required": is_required,
                    "help_text": field.help_text or "",
                    "placeholder": field.placeholder or "",
                    "field_options": (
                        field.field_options.filter(is_active=True).order_by("order")
                        if field_type in ["select", "radio", "checkbox"]
                        else []
                    ),
                },
            )
            fields_html.append(field_html)

        return JsonResponse(
            {"success": True, "html": "".join(fields_html), "has_fields": True}
        )

    except Category.DoesNotExist:
        return JsonResponse({"success": True, "html": "", "has_fields": False})


# ========== Publisher Ad Management Actions ==========


@login_required
@require_POST
def publisher_toggle_cart(request, ad_id):
    """Toggle cart enabled status for an ad"""
    ad = get_object_or_404(
        ClassifiedAd, id=ad_id, user=request.user, deleted_at__isnull=True
    )

    # Toggle cart status
    ad.is_cart_enabled = not ad.is_cart_enabled
    ad.save(update_fields=["is_cart_enabled"])

    messages.success(
        request,
        (
            _("تم تفعيل السلة للإعلان")
            if ad.is_cart_enabled
            else _("تم إلغاء تفعيل السلة للإعلان")
        ),
    )
    return redirect("main:my_ads")


@login_required
@require_POST
def publisher_hide_ad(request, ad_id):
    """Hide an ad (change status to draft)"""
    ad = get_object_or_404(
        ClassifiedAd, id=ad_id, user=request.user, deleted_at__isnull=True
    )

    if ad.status == ClassifiedAd.AdStatus.ACTIVE:
        ad.status = ClassifiedAd.AdStatus.DRAFT
        ad.save(update_fields=["status"])
        messages.success(request, _("تم إخفاء الإعلان بنجاح"))
    else:
        messages.warning(request, _("يمكن إخفاء الإعلانات النشطة فقط"))

    return redirect("main:my_ads")


@login_required
@require_POST
def publisher_activate_ad(request, ad_id):
    """Activate a hidden ad (change status from draft to active)"""
    ad = get_object_or_404(
        ClassifiedAd, id=ad_id, user=request.user, deleted_at__isnull=True
    )

    if ad.status == ClassifiedAd.AdStatus.DRAFT:
        # Check if user has available ads in package
        from django.utils import timezone

        active_package = UserPackage.objects.filter(
            user=request.user, expiry_date__gte=timezone.now(), ads_remaining__gt=0
        ).first()

        if active_package:
            ad.status = ClassifiedAd.AdStatus.ACTIVE
            ad.save(update_fields=["status"])
            messages.success(request, _("تم تفعيل الإعلان بنجاح"))
        else:
            messages.error(
                request, _("ليس لديك رصيد إعلانات متاح. يرجى شراء باقة جديدة")
            )
    else:
        messages.warning(request, _("يمكن تفعيل الإعلانات المخفية فقط"))

    return redirect("main:my_ads")


@login_required
@require_POST
def publisher_restore_ad(request, ad_id):
    """Restore a deleted ad"""
    ad = get_object_or_404(
        ClassifiedAd, id=ad_id, user=request.user, deleted_at__isnull=False
    )

    ad.deleted_at = None
    ad.status = ClassifiedAd.AdStatus.DRAFT  # Restore as draft
    ad.save(update_fields=["deleted_at", "status"])

    messages.success(
        request, _("تم استعادة الإعلان بنجاح. يمكنك تفعيله من قائمة إعلاناتك")
    )
    return redirect("main:my_ads")


@login_required
@require_POST
def publisher_permanent_delete_ad(request, ad_id):
    """Permanently delete an ad"""
    ad = get_object_or_404(
        ClassifiedAd, id=ad_id, user=request.user, deleted_at__isnull=False
    )

    ad_title = ad.title
    ad.delete()  # Permanent deletion

    messages.success(request, _("تم حذف الإعلان '{}' نهائياً").format(ad_title))
    return redirect("main:my_ads")


@login_required
def publisher_renew_ad(request, ad_id):
    """Renew an expired ad"""
    ad = get_object_or_404(
        ClassifiedAd,
        id=ad_id,
        user=request.user,
        deleted_at__isnull=True,
        status=ClassifiedAd.AdStatus.EXPIRED,
    )

    from django.utils import timezone
    from datetime import timedelta

    # Check if user has available ads in package
    active_package = UserPackage.objects.filter(
        user=request.user, expiry_date__gte=timezone.now(), ads_remaining__gt=0
    ).first()

    if active_package:
        # Renew the ad
        ad.status = ClassifiedAd.AdStatus.ACTIVE
        ad.expires_at = timezone.now() + timedelta(
            days=active_package.package.duration_days
        )
        ad.save(update_fields=["status", "expires_at"])

        # Deduct from package
        active_package.ads_remaining -= 1
        active_package.save(update_fields=["ads_remaining"])

        messages.success(request, _("تم تجديد الإعلان بنجاح"))
    else:
        messages.error(request, _("ليس لديك رصيد إعلانات متاح. يرجى شراء باقة جديدة"))

    return redirect("main:my_ads")


class AdUnifiedUpgradeView(LoginRequiredMixin, DetailView):
    """
    Unified upgrade page combining all upgrades and features in one place
    """

    model = ClassifiedAd
    template_name = "classifieds/ad_unified_upgrade.html"
    context_object_name = "ad"

    def get_queryset(self):
        # Only allow users to upgrade their own ads
        return ClassifiedAd.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from constance import config
        from .models import UserPackage
        from content.models import SiteConfiguration

        # Get upgrade pricing from constance
        # 7 days pricing
        context["highlighted_price"] = getattr(
            config, "FEATURED_AD_PRICE_7DAYS", Decimal("50.00")
        )
        context["pinned_price"] = getattr(
            config, "PINNED_AD_PRICE_7DAYS", Decimal("75.00")
        )
        context["urgent_price"] = getattr(
            config, "URGENT_AD_PRICE_7DAYS", Decimal("30.00")
        )

        # 14 days pricing
        context["highlighted_price_14"] = getattr(
            config, "FEATURED_AD_PRICE_14DAYS", Decimal("80.00")
        )
        context["pinned_price_14"] = getattr(
            config, "PINNED_AD_PRICE_14DAYS", Decimal("120.00")
        )
        context["urgent_price_14"] = getattr(
            config, "URGENT_AD_PRICE_14DAYS", Decimal("48.00")
        )

        # 30 days pricing
        context["highlighted_price_30"] = getattr(
            config, "FEATURED_AD_PRICE_30DAYS", Decimal("100.00")
        )
        context["pinned_price_30"] = getattr(
            config, "PINNED_AD_PRICE_30DAYS", Decimal("150.00")
        )
        context["urgent_price_30"] = getattr(
            config, "URGENT_AD_PRICE_30DAYS", Decimal("60.00")
        )

        # Get user's active package for feature pricing
        active_package = (
            UserPackage.objects.filter(
                user=self.request.user,
                expiry_date__gte=timezone.now(),
            )
            .order_by("expiry_date")
            .first()
        )

        # Determine feature prices based on package or site defaults
        if active_package and active_package.package:
            package = active_package.package
            feature_prices = {
                "contact_for_price": package.feature_contact_for_price,
                "facebook_share": Decimal("100.00"),  # Fixed price for FB share
                "video": Decimal("75.00"),  # Fixed price for video (coming soon)
            }
        else:
            # Use site default prices or make features free/unavailable
            feature_prices = {
                "contact_for_price": Decimal("0.00"),  # Free without package
                "facebook_share": Decimal("100.00"),
                "video": Decimal("75.00"),
            }

        context["feature_prices"] = feature_prices
        context["site_config"] = SiteConfiguration.get_solo()

        return context


class AdUnifiedUpgradeProcessView(LoginRequiredMixin, View):
    """
    Process unified upgrade selections (both upgrades and features) and redirect to payment
    """

    def post(self, request, pk):
        ad = get_object_or_404(ClassifiedAd, pk=pk, user=request.user)

        # Get selected upgrades
        upgrade_highlighted = request.POST.get("upgrade_highlighted") == "1"
        upgrade_pinned = request.POST.get("upgrade_pinned") == "1"
        upgrade_urgent = request.POST.get("upgrade_urgent") == "1"

        # Get selected features
        feature_contact = request.POST.get("feature_contact_for_price") == "1"
        feature_facebook = request.POST.get("feature_facebook_share") == "1"

        # Get durations for upgrades
        highlighted_duration = int(request.POST.get("highlighted_duration") or 0)
        pinned_duration = int(request.POST.get("pinned_duration") or 0)
        urgent_duration = int(request.POST.get("urgent_duration") or 0)

        # Calculate total amount
        total_amount = Decimal("0.00")
        upgrades = []
        features_to_enable = {}

        from constance import config
        from .models import UserPackage

        # Process upgrades
        if upgrade_highlighted and highlighted_duration > 0:
            if highlighted_duration == 7:
                price = Decimal(str(getattr(config, "FEATURED_AD_PRICE_7DAYS", 50.00)))
            elif highlighted_duration == 14:
                price = Decimal(str(getattr(config, "FEATURED_AD_PRICE_14DAYS", 80.00)))
            else:  # 30
                price = Decimal(
                    str(getattr(config, "FEATURED_AD_PRICE_30DAYS", 100.00))
                )

            total_amount += price
            upgrades.append(
                {
                    "type": "featured",
                    "duration": highlighted_duration,
                    "price": str(price),
                    "name": _("إعلان مميز"),
                }
            )

        if upgrade_pinned and pinned_duration > 0:
            if pinned_duration == 7:
                price = Decimal(str(getattr(config, "PINNED_AD_PRICE_7DAYS", 75.00)))
            elif pinned_duration == 14:
                price = Decimal(str(getattr(config, "PINNED_AD_PRICE_14DAYS", 120.00)))
            else:  # 30
                price = Decimal(str(getattr(config, "PINNED_AD_PRICE_30DAYS", 150.00)))

            total_amount += price
            upgrades.append(
                {
                    "type": "pinned",
                    "duration": pinned_duration,
                    "price": str(price),
                    "name": _("تثبيت في الأعلى"),
                }
            )

        if upgrade_urgent and urgent_duration > 0:
            if urgent_duration == 7:
                price = Decimal(str(getattr(config, "URGENT_AD_PRICE_7DAYS", 30.00)))
            elif urgent_duration == 14:
                price = Decimal(str(getattr(config, "URGENT_AD_PRICE_14DAYS", 48.00)))
            else:  # 30
                price = Decimal(str(getattr(config, "URGENT_AD_PRICE_30DAYS", 60.00)))

            total_amount += price
            upgrades.append(
                {
                    "type": "urgent",
                    "duration": urgent_duration,
                    "price": str(price),
                    "name": _("إعلان عاجل"),
                }
            )

        # Get feature prices
        active_package = (
            UserPackage.objects.filter(
                user=request.user,
                expiry_date__gte=timezone.now(),
            )
            .order_by("expiry_date")
            .first()
        )

        if active_package and active_package.package:
            package = active_package.package
            contact_price = package.feature_contact_for_price
        else:
            contact_price = Decimal("0.00")

        facebook_price = Decimal("100.00")
        video_price = Decimal("75.00")

        # Process features
        if feature_contact and not ad.contact_for_price:
            total_amount += contact_price
            features_to_enable["contact_for_price"] = True

        if feature_facebook and not ad.share_on_facebook:
            total_amount += facebook_price
            features_to_enable["facebook_share"] = True

        # Video feature
        feature_video = request.POST.get("feature_video") == "1"
        video_type = request.POST.get("video_type", "url")
        video_url = request.POST.get("video_url", "").strip()
        video_file = request.FILES.get("video_file")

        if feature_video and not ad.video_url and not ad.video_file:
            total_amount += video_price
            features_to_enable["video"] = True
            features_to_enable["video_type"] = video_type
            if video_type == "url" and video_url:
                features_to_enable["video_url"] = video_url
            elif video_type == "file" and video_file:
                # Store video file temporarily
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                import uuid

                temp_filename = f"temp_videos/{uuid.uuid4()}_{video_file.name}"
                saved_path = default_storage.save(
                    temp_filename, ContentFile(video_file.read())
                )
                request.session["pending_video_file"] = saved_path
                features_to_enable["has_video_file"] = True

        # If nothing selected
        if not upgrades and not features_to_enable:
            messages.warning(request, _("لم يتم اختيار أي مميزات أو ترقيات"))
            return redirect("main:ad_unified_upgrade", pk=ad.pk)

        # Store in session
        request.session["ad_upgrade_id"] = ad.pk
        request.session["ad_upgrades"] = upgrades
        request.session["upgrade_features"] = features_to_enable
        request.session["upgrade_total_cost"] = str(total_amount)

        if total_amount > 0:
            # Redirect to payment
            currency = ad.country.currency_symbol if ad.country else "ج.م"
            messages.info(
                request,
                _(
                    "يرجى إتمام الدفع لتفعيل المميزات والترقيات. المبلغ المطلوب: {} {}"
                ).format(total_amount, currency),
            )
            return redirect("main:ad_upgrade_payment", ad_id=ad.pk)
        else:
            # Free features - activate immediately
            from .models import FacebookShareRequest

            updated_items = []

            if features_to_enable.get("contact_for_price"):
                ad.contact_for_price = True
                updated_items.append(_("تواصل ليصلك عرض سعر"))

            if features_to_enable.get("facebook_share"):
                ad.share_on_facebook = True
                ad.facebook_share_requested = True
                updated_items.append(_("نشر على فيسبوك"))

                FacebookShareRequest.objects.create(
                    ad=ad,
                    user=request.user,
                    payment_confirmed=True,
                    payment_amount=Decimal("0.00"),
                )

            # Handle video feature
            if features_to_enable.get("video"):
                if features_to_enable.get("video_url"):
                    ad.video_url = features_to_enable["video_url"]
                    updated_items.append(_("إضافة فيديو"))
                elif features_to_enable.get("has_video_file"):
                    # Move temp video file to permanent location
                    temp_path = request.session.get("pending_video_file")
                    if temp_path:
                        from django.core.files.storage import default_storage
                        import os

                        # Read temp file and save to ad
                        with default_storage.open(temp_path) as f:
                            filename = os.path.basename(temp_path)
                            ad.video_file.save(filename, f, save=False)

                        # Delete temp file
                        default_storage.delete(temp_path)
                        del request.session["pending_video_file"]
                        updated_items.append(_("إضافة فيديو"))

            ad.save()
            messages.success(
                request,
                _("تم تحديث مميزات الإعلان: ") + ", ".join(updated_items),
            )
            return redirect("main:ad_detail", ad_id=ad.pk)

        return redirect("main:ad_detail", ad_id=ad.pk)
