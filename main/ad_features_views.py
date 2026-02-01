"""Views for Ad Features (contact_for_price, facebook_share, video)"""

import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from constance import config

from .models import ClassifiedAd, FacebookShareRequest


@login_required
def ad_features_upgrade(request, ad_id):
    """
    View for upgrading ad features (contact_for_price, facebook_share, video)
    """
    from .models import UserPackage
    from content.models import SiteConfiguration

    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)
    site_config = SiteConfiguration.get_solo()

    # Get user's active package to determine feature prices
    active_package = (
        UserPackage.objects.filter(
            user=request.user,
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
        pricing_source = "package"
        active_package_info = active_package
    else:
        # Use site default prices or make features free/unavailable
        feature_prices = {
            "contact_for_price": Decimal("0.00"),  # Free without package
            "facebook_share": Decimal("100.00"),
            "video": Decimal("75.00"),
        }
        pricing_source = "site_default"
        active_package_info = None

    if request.method == "POST":
        selected_features_json = request.POST.get("selected_features", "{}")
        try:
            selected_features = json.loads(selected_features_json)
        except json.JSONDecodeError:
            messages.error(request, _("خطأ في معالجة البيانات"))
            return redirect("main:ad_features_upgrade", ad_id=ad_id)

        # Calculate total cost for selected features
        total_cost = Decimal("0.00")
        features_to_enable = {}

        # Contact for Price
        if selected_features.get("contact_for_price") and not ad.contact_for_price:
            total_cost += feature_prices["contact_for_price"]
            features_to_enable["contact_for_price"] = True

        # Facebook Share
        if selected_features.get("facebook_share") and not ad.share_on_facebook:
            total_cost += feature_prices["facebook_share"]
            features_to_enable["facebook_share"] = True

        # Video (coming soon)
        if selected_features.get("video") and not ad.video_url:
            total_cost += feature_prices["video"]
            features_to_enable["video"] = True

        # If no new features selected
        if not features_to_enable:
            messages.info(request, _("لم يتم تحديد أي مميزات جديدة"))
            return redirect("main:ad_detail", slug=ad.slug)

        # Store upgrade info in session for payment
        request.session["upgrade_ad_id"] = ad.id
        request.session["upgrade_features"] = features_to_enable
        request.session["upgrade_total_cost"] = str(total_cost)

        if total_cost > 0:
            # Redirect to payment
            currency = ad.country.currency_symbol if ad.country else "ج.م"
            messages.info(
                request,
                _("يرجى إتمام الدفع لتفعيل المميزات. المبلغ المطلوب: {} {}").format(
                    total_cost, currency
                ),
            )
            return redirect("main:ad_upgrade_payment", ad_id=ad.id)
        else:
            # Free features - activate immediately
            updated_features = []
            if features_to_enable.get("contact_for_price"):
                ad.contact_for_price = True
                updated_features.append(_("تواصل ليصلك عرض سعر"))

            if features_to_enable.get("facebook_share"):
                ad.share_on_facebook = True
                ad.facebook_share_requested = True
                updated_features.append(_("نشر على فيسبوك"))

                FacebookShareRequest.objects.create(
                    ad=ad,
                    user=request.user,
                    payment_confirmed=True,
                    payment_amount=Decimal("0.00"),
                )

            if features_to_enable.get("video"):
                # Handle video URL
                video_url = request.POST.get("video_url", "").strip()
                if video_url:
                    ad.video_url = video_url
                    updated_features.append(_("إضافة فيديو"))

                # Handle video file upload
                video_file = request.FILES.get("video_file")
                if video_file:
                    ad.video_file = video_file
                    updated_features.append(_("رفع ملف فيديو"))

            ad.save()
            messages.success(
                request,
                _("تم تحديث مميزات الإعلان: ") + ", ".join(updated_features),
            )
            return redirect("main:ad_detail", slug=ad.slug)

    # Get tax rate from Constance config (default 15%)
    tax_rate_percentage = getattr(config, "TAX_RATE", 15.0)

    context = {
        "ad": ad,
        "feature_prices": feature_prices,
        "pricing_source": pricing_source,
        "active_package": active_package_info,
        "site_config": site_config,
        "tax_rate": tax_rate_percentage / 100.0,  # Convert to decimal (0.15)
        "tax_rate_percentage": tax_rate_percentage,  # For display (15)
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

    return redirect("main:ad_detail", slug=ad.slug)


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
        return redirect("main:ad_detail", slug=ad.slug)

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

    return redirect("main:ad_detail", slug=ad.slug)
