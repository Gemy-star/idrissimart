"""
Admin Views for Ad Management
Full CRUD operations for ClassifiedAd and AdUpgradeHistory
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from main.models import (
    ClassifiedAd,
    Notification,
    AdUpgradeHistory,
    AdPackage,
    Category,
)
from main.decorators import SuperadminRequiredMixin


class AdminPendingAdsView(SuperadminRequiredMixin, ListView):
    """
    Admin view for pending ads review
    Shows all ads pending approval
    """

    model = ClassifiedAd
    template_name = "admin_dashboard/pending_ads.html"
    context_object_name = "pending_ads"
    paginate_by = 20

    def get_queryset(self):
        """Get pending ads"""
        return (
            ClassifiedAd.objects.pending_review()
            .select_related("user", "category", "country")
            .prefetch_related("images", "upgrade_history")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pending_ads = self.get_queryset()

        context["stats"] = {
            "total_pending": pending_ads.count(),
            "today_pending": pending_ads.filter(
                created_at__date=timezone.now().date()
            ).count(),
            "default_users": pending_ads.filter(user__profile_type="default").count(),
            "with_upgrades": pending_ads.filter(
                Q(is_highlighted=True) | Q(is_urgent=True) | Q(is_pinned=True)
            ).count(),
            "paid_ads": pending_ads.filter(is_paid=True).count(),
            "unpaid_ads": pending_ads.filter(is_paid=False).count(),
        }

        context["active_nav"] = "pending_ads"
        context["page_title"] = "مراجعة الإعلانات المعلقة"

        return context


@staff_member_required
def approve_ad_view(request, ad_id):
    """Approve a pending ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    if ad.approve(request.user):
        messages.success(request, f'تم الموافقة على الإعلان "{ad.title}" بنجاح.')

        # Create notification
        Notification.objects.create(
            user=ad.user,
            title="تم الموافقة على إعلانك",
            message=f'تم الموافقة على إعلانك "{ad.title}" وهو الآن نشط.',
            notification_type="ad_approved",
        )
    else:
        messages.error(request, "لا يمكن الموافقة على هذا الإعلان.")

    # Return to previous page or pending ads
    return redirect(request.META.get("HTTP_REFERER", "admin:pending_ads"))


@staff_member_required
def reject_ad_view(request, ad_id):
    """Reject a pending ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    if request.method == "POST":
        reason = request.POST.get("reason", "")

        if ad.reject(request.user, reason):
            messages.warning(request, f'تم رفض الإعلان "{ad.title}".')

            # Create notification
            Notification.objects.create(
                user=ad.user,
                title="تم رفض إعلانك",
                message=f'تم رفض إعلانك "{ad.title}". السبب: {reason}',
                notification_type="ad_rejected",
            )
        else:
            messages.error(request, "لا يمكن رفض هذا الإعلان.")

    return redirect(request.META.get("HTTP_REFERER", "admin:pending_ads"))


@staff_member_required
def ad_quick_review_ajax(request, ad_id):
    """AJAX view for quick ad review"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    action = request.POST.get("action")  # 'approve' or 'reject'

    if action == "approve":
        success = ad.approve(request.user)
        if success:
            return JsonResponse(
                {"success": True, "message": "تم الموافقة على الإعلان بنجاح"}
            )
    elif action == "reject":
        reason = request.POST.get("reason", "لم يتم تحديد سبب")
        success = ad.reject(request.user, reason)
        if success:
            return JsonResponse({"success": True, "message": "تم رفض الإعلان"})

    return JsonResponse({"error": "فشل الإجراء"}, status=400)


