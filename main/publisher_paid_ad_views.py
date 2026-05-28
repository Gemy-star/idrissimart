"""
Publisher Paid Banner Views
Allows publishers to create paid banner ads, pay for them, then await admin approval.

Flow:
  1. Publisher fills the creation form.
  2. Form POST → creates PaidBanner (status=DRAFT, payment_status=unpaid) so the
     uploaded image is persisted correctly.  The pk is stored in the session.
  3. Publisher is redirected to the payment page (no pk in URL – read from session).
  4. After successful payment, process_paid_banner_payment() updates the ad to
     status=PENDING_APPROVAL / payment_status=paid and sends email alerts.
"""

import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from main.decorators import PublisherRequiredMixin, publisher_required
from main.models import Notification, PaidBanner, Payment
from main.payment_services import PaymentService
from main.payment_utils import PaymentContext, get_allowed_payment_methods

logger = logging.getLogger(__name__)

SESSION_KEY_PENDING_AD = "pending_paid_banner_id"


def _validate_image_file(image_file, expected_dims, label):
    """Return a list of error strings if image_file doesn't match expected_dims (w, h)."""
    try:
        from PIL import Image as PilImage
        image_file.seek(0)
        img = PilImage.open(image_file)
        w, h = img.size
        image_file.seek(0)
        if (w, h) != tuple(expected_dims):
            return [
                _(
                    "%(label)s: المقاس المرفوع %(w)s×%(h)s بكسل. المطلوب %(rw)s×%(rh)s بكسل."
                ) % {"label": label, "w": w, "h": h, "rw": expected_dims[0], "rh": expected_dims[1]}
            ]
    except Exception:
        pass  # إذا فشل فتح الصورة، سيُكتشف لاحقاً عند الحفظ
    return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _notify_staff_new_paid_ad(paid_ad):
    """Create in-app notifications for all staff about a newly submitted paid ad."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin_url = reverse("admin:main_paidbanner_change", args=[paid_ad.pk])
    for staff_user in User.objects.filter(is_staff=True, is_active=True):
        Notification.objects.create(
            user=staff_user,
            notification_type=Notification.NotificationType.GENERAL,
            title=_("إعلان بانر مدفوع جديد ينتظر المراجعة"),
            message=_(
                "المعلن {} قدّم إعلاناً مدفوعاً بعنوان «{}» وأتمّ عملية الدفع."
                " يرجى مراجعته والموافقة عليه."
            ).format(
                paid_ad.advertiser.get_full_name() or paid_ad.advertiser.username,
                paid_ad.title,
            ),
            link=admin_url,
        )


# ---------------------------------------------------------------------------
# List view  (publisher dashboard  ▶  My Paid Banner Ads)
# ---------------------------------------------------------------------------

class PublisherPaidAdListView(PublisherRequiredMixin, ListView):
    """Show the logged-in publisher's paid banner advertisements."""

    model = PaidBanner
    template_name = "dashboard/publisher_paid_ads.html"
    context_object_name = "paid_ads"
    paginate_by = 20

    def get_queryset(self):
        return (
            PaidBanner.objects.filter(advertiser=self.request.user)
            .select_related("country", "category")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "publisher_paid_ads"

        qs = self.get_queryset()
        context["stats"] = {
            "total": qs.count(),
            "pending": qs.filter(status=PaidBanner.Status.PENDING_APPROVAL).count(),
            "active": qs.filter(status=PaidBanner.Status.ACTIVE).count(),
            "unpaid": qs.filter(payment_status="unpaid").count(),
            "receipt_submitted": qs.filter(payment_status="receipt_submitted").count(),
        }
        return context


# ---------------------------------------------------------------------------
# Create view
# ---------------------------------------------------------------------------

@publisher_required
def publisher_paid_ad_create(request):
    """
    Let a publisher fill in the details for a paid banner ad.
    On POST, create the PaidBanner (DRAFT / unpaid) so the uploaded image
    is persisted, then store only the pk in the session and redirect to the
    payment page.  The ad remains DRAFT until payment is confirmed.
    """
    from main.models import Category, BannerPricing
    from content.models import Country
    from constance import config as constance_config

    current_country_code = request.session.get("selected_country", "EG")

    categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by("name")
    all_countries = Country.objects.filter(is_active=True).order_by("order", "name")
    all_site_pages = PaidBanner.get_all_site_pages()

    _STATIC_KEYS = {"home","categories","category_page","ad_detail","search","about","contact","faq","privacy","terms"}
    _BLOG_STATIC_KEYS = {"blog_list","blog_detail"}
    _SHOP_KEYS = {"cart","checkout","wishlist"}
    _USER_KEYS = {"profile","dashboard","chat"}
    site_page_groups = [
        {"icon": "fas fa-home",          "label": str(_("الصفحات الرئيسية")), "pages": [(k, l) for k, l in all_site_pages if k in _STATIC_KEYS]},
        {"icon": "fas fa-blog",          "label": str(_("المدونة")),           "pages": [(k, l) for k, l in all_site_pages if k in _BLOG_STATIC_KEYS or k.startswith("blog_category_")]},
        {"icon": "fas fa-shopping-cart", "label": str(_("المتجر والدفع")),     "pages": [(k, l) for k, l in all_site_pages if k in _SHOP_KEYS]},
        {"icon": "fas fa-user",          "label": str(_("منطقة المستخدم")),    "pages": [(k, l) for k, l in all_site_pages if k in _USER_KEYS]},
        {"icon": "fas fa-file-alt",      "label": str(_("صفحات مخصصة")),       "pages": [(k, l) for k, l in all_site_pages if k.startswith("custom_page_")]},
    ]
    site_page_groups = [g for g in site_page_groups if g["pages"]]

    # Per-day rates per ad_type (GENERAL placement as display base)
    pricing = {}
    for ad_type_choice in PaidBanner.AdType.choices:
        ad_type = ad_type_choice[0]
        pricing[ad_type] = BannerPricing.get_price(ad_type, PaidBanner.PlacementType.GENERAL)

    # Extra fee per additional country per day (from constance)
    extra_country_fee_per_day = float(getattr(constance_config, "PAID_BANNER_EXTRA_COUNTRY_FEE_PER_DAY", 20.0))

    # Phone & email verification
    from content.site_config import SiteConfiguration
    site_config = SiteConfiguration.get_solo()

    constance_verif_enabled = getattr(constance_config, "ENABLE_MOBILE_VERIFICATION", True)
    mobile_verification_enabled = constance_verif_enabled or site_config.require_phone_verification
    phone_verification_needed = (
        mobile_verification_enabled
        and not getattr(request.user, "is_mobile_verified", True)
    )

    constance_email_verif_enabled = getattr(constance_config, "ENABLE_EMAIL_VERIFICATION", True)
    email_verification_enabled = constance_email_verif_enabled or site_config.require_email_verification
    email_verification_needed = (
        email_verification_enabled
        and not getattr(request.user, "is_email_verified", True)
    )

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        title_ar = request.POST.get("title_ar", "").strip()
        description = request.POST.get("description", "").strip()
        ad_type = request.POST.get("ad_type", PaidBanner.AdType.BANNER)
        placement_type = request.POST.get("placement_type", PaidBanner.PlacementType.GENERAL)
        target_url = request.POST.get("target_url", "").strip()
        cta_text = request.POST.get("cta_text", "").strip() or str(_("المزيد"))
        # Multi-country: first id is primary, rest are extra
        country_ids = request.POST.getlist("country_ids")
        category_id = request.POST.get("category_id") or None
        try:
            duration_days = max(1, int(request.POST.get("duration_days", 1)))
        except (ValueError, TypeError):
            duration_days = 1
        company_name = request.POST.get("company_name", "").strip()
        contact_email = request.POST.get("contact_email", request.user.email).strip()
        contact_phone = request.POST.get("contact_phone", "").strip()
        image        = request.FILES.get("image")
        mobile_image = request.FILES.get("mobile_image")
        target_pages = request.POST.getlist("target_pages")

        errors = []
        if not title:
            errors.append(_("العنوان مطلوب."))
        if not target_url:
            errors.append(_("رابط الإعلان مطلوب."))
        if not image:
            errors.append(_("صورة الإعلان مطلوبة."))
        if duration_days < 1:
            errors.append(_("مدة الإعلان يجب أن تكون يوماً واحداً على الأقل."))
        if not country_ids:
            errors.append(_("يجب اختيار دولة واحدة على الأقل."))

        specs = PaidBanner.IMAGE_SPECS.get(ad_type)
        if specs and image:
            errors.extend(_validate_image_file(image, specs["desktop"], _("صورة الإعلان")))
        if specs:
            if specs["mobile_required"] and not mobile_image:
                errors.append(
                    _("صورة الموبايل إجبارية للبانر الإعلاني. المقاس المطلوب: %(w)s×%(h)s بكسل.")
                    % {"w": specs["mobile"][0], "h": specs["mobile"][1]}
                )
            elif specs["mobile"] and mobile_image:
                errors.extend(_validate_image_file(mobile_image, specs["mobile"], _("صورة الموبايل")))

        # Resolve primary and extra countries
        primary_country = None
        extra_country_objs = []
        if country_ids:
            primary_country = Country.objects.filter(pk=country_ids[0], is_active=True).first()
            if len(country_ids) > 1:
                extra_country_objs = list(Country.objects.filter(pk__in=country_ids[1:], is_active=True))
        if not primary_country:
            primary_country = Country.objects.filter(code=current_country_code, is_active=True).first()
        if not primary_country:
            primary_country = Country.objects.filter(is_active=True).first()
        if not primary_country:
            errors.append(_("لا توجد دولة متاحة. تواصل مع الإدارة."))

        category = None
        if category_id:
            category = Category.objects.filter(pk=category_id).first()
        if placement_type == PaidBanner.PlacementType.CATEGORY and not category:
            errors.append(_("يجب تحديد القسم عند اختيار موضع 'قسم محدد'."))

        if errors:
            for e in errors:
                messages.error(request, e)
            from main.utils import strip_phone_to_local as _strip
            _mob_local = _strip(request.user.mobile) if request.user.mobile else _strip(request.user.phone)
            return render(request, "dashboard/publisher_paid_ad_create.html", {
                "active_nav": "publisher_paid_ads",
                "categories": categories,
                "all_countries": all_countries,
                "all_site_pages": all_site_pages,
                "site_page_groups": site_page_groups,
                "selected_target_pages": request.POST.getlist("target_pages"),
                "pricing": pricing,
                "extra_country_fee_per_day": extra_country_fee_per_day,
                "ad_types": PaidBanner.AdType.choices,
                "placement_types": PaidBanner.PlacementType.choices,
                "current_country": current_country_code,
                "post_data": request.POST,
                "user_mobile_local": _mob_local,
                "mobile_verification_enabled": mobile_verification_enabled,
                "phone_verification_needed": phone_verification_needed,
                "email_verification_enabled": email_verification_enabled,
                "email_verification_needed": email_verification_needed,
            })

        # Total price: base per-day rate + extra_country_fee per extra country, × chosen days
        per_day_rate = BannerPricing.get_price(ad_type, placement_type)
        extra_per_day = Decimal(str(extra_country_fee_per_day)) * len(extra_country_objs)
        price = (per_day_rate + extra_per_day) * duration_days
        currency = getattr(primary_country, "currency", None) or "EGP"

        paid_ad = PaidBanner.objects.create(
            title=title,
            title_ar=title_ar,
            description=description,
            advertiser=request.user,
            company_name=company_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            image=image,
            mobile_image=mobile_image,
            target_url=target_url,
            cta_text=cta_text,
            ad_type=ad_type,
            placement_type=placement_type,
            country=primary_country,
            category=category,
            duration_days=duration_days,
            start_date=None,
            end_date=None,
            status=PaidBanner.Status.DRAFT,
            payment_status="unpaid",
            price=price,
            currency=currency,
            target_pages=target_pages,
        )
        if extra_country_objs:
            paid_ad.extra_countries.set(extra_country_objs)

        request.session[SESSION_KEY_PENDING_AD] = paid_ad.pk

        messages.info(request, _("يرجى إتمام عملية الدفع لإرسال الإعلان للمراجعة."))
        return redirect("main:publisher_paid_ad_payment")

    from main.utils import strip_phone_to_local
    user_mobile_local = strip_phone_to_local(request.user.mobile) if request.user.mobile else strip_phone_to_local(request.user.phone)
    context = {
        "active_nav": "publisher_paid_ads",
        "categories": categories,
        "all_countries": all_countries,
        "all_site_pages": all_site_pages,
        "site_page_groups": site_page_groups,
        "selected_target_pages": [],
        "pricing": pricing,
        "extra_country_fee_per_day": extra_country_fee_per_day,
        "ad_types": PaidBanner.AdType.choices,
        "placement_types": PaidBanner.PlacementType.choices,
        "current_country": current_country_code,
        "post_data": {},
        "user_mobile_local": user_mobile_local,
        "mobile_verification_enabled": mobile_verification_enabled,
        "phone_verification_needed": phone_verification_needed,
        "email_verification_enabled": email_verification_enabled,
        "email_verification_needed": email_verification_needed,
    }
    return render(request, "dashboard/publisher_paid_ad_create.html", context)


# ---------------------------------------------------------------------------
# Retry payment view  (from the list's "Pay Now" button)
# ---------------------------------------------------------------------------

@publisher_required
def publisher_paid_ad_retry_payment(request, pk):
    """
    Reached when the publisher clicks "Pay Now" for an unpaid DRAFT ad in
    their list.  Sets the session key and redirects to the payment page.
    """
    paid_ad = get_object_or_404(
        PaidBanner,
        pk=pk,
        advertiser=request.user,
        payment_status="unpaid",
    )
    request.session[SESSION_KEY_PENDING_AD] = paid_ad.pk
    return redirect("main:publisher_paid_ad_payment")


# ---------------------------------------------------------------------------
# Payment view  (no pk in URL – reads pending ad pk from session)
# ---------------------------------------------------------------------------

@login_required
def publisher_paid_ad_payment(request):
    """
    Payment page for a publisher's pending paid banner.
    The ad pk comes from the session (set by publisher_paid_ad_create), not the URL,
    so the payment step cannot be bypassed by guessing a URL.
    """
    from constance import config as constance_config

    from content.site_config import SiteConfiguration

    paid_ad_pk = request.session.get(SESSION_KEY_PENDING_AD)
    if not paid_ad_pk:
        messages.warning(request, _("لا يوجد إعلان قيد المعالجة. يرجى ملء النموذج أولاً."))
        return redirect("main:publisher_paid_ad_create")

    paid_ad = get_object_or_404(
        PaidBanner,
        pk=paid_ad_pk,
        advertiser=request.user,
    )

    # If already paid (e.g. back-button after payment), redirect to list
    if paid_ad.payment_status == "paid":
        request.session.pop(SESSION_KEY_PENDING_AD, None)
        messages.info(request, _("تم الدفع بالفعل لهذا الإعلان. ننتظر موافقة الإدارة."))
        return redirect("main:publisher_paid_ads")

    # Phone verification check
    constance_enabled = getattr(constance_config, "ENABLE_MOBILE_VERIFICATION", True)
    site_config = SiteConfiguration.get_solo()
    site_config_enabled = site_config.require_phone_verification
    is_mobile_verified = getattr(request.user, "is_mobile_verified", True)
    if (constance_enabled or site_config_enabled) and not is_mobile_verified:
        messages.warning(request, _("يجب التحقق من رقم هاتفك أولاً."))
        return redirect("main:phone_verification_required")

    total_amount = paid_ad.price
    currency = paid_ad.currency or "EGP"

    allowed_payment_methods = get_allowed_payment_methods(PaymentContext.PLATFORM_PAYMENT)

    from constance import config
    paymob_wallet_enabled = bool(getattr(config, "PAYMOB_WALLET_INTEGRATION_ID", ""))

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        from main.payment_utils import is_payment_method_allowed
        if payment_method not in ("instapay", "wallet") and not is_payment_method_allowed(
            payment_method, PaymentContext.PLATFORM_PAYMENT
        ):
            if payment_method == "offline":
                if not (
                    is_payment_method_allowed("instapay", PaymentContext.PLATFORM_PAYMENT) or
                    is_payment_method_allowed("wallet", PaymentContext.PLATFORM_PAYMENT)
                ):
                    messages.error(request, _("طريقة الدفع المختارة غير متاحة."))
                    return redirect("main:publisher_paid_ad_payment")
                payment_method = "instapay"
            else:
                messages.error(request, _("طريقة الدفع المختارة غير متاحة."))
                return redirect("main:publisher_paid_ad_payment")

        common_metadata = {
            "payment_type": "paid_banner",
            "paid_banner_ad_id": paid_ad.pk,
        }

        # --- Offline (Instapay / manual wallet upload) ---
        if payment_method == "instapay" or (
            payment_method == "wallet" and not paymob_wallet_enabled
        ):
            receipt = request.FILES.get("payment_receipt")
            if not receipt:
                messages.error(request, _("يرجى رفع إيصال الدفع."))
                return render(request, "payments/publisher_paid_ad_payment.html", {
                    "paid_ad": paid_ad,
                    "total_amount": total_amount,
                    "currency": currency,
                    "allowed_payment_methods": allowed_payment_methods,
                    "site_config": site_config,
                    "paymob_wallet_enabled": paymob_wallet_enabled,
                    "active_nav": "publisher_paid_ads",
                })

            Payment.objects.create(
                user=request.user,
                provider=Payment.PaymentProvider.BANK_TRANSFER,
                amount=total_amount,
                currency=currency,
                status=Payment.PaymentStatus.PENDING,
                description=f"إعلان بانر مدفوع: {paid_ad.title}",
                offline_payment_receipt=receipt,
                metadata=common_metadata,
            )
            # Mark receipt as submitted and status as PENDING_APPROVAL
            paid_ad.status = PaidBanner.Status.PENDING_APPROVAL
            paid_ad.payment_status = "receipt_submitted"
            paid_ad.save(update_fields=["status", "payment_status"])

            # Clear session key
            request.session.pop(SESSION_KEY_PENDING_AD, None)

            _notify_staff_new_paid_ad(paid_ad)
            messages.success(
                request,
                _("تم استلام طلب الدفع. سيتم مراجعته خلال 24 ساعة وتفعيل إعلانك بعد الموافقة.")
            )
            return redirect("main:publisher_paid_ads")

        # --- Online (Paymob / PayPal / wallet online) ---
        from django.urls import reverse

        if payment_method == "paypal":
            provider_key = "paypal"
        elif payment_method == "wallet":
            provider_key = "wallet"
        else:
            provider_key = "paymob"

        payment_obj = Payment.objects.create(
            user=request.user,
            provider=(
                Payment.PaymentProvider.PAYMOB
                if provider_key in ("paymob", "wallet")
                else Payment.PaymentProvider.PAYPAL
            ),
            amount=total_amount,
            currency=currency,
            status=Payment.PaymentStatus.PENDING,
            description=f"إعلان بانر مدفوع: {paid_ad.title}",
            metadata=common_metadata,
        )

        user_data = {
            "email": request.user.email,
            "first_name": request.user.first_name or request.user.username,
            "last_name": request.user.last_name or "",
            "phone": getattr(request.user, "mobile", "") or getattr(request.user, "phone", ""),
        }

        extra_kwargs = {}
        if provider_key == "paypal":
            extra_kwargs["return_url"] = request.build_absolute_uri(
                reverse("main:paypal_success")
            )
            extra_kwargs["cancel_url"] = request.build_absolute_uri(
                reverse("main:publisher_paid_ad_payment")
            )

        success, result = PaymentService().create_payment(
            provider_key,
            float(total_amount),
            currency,
            f"إعلان بانر مدفوع: {paid_ad.title}",
            user_data,
            **extra_kwargs,
        )

        if success:
            payment_url = result.get("approval_url") or result.get("iframe_url")
            if result.get("paypal_order_id"):
                payment_obj.metadata["paypal_order_id"] = result["paypal_order_id"]
            if result.get("paymob_order_id"):
                payment_obj.metadata["paymob_order_id"] = result["paymob_order_id"]
            if payment_url:
                payment_obj.save()
                return redirect(payment_url)

        payment_obj.status = Payment.PaymentStatus.FAILED
        payment_obj.save()
        logger.error(
            "Publisher paid ad: payment creation failed for ad %s: %s",
            paid_ad.pk,
            result,
        )
        messages.error(request, _("فشل إنشاء الدفع. يرجى المحاولة مرة أخرى."))

    context = {
        "paid_ad": paid_ad,
        "total_amount": total_amount,
        "currency": currency,
        "allowed_payment_methods": allowed_payment_methods,
        "site_config": site_config,
        "paymob_wallet_enabled": paymob_wallet_enabled,
        "active_nav": "publisher_paid_ads",
    }
    return render(request, "payments/publisher_paid_ad_payment.html", context)
