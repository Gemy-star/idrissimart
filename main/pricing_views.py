"""Views for pricing and packages display"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from constance import config

from .models import AdPackage, UserPackage, Category
from content.models import SiteConfiguration


@login_required
def ad_pricing_view(request):
    """
    Show pricing for posting an ad when user has no free ads remaining.
    Display:
    1. Category-specific pricing (if category_id in session/GET)
    2. Available packages
    3. Option to pay per ad
    """
    user = request.user
    site_config = SiteConfiguration.get_solo()

    # Check if user has active package with remaining ads
    active_package = (
        UserPackage.objects.filter(
            user=user,
            expiry_date__gte=timezone.now(),
            ads_remaining__gt=0,
        )
        .order_by("expiry_date")
        .first()
    )

    # If user has remaining ads, redirect to create ad
    if active_package:
        return redirect("main:ad_create")

    # Get category if specified
    category_id = request.GET.get("category")
    category = None
    category_base_price = None

    if category_id:
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            # Check if category has custom pricing (including 0)
            if (
                hasattr(category, "ad_creation_price")
                and category.ad_creation_price is not None
            ):
                category_base_price = category.ad_creation_price
            else:
                category_base_price = site_config.ad_base_fee
        except Category.DoesNotExist:
            pass

    # Default pricing
    if category_base_price is None:
        category_base_price = site_config.ad_base_fee

    # Get all active packages
    packages = AdPackage.objects.filter(is_active=True).order_by("price")

    # Get tax rate from Constance config (default 15%)
    tax_rate_percentage = getattr(config, "TAX_RATE", 15.0)
    tax_rate_decimal = Decimal(str(tax_rate_percentage)) / Decimal("100")

    # Calculate pricing details
    pricing_details = {
        "base_price": Decimal(str(category_base_price)),
        "tax_rate": tax_rate_decimal,
        "tax_rate_percentage": tax_rate_percentage,  # For display
    }

    pricing_details["tax_amount"] = (
        pricing_details["base_price"] * pricing_details["tax_rate"]
    )
    pricing_details["total_price"] = (
        pricing_details["base_price"] + pricing_details["tax_amount"]
    )

    context = {
        "category": category,
        "pricing_details": pricing_details,
        "packages": packages,
        "site_config": site_config,
        "user_has_active_package": False,
    }

    return render(request, "classifieds/ad_pricing.html", context)


@login_required
def check_and_redirect_to_pricing(request, category_id=None):
    """
    Helper view to check if user needs to see pricing page.
    Can be called before ad creation.
    """
    user = request.user

    # Check if user has active package with remaining ads
    active_package = (
        UserPackage.objects.filter(
            user=user,
            expiry_date__gte=timezone.now(),
            ads_remaining__gt=0,
        )
        .order_by("expiry_date")
        .first()
    )

    if active_package:
        # User has free ads, proceed to create
        if category_id:
            return redirect(f"{reverse('main:ad_create')}?category={category_id}")
        return redirect("main:ad_create")
    else:
        # No free ads, show pricing
        if category_id:
            return redirect(f"{reverse('main:ad_pricing')}?category={category_id}")
        return redirect("main:ad_pricing")