class AdminAllAdsView(SuperadminRequiredMixin, ListView):
    """
    Admin view for all ads
    Shows all ads with filtering
    """

    model = ClassifiedAd
    template_name = "admin_dashboard/all_ads.html"
    context_object_name = "ads"
    paginate_by = 30

    def get_queryset(self):
        """Get all ads with filters"""
        queryset = (
            ClassifiedAd.objects.all()
            .select_related("user", "category", "country")
            .prefetch_related("images", "upgrade_history")
        )

        # Check and expire old upgrades
        for ad in queryset:
            ad.check_and_expire_upgrades()

        # Filter by status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Filter by upgrade
        upgrade_filter = self.request.GET.get("upgrade")
        if upgrade_filter == "highlighted":
            queryset = queryset.filter(is_highlighted=True)
        elif upgrade_filter == "urgent":
            queryset = queryset.filter(is_urgent=True)
        elif upgrade_filter == "pinned":
            queryset = queryset.filter(is_pinned=True)

        # Search
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(user__username__icontains=search)
            )

        # Sorting - default by priority
        sort_by = self.request.GET.get("sort", "priority")
        if sort_by == "priority":
            queryset = queryset.order_by(
                "-is_pinned", "-is_urgent", "-is_highlighted", "-created_at"
            )
        else:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_ads = ClassifiedAd.objects.all()

        context["stats"] = {
            "total": all_ads.count(),
            "active": all_ads.filter(status="active").count(),
            "pending": all_ads.filter(status="pending").count(),
            "expired": all_ads.filter(status="expired").count(),
            "highlighted": all_ads.filter(is_highlighted=True).count(),
            "urgent": all_ads.filter(is_urgent=True).count(),
            "pinned": all_ads.filter(is_pinned=True).count(),
        }

        context["status_choices"] = ClassifiedAd.AdStatus.choices
        context["current_filters"] = {
            "status": self.request.GET.get("status", ""),
            "upgrade": self.request.GET.get("upgrade", ""),
            "search": self.request.GET.get("search", ""),
            "sort": self.request.GET.get("sort", "priority"),
        }

        context["active_nav"] = "all_ads"
        context["page_title"] = "جميع الإعلانات"

        return context


