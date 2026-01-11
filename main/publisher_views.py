"""
Publisher Dashboard Views - CRUD Operations
Full CRUD operations for publishers to manage their own ads and upgrades
"""

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Sum
from django.db import models
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from datetime import timedelta

from main.models import (
    ClassifiedAd,
    AdUpgradeHistory,
    UserPackage,
    Notification,
    AdPackage,
    Payment,
)
from main.decorators import PublisherRequiredMixin, publisher_required


# ============================================================================
# PUBLISHER AD CRUD OPERATIONS
# ============================================================================


class PublisherMyAdsView(PublisherRequiredMixin, ListView):
    """
    Publisher's own ads list with filters
    """

    model = ClassifiedAd
    template_name = "dashboard/publisher_my_ads.html"
    context_object_name = "ads"
    paginate_by = 20

    def get_queryset(self):
        from content.site_config import SiteConfiguration

        config = SiteConfiguration.get_solo()

        # Base queryset - include all ads by default (even soft-deleted)
        queryset = (
            ClassifiedAd.objects.filter(user=self.request.user)
            .select_related("category", "country")
            .prefetch_related("images", "upgrade_history")
            .order_by("-is_pinned", "-is_urgent", "-is_highlighted", "-created_at")
        )

        # Check and expire old upgrades
        for ad in queryset:
            ad.check_and_expire_upgrades()

        # Filters
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Filter for deleted ads
        show_deleted = self.request.GET.get("deleted")
        if show_deleted == "true" and config.show_deleted_ads_to_publisher:
            queryset = queryset.filter(deleted_at__isnull=False)
        elif show_deleted != "true":
            # By default, exclude soft-deleted ads unless specifically requested
            queryset = queryset.filter(deleted_at__isnull=True)

        # Filter for resubmitted ads
        resubmitted = self.request.GET.get("resubmitted")
        if resubmitted == "true":
            queryset = queryset.filter(is_resubmitted=True)

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        from content.site_config import SiteConfiguration

        context = super().get_context_data(**kwargs)
        config = SiteConfiguration.get_solo()

        # Get all user ads (including deleted for counting)
        user_ads = ClassifiedAd.objects.filter(user=self.request.user)

        # Non-deleted ads
        active_ads = user_ads.filter(deleted_at__isnull=True)

        # Deleted ads
        deleted_ads = user_ads.filter(deleted_at__isnull=False)

        context["stats"] = {
            "total": active_ads.count(),
            "active": active_ads.filter(status="active").count(),
            "pending": active_ads.filter(status="pending").count(),
            "resubmitted": active_ads.filter(
                status="pending", is_resubmitted=True
            ).count(),
            "expired": active_ads.filter(status="expired").count(),
            "draft": active_ads.filter(status="draft").count(),
            "highlighted": active_ads.filter(is_highlighted=True).count(),
            "urgent": active_ads.filter(is_urgent=True).count(),
            "pinned": active_ads.filter(is_pinned=True).count(),
            "deleted": deleted_ads.count(),
        }

        # Ad balance
        active_packages = UserPackage.objects.filter(
            user=self.request.user, expiry_date__gte=timezone.now(), ads_remaining__gt=0
        )

        context["ad_balance"] = {
            "total": sum(pkg.total_ads() for pkg in active_packages),
            "used": sum(pkg.ads_used for pkg in active_packages),
            "available": sum(pkg.ads_remaining for pkg in active_packages),
        }

        context["current_filters"] = {
            "status": self.request.GET.get("status", ""),
            "search": self.request.GET.get("search", ""),
            "deleted": self.request.GET.get("deleted", ""),
        }

        context["status_choices"] = ClassifiedAd.AdStatus.choices
        context["show_deleted_to_publisher"] = config.show_deleted_ads_to_publisher
        context["show_expired_to_publisher"] = config.show_expired_ads_to_publisher
        context["deleted_retention_days"] = config.deleted_ads_retention_days
        context["expired_retention_days"] = config.expired_ads_retention_days

        return context


