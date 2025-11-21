from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, F, IntegerField, Value, When
from django.http import JsonResponse
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
        return context


class ClassifiedAdCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new classified ad."""

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:my_ads")

    def dispatch(self, request, *args, **kwargs):
        """
        Allow access only if the user has an active package with remaining ads.
        If none, redirect to packages page to acquire a package (free or paid).
        """
        user = request.user

        # Require an active user package with remaining ads
        has_quota = (
            UserPackage.objects.filter(
                user=user,
                expiry_date__gte=timezone.now(),
                ads_remaining__gt=0,
            )
            .order_by("expiry_date")
            .exists()
        )

        if not has_quota:
            messages.error(
                request,
                _(
                    "لقد استنفدت إعلانك المجاني! يرجى شراء باقة للاستمرار في نشر الإعلانات."
                ),
            )
            return redirect("main:packages_list")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pass user to form for mobile verification"""
        kwargs = super().get_form_kwargs()
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
            section_type=Category.SectionType.CLASSIFIED, is_active=True
        )
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
            section_type=Category.SectionType.CLASSIFIED, is_active=True
        )
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

    def get_queryset(self):
        # Only show active ads to the public
        return ClassifiedAd.objects.filter(status=ClassifiedAd.AdStatus.ACTIVE)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count without causing a race condition
        ClassifiedAd.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        # obj.refresh_from_db() # The template will display the updated count
        return obj

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
            .order_by("-relevance_score", "-created_at")[:3]
        )

        context["related_ads"] = related_ads
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

        ad = get_object_or_404(ClassifiedAd, id=ad_id)

        import json

        data = json.loads(request.body)
        ad.is_hidden = data.get("hide", False)
        ad.save()

        # Send notification to user
        Notification.objects.create(
            user=ad.user,
            title=_("تغيير حالة الإعلان"),
            message=_("تم {} إعلانك '{}'").format(
                _("إخفاء") if ad.is_hidden else _("إظهار"), ad.title
            ),
            link=ad.get_absolute_url(),
        )

        return JsonResponse({"success": True})


class EnableAdCartView(LoginRequiredMixin, View):
    """AJAX view to enable cart for an ad"""

    def post(self, request, ad_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        ad = get_object_or_404(ClassifiedAd, id=ad_id)

        if not ad.allow_cart:
            return JsonResponse(
                {"success": False, "error": "Cart not allowed for this ad"}, status=400
            )

        ad.cart_enabled_by_admin = True
        ad.save()

        # Send notification to user
        Notification.objects.create(
            user=ad.user,
            title=_("تفعيل السلة"),
            message=_("تم تفعيل السلة لإعلانك '{}'").format(ad.title),
            link=ad.get_absolute_url(),
        )

        return JsonResponse({"success": True})


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
        context["all_categories"] = Category.objects.filter(parent__isnull=True)
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
        slug = request.POST.get("slug")
        slug_ar = request.POST.get("slug_ar")
        parent_id = request.POST.get("parent")
        section_type = request.POST.get("section_type")
        description = request.POST.get("description", "")
        allow_cart = request.POST.get("allow_cart") == "on"
        require_admin_approval = request.POST.get("require_admin_approval") == "on"
        is_active = request.POST.get("is_active") == "on"
        order = request.POST.get("order") or 0
        icon = request.POST.get("icon", "")
        color = request.POST.get("color", "")
        country_code = request.POST.get("country")  # optional

        try:
            if category_id:
                # Update existing category
                category = Category.objects.get(id=category_id)
            else:
                # Create new category
                category = Category()

            # Basic required fields
            category.name = name
            category.name_ar = name_ar
            category.slug = slug
            category.slug_ar = slug_ar
            category.section_type = section_type
            category.description = description
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
                "slug": category.slug,
                "slug_ar": category.slug_ar,
                "parent": category.parent_id if category.parent else None,
                "section_type": category.section_type,
                "description": category.description,
                "allow_cart": getattr(category, "allow_cart", False),
                "require_admin_approval": getattr(
                    category, "require_admin_approval", True
                ),
                "is_active": category.is_active,
                "order": getattr(category, "order", 0),
                "icon": getattr(category, "icon", ""),
                "color": getattr(category, "color", ""),
                "country": getattr(category.country, "code", None),
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
