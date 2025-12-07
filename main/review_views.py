# Review Views
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .models import AdReview, ClassifiedAd


@require_http_methods(["POST"])
@login_required
def submit_ad_review(request, ad_id):
    """Submit a review for an ad"""
    ad = get_object_or_404(ClassifiedAd, pk=ad_id)

    # Check if user is trying to review their own ad
    if ad.user == request.user:
        messages.error(request, _("لا يمكنك تقييم إعلانك الخاص"))
        return redirect("main:ad_detail", slug=ad.slug)

    # Check if user has already reviewed this ad
    if AdReview.objects.filter(ad=ad, user=request.user).exists():
        messages.warning(request, _("لقد قمت بتقييم هذا الإعلان مسبقاً"))
        return redirect("main:ad_detail", slug=ad.slug)

    # Get rating and comment
    rating = request.POST.get("rating")
    comment = request.POST.get("comment", "").strip()

    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, _("يرجى اختيار تقييم صحيح من 1 إلى 5"))
        return redirect("main:ad_detail", slug=ad.slug)

    # Create review (requires admin approval)
    AdReview.objects.create(
        ad=ad,
        user=request.user,
        rating=rating,
        comment=comment,
        is_approved=False,  # Requires admin approval before showing
    )

    messages.success(request, _("شكراً لك! تم إضافة تقييمك وسيظهر بعد موافقة المشرف"))
    return redirect("main:ad_detail", pk=ad_id)
