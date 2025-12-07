"""
Publisher Reviews Views
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.shortcuts import render
from django.core.paginator import Paginator

from .models import AdReview, ClassifiedAd


@login_required
def publisher_reviews_list(request):
    """List all reviews for publisher's ads"""
    # Get all ads owned by the current user
    user_ads = ClassifiedAd.objects.filter(user=request.user)

    # Get all reviews for user's ads
    reviews = (
        AdReview.objects.filter(ad__in=user_ads)
        .select_related("ad", "user")
        .order_by("-created_at")
    )

    # Filters
    rating_filter = request.GET.get("rating")
    ad_filter = request.GET.get("ad")
    search = request.GET.get("search")

    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)

    if ad_filter:
        reviews = reviews.filter(ad_id=ad_filter)

    if search:
        reviews = reviews.filter(
            Q(comment__icontains=search) | Q(user__username__icontains=search)
        )

    # Statistics
    stats = {
        "total": reviews.count(),
        "approved": reviews.filter(is_approved=True).count(),
        "pending": reviews.filter(is_approved=False).count(),
        "average_rating": reviews.aggregate(Avg("rating"))["rating__avg"] or 0,
        "total_ads_with_reviews": user_ads.filter(reviews__isnull=False)
        .distinct()
        .count(),
    }

    # Get ads for filter dropdown
    ads_with_reviews = user_ads.annotate(reviews_count=Count("reviews")).filter(
        reviews_count__gt=0
    )

    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get("page")
    reviews_page = paginator.get_page(page_number)

    context = {
        "reviews": reviews_page,
        "stats": stats,
        "rating_filter": rating_filter,
        "ad_filter": ad_filter,
        "search": search,
        "user_ads": ads_with_reviews,
    }

    return render(request, "publisher_dashboard/reviews_list.html", context)
