from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, F, IntegerField, Value, When
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
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

    def get_queryset(self):
        # Start with only active ads for the selected country
        selected_country = get_selected_country_from_request(self.request)
        queryset = ClassifiedAd.objects.active_for_country(selected_country)
        return queryset


class MyClassifiedAdsView(LoginRequiredMixin, ListView):
    """View to list the current user's classified ads."""

    model = ClassifiedAd
    template_name = "classifieds/my_ads_list.html"
    context_object_name = "ads"

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
        Check user's ad balance before allowing ad creation.
        If ads_remaining = 0, redirect to packages page.
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

        user = request.user

        # Check if user has any active package with remaining ads
        active_package = (
            UserPackage.objects.filter(
                user=user,
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

        # Store remaining ads count in session for display
        request.session["ads_remaining"] = active_package.ads_remaining

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
                self.request.POST, self.request.FILES, prefix="images"
            )
        else:
            # Limit extra forms to 5 as requested
            AdImageFormSet.extra = 5
            context["image_formset"] = AdImageFormSet(
                prefix="images", queryset=AdImage.objects.none()
            )

        context["ad_categories"] = Category.objects.filter(
            section_type=Category.SectionType.CLASSIFIED,
            is_active=True,
            parent__isnull=True,  # Only root categories
        ).prefetch_related("subcategories")
        context["active_nav"] = "create_ad"
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Auto-approve ads for verified users
        if self.request.user.verification_status == User.VerificationStatus.VERIFIED:
            form.instance.status = ClassifiedAd.AdStatus.ACTIVE
            messages.success(
                self.request, _("إعلانك نشط الآن لأنه تم التحقق من حسابك.")
            )
        else:
            form.instance.status = ClassifiedAd.AdStatus.PENDING
            messages.info(self.request, _("تم إرسال إعلانك للمراجعة وسيتم نشره قريباً."))

        context = self.get_context_data()
        image_formset = context["image_formset"]

        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()

            # Decrement ad count from user's package
            active_package = (
                UserPackage.objects.filter(user=self.request.user, ads_remaining__gt=0)
                .order_by("expiry_date")
                .first()
            )
            if active_package:
                active_package.use_ad()

            return redirect("main:ad_create_success", pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ClassifiedAdUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing classified ad."""

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:my_ads")

    def get_queryset(self):
        # Ensure users can only edit their own ads
        return ClassifiedAd.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = AdImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="images",
            )
        else:
            # Limit extra forms to 5
            AdImageFormSet.extra = 5 - self.object.images.count()
            context["image_formset"] = AdImageFormSet(
                instance=self.object, prefix="images", queryset=self.object.images.all()
            )
        context["ad_categories"] = Category.objects.filter(
            section_type=Category.SectionType.CLASSIFIED,
            is_active=True,
            parent__isnull=True,  # Only root categories
        ).prefetch_related("subcategories")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.save()
            messages.success(self.request, _("تم تحديث الإعلان بنجاح!"))
            return redirect(self.get_success_url())
        else:
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
        """Override dispatch to handle inactive ads gracefully."""
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
        return ClassifiedAd.objects.all()

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
            search.email_notifications = "email_notifications" in request.POST
            search.save(update_fields=["email_notifications"])
            messages.success(request, _("تم تحديث تفضيلات الإشعارات بنجاح."))
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

        # إذا كان المستخدم غير موثق، عرض الباقات المجانية فقط
        # If user is not verified, show only free packages
        if (
            self.request.user.is_authenticated
            and not self.request.user.is_email_verified
        ):
            all_packages = all_packages.filter(price=0)

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

        # إضافة معلومة إذا كان المستخدم غير موثق
        if (
            self.request.user.is_authenticated
            and not self.request.user.is_email_verified
        ):
            context["show_verification_notice"] = True

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
            # Redirect to payment gateway
            # TODO: Integrate with payment gateway
            messages.info(request, _("سيتم تحويلك إلى بوابة الدفع لإتمام عملية الشراء"))
            return redirect("main:packages_list")

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
        order = request.POST.get("order") or 0
        icon = request.POST.get("icon", "")
        color = request.POST.get("color", "")
        country_code = request.POST.get("country")  # optional

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
            category.section_type = section_type
            category.description = description

            # Save bilingual descriptions if model supports them
            if hasattr(category, "description_ar"):
                category.description_ar = description_ar
            if hasattr(category, "description_en"):
                category.description_en = description_en

            category.icon = icon
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
            currency="SAR",
            status=Payment.PaymentStatus.PENDING,
            description=_("ترقية إعلان: {}").format(ad.title),
            metadata={"ad_id": ad.pk, "upgrades": upgrades},
        )

        # Redirect to payment page with payment ID
        return redirect("main:payment_page_upgrade", payment_id=payment.pk)