@staff_member_required
def bulk_approve_ads(request):
    """Bulk approve multiple ads"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    ad_ids = request.POST.getlist("ad_ids[]")

    count = 0
    for ad_id in ad_ids:
        try:
            ad = ClassifiedAd.objects.get(pk=ad_id)
            if ad.approve(request.user):
                count += 1
                # Create notification
                Notification.objects.create(
                    user=ad.user,
                    title="تم الموافقة على إعلانك",
                    message=f'تم الموافقة على إعلانك "{ad.title}".',
                    notification_type="ad_approved",
                )
        except ClassifiedAd.DoesNotExist:
            continue

    return JsonResponse(
        {"success": True, "message": f"تم الموافقة على {count} إعلان", "count": count}
    )


# ============================================================================
# CRUD OPERATIONS FOR CLASSIFIED ADS
# ============================================================================


class AdminAdDetailView(SuperadminRequiredMixin, DetailView):
    """
    Admin view for ad detail with full information
    """

    model = ClassifiedAd
    template_name = "admin_dashboard/ad_detail.html"
    context_object_name = "ad"
    pk_url_kwarg = "ad_id"

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
            "days_active": (
                (timezone.now() - ad.created_at).days if ad.status == "active" else 0
            ),
            "is_paid": ad.is_paid,
        }

        context["active_nav"] = "all_ads"
        context["page_title"] = f"تفاصيل الإعلان: {ad.title}"

        return context


class AdminAdCreateView(SuperadminRequiredMixin, CreateView):
    """
    Admin view to create a new ad with custom fields support
    """

    model = ClassifiedAd
    template_name = "admin_dashboard/ad_form.html"
    form_class = None  # Will be set dynamically
    success_url = reverse_lazy("main:admin_all_ads")

    def get_form_class(self):
        """Use the AdminClassifiedAdForm that supports custom fields"""
        from main.forms import AdminClassifiedAdForm

        return AdminClassifiedAdForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "all_ads"
        context["page_title"] = "إضافة إعلان جديد"
        context["form_action"] = "create"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f'تم إنشاء الإعلان "{form.instance.title}" بنجاح.'
        )
        return super().form_valid(form)


class AdminAdUpdateView(SuperadminRequiredMixin, UpdateView):
    """
    Admin view to update an existing ad with custom fields support
    """

    model = ClassifiedAd
    template_name = "admin_dashboard/ad_form.html"
    form_class = None  # Will be set dynamically
    pk_url_kwarg = "ad_id"

    def get_form_class(self):
        """Use the AdminClassifiedAdForm that supports custom fields"""
        from main.forms import AdminClassifiedAdForm

        return AdminClassifiedAdForm

    def get_success_url(self):
        return reverse_lazy("main:admin_ad_detail", kwargs={"ad_id": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "all_ads"
        context["page_title"] = f"تعديل الإعلان: {self.object.title}"
        context["form_action"] = "update"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f'تم تحديث الإعلان "{form.instance.title}" بنجاح.'
        )
        return super().form_valid(form)


class AdminAdDeleteView(SuperadminRequiredMixin, DeleteView):
    """
    Admin view to delete an ad
    """

    model = ClassifiedAd
    template_name = "admin_dashboard/ad_confirm_delete.html"
    pk_url_kwarg = "ad_id"
    success_url = reverse_lazy("main:admin_all_ads")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "all_ads"
        context["page_title"] = f"حذف الإعلان: {self.object.title}"
        return context

    def delete(self, request, *args, **kwargs):
        ad = self.get_object()
        title = ad.title
        messages.warning(request, f'تم حذف الإعلان "{title}" بشكل نهائي.')
        return super().delete(request, *args, **kwargs)


@staff_member_required
@require_POST
def bulk_delete_ads(request):
    """Bulk delete multiple ads"""
    ad_ids = request.POST.getlist("ad_ids[]")

    count = 0
    for ad_id in ad_ids:
        try:
            ad = ClassifiedAd.objects.get(pk=ad_id)
            ad.delete()
            count += 1
        except ClassifiedAd.DoesNotExist:
            continue

    return JsonResponse(
        {"success": True, "message": f"تم حذف {count} إعلان", "count": count}
    )


@staff_member_required
@require_POST
def bulk_change_status(request):
    """Bulk change status of multiple ads"""
    ad_ids = request.POST.getlist("ad_ids[]")
    new_status = request.POST.get("status")

    if new_status not in dict(ClassifiedAd.AdStatus.choices):
        return JsonResponse({"error": "حالة غير صالحة"}, status=400)

    count = 0
    for ad_id in ad_ids:
        try:
            ad = ClassifiedAd.objects.get(pk=ad_id)
            ad.status = new_status
            ad.save()
            count += 1

            # Create notification
            Notification.objects.create(
                user=ad.user,
                title="تغيير حالة الإعلان",
                message=f'تم تغيير حالة إعلانك "{ad.title}" إلى {ad.get_status_display()}.',
                notification_type="ad_status_changed",
            )
        except ClassifiedAd.DoesNotExist:
            continue

    return JsonResponse(
        {"success": True, "message": f"تم تحديث {count} إعلان", "count": count}
    )


# ============================================================================
# CRUD OPERATIONS FOR AD UPGRADE HISTORY
# ============================================================================


class AdminUpgradeHistoryListView(SuperadminRequiredMixin, ListView):
    """
    Admin view for all upgrade history
    """

    model = AdUpgradeHistory
    template_name = "admin_dashboard/upgrade_history.html"
    context_object_name = "upgrades"
    paginate_by = 30

    def get_queryset(self):
        queryset = (
            AdUpgradeHistory.objects.all()
            .select_related("ad", "ad__user")
            .order_by("-created_at")
        )

        # Filter by ad
        ad_id = self.request.GET.get("ad_id")
        if ad_id:
            queryset = queryset.filter(ad_id=ad_id)

        # Filter by upgrade type
        upgrade_type = self.request.GET.get("upgrade_type")
        if upgrade_type:
            queryset = queryset.filter(upgrade_type=upgrade_type)

        # Filter by status
        is_active = self.request.GET.get("is_active")
        if is_active == "true":
            queryset = queryset.filter(is_active=True)
        elif is_active == "false":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_upgrades = AdUpgradeHistory.objects.all()

        context["stats"] = {
            "total": all_upgrades.count(),
            "active": all_upgrades.filter(is_active=True).count(),
            "expired": all_upgrades.filter(is_active=False).count(),
            "highlighted": all_upgrades.filter(upgrade_type="HIGHLIGHTED").count(),
            "urgent": all_upgrades.filter(upgrade_type="URGENT").count(),
            "pinned": all_upgrades.filter(upgrade_type="PINNED").count(),
        }

        context["upgrade_types"] = AdUpgradeHistory.UPGRADE_CHOICES
        context["current_filters"] = {
            "ad_id": self.request.GET.get("ad_id", ""),
            "upgrade_type": self.request.GET.get("upgrade_type", ""),
            "is_active": self.request.GET.get("is_active", ""),
        }

        context["active_nav"] = "upgrades"
        context["page_title"] = "سجل الترقيات"

        return context


class AdminUpgradeCreateView(SuperadminRequiredMixin, CreateView):
    """
    Admin view to create a new upgrade
    """

    model = AdUpgradeHistory
    template_name = "admin_dashboard/upgrade_form.html"
    fields = ["ad", "upgrade_type", "price_paid", "duration_days", "is_active"]
    success_url = reverse_lazy("main:admin_upgrade_history")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "upgrades"
        context["page_title"] = "إضافة ترقية جديدة"
        context["form_action"] = "create"
        return context

    def form_valid(self, form):
        upgrade = form.instance
        upgrade.start_date = timezone.now()
        upgrade.end_date = upgrade.start_date + timezone.timedelta(
            days=upgrade.duration_days
        )

        # Activate the upgrade on the ad
        if upgrade.is_active:
            if upgrade.upgrade_type == "HIGHLIGHTED":
                upgrade.ad.is_highlighted = True
            elif upgrade.upgrade_type == "URGENT":
                upgrade.ad.is_urgent = True
            elif upgrade.upgrade_type == "PINNED":
                upgrade.ad.is_pinned = True
            upgrade.ad.save()

        messages.success(
            self.request, f'تم إنشاء الترقية للإعلان "{upgrade.ad.title}" بنجاح.'
        )
        return super().form_valid(form)


class AdminUpgradeUpdateView(SuperadminRequiredMixin, UpdateView):
    """
    Admin view to update an existing upgrade
    """

    model = AdUpgradeHistory
    template_name = "admin_dashboard/upgrade_form.html"
    fields = ["upgrade_type", "price_paid", "duration_days", "is_active"]
    pk_url_kwarg = "upgrade_id"
    success_url = reverse_lazy("main:admin_upgrade_history")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "upgrades"
        context["page_title"] = f"تعديل ترقية: {self.object.get_upgrade_type_display()}"
        context["form_action"] = "update"
        return context

    def form_valid(self, form):
        upgrade = form.instance

        # Update end date if duration changed
        if "duration_days" in form.changed_data:
            upgrade.end_date = upgrade.start_date + timezone.timedelta(
                days=upgrade.duration_days
            )

        # Update ad flags based on is_active status
        if "is_active" in form.changed_data:
            if upgrade.upgrade_type == "HIGHLIGHTED":
                upgrade.ad.is_highlighted = upgrade.is_active
            elif upgrade.upgrade_type == "URGENT":
                upgrade.ad.is_urgent = upgrade.is_active
            elif upgrade.upgrade_type == "PINNED":
                upgrade.ad.is_pinned = upgrade.is_active
            upgrade.ad.save()

        messages.success(self.request, f"تم تحديث الترقية بنجاح.")
        return super().form_valid(form)


class AdminUpgradeDeleteView(SuperadminRequiredMixin, DeleteView):
    """
    Admin view to delete an upgrade
    """

    model = AdUpgradeHistory
    template_name = "admin_dashboard/upgrade_confirm_delete.html"
    pk_url_kwarg = "upgrade_id"
    success_url = reverse_lazy("main:admin_upgrade_history")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "upgrades"
        context["page_title"] = "حذف الترقية"
        return context

    def delete(self, request, *args, **kwargs):
        upgrade = self.get_object()

        # Deactivate the upgrade on the ad
        upgrade.deactivate()

        messages.warning(request, f'تم حذف الترقية من الإعلان "{upgrade.ad.title}".')
        return super().delete(request, *args, **kwargs)


@staff_member_required
@require_POST
def toggle_upgrade_status(request, upgrade_id):
    """Toggle upgrade active status via AJAX"""
    upgrade = get_object_or_404(AdUpgradeHistory, pk=upgrade_id)

    if upgrade.is_active:
        upgrade.deactivate()
        message = "تم إلغاء تفعيل الترقية"
    else:
        upgrade.is_active = True
        upgrade.save()

        # Activate on ad
        if upgrade.upgrade_type == "HIGHLIGHTED":
            upgrade.ad.is_highlighted = True
        elif upgrade.upgrade_type == "URGENT":
            upgrade.ad.is_urgent = True
        elif upgrade.upgrade_type == "PINNED":
            upgrade.ad.is_pinned = True
        upgrade.ad.save()

        message = "تم تفعيل الترقية"

    return JsonResponse(
        {"success": True, "message": message, "is_active": upgrade.is_active}
    )


@staff_member_required
@require_POST
def bulk_deactivate_upgrades(request):
    """Bulk deactivate multiple upgrades"""
    upgrade_ids = request.POST.getlist("upgrade_ids[]")

    count = 0
    for upgrade_id in upgrade_ids:
        try:
            upgrade = AdUpgradeHistory.objects.get(pk=upgrade_id)
            upgrade.deactivate()
            count += 1
        except AdUpgradeHistory.DoesNotExist:
            continue

    return JsonResponse(
        {"success": True, "message": f"تم إلغاء تفعيل {count} ترقية", "count": count}
    )


# ============================================================================
# EXTENDED AD MANAGEMENT ACTIONS
# ============================================================================


@staff_member_required
@require_POST
def admin_suspend_ad(request, ad_id):
    """Suspend/Hide an ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    reason = request.POST.get("reason", "")

    ad.status = "suspended"
    ad.save(update_fields=["status"])

    # Notify user
    Notification.objects.create(
        user=ad.user,
        title="تم تعليق إعلانك",
        message=f'تم تعليق إعلانك "{ad.title}". السبب: {reason}',
        notification_type="ad_suspended",
        link=f"/classifieds/{ad.id}/",
    )

    messages.warning(request, f'تم تعليق الإعلان "{ad.title}".')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_activate_ad(request, ad_id):
    """Activate a suspended ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.status = "active"
    ad.save(update_fields=["status"])

    # Notify user
    Notification.objects.create(
        user=ad.user,
        title="تم تفعيل إعلانك",
        message=f'تم إعادة تفعيل إعلانك "{ad.title}". الإعلان الآن نشط.',
        notification_type="ad_activated",
        link=f"/classifieds/{ad.id}/",
    )

    messages.success(request, f'تم تفعيل الإعلان "{ad.title}".')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_extend_ad(request, ad_id):
    """Extend ad expiration date"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    days = int(request.POST.get("days", 30))

    if ad.expires_at:
        ad.expires_at = ad.expires_at + timezone.timedelta(days=days)
    else:
        ad.expires_at = timezone.now() + timezone.timedelta(days=days)

    ad.save(update_fields=["expires_at"])

    # Notify user
    Notification.objects.create(
        user=ad.user,
        title="تم تمديد إعلانك",
        message=f'تم تمديد إعلانك "{ad.title}" لمدة {days} يوم إضافي.',
        notification_type="ad_extended",
        link=f"/classifieds/{ad.id}/",
    )

    messages.success(request, f'تم تمديد الإعلان "{ad.title}" لمدة {days} يوم.')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_toggle_featured(request, ad_id):
    """Toggle ad featured status"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.is_highlighted = not ad.is_highlighted
    ad.save(update_fields=["is_highlighted"])

    status = "مميز" if ad.is_highlighted else "عادي"
    messages.success(request, f'تم تغيير حالة الإعلان "{ad.title}" إلى {status}.')

    return JsonResponse(
        {
            "success": True,
            "is_highlighted": ad.is_highlighted,
            "message": f"الإعلان الآن {status}",
        }
    )


@staff_member_required
@require_POST
def admin_toggle_urgent(request, ad_id):
    """Toggle ad urgent status"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.is_urgent = not ad.is_urgent
    ad.save(update_fields=["is_urgent"])

    status = "عاجل" if ad.is_urgent else "عادي"
    messages.success(request, f'تم تغيير حالة الإعلان "{ad.title}" إلى {status}.')

    return JsonResponse(
        {
            "success": True,
            "is_urgent": ad.is_urgent,
            "message": f"الإعلان الآن {status}",
        }
    )


