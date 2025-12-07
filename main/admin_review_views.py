"""
Admin Review Management Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from .decorators import superadmin_required
from .models import AdReview, ClassifiedAd, Notification


@login_required
@superadmin_required
def admin_reviews_list(request):
    """List all reviews with filtering options"""
    reviews = AdReview.objects.select_related("ad", "user").order_by("-created_at")

    # Filters
    rating_filter = request.GET.get("rating")
    status_filter = request.GET.get("status")
    search = request.GET.get("search")

    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)

    if status_filter:
        if status_filter == "approved":
            reviews = reviews.filter(is_approved=True)
        elif status_filter == "pending":
            reviews = reviews.filter(is_approved=False)

    if search:
        reviews = reviews.filter(
            Q(ad__title__icontains=search)
            | Q(user__username__icontains=search)
            | Q(comment__icontains=search)
        )

    # Statistics
    stats = {
        "total": AdReview.objects.count(),
        "approved": AdReview.objects.filter(is_approved=True).count(),
        "pending": AdReview.objects.filter(is_approved=False).count(),
        "average_rating": AdReview.objects.aggregate(Avg("rating"))["rating__avg"] or 0,
    }

    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get("page")
    reviews_page = paginator.get_page(page_number)

    context = {
        "reviews": reviews_page,
        "stats": stats,
        "rating_filter": rating_filter,
        "status_filter": status_filter,
        "search": search,
    }

    return render(request, "admin_dashboard/reviews_list.html", context)


@login_required
@superadmin_required
def admin_review_detail(request, review_id):
    """View single review details"""
    review = get_object_or_404(
        AdReview.objects.select_related("ad", "user"), id=review_id
    )

    context = {
        "review": review,
    }

    return render(request, "admin_dashboard/review_detail.html", context)


@login_required
@superadmin_required
@require_http_methods(["POST"])
def admin_approve_review(request, review_id):
    """Approve a review"""
    review = get_object_or_404(AdReview, id=review_id)
    review.is_approved = True
    review.save()

    # Update ad rating automatically
    review.update_ad_rating()

    # Send notification to the reviewer
    Notification.objects.create(
        user=review.user,
        notification_type="review_approved",
        title=_("تم قبول تقييمك"),
        message=_('تم قبول تقييمك على الإعلان "{}"').format(review.ad.title),
        link=f"/classifieds/{review.ad.id}/",
    )

    # Send notification to the ad owner
    if review.ad.user != review.user:  # Don't notify if owner reviewed their own ad
        Notification.objects.create(
            user=review.ad.user,
            notification_type="new_review",
            title=_("تقييم جديد على إعلانك"),
            message=_('{} قام بتقييم إعلانك "{}" بـ {} نجوم').format(
                review.user.get_display_name(), review.ad.title, review.rating
            ),
            link=f"/classifieds/{review.ad.id}/#reviews-section",
        )

    messages.success(request, _("تم قبول التقييم بنجاح"))
    return redirect("main:admin_reviews_list")


@login_required
@superadmin_required
@require_http_methods(["POST"])
def admin_reject_review(request, review_id):
    """Reject/hide a review"""
    review = get_object_or_404(AdReview, id=review_id)
    review.is_approved = False
    review.save()

    # Update ad rating automatically
    review.update_ad_rating()

    messages.success(request, _("تم رفض التقييم بنجاح"))
    return redirect("main:admin_reviews_list")


@login_required
@superadmin_required
@require_http_methods(["POST"])
def admin_delete_review(request, review_id):
    """Delete a review permanently"""
    review = get_object_or_404(AdReview, id=review_id)
    ad = review.ad
    review.delete()

    # Recalculate ad rating
    ad_reviews = AdReview.objects.filter(ad=ad, is_approved=True)
    if ad_reviews.exists():
        avg_rating = ad_reviews.aggregate(Avg("rating"))["rating__avg"]
        ad.rating = avg_rating
        ad.rating_count = ad_reviews.count()
    else:
        ad.rating = None
        ad.rating_count = 0
    ad.save(update_fields=["rating", "rating_count"])

    messages.success(request, _("تم حذف التقييم بنجاح"))
    return redirect("main:admin_reviews_list")


@login_required
@superadmin_required
@require_http_methods(["POST"])
def admin_bulk_approve_reviews(request):
    """Bulk approve selected reviews"""
    review_ids = request.POST.getlist("review_ids")
    if review_ids:
        reviews = AdReview.objects.filter(id__in=review_ids).select_related(
            "ad", "user"
        )

        # Update reviews to approved
        AdReview.objects.filter(id__in=review_ids).update(is_approved=True)

        # Update all affected ads and send notifications
        for review in reviews:
            review.update_ad_rating()

            # Send notification to reviewer
            Notification.objects.create(
                user=review.user,
                notification_type="review_approved",
                title=_("تم قبول تقييمك"),
                message=_('تم قبول تقييمك على الإعلان "{}"').format(review.ad.title),
                link=f"/classifieds/{review.ad.id}/",
            )

            # Send notification to ad owner
            if review.ad.user != review.user:
                Notification.objects.create(
                    user=review.ad.user,
                    notification_type="new_review",
                    title=_("تقييم جديد على إعلانك"),
                    message=_('{} قام بتقييم إعلانك "{}" بـ {} نجوم').format(
                        review.user.get_display_name(), review.ad.title, review.rating
                    ),
                    link=f"/classifieds/{review.ad.id}/#reviews-section",
                )

        messages.success(request, _(f"تم قبول {len(review_ids)} تقييم"))
    return redirect("main:admin_reviews_list")


@login_required
@superadmin_required
@require_http_methods(["POST"])
def admin_bulk_reject_reviews(request):
    """Bulk reject selected reviews"""
    review_ids = request.POST.getlist("review_ids")
    if review_ids:
        AdReview.objects.filter(id__in=review_ids).update(is_approved=False)
        # Update all affected ads
        for review in AdReview.objects.filter(id__in=review_ids).select_related("ad"):
            review.update_ad_rating()
        messages.success(request, _(f"تم رفض {len(review_ids)} تقييم"))
    return redirect("main:admin_reviews_list")


@login_required
@superadmin_required
@require_http_methods(["POST"])
def admin_bulk_delete_reviews(request):
    """Bulk delete selected reviews"""
    review_ids = request.POST.getlist("review_ids")
    if review_ids:
        reviews = AdReview.objects.filter(id__in=review_ids)
        affected_ads = set([review.ad for review in reviews])
        reviews.delete()

        # Recalculate ratings for all affected ads
        for ad in affected_ads:
            ad_reviews = AdReview.objects.filter(ad=ad, is_approved=True)
            if ad_reviews.exists():
                avg_rating = ad_reviews.aggregate(Avg("rating"))["rating__avg"]
                ad.rating = avg_rating
                ad.rating_count = ad_reviews.count()
            else:
                ad.rating = None
                ad.rating_count = 0
            ad.save(update_fields=["rating", "rating_count"])

        messages.success(request, _(f"تم حذف {len(review_ids)} تقييم"))
    return redirect("main:admin_reviews_list")
