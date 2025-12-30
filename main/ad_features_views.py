"""Views for Ad Features (contact_for_price, facebook_share, video)"""

import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import ClassifiedAd, FacebookShareRequest


@login_required
def ad_features_upgrade(request, ad_id):
    """
    View for upgrading ad features (contact_for_price, facebook_share, video)
    """
    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)

    if request.method == "POST":
        selected_features_json = request.POST.get("selected_features", "{}")
        try:
            selected_features = json.loads(selected_features_json)
        except json.JSONDecodeError:
            messages.error(request, _("خطأ في معالجة البيانات"))
            return redirect("main:ad_features_upgrade", ad_id=ad_id)

        # Process selected features
        updated_features = []

        # Contact for Price
        if selected_features.get("contact_for_price"):
            if not ad.contact_for_price:
                ad.contact_for_price = True
                updated_features.append(_("تواصل ليصلك عرض سعر"))
        else:
            if ad.contact_for_price:
                ad.contact_for_price = False

        # Facebook Share
        if selected_features.get("facebook_share"):
            if not ad.share_on_facebook:
                ad.share_on_facebook = True
                ad.facebook_share_requested = True
                updated_features.append(_("نشر على فيسبوك"))

                # Create FacebookShareRequest for admin
                FacebookShareRequest.objects.create(
                    ad=ad,
                    user=request.user,
                    payment_confirmed=True,  # Assuming payment is processed
                    payment_amount=Decimal("100.00"),
                )

                messages.info(
                    request,
                    _(
                        "تم إرسال طلب النشر على فيسبوك. سيتم مراجعته خلال 24 ساعة."
                    ),
                )

        # Save ad changes
        if updated_features:
            ad.save()
            messages.success(
                request,
                _("تم تحديث مميزات الإعلان: ") + ", ".join(updated_features),
            )
        else:
            messages.info(request, _("لم يتم تحديد أي مميزات جديدة"))

        return redirect("main:ad_detail", ad_id=ad.id)

    context = {
        "ad": ad,
    }

    return render(request, "classifieds/ad_features_upgrade.html", context)


@login_required
def toggle_contact_for_price(request, ad_id):
    """
    Quick toggle for contact_for_price feature
    """
    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)

    ad.contact_for_price = not ad.contact_for_price
    ad.save()

    if ad.contact_for_price:
        messages.success(
            request,
            _("تم تفعيل ميزة 'تواصل ليصلك عرض سعر'. السعر الآن مخفي."),
        )
    else:
        messages.success(
            request,
            _("تم إلغاء تفعيل ميزة 'تواصل ليصلك عرض سعر'. السعر الآن ظاهر."),
        )

    return redirect("main:ad_detail", ad_id=ad.id)


@login_required
def request_facebook_share(request, ad_id):
    """
    Request Facebook share for an ad
    """
    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)

    # Check if already requested
    if ad.facebook_share_requested:
        messages.warning(
            request,
            _("لديك طلب نشر على فيسبوك قيد المراجعة بالفعل لهذا الإعلان."),
        )
        return redirect("main:ad_detail", ad_id=ad.id)

    # Create Facebook share request
    FacebookShareRequest.objects.create(
        ad=ad,
        user=request.user,
        payment_confirmed=True,  # Assuming payment is processed
        payment_amount=Decimal("100.00"),
    )

    # Update ad
    ad.share_on_facebook = True
    ad.facebook_share_requested = True
    ad.save()

    messages.success(
        request,
        _(
            "تم إرسال طلب النشر على فيسبوك بنجاح! سيتم مراجعته من قبل الإدارة خلال 24 ساعة."
        ),
    )

    return redirect("main:ad_detail", ad_id=ad.id)