@staff_member_required
@require_POST
def admin_toggle_pinned(request, ad_id):
    """Toggle ad pinned status"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.is_pinned = not ad.is_pinned
    ad.save(update_fields=["is_pinned"])

    status = "مثبت" if ad.is_pinned else "عادي"
    messages.success(request, f'تم تغيير حالة الإعلان "{ad.title}" إلى {status}.')

    return JsonResponse(
        {
            "success": True,
            "is_pinned": ad.is_pinned,
            "message": f"الإعلان الآن {status}",
        }
    )


@staff_member_required
@require_POST
def admin_toggle_auto_refresh(request, ad_id):
    """Toggle ad auto_refresh status"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.auto_refresh = not ad.auto_refresh
    ad.save(update_fields=["auto_refresh"])

    status = "مفعّل التحديث التلقائي" if ad.auto_refresh else "موقوف التحديث التلقائي"
    messages.success(request, f'تم تغيير حالة الإعلان "{ad.title}" إلى {status}.')

    return JsonResponse(
        {
            "success": True,
            "auto_refresh": ad.auto_refresh,
            "message": f"الإعلان الآن {status}",
        }
    )


@staff_member_required
@require_POST
def admin_change_ad_category(request, ad_id):
    """Change ad category"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    category_id = request.POST.get("category_id")

    if category_id:
        category = get_object_or_404(Category, pk=category_id)
        ad.category = category
        ad.save(update_fields=["category"])

        messages.success(
            request, f'تم تغيير قسم الإعلان "{ad.title}" إلى "{category.name_ar}".'
        )
        return JsonResponse(
            {"success": True, "message": f"تم تغيير القسم إلى {category.name_ar}"}
        )

    return JsonResponse({"success": False, "message": "يرجى اختيار قسم"}, status=400)


@staff_member_required
@require_POST
def admin_bulk_actions(request):
    """Bulk actions on multiple ads"""
    ad_ids = request.POST.getlist("ad_ids[]")
    action = request.POST.get("action")

    count = 0
    ads = ClassifiedAd.objects.filter(pk__in=ad_ids)

    if action == "approve":
        for ad in ads:
            if ad.approve(request.user):
                count += 1
                Notification.objects.create(
                    user=ad.user,
                    title="تم الموافقة على إعلانك",
                    message=f'تم الموافقة على إعلانك "{ad.title}".',
                    notification_type="ad_approved",
                )

    elif action == "reject":
        reason = request.POST.get("reason", "لم يتم تحديد سبب")
        for ad in ads:
            if ad.reject(request.user, reason):
                count += 1
                Notification.objects.create(
                    user=ad.user,
                    title="تم رفض إعلانك",
                    message=f'تم رفض إعلانك "{ad.title}". السبب: {reason}',
                    notification_type="ad_rejected",
                )

    elif action == "suspend":
        reason = request.POST.get("reason", "")
        ads.update(status="suspended")
        count = ads.count()
        for ad in ads:
            Notification.objects.create(
                user=ad.user,
                title="تم تعليق إعلانك",
                message=f'تم تعليق إعلانك "{ad.title}". السبب: {reason}',
                notification_type="ad_suspended",
            )

    elif action == "activate":
        ads.update(status="active")
        count = ads.count()
        for ad in ads:
            Notification.objects.create(
                user=ad.user,
                title="تم تفعيل إعلانك",
                message=f'تم إعادة تفعيل إعلانك "{ad.title}".',
                notification_type="ad_activated",
            )

    elif action == "delete":
        count = ads.count()
        ads.delete()

    elif action == "featured_on":
        ads.update(is_highlighted=True)
        count = ads.count()

    elif action == "featured_off":
        ads.update(is_highlighted=False)
        count = ads.count()

    elif action == "urgent_on":
        ads.update(is_urgent=True)
        count = ads.count()

    elif action == "urgent_off":
        ads.update(is_urgent=False)
        count = ads.count()

    elif action == "pin":
        ads.update(is_pinned=True)
        count = ads.count()

    elif action == "unpin":
        ads.update(is_pinned=False)
        count = ads.count()

    return JsonResponse(
        {
            "success": True,
            "message": f"تم تنفيذ الإجراء على {count} إعلان",
            "count": count,
        }
    )


# ============================================================================
# ADDITIONAL ADMIN AD ACTIONS
# ============================================================================


@staff_member_required
@require_POST
def admin_ban_ad(request, ad_id):
    """Ban an ad permanently"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    reason = request.POST.get("reason", "تم الحظر من قبل الإدارة")

    ad.status = "BANNED"
    ad.is_hidden = True
    ad.save(update_fields=["status", "is_hidden"])

    # Notify user
    Notification.objects.create(
        user=ad.user,
        title="تم حظر إعلانك نهائياً",
        message=f'تم حظر إعلانك "{ad.title}" نهائياً. السبب: {reason}',
        notification_type="ad_banned",
        link=f"/classifieds/{ad.id}/",
    )

    messages.error(request, f'تم حظر الإعلان "{ad.title}" نهائياً.')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_unban_ad(request, ad_id):
    """Unban a banned ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.status = "ACTIVE"
    ad.is_hidden = False
    ad.save(update_fields=["status", "is_hidden"])

    # Notify user
    Notification.objects.create(
        user=ad.user,
        title="تم إلغاء حظر إعلانك",
        message=f'تم إلغاء حظر إعلانك "{ad.title}". الإعلان الآن نشط.',
        notification_type="ad_unbanned",
        link=f"/classifieds/{ad.id}/",
    )

    messages.success(request, f'تم إلغاء حظر الإعلان "{ad.title}".')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_duplicate_ad(request, ad_id):
    """Duplicate an ad with all its details"""
    original_ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    # Create a copy
    duplicated_ad = ClassifiedAd.objects.get(pk=ad_id)
    duplicated_ad.pk = None  # Create new instance
    duplicated_ad.title = f"{original_ad.title} (نسخة)"
    duplicated_ad.slug = None  # Will be auto-generated
    duplicated_ad.status = "PENDING"  # Requires review
    duplicated_ad.created_at = timezone.now()
    duplicated_ad.updated_at = timezone.now()
    duplicated_ad.views_count = 0
    duplicated_ad.expires_at = None  # Will be set on approval
    duplicated_ad.save()

    # Copy images
    for image in original_ad.images.all():
        AdImage.objects.create(
            ad=duplicated_ad,
            image=image.image,
            order=image.order,
        )

    # Notify user
    Notification.objects.create(
        user=original_ad.user,
        title="تم نسخ إعلانك",
        message=f'تم إنشاء نسخة من إعلانك "{original_ad.title}". الإعلان الجديد بحاجة إلى مراجعة.',
        notification_type="ad_duplicated",
        link=f"/publisher/ads/{duplicated_ad.id}/",
    )

    messages.success(
        request,
        f'تم نسخ الإعلان "{original_ad.title}" بنجاح. الإعلان الجديد ID: {duplicated_ad.id}',
    )
    return redirect("main:admin_ad_detail", ad_id=duplicated_ad.id)


@staff_member_required
@require_POST
def admin_permanent_delete_ad(request, ad_id):
    """Permanently delete an ad from database (hard delete)"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    ad_title = ad.title
    ad_user = ad.user

    # Send notification before deleting
    Notification.objects.create(
        user=ad_user,
        title="تم حذف إعلانك نهائياً",
        message=f'تم حذف إعلانك "{ad_title}" نهائياً من النظام ولا يمكن استرجاعه.',
        notification_type="ad_deleted",
    )

    # Delete related images (will be auto-deleted due to CASCADE)
    # Delete the ad (hard delete)
    ad.delete()

    messages.warning(request, f'تم حذف الإعلان "{ad_title}" نهائياً من قاعدة البيانات.')
    return redirect("main:admin_ads")


