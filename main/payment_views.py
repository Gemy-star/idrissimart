"""
Payment Views for PayPal and Paymob integration
"""

import json
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from constance import config
from .models import Payment, AdPackage, UserPackage
from .payment_services import PaymentService
from .services.paypal_service import PayPalService
from .services.paymob_service import PaymobService
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@login_required
def payment_page(request, package_id=None):
    """Display payment options page"""
    from constance import config as constance_config
    from content.site_config import SiteConfiguration
    from django.contrib import messages

    package = None
    if package_id:
        package = get_object_or_404(AdPackage, id=package_id)

    payment_service = PaymentService()
    supported_providers = payment_service.get_supported_providers()

    context = {
        "package": package,
        "supported_providers": supported_providers,
        "site_url": config.SITE_URL,
    }

    return render(request, "payments/payment_page.html", context)


@login_required
@require_POST
def create_payment(request):
    """Create a new payment"""
    provider = request.POST.get("provider")
    package_id = request.POST.get("package_id")
    amount = request.POST.get("amount")
    currency = request.POST.get("currency", "EGP")

    if not all([provider, amount]):
        return JsonResponse({"success": False, "message": _("بيانات الدفع غير مكتملة")})

    try:
        amount = Decimal(amount)
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "message": _("مبلغ غير صحيح")})

    # Get package if specified
    package = None
    description = _("دفعة عامة")
    if package_id:
        try:
            package = AdPackage.objects.get(id=package_id)
            description = f"شراء باقة: {package.name}"
            amount = package.price
        except AdPackage.DoesNotExist:
            return JsonResponse({"success": False, "message": _("الباقة غير موجودة")})

    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        provider=provider,
        amount=amount,
        currency=currency,
        description=description,
        metadata={
            "package_id": package_id if package else None,
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "ip_address": request.META.get("REMOTE_ADDR", ""),
        },
    )

    # Initialize payment service
    payment_service = PaymentService()

    # Prepare user data
    user_data = {
        "email": request.user.email,
        "first_name": request.user.first_name or request.user.username,
        "last_name": request.user.last_name or "",
        "phone": getattr(request.user, "mobile", "")
        or getattr(request.user, "phone", ""),
    }

    # Create payment with provider
    if provider == "paypal":
        success, result = payment_service.create_payment(
            provider="paypal",
            amount=amount,
            currency=currency,
            description=description,
            return_url=request.build_absolute_uri(reverse("main:paypal_success")),
            cancel_url=request.build_absolute_uri(reverse("main:paypal_cancel")),
        )
    elif provider == "paymob":
        success, result = payment_service.create_payment(
            provider="paymob",
            amount=amount,
            currency="EGP",  # Paymob primarily uses EGP
            description=description,
            user_data=user_data,
        )
    else:
        success = False
        result = _("مزود الدفع غير مدعوم")

    if success:
        # result is always a dict: {"approval_url"/"paypal_order_id"} or {"iframe_url"}
        if provider == "paypal":
            payment.provider_transaction_id = result.get("paypal_order_id", "")
            payment.metadata.update(
                {
                    "paypal_order_id": result.get("paypal_order_id"),
                    "approval_url": result.get("approval_url"),
                }
            )
        elif provider in ["paymob", "mastercard", "visa"]:
            payment.metadata.update({
                "iframe_url": result.get("iframe_url"),
                "paymob_order_id": result.get("paymob_order_id"),
            })

        payment.save()

        redirect_url = result.get("approval_url") or result.get("iframe_url")
        return JsonResponse(
            {
                "success": True,
                "payment_id": payment.id,
                "redirect_url": redirect_url,
            }
        )
    else:
        payment.mark_failed(str(result))
        return JsonResponse({"success": False, "message": result})


@login_required
def paypal_success(request):
    """Handle PayPal payment success (PayPal v2 Orders API)"""
    # PayPal v2 returns ?token=ORDER_ID after user approval
    paypal_order_id = request.GET.get("token")

    if not paypal_order_id:
        messages.error(request, _("بيانات الدفع غير مكتملة"))
        return redirect("main:payment_failed")

    try:
        # Find payment record by the stored PayPal order ID
        payment = Payment.objects.get(
            user=request.user,
            metadata__paypal_order_id=paypal_order_id,
            status=Payment.PaymentStatus.PENDING,
        )

        # Capture the PayPal order
        success, capture_data, error = PayPalService.capture_order(paypal_order_id)

        if success and capture_data.get("status") == "COMPLETED":
            # Mark payment as completed
            payment.mark_completed(paypal_order_id)

            # Process package purchase if applicable
            package_id = payment.metadata.get("package_id")
            if package_id:
                process_package_purchase(payment, package_id)

            # Process ad payment or upgrade if applicable
            ad_id = payment.metadata.get("ad_id")
            payment_type = payment.metadata.get("payment_type", "ad_payment")
            if ad_id:
                if payment_type == "ad_upgrade":
                    process_ad_upgrade_payment(payment)
                else:
                    process_ad_payment(payment)

            messages.success(request, _("تم الدفع بنجاح"))
            return redirect("main:payment_success", payment_id=payment.id)
        else:
            payment.mark_failed(f"PayPal capture failed: {error or 'unknown'}")
            messages.error(request, _("فشل في تأكيد الدفع"))
            return redirect("main:payment_failed")

    except Payment.DoesNotExist:
        messages.error(request, _("عملية الدفع غير موجودة"))
        return redirect("main:payment_failed")
    except Exception as e:
        logger.error(f"PayPal success handling error: {str(e)}")
        messages.error(request, _("حدث خطأ في معالجة الدفع"))
        return redirect("main:payment_failed")