class PublisherAdDetailView(PublisherRequiredMixin, DetailView):
    """
    Publisher's ad detail view
    """

    model = ClassifiedAd
    template_name = "dashboard/publisher_ad_detail.html"
    context_object_name = "ad"
    pk_url_kwarg = "ad_id"

    def get_queryset(self):
        # Only show user's own ads
        return ClassifiedAd.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.object

        # Check and expire old upgrades
        ad.check_and_expire_upgrades()

        # Get upgrade history
        context["upgrade_history"] = ad.upgrade_history.all().order_by("-created_at")
        context["active_upgrades"] = ad.get_active_upgrades()

        # Stats
        context["stats"] = {
            "total_views": ad.views_count,
            "total_favorites": ad.favorited_by.count(),
            "days_since_created": (timezone.now() - ad.created_at).days,
        }

        # Available upgrade packages
        context["upgrade_packages"] = AdPackage.objects.filter(is_active=True)

        return context


class PublisherAdUpdateView(PublisherRequiredMixin, UpdateView):
    """
    Publisher edit own ad
    """

    model = ClassifiedAd
    template_name = "dashboard/publisher_ad_form.html"
    fields = [
        "title",
        "description",
        "price",
        "category",
        "subcategory",
        "country",
        "city",
        "status",
    ]
    pk_url_kwarg = "ad_id"

    def get_queryset(self):
        # Only allow editing own ads
        return ClassifiedAd.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            "main:publisher_ad_detail", kwargs={"ad_id": self.object.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"تعديل الإعلان: {self.object.title}"
        context["form_action"] = "update"
        return context

    def form_valid(self, form):
        # If status changed to active, check if user has available ads
        if form.instance.status == "active" and form.instance.pk:
            old_status = ClassifiedAd.objects.get(pk=form.instance.pk).status
            if old_status != "active":
                # Check ad balance
                active_packages = UserPackage.objects.filter(
                    user=self.request.user,
                    expiry_date__gte=timezone.now(),
                    ads_remaining__gt=0,
                )
                if not active_packages.exists():
                    messages.error(
                        self.request, "ليس لديك رصيد إعلاني كافٍ. يرجى شراء باقة جديدة."
                    )
                    return self.form_invalid(form)

        messages.success(
            self.request, f'تم تحديث الإعلان "{form.instance.title}" بنجاح.'
        )
        return super().form_valid(form)


class PublisherAdDeleteView(PublisherRequiredMixin, DeleteView):
    """
    Publisher delete own ad
    """

    model = ClassifiedAd
    template_name = "dashboard/publisher_ad_confirm_delete.html"
    pk_url_kwarg = "ad_id"
    success_url = reverse_lazy("main:publisher_my_ads")

    def get_queryset(self):
        # Only allow deleting own ads
        return ClassifiedAd.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        ad = self.get_object()
        title = ad.title
        messages.warning(request, f'تم حذف الإعلان "{title}" بنجاح.')
        return super().delete(request, *args, **kwargs)


@publisher_required
@require_POST
def publisher_renew_ad(request, ad_id):
    """
    Renew an expired ad
    """
    ad = get_object_or_404(ClassifiedAd, pk=ad_id, user=request.user)

    if ad.status != ClassifiedAd.AdStatus.EXPIRED:
        messages.error(request, "يمكن فقط تجديد الإعلانات المنتهية.")
        return redirect("main:publisher_ad_detail", ad_id=ad_id)

    # Check ad balance
    active_packages = UserPackage.objects.filter(
        user=request.user, expiry_date__gte=timezone.now(), ads_remaining__gt=0
    )

    if not active_packages.exists():
        messages.error(request, "ليس لديك رصيد إعلاني كافٍ. يرجى شراء باقة جديدة.")
        return redirect("main:publisher_ad_detail", ad_id=ad_id)

    # Renew the ad
    ad.status = ClassifiedAd.AdStatus.PENDING
    ad.save()

    # Deduct from package
    package = active_packages.first()
    package.ads_used += 1
    package.save()

    messages.success(
        request, f'تم تجديد الإعلان "{ad.title}" بنجاح. الآن في حالة المراجعة.'
    )
    return redirect("main:publisher_ad_detail", ad_id=ad_id)


@publisher_required
@require_POST
def publisher_change_ad_status(request, ad_id):
    """
    Change ad status (activate/deactivate)
    """
    ad = get_object_or_404(ClassifiedAd, pk=ad_id, user=request.user)
    new_status = request.POST.get("status")

    if new_status not in dict(ClassifiedAd.AdStatus.choices):
        return JsonResponse({"error": "حالة غير صالحة"}, status=400)

    # If activating, check balance
    if new_status == "active" and ad.status != "active":
        active_packages = UserPackage.objects.filter(
            user=request.user, expiry_date__gte=timezone.now(), ads_remaining__gt=0
        )
        if not active_packages.exists():
            return JsonResponse({"error": "ليس لديك رصيد إعلاني كافٍ"}, status=400)

    ad.status = new_status
    ad.save()

    return JsonResponse(
        {
            "success": True,
            "message": f"تم تغيير حالة الإعلان إلى {ad.get_status_display()}",
            "new_status": ad.status,
        }
    )


# ============================================================================
# PUBLISHER UPGRADE MANAGEMENT
# ============================================================================


class PublisherUpgradeHistoryView(PublisherRequiredMixin, ListView):
    """
    Publisher's upgrade history
    """

    model = AdUpgradeHistory
    template_name = "dashboard/publisher_upgrade_history.html"
    context_object_name = "upgrades"
    paginate_by = 20

    def get_queryset(self):
        return (
            AdUpgradeHistory.objects.filter(ad__user=self.request.user)
            .select_related("ad")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_upgrades = AdUpgradeHistory.objects.filter(ad__user=self.request.user)

        context["stats"] = {
            "total": user_upgrades.count(),
            "active": user_upgrades.filter(is_active=True).count(),
            "expired": user_upgrades.filter(is_active=False).count(),
            "total_spent": user_upgrades.aggregate(total=models.Sum("price_paid"))[
                "total"
            ]
            or 0,
        }

        return context


class PublisherUpgradeCreateView(PublisherRequiredMixin, CreateView):
    """
    Publisher purchase upgrade for ad
    """

    model = AdUpgradeHistory
    template_name = "dashboard/publisher_upgrade_form.html"
    fields = ["ad", "upgrade_type", "duration_days"]
    success_url = reverse_lazy("main:publisher_upgrade_history")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show user's own ads in dropdown
        form.fields["ad"].queryset = ClassifiedAd.objects.filter(
            user=self.request.user, status="active"
        )
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "شراء ترقية جديدة"
        context["upgrade_packages"] = AdPackage.objects.filter(is_active=True)

        # Pre-fill ad from URL parameter
        ad_id = self.request.GET.get("ad_id")
        if ad_id:
            context["selected_ad_id"] = ad_id

        return context

    def form_valid(self, form):
        upgrade = form.instance

        # Set prices based on upgrade type
        prices = {
            "HIGHLIGHTED": 50.00,
            "URGENT": 30.00,
            "PINNED": 100.00,
        }

        upgrade.price_paid = prices.get(upgrade.upgrade_type, 0)
        upgrade.start_date = timezone.now()
        upgrade.end_date = upgrade.start_date + timedelta(days=upgrade.duration_days)
        upgrade.is_active = True

        # Save upgrade
        upgrade.save()

        # Activate on ad
        if upgrade.upgrade_type == "HIGHLIGHTED":
            upgrade.ad.is_highlighted = True
        elif upgrade.upgrade_type == "URGENT":
            upgrade.ad.is_urgent = True
        elif upgrade.upgrade_type == "PINNED":
            upgrade.ad.is_pinned = True
        upgrade.ad.save()

        messages.success(
            self.request, f"تم شراء ترقية {upgrade.get_upgrade_type_display()} بنجاح!"
        )

        # Create notification
        Notification.objects.create(
            user=self.request.user,
            title="تم شراء ترقية جديدة",
            message=f'تم تفعيل ترقية {upgrade.get_upgrade_type_display()} على إعلانك "{upgrade.ad.title}"',
            notification_type="upgrade_purchased",
        )

        return super().form_valid(form)


@publisher_required
@require_POST
def publisher_cancel_upgrade(request, upgrade_id):
    """
    Cancel an active upgrade
    """
    upgrade = get_object_or_404(AdUpgradeHistory, pk=upgrade_id, ad__user=request.user)

    if not upgrade.is_active:
        return JsonResponse({"error": "الترقية غير نشطة بالفعل"}, status=400)

    # Deactivate upgrade
    upgrade.deactivate()

    return JsonResponse({"success": True, "message": "تم إلغاء الترقية بنجاح"})


# ============================================================================
# PUBLISHER STATISTICS & REPORTS
# ============================================================================


@publisher_required
def publisher_ad_statistics(request, ad_id):
    """
    Detailed statistics for a specific ad
    """
    ad = get_object_or_404(ClassifiedAd, pk=ad_id, user=request.user)

    # Calculate statistics
    stats = {
        "views_total": ad.views_count,
        "favorites_total": ad.favorited_by.count(),
        "days_active": (timezone.now() - ad.created_at).days,
        "upgrade_history": ad.upgrade_history.all().order_by("-created_at"),
        "active_upgrades": ad.get_active_upgrades(),
        "total_spent_on_upgrades": ad.upgrade_history.aggregate(
            total=models.Sum("price_paid")
        )["total"]
        or 0,
    }

    return render(
        request, "dashboard/publisher_ad_statistics.html", {"ad": ad, "stats": stats}
    )


@publisher_required
def publisher_dashboard_stats_ajax(request):
    """
    AJAX endpoint for dashboard statistics refresh
    """
    user_ads = ClassifiedAd.objects.filter(user=request.user)

    stats = {
        "total_ads": user_ads.count(),
        "active_ads": user_ads.filter(status="active").count(),
        "pending_ads": user_ads.filter(status="pending").count(),
        "expired_ads": user_ads.filter(status="expired").count(),
        "total_views": user_ads.aggregate(total=models.Sum("views_count"))["total"]
        or 0,
        "highlighted_ads": user_ads.filter(is_highlighted=True).count(),
        "urgent_ads": user_ads.filter(is_urgent=True).count(),
        "pinned_ads": user_ads.filter(is_pinned=True).count(),
    }

    return JsonResponse(stats)


# ============================================================================
# EXPIRED ADS & RENEWAL
# ============================================================================


class PublisherExpiredAdsView(PublisherRequiredMixin, ListView):
    """
    View expired ads with renewal options
    """

    model = ClassifiedAd
    template_name = "dashboard/expired_ads.html"
    context_object_name = "expired_ads"
    paginate_by = 20

    def get_queryset(self):
        # Get only expired ads or ads expiring soon
        queryset = (
            ClassifiedAd.objects.filter(user=self.request.user)
            .select_related("category", "country")
            .prefetch_related("images")
        )

        # Filter for expired or expiring soon
        queryset = queryset.filter(
            Q(status=ClassifiedAd.AdStatus.EXPIRED)
            | Q(
                status=ClassifiedAd.AdStatus.ACTIVE,
                expires_at__isnull=False,
                expires_at__lte=timezone.now() + timedelta(days=7),
            )
        ).order_by("expires_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "expired_ads"

        # Count expired vs expiring soon
        expired_count = (
            self.get_queryset().filter(status=ClassifiedAd.AdStatus.EXPIRED).count()
        )
        expiring_soon_count = (
            self.get_queryset().filter(status=ClassifiedAd.AdStatus.ACTIVE).count()
        )

        context["stats"] = {
            "expired": expired_count,
            "expiring_soon": expiring_soon_count,
            "total": expired_count + expiring_soon_count,
        }

        return context


@publisher_required
def publisher_renew_ad_options(request, ad_id):
    """
    Show renewal options for an ad
    """
    ad = get_object_or_404(ClassifiedAd, pk=ad_id, user=request.user)

    # Check if ad can be renewed
    if not ad.can_be_renewed():
        messages.error(request, "هذا الإعلان لا يمكن تجديده في الوقت الحالي.")
        return redirect("main:publisher_my_ads")

    # Get renewal options
    renewal_options = ad.get_renewal_options()

    context = {
        "ad": ad,
        "renewal_options": renewal_options,
        "days_left": ad.days_until_expiry(),
        "is_expired": ad.is_expired(),
    }

    return render(request, "dashboard/renew_ad_options.html", context)


@publisher_required
@require_POST
def publisher_process_renewal(request, ad_id):
    """
    Process ad renewal with selected option
    """
    ad = get_object_or_404(ClassifiedAd, pk=ad_id, user=request.user)

    # Check if ad can be renewed
    if not ad.can_be_renewed():
        return JsonResponse(
            {
                "success": False,
                "message": "هذا الإعلان لا يمكن تجديده في الوقت الحالي.",
            },
            status=400,
        )

    # Get selected renewal type
    renewal_type = request.POST.get("renewal_type")
    renew_upgrades = request.POST.get("renew_upgrades") == "true"

    # Get renewal options
    renewal_options = ad.get_renewal_options()
    selected_option = next(
        (opt for opt in renewal_options if opt["type"] == renewal_type), None
    )

    if not selected_option:
        return JsonResponse(
            {"success": False, "message": "خيار التجديد غير صالح."}, status=400
        )

    # Check if payment required
    if selected_option["price"] > 0:
        # For paid renewals, create payment intent or redirect to payment
        # This is a placeholder - implement payment logic here
        return JsonResponse(
            {
                "success": False,
                "message": "يتطلب هذا الخيار الدفع. سيتم توجيهك لصفحة الدفع.",
                "requires_payment": True,
                "amount": float(selected_option["price"]),
                "payment_url": f"/payments/renew-ad/{ad_id}/?type={renewal_type}",
            }
        )

    # Process free renewal
    success = ad.renew(
        duration_days=selected_option["duration_days"],
        is_free=True,
        renew_upgrades=renew_upgrades,
    )

    if success:
        # Create notification
        Notification.objects.create(
            user=request.user,
            notification_type="ad_renewed",
            message_ar=f'تم تجديد إعلانك "{ad.title}" بنجاح لمدة {selected_option["duration_days"]} يوم.',
            message_en=f'Your ad "{ad.title}" has been renewed for {selected_option["duration_days"]} days.',
            related_ad=ad,
        )

        return JsonResponse(
            {
                "success": True,
                "message": f'تم تجديد الإعلان بنجاح لمدة {selected_option["duration_days"]} يوم!',
                "new_expiry": ad.expires_at.strftime("%Y-%m-%d"),
                "redirect_url": reverse_lazy("main:publisher_my_ads"),
            }
        )
    else:
        return JsonResponse(
            {
                "success": False,
                "message": "حدث خطأ أثناء تجديد الإعلان. يرجى المحاولة مرة أخرى.",
            },
            status=500,
        )


@publisher_required
def publisher_payment_history(request):
    """
    عرض سجل المدفوعات للعضو
    Display payment history for the publisher
    """
    payments = (
        Payment.objects.filter(user=request.user)
        .select_related("user")
        .prefetch_related("packages")
        .order_by("-created_at")
    )

    # Add package info from metadata for each payment
    for payment in payments:
        if payment.metadata.get("package_id"):
            try:
                payment.package_info = AdPackage.objects.get(
                    id=payment.metadata["package_id"]
                )
            except AdPackage.DoesNotExist:
                payment.package_info = None
        else:
            payment.package_info = None

    context = {
        "payments": payments,
        "total_payments": payments.count(),
        "completed_payments": payments.filter(status="completed").count(),
        "pending_payments": payments.filter(status="pending").count(),
        "total_spent": payments.filter(status="completed").aggregate(
            total=Sum("amount")
        )["total"]
        or 0,
        "active_nav": "payment_history",
    }

    return render(request, "dashboard/publisher_payment_history.html", context)


@publisher_required
def publisher_restore_ad(request, ad_id):
    """
    استعادة إعلان محذوف
    Restore a soft-deleted ad
    """
    from django.http import JsonResponse

    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)

    if request.method == "POST":
        if ad.restore_from_soft_delete():
            return JsonResponse(
                {"success": True, "message": _("تم استعادة الإعلان بنجاح")}
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("الإعلان غير محذوف أو لا يمكن استعادته"),
                },
                status=400,
            )

    return JsonResponse(
        {"success": False, "message": _("طريقة غير مسموحة")}, status=405
    )


@publisher_required
def publisher_permanent_delete_ad(request, ad_id):
    """
    حذف إعلان نهائياً
    Permanently delete an ad
    """
    from django.http import JsonResponse

    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)

    if request.method == "POST":
        # Check if ad is eligible for permanent deletion
        can_delete, reason = ad.can_be_permanently_deleted()

        if (
            can_delete or ad.deleted_at
        ):  # Allow manual permanent delete if already soft-deleted
            ad_title = ad.title
            ad.delete()  # Hard delete from database

            return JsonResponse(
                {
                    "success": True,
                    "message": _('تم حذف الإعلان "{}" نهائياً').format(ad_title),
                }
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": _(
                        "لا يمكن حذف الإعلان نهائياً في الوقت الحالي. السبب: {}"
                    ).format(reason),
                },
                status=400,
            )

    return JsonResponse(
        {"success": False, "message": _("طريقة غير مسموحة")}, status=405
    )