@staff_member_required
@require_POST
def admin_transfer_ownership(request, ad_id):
    """Transfer ad ownership to another user"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    new_user_id = request.POST.get("new_user_id")

    if not new_user_id:
        messages.error(request, "يرجى تحديد المستخدم الجديد.")
        return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))

    try:
        from main.models import User

        new_user = get_object_or_404(User, pk=new_user_id)
        old_user = ad.user

        ad.user = new_user
        ad.save(update_fields=["user"])

        # Notify old user
        Notification.objects.create(
            user=old_user,
            title="تم نقل ملكية إعلانك",
            message=f'تم نقل ملكية إعلانك "{ad.title}" إلى مستخدم آخر.',
            notification_type="ad_transferred",
        )

        # Notify new user
        Notification.objects.create(
            user=new_user,
            title="تم نقل إعلان إليك",
            message=f'تم نقل ملكية الإعلان "{ad.title}" إليك.',
            notification_type="ad_received",
            link=f"/publisher/ads/{ad.id}/",
        )

        messages.success(
            request,
            f'تم نقل ملكية الإعلان "{ad.title}" من {old_user.username} إلى {new_user.username}.',
        )
    except Exception as e:
        messages.error(request, f"حدث خطأ: {str(e)}")

    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
def admin_ad_full_edit(request, ad_id):
    """Full edit page for admin to modify all ad content"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    if request.method == "POST":
        # Handle form submission
        form = ClassifiedAdForm(request.POST, request.FILES, instance=ad)
        image_formset = AdImageFormSet(
            request.POST, request.FILES, instance=ad, prefix="images"
        )

        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()

            # Notify user
            Notification.objects.create(
                user=ad.user,
                title="تم تعديل إعلانك",
                message=f'تم تعديل إعلانك "{ad.title}" من قبل الإدارة.',
                notification_type="ad_updated",
                link=f"/classifieds/{ad.id}/",
            )

            messages.success(request, f'تم تعديل الإعلان "{ad.title}" بنجاح.')
            return redirect("main:admin_ad_detail", ad_id=ad.id)
    else:
        form = ClassifiedAdForm(instance=ad)
        image_formset = AdImageFormSet(instance=ad, prefix="images")

    context = {
        "ad": ad,
        "form": form,
        "image_formset": image_formset,
        "page_title": f"تعديل كامل: {ad.title}",
        "active_nav": "ads",
    }

    return render(request, "admin_dashboard/ad_full_edit.html", context)