@login_required
def paypal_cancel(request):
    """Handle PayPal payment cancellation"""
    messages.warning(request, _("تم إلغاء عملية الدفع"))
    ad_id = request.GET.get("ad_id")
    if ad_id:
        return redirect("main:ad_payment", ad_id=ad_id)
    return redirect("main:packages_list")


@csrf_exempt
@require_POST
def paymob_callback(request):
    """Handle Paymob payment callback"""
    try:
        # Parse callback data
        callback_data = json.loads(request.body)

        # Extract payment information
        order_id = callback_data.get("order", {}).get("id")
        transaction_id = callback_data.get("id")
        success = callback_data.get("success", False)

        if not order_id:
            return HttpResponse("Invalid callback data", status=400)

        # Find payment record
        payment = Payment.objects.get(
            metadata__paymob_order_id=order_id, status=Payment.PaymentStatus.PENDING
        )

        if success:
            # Mark payment as completed
            payment.mark_completed(str(transaction_id))

            # Process package purchase if applicable
            package_id = payment.metadata.get("package_id")
            if package_id:
                process_package_purchase(payment, package_id)

            # Process ad payment or upgrade if applicable
            ad_id = payment.metadata.get("ad_id")
            payment_type = payment.metadata.get("payment_type", "ad_payment")
            if ad_id:
                if payment_type == "ad_upgrade":
                    process_ad_upgrade_payment(payment)
                else:
                    process_ad_payment(payment)

            logger.info(f"Paymob payment completed: {payment.id}")
        else:
            payment.mark_failed("Paymob payment failed")
            logger.warning(f"Paymob payment failed: {payment.id}")

        return HttpResponse("OK")

    except Payment.DoesNotExist:
        logger.error(f"Paymob callback: Payment not found for order {order_id}")
        return HttpResponse("Payment not found", status=404)
    except Exception as e:
        logger.error(f"Paymob callback error: {str(e)}")
        return HttpResponse("Error processing callback", status=500)


def process_package_purchase(payment, package_id):
    """Process package purchase after successful payment"""
    try:
        package = AdPackage.objects.get(id=package_id)

        # Create user package
        expiry_date = timezone.now() + timedelta(days=package.duration_days)

        user_package = UserPackage.objects.create(
            user=payment.user,
            payment=payment,
            package=package,
            expiry_date=expiry_date,
            ads_remaining=package.max_ads,
        )

        logger.info(f"Package purchased: User {payment.user.id}, Package {package.id}")

    except AdPackage.DoesNotExist:
        logger.error(f"Package not found: {package_id}")
    except Exception as e:
        logger.error(f"Error processing package purchase: {str(e)}")


@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    context = {"payment": payment, "package": None}

    # Get associated package if any
    if payment.packages.exists():
        context["package"] = payment.packages.first().package

    return render(request, "payments/payment_success.html", context)


@login_required
def payment_failed(request):
    """Payment failed page"""
    return render(request, "payments/payment_failed.html")