@staff_member_required
@require_POST
def admin_republish_ad(request, ad_id):
    """Republish an expired ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    # Set new expiration date
    ad.expires_at = timezone.now() + timezone.timedelta(days=30)
    ad.status = "ACTIVE"
    ad.created_at = timezone.now()  # Reset creation date
    ad.save(update_fields=["expires_at", "status", "created_at"])

    # Notify user
    Notification.objects.create(
        user=ad.user,
        title="تم إعادة نشر إعلانك",
        message=f'تم إعادة نشر إعلانك "{ad.title}" بتاريخ انتهاء جديد.',
        notification_type="ad_republished",
        link=f"/classifieds/{ad.id}/",
    )

    messages.success(request, f'تم إعادة نشر الإعلان "{ad.title}" بنجاح.')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_approve_ad(request, ad_id):
    """Approve a single ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    # Change status to active
    ad.status = "ACTIVE"
    ad.save(update_fields=["status"])

    # Send notification to user
    Notification.objects.create(
        user=ad.user,
        title="تمت الموافقة على إعلانك",
        message=f'تمت الموافقة على إعلانك "{ad.title}" وأصبح نشطاً الآن.',
        notification_type="ad_approved",
        link=f"/classifieds/{ad.id}/",
    )

    messages.success(request, f'تمت الموافقة على الإعلان "{ad.title}" بنجاح.')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_reject_ad(request, ad_id):
    """Reject a single ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)
    reason = request.POST.get("reason", "")

    # Change status to rejected
    ad.status = "REJECTED"
    ad.save(update_fields=["status"])

    # Send notification to user with reason
    Notification.objects.create(
        user=ad.user,
        title="تم رفض إعلانك",
        message=(
            f'تم رفض إعلانك "{ad.title}". السبب: {reason}'
            if reason
            else f'تم رفض إعلانك "{ad.title}".'
        ),
        notification_type="ad_rejected",
        link=f"/classifieds/{ad.id}/",
    )

    messages.warning(request, f'تم رفض الإعلان "{ad.title}".')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_hide_ad(request, ad_id):
    """Hide a single ad (toggle is_hidden)"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    # Toggle hidden status
    ad.is_hidden = not ad.is_hidden
    ad.save(update_fields=["is_hidden"])

    if ad.is_hidden:
        # Send notification when hiding
        Notification.objects.create(
            user=ad.user,
            title="تم إخفاء إعلانك",
            message=f'تم إخفاء إعلانك "{ad.title}" من قبل الإدارة.',
            notification_type="ad_hidden",
            link=f"/classifieds/{ad.id}/",
        )
        messages.warning(request, f'تم إخفاء الإعلان "{ad.title}".')
    else:
        # Send notification when unhiding
        Notification.objects.create(
            user=ad.user,
            title="تم إظهار إعلانك",
            message=f'تم إظهار إعلانك "{ad.title}" مرة أخرى.',
            notification_type="ad_shown",
            link=f"/classifieds/{ad.id}/",
        )
        messages.success(request, f'تم إظهار الإعلان "{ad.title}" مرة أخرى.')

    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_enable_cart_for_ad(request, ad_id):
    """Enable cart for a single ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.cart_enabled_by_admin = True
    ad.save(update_fields=["cart_enabled_by_admin"])

    # Send notification
    Notification.objects.create(
        user=ad.user,
        title="تم تفعيل السلة لإعلانك",
        message=f'تم تفعيل السلة لإعلانك "{ad.title}". يمكن للمشترين الآن إضافته إلى سلة التسوق.',
        notification_type="cart_enabled",
        link=f"/classifieds/{ad.id}/",
    )

    messages.success(request, f'تم تفعيل السلة للإعلان "{ad.title}".')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))


@staff_member_required
@require_POST
def admin_disable_cart_for_ad(request, ad_id):
    """Disable cart for a single ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    ad.cart_enabled_by_admin = False
    ad.save(update_fields=["cart_enabled_by_admin"])

    # Send notification
    Notification.objects.create(
        user=ad.user,
        title="تم تعطيل السلة لإعلانك",
        message=f'تم تعطيل السلة لإعلانك "{ad.title}".',
        notification_type="cart_disabled",
        link=f"/classifieds/{ad.id}/",
    )

    messages.warning(request, f'تم تعطيل السلة للإعلان "{ad.title}".')
    return redirect(request.META.get("HTTP_REFERER", "main:admin_ads"))