@login_required
def payment_history(request):
    """Display user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "payments": payments,
        "active_nav": "payment_history",
    }

    return render(request, "payments/payment_history.html", context)


@login_required
def payment_page_upgrade(request, payment_id):
    """Display payment options page for ad upgrades"""
    from constance import config as constance_config
    from content.site_config import SiteConfiguration
    from django.contrib import messages

    # Check phone verification requirement
    constance_enabled = getattr(constance_config, "ENABLE_MOBILE_VERIFICATION", True)
    site_config = SiteConfiguration.get_solo()
    site_config_enabled = site_config.require_phone_verification

    # If either is enabled and user's phone is not verified, redirect
    if (constance_enabled or site_config_enabled) and not request.user.is_mobile_verified:
        messages.warning(
            request,
            _("يجب التحقق من رقم هاتفك قبل ترقية الإعلانات. الرجاء تأكيد رقم هاتفك أولاً.")
        )
        return redirect("main:phone_verification_required")

    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # Get upgrade data from payment metadata
    upgrade_data = payment.metadata
    ad_id = payment.metadata.get("ad_id")

    # Get the ad to extract currency info
    ad = None
    if ad_id:
        from .models import ClassifiedAd
        try:
            ad = ClassifiedAd.objects.select_related('country').get(id=ad_id)
        except ClassifiedAd.DoesNotExist:
            pass

    payment_service = PaymentService()
    supported_providers = payment_service.get_supported_providers()

    # Get currency from payment or ad's country
    currency = payment.currency
    if ad and ad.country:
        currency = ad.country.currency or payment.currency

    context = {
        "payment": payment,
        "ad": ad,
        "upgrade_data": upgrade_data,
        "supported_providers": supported_providers,
        "site_url": config.SITE_URL,
        "is_upgrade": True,
        "currency": currency,
        "total_amount": payment.amount,
    }

    return render(request, "payments/payment_page.html", context)


@login_required
def ad_payment(request, ad_id):
    """Payment page for new ad with features"""
    from .models import ClassifiedAd
    from constance import config as constance_config
    from content.models import SiteConfiguration
    from .payment_utils import get_allowed_payment_methods, PaymentContext
    from django.contrib import messages

    # Check phone verification requirement
    constance_enabled = getattr(constance_config, "ENABLE_MOBILE_VERIFICATION", True)
    site_config = SiteConfiguration.get_solo()
    site_config_enabled = site_config.require_phone_verification

    # If either is enabled and user's phone is not verified, redirect
    if (constance_enabled or site_config_enabled) and not request.user.is_mobile_verified:
        messages.warning(
            request,
            _("يجب التحقق من رقم هاتفك قبل نشر الإعلانات. الرجاء تأكيد رقم هاتفك أولاً.")
        )
        return redirect("main:phone_verification_required")

    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)

    # Get payment details from session
    total_amount = Decimal(request.session.get("ad_payment_amount", "0"))
    base_fee = Decimal(request.session.get("ad_base_fee", "0"))
    features_cost = Decimal(request.session.get("ad_features_cost", "0"))
    features = request.session.get("ad_features", {})
    is_renewal = request.session.get("ad_renewal", False)

    # Get currency from ad's country
    currency = "EGP"  # default
    if ad.country:
        currency = ad.country.currency or "EGP"

    # Get allowed payment methods for platform payments
    allowed_payment_methods = get_allowed_payment_methods(
        PaymentContext.PLATFORM_PAYMENT
    )

    # Wallet online = Paymob wallet integration is configured
    paymob_wallet_enabled = bool(getattr(config, "PAYMOB_WALLET_INTEGRATION_ID", ""))

    # If ad is already active, redirect to it
    if ad.status == ClassifiedAd.AdStatus.ACTIVE:
        messages.info(request, _("هذا الإعلان نشط بالفعل"))
        return redirect("main:ad_detail", slug=ad.slug)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # Handle free ad confirmation (no cost)
        if payment_method == "free" and total_amount == 0:
            if ad.status == ClassifiedAd.AdStatus.DRAFT:
                features = request.session.get("ad_features", {})
                ad.is_paid = True
                ad.status = ClassifiedAd.AdStatus.PENDING
                ad.is_highlighted = features.get("highlighted", False)
                ad.is_urgent = features.get("urgent", False)
                ad.is_pinned = features.get("pinned", False)
                ad.contact_for_price = features.get("contact_for_price", False)
                ad.features_price = Decimal("0.00")
                ad.save()

                has_free_ads = request.session.get("has_free_ads", False)
                if has_free_ads:
                    from .models import UserPackage
                    package_with_ads = UserPackage.objects.filter(
                        user=ad.user,
                        expiry_date__gte=timezone.now(),
                        ads_remaining__gt=0,
                    ).order_by("expiry_date").first()
                    if package_with_ads:
                        package_with_ads.use_ad()

                from .models import Notification
                staff_users = User.objects.filter(is_staff=True, is_active=True)
                for staff_user in staff_users:
                    Notification.objects.create(
                        user=staff_user,
                        notification_type=Notification.NotificationType.GENERAL,
                        title=_("إعلان جديد ينتظر المراجعة"),
                        message=_("تم تقديم إعلان جديد بعنوان '{}' من المستخدم {}.").format(
                            ad.title, ad.user.get_full_name() or ad.user.username
                        ),
                        link=ad.get_absolute_url(),
                    )

                messages.info(request, _("تم إرسال إعلانك للمراجعة وسيتم نشره بعد موافقة الإدارة."))
            return redirect("main:ad_create_success", pk=ad.pk)

        # Handle legacy "offline" payment method by checking if instapay/wallet are allowed
        if payment_method == "offline":
            # Check if any offline method is allowed
            from .payment_utils import is_payment_method_allowed
            if not (is_payment_method_allowed("instapay", PaymentContext.PLATFORM_PAYMENT) or
                    is_payment_method_allowed("wallet", PaymentContext.PLATFORM_PAYMENT)):
                messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
                return redirect("main:ad_payment", ad_id=ad.id)
            # Set to instapay as default for offline payments
            payment_method = "instapay"
        else:
            # Validate payment method is allowed for platform payments
            from .payment_utils import is_payment_method_allowed
            if not is_payment_method_allowed(
                payment_method, PaymentContext.PLATFORM_PAYMENT
            ):
                messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
                return redirect("main:ad_payment", ad_id=ad.id)

        if payment_method == "instapay" or (payment_method == "wallet" and not paymob_wallet_enabled):
            # Handle offline payment with receipt
            receipt = request.FILES.get("payment_receipt")

            if not receipt:
                messages.error(request, _("يرجى رفع إيصال الدفع"))
                return render(
                    request,
                    "payments/ad_payment.html",
                    {
                        "ad": ad,
                        "total_amount": total_amount,
                        "base_fee": base_fee,
                        "features_cost": features_cost,
                        "features": features,
                        "site_config": site_config,
                        "allowed_payment_methods": allowed_payment_methods,
                        "currency": currency,
                    },
                )

            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                provider=Payment.PaymentProvider.BANK_TRANSFER,
                amount=total_amount,
                currency=currency,
                status=Payment.PaymentStatus.PENDING,
                description=f"دفع إعلان: {ad.title}",
                offline_payment_receipt=receipt,
                metadata={
                    "ad_id": ad.id,
                    "features": features,
                    "base_fee": str(base_fee),
                    "features_cost": str(features_cost),
                    "is_renewal": is_renewal,
                },
            )

            messages.success(
                request,
                _("تم استلام طلب الدفع. سيتم مراجعته خلال 24 ساعة وتفعيل إعلانك."),
            )

            # Clear session
            for key in [
                "pending_ad_id",
                "ad_features",
                "ad_payment_amount",
                "ad_base_fee",
                "ad_features_cost",
                "ad_renewal",
            ]:
                request.session.pop(key, None)

            return redirect("main:my_ads")

        elif payment_method in ["paymob", "paypal", "visa", "wallet"]:
            payment = Payment.objects.create(
                user=request.user,
                provider=(
                    Payment.PaymentProvider.PAYMOB
                    if payment_method in ["paymob", "visa", "wallet"]
                    else Payment.PaymentProvider.PAYPAL
                ),
                amount=total_amount,
                currency=currency,
                status=Payment.PaymentStatus.PENDING,
                description=f"دفع إعلان: {ad.title}",
                metadata={
                    "ad_id": ad.id,
                    "features": features,
                    "base_fee": str(base_fee),
                    "features_cost": str(features_cost),
                    "is_renewal": is_renewal,
                },
            )

            user_data = {
                "email": request.user.email,
                "first_name": request.user.first_name or request.user.username,
                "last_name": request.user.last_name or "",
                "phone": getattr(request.user, "mobile", "") or getattr(request.user, "phone", ""),
            }

            if payment_method == "paypal":
                provider_key = "paypal"
            elif payment_method == "wallet":
                provider_key = "wallet"
            else:
                provider_key = "paymob"
            extra_kwargs = {}
            if payment_method == "paypal":
                extra_kwargs["return_url"] = request.build_absolute_uri(
                    reverse("main:paypal_success")
                )
                extra_kwargs["cancel_url"] = request.build_absolute_uri(
                    reverse("main:paypal_cancel") + f"?ad_id={ad.id}"
                )
            success, result = PaymentService().create_payment(
                provider_key,
                float(total_amount),
                currency,
                f"دفع إعلان: {ad.title}",
                user_data,
                **extra_kwargs,
            )

            if success:
                payment_url = result.get("approval_url") or result.get("iframe_url")
                # Store gateway order IDs in metadata so callbacks can find this payment
                if result.get("paypal_order_id"):
                    payment.metadata["paypal_order_id"] = result["paypal_order_id"]
                if result.get("paymob_order_id"):
                    payment.metadata["paymob_order_id"] = result["paymob_order_id"]
                if payment_url:
                    payment.save()
                    return redirect(payment_url)

            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            logger.error("Payment creation failed: %s", result)
            if not success and "disabled" in str(result).lower():
                messages.error(request, _("بوابة الدفع غير مفعّلة حالياً. يرجى التواصل مع الإدارة."))
            else:
                messages.error(request, _("فشل إنشاء الدفع. يرجى المحاولة مرة أخرى أو اختيار طريقة دفع أخرى."))

    context = {
        "ad": ad,
        "total_amount": total_amount,
        "base_fee": base_fee,
        "features_cost": features_cost,
        "features": features,
        "site_config": site_config,
        "allowed_payment_methods": allowed_payment_methods,
        "currency": currency,
        "paymob_wallet_enabled": paymob_wallet_enabled,
    }

    return render(request, "payments/ad_payment.html", context)


def process_ad_payment(payment):
    """
    Process ad payment after successful payment confirmation.
    Changes ad status from DRAFT to PENDING/ACTIVE and applies features.
    """
    from .models import ClassifiedAd, User, Notification, UserPackage

    ad_id = payment.metadata.get("ad_id")
    features = payment.metadata.get("features", {})
    base_fee = Decimal(payment.metadata.get("base_fee", "0"))

    if not ad_id:
        logger.error(f"No ad_id in payment metadata for payment {payment.id}")
        return False

    try:
        ad = ClassifiedAd.objects.get(id=ad_id)

        # Apply features
        ad.is_highlighted = features.get("highlighted", False)
        ad.is_urgent = features.get("urgent", False)
        ad.is_pinned = features.get("pinned", False)
        ad.contact_for_price = features.get("contact_for_price", False)
        ad.auto_refresh = features.get("auto_refresh", False)
        # video_url/video_file were already saved when the ad was created;
        # no extra action needed for add_video beyond what was saved.
        ad.features_price = Decimal(payment.metadata.get("features_cost", "0"))

        # Mark ad as paid
        ad.is_paid = True

        # Change status based on current ad state
        is_renewal = payment.metadata.get("is_renewal", False)

        if ad.status == ClassifiedAd.AdStatus.DRAFT or (
            is_renewal and ad.status == ClassifiedAd.AdStatus.EXPIRED
        ):
            ad.status = ClassifiedAd.AdStatus.PENDING
            status_msg = _("قيد المراجعة")

            # Notify all staff users that an ad needs review
            from .models import User as UserModel
            staff_users = UserModel.objects.filter(is_staff=True, is_active=True)
            for staff_user in staff_users:
                Notification.objects.create(
                    user=staff_user,
                    notification_type=Notification.NotificationType.GENERAL,
                    title=_("إعلان ينتظر المراجعة"),
                    message=_("تم تقديم إعلان بعنوان '{}' وتم سداد رسومه.").format(ad.title),
                    link=ad.get_absolute_url(),
                )

            # If user paid base fee (no package), don't deduct from package
            if base_fee == 0 and not is_renewal:
                # User had a package, deduct ad count
                active_package = (
                    UserPackage.objects.filter(
                        user=ad.user,
                        ads_remaining__gt=0,
                        expiry_date__gte=timezone.now(),
                    )
                    .order_by("expiry_date")
                    .first()
                )
                if active_package:
                    active_package.use_ad()

            ad.save()

            # Send notification to user
            Notification.objects.create(
                user=ad.user,
                notification_type=Notification.NotificationType.GENERAL,
                title=_("تم تأكيد الدفع"),
                message=_("تم تأكيد دفع إعلانك {} وتحويله إلى {}.").format(
                    ad.title, status_msg
                ),
                link=ad.get_absolute_url(),
            )

            logger.info(
                f"Ad {ad.id} status changed to PENDING after payment {payment.id}"
            )
            return True
        else:
            logger.warning(
                f"Ad {ad.id} is not in DRAFT/EXPIRED status, current status: {ad.status}"
            )
            return False

    except ClassifiedAd.DoesNotExist:
        logger.error(f"Ad {ad_id} not found for payment {payment.id}")
        return False
    except Exception as e:
        logger.error(f"Error processing ad payment {payment.id}: {str(e)}")
        return False


@login_required
@require_POST
def confirm_ad_payment(request, payment_id):
    """Admin confirms offline ad payment or upgrade"""
    from .models import ClassifiedAd, User

    if not request.user.is_staff:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)

    payment = get_object_or_404(Payment, id=payment_id)

    # Check payment type and process accordingly
    payment_type = payment.metadata.get("payment_type", "ad_payment")
    if payment_type == "ad_upgrade":
        success = process_ad_upgrade_payment(payment)
    else:
        success = process_ad_payment(payment)

    if not success:
        return JsonResponse(
            {"success": False, "message": _("فشل في معالجة دفع الإعلان")}
        )

    # Mark payment as completed
    payment.mark_completed()

    return JsonResponse(
        {"success": True, "message": _("تم تأكيد الدفع وتفعيل الإعلان")}
    )


@login_required
def package_checkout(request, package_id):
    """Checkout page for package purchase with offline/online payment options"""
    from constance import config
    from content.models import SiteConfiguration
    from .payment_utils import get_allowed_payment_methods, PaymentContext

    from content.verification_utils import is_phone_verification_required
    phone_verification_required = is_phone_verification_required()

    site_config = SiteConfiguration.get_solo()
    package = get_object_or_404(AdPackage, id=package_id, is_active=True)

    # Verify package is in session
    session_package_id = request.session.get("package_checkout_id")
    if not session_package_id or int(session_package_id) != package.id:
        messages.error(request, _("جلسة الدفع غير صالحة. يرجى المحاولة مرة أخرى."))
        return redirect("main:packages_list")

    total_amount = package.price

    # If package is free, activate it immediately
    if total_amount == 0:
        from .models import UserPackage
        from django.utils import timezone
        from datetime import timedelta

        # Create and activate the package
        user_package = UserPackage.objects.create(
            user=request.user,
            package=package,
            ads_remaining=package.ad_count,
            expiry_date=timezone.now() + timedelta(days=package.duration_days),
            is_active=True,
        )

        # Clear session
        request.session.pop("package_checkout_id", None)

        messages.success(
            request,
            _("تم تفعيل الباقة المجانية {} بنجاح! لديك {} إعلانات متاحة.").format(
                package.name, package.ad_count
            ),
        )
        return redirect("main:my_ads")

    # Get currency from session (selected country) or default
    selected_country_code = request.session.get("selected_country", "EG")
    currency = "EGP"  # default
    try:
        from content.models import Country
        country = Country.objects.get(code=selected_country_code)
        currency = country.currency or "EGP"
    except:
        pass

    # Get allowed payment methods for platform payments
    allowed_payment_methods = get_allowed_payment_methods(
        PaymentContext.PLATFORM_PAYMENT
    )

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # Handle legacy "offline" payment method by checking if instapay/wallet are allowed
        if payment_method == "offline":
            # Check if any offline method is allowed
            from .payment_utils import is_payment_method_allowed
            if not (is_payment_method_allowed("instapay", PaymentContext.PLATFORM_PAYMENT) or
                    is_payment_method_allowed("wallet", PaymentContext.PLATFORM_PAYMENT)):
                messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
                return redirect("main:package_checkout", package_id=package.id)
            # Set to instapay as default for offline payments
            payment_method = "instapay"
        else:
            # Validate payment method is allowed for platform payments
            from .payment_utils import is_payment_method_allowed
            if not is_payment_method_allowed(
                payment_method, PaymentContext.PLATFORM_PAYMENT
            ):
                messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
                return redirect("main:package_checkout", package_id=package.id)

        if payment_method in ["instapay", "wallet"]:
            # Handle offline payment methods with receipt
            receipt = request.FILES.get("payment_receipt")

            if not receipt:
                messages.error(request, _("يرجى رفع إيصال الدفع"))
                return render(
                    request,
                    "payments/package_checkout.html",
                    {
                        "package": package,
                        "total_amount": total_amount,
                        "site_config": site_config,
                        "allowed_payment_methods": allowed_payment_methods,
                        "currency": currency,
                    },
                )

            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                provider=Payment.PaymentProvider.BANK_TRANSFER,
                amount=total_amount,
                currency=currency,
                status=Payment.PaymentStatus.PENDING,
                description=f"شراء باقة: {package.name} ({payment_method})",
                offline_payment_receipt=receipt,
                metadata={
                    "package_id": package.id,
                    "package_name": package.name,
                    "ad_count": package.ad_count,
                    "duration_days": package.duration_days,
                    "payment_method": payment_method,
                },
            )

            messages.success(
                request,
                _("تم استلام طلب الدفع. سيتم مراجعته خلال 24 ساعة وتفعيل باقتك."),
            )

            # Clear session
            request.session.pop("package_checkout_id", None)
            request.session.pop("package_checkout_amount", None)

            return redirect("main:my_ads")

        elif payment_method in ["paymob", "paypal", "visa", "card"]:
            # Determine provider based on payment method
            if payment_method == "paypal":
                provider = Payment.PaymentProvider.PAYPAL
            elif payment_method in ["paymob", "visa", "card"]:
                provider = Payment.PaymentProvider.PAYMOB
            else:
                provider = Payment.PaymentProvider.PAYMOB

            # Create payment record for online payment
            payment = Payment.objects.create(
                user=request.user,
                provider=provider,
                amount=total_amount,
                currency=currency,
                status=Payment.PaymentStatus.PENDING,
                description=f"شراء باقة: {package.name}",
                metadata={
                    "package_id": package.id,
                    "package_name": package.name,
                    "ad_count": package.ad_count,
                    "duration_days": package.duration_days,
                    "payment_method": payment_method,
                },
            )

            # Initialize payment service
            payment_service = PaymentService()

            # Prepare user data
            user_data = {
                "email": request.user.email,
                "first_name": request.user.first_name or request.user.username,
                "last_name": request.user.last_name or "",
                "phone": getattr(request.user, "mobile", "")
                or getattr(request.user, "phone", ""),
            }

            provider_key = "paypal" if payment_method == "paypal" else "paymob"
            success, result = payment_service.create_payment(
                provider_key,
                float(total_amount),
                currency,
                f"شراء باقة: {package.name}",
                user_data,
            )

            if success:
                payment_url = result.get("approval_url") or result.get("iframe_url")
                if payment_url:
                    payment.payment_url = payment_url
                    payment.save()
                    # Clear session
                    request.session.pop("package_checkout_id", None)
                    request.session.pop("package_checkout_amount", None)
                    return redirect(payment_url)

            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            logger.error("Payment creation failed: %s", result)
            if not success and "disabled" in str(result).lower():
                messages.error(request, _("بوابة الدفع غير مفعّلة حالياً. يرجى التواصل مع الإدارة."))
            else:
                messages.error(request, _("فشل إنشاء الدفع. يرجى المحاولة مرة أخرى أو اختيار طريقة دفع أخرى."))

    context = {
        "package": package,
        "total_amount": total_amount,
        "site_config": site_config,
        "allowed_payment_methods": allowed_payment_methods,
        "allow_offline_payment": site_config.allow_offline_payment,
        "offline_payment_instructions": site_config.offline_payment_instructions,
        "currency": currency,
        "phone_verification_required": phone_verification_required,
    }

    return render(request, "payments/package_checkout.html", context)


@login_required
@require_POST
def confirm_package_payment(request, payment_id):
    """Admin confirms offline package payment"""
    if not request.user.is_staff:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)

    payment = get_object_or_404(Payment, id=payment_id)
    package_id = payment.metadata.get("package_id")

    if not package_id:
        return JsonResponse({"success": False, "message": "Invalid payment data"})

    package = get_object_or_404(AdPackage, id=package_id)

    # Create user package with payment link
    user_package = UserPackage.objects.create(
        user=payment.user,
        payment=payment,  # Link payment to UserPackage
        package=package,
        ads_remaining=package.ad_count,
        expiry_date=timezone.now() + timedelta(days=package.duration_days),
    )

    # Mark payment as completed
    payment.mark_completed()

    # Send notification to user
    from .models import Notification

    Notification.objects.create(
        user=payment.user,
        notification_type=Notification.NotificationType.GENERAL,
        title=_("تم تأكيد الدفع"),
        message=_("تم تأكيد دفع باقة {} وإضافة {} إعلانات إلى رصيدك.").format(
            package.name, package.ad_count
        ),
    )

    return JsonResponse({"success": True, "message": _("تم تأكيد الدفع وتفعيل الباقة")})


@login_required
def ad_upgrade_payment(request, ad_id):
    """Payment page for upgrading existing ad features"""
    from .models import ClassifiedAd
    from content.models import SiteConfiguration
    from .payment_utils import get_allowed_payment_methods, PaymentContext

    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)
    site_config = SiteConfiguration.get_solo()

    # Get payment details from session
    total_amount = Decimal(request.session.get("upgrade_total_cost", "0"))
    upgrade_features = request.session.get("upgrade_features", {})

    # Get currency from ad's country
    currency = "EGP"  # default
    if ad.country:
        currency = ad.country.currency or "EGP"

    # Get allowed payment methods for platform payments
    allowed_payment_methods = get_allowed_payment_methods(
        PaymentContext.PLATFORM_PAYMENT
    )

    # If no payment needed (features are free in site config), apply them directly
    if total_amount == 0:
        # Apply features directly if they're free
        if upgrade_features:
            ad.is_highlighted = upgrade_features.get("highlighted", ad.is_highlighted)
            ad.is_urgent = upgrade_features.get("urgent", ad.is_urgent)
            ad.is_pinned = upgrade_features.get("pinned", ad.is_pinned)
            ad.auto_refresh = upgrade_features.get("auto_refresh", ad.auto_refresh)
            ad.save()

            # Clear session
            for key in ["upgrade_ad_id", "upgrade_features", "upgrade_total_cost"]:
                request.session.pop(key, None)

            messages.success(request, _("تم تطبيق المميزات على إعلانك بنجاح"))
        else:
            messages.info(request, _("لا توجد مميزات جديدة تتطلب دفع"))
        return redirect("main:ad_detail", slug=ad.slug)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # Handle legacy "offline" payment method by checking if instapay/wallet are allowed
        if payment_method == "offline":
            # Check if any offline method is allowed
            from .payment_utils import is_payment_method_allowed
            if not (is_payment_method_allowed("instapay", PaymentContext.PLATFORM_PAYMENT) or
                    is_payment_method_allowed("wallet", PaymentContext.PLATFORM_PAYMENT)):
                messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
                return redirect("main:ad_upgrade_payment", ad_id=ad.id)
            # Set to instapay as default for offline payments
            payment_method = "instapay"
        else:
            # Validate payment method is allowed for platform payments
            from .payment_utils import is_payment_method_allowed
            if not is_payment_method_allowed(
                payment_method, PaymentContext.PLATFORM_PAYMENT
            ):
                messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
                return redirect("main:ad_upgrade_payment", ad_id=ad.id)

        if payment_method in ["instapay", "wallet"]:
            # Handle offline payment with receipt
            receipt = request.FILES.get("payment_receipt")

            if not receipt:
                messages.error(request, _("يرجى رفع إيصال الدفع"))
                return render(
                    request,
                    "payments/ad_upgrade_payment.html",
                    {
                        "ad": ad,
                        "total_amount": total_amount,
                        "upgrade_features": upgrade_features,
                        "site_config": site_config,
                        "allowed_payment_methods": allowed_payment_methods,
                        "currency": currency,
                    },
                )

            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                provider=Payment.PaymentProvider.BANK_TRANSFER,
                amount=total_amount,
                currency=currency,
                status=Payment.PaymentStatus.PENDING,
                description=f"ترقية مميزات الإعلان: {ad.title}",
                offline_payment_receipt=receipt,
                metadata={
                    "ad_id": ad.id,
                    "upgrade_features": upgrade_features,
                    "payment_type": "ad_upgrade",
                },
            )

            messages.success(
                request,
                _("تم استلام طلب الدفع. سيتم مراجعته خلال 24 ساعة وتفعيل المميزات."),
            )

            # Clear session
            for key in ["upgrade_ad_id", "upgrade_features", "upgrade_total_cost"]:
                request.session.pop(key, None)

            return redirect("main:my_ads")

        elif payment_method in ["paymob", "paypal", "visa", "card"]:
            payment = Payment.objects.create(
                user=request.user,
                provider=(
                    Payment.PaymentProvider.PAYMOB
                    if payment_method in ["paymob", "visa", "card"]
                    else Payment.PaymentProvider.PAYPAL
                ),
                amount=total_amount,
                currency=currency,
                status=Payment.PaymentStatus.PENDING,
                description=f"ترقية مميزات الإعلان: {ad.title}",
                metadata={
                    "ad_id": ad.id,
                    "upgrade_features": upgrade_features,
                    "payment_type": "ad_upgrade",
                },
            )

            user_data = {
                "email": request.user.email,
                "first_name": request.user.first_name or request.user.username,
                "last_name": request.user.last_name or "",
                "phone": getattr(request.user, "mobile", "") or getattr(request.user, "phone", ""),
            }

            provider_key = "paypal" if payment_method == "paypal" else "paymob"
            success, result = PaymentService().create_payment(
                provider_key,
                float(total_amount),
                currency,
                f"ترقية مميزات الإعلان: {ad.title}",
                user_data,
            )

            if success:
                payment_url = result.get("approval_url") or result.get("iframe_url")
                if payment_url:
                    payment.payment_url = payment_url
                    payment.save()
                    return redirect(payment_url)

            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            logger.error("Payment creation failed: %s", result)
            if not success and "disabled" in str(result).lower():
                messages.error(request, _("بوابة الدفع غير مفعّلة حالياً. يرجى التواصل مع الإدارة."))
            else:
                messages.error(request, _("فشل إنشاء الدفع. يرجى المحاولة مرة أخرى أو اختيار طريقة دفع أخرى."))

    context = {
        "ad": ad,
        "total_amount": total_amount,
        "upgrade_features": upgrade_features,
        "site_config": site_config,
        "allowed_payment_methods": allowed_payment_methods,
        "currency": currency,
    }

    return render(request, "payments/ad_upgrade_payment.html", context)


def process_ad_upgrade_payment(payment):
    """
    Process ad upgrade payment after successful payment confirmation.
    Applies additional features to existing ad.
    """
    from .models import ClassifiedAd, FacebookShareRequest, Notification

    ad_id = payment.metadata.get("ad_id")
    upgrade_features = payment.metadata.get("upgrade_features", {})

    if not ad_id:
        logger.error(f"No ad_id in payment metadata for payment {payment.id}")
        return False

    try:
        ad = ClassifiedAd.objects.get(id=ad_id)
        applied_features = []

        # Apply upgrade features
        if upgrade_features.get("contact_for_price"):
            ad.contact_for_price = True
            applied_features.append(_("تواصل ليصلك عرض سعر"))

        if upgrade_features.get("facebook_share"):
            ad.share_on_facebook = True
            ad.facebook_share_requested = True
            applied_features.append(_("نشر على فيسبوك"))

            # Create FacebookShareRequest
            FacebookShareRequest.objects.create(
                ad=ad,
                user=ad.user,
                payment_confirmed=True,
                payment_amount=payment.amount,
            )

        if upgrade_features.get("video") or upgrade_features.get("add_video"):
            # video_url/video_file already saved on the ad; just acknowledge the feature
            applied_features.append(_("فيديو"))

        if upgrade_features.get("auto_refresh"):
            ad.auto_refresh = True
            applied_features.append(_("تحديث تلقائي يومي"))

        ad.save()

        # Send notification to user
        Notification.objects.create(
            user=ad.user,
            notification_type=Notification.NotificationType.GENERAL,
            title=_("تم تأكيد الدفع"),
            message=_("تم تأكيد دفع ترقية الإعلان {} وتفعيل المميزات: {}.").format(
                ad.title, ", ".join(applied_features)
            ),
            link=ad.get_absolute_url(),
        )

        logger.info(
            f"Ad {ad.id} upgraded with features {upgrade_features} after payment {payment.id}"
        )
        return True

    except ClassifiedAd.DoesNotExist:
        logger.error(f"Ad {ad_id} not found for payment {payment.id}")
        return False
    except Exception as e:
        logger.error(f"Error processing ad upgrade payment {payment.id}: {str(e)}")
        return False
