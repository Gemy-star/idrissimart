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
    currency = request.POST.get("currency", "SAR")

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
        # Update payment with provider data
        if provider == "paypal":
            payment.provider_transaction_id = result.get("payment_id", "")
            payment.metadata.update(
                {
                    "paypal_payment_id": result.get("payment_id"),
                    "approval_url": result.get("approval_url"),
                }
            )
        elif provider == "paymob":
            payment.metadata.update(
                {
                    "paymob_order_id": result.get("order_id"),
                    "payment_key": result.get("payment_key"),
                    "iframe_url": result.get("iframe_url"),
                }
            )

        payment.save()

        return JsonResponse(
            {
                "success": True,
                "payment_id": payment.id,
                "redirect_url": result.get("approval_url") or result.get("iframe_url"),
                "provider_data": result,
            }
        )
    else:
        payment.mark_failed(str(result))
        return JsonResponse({"success": False, "message": result})


@login_required
def paypal_success(request):
    """Handle PayPal payment success"""
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    if not payment_id or not payer_id:
        messages.error(request, _("بيانات الدفع غير مكتملة"))
        return redirect("main:payment_failed")

    try:
        # Find payment record
        payment = Payment.objects.get(
            user=request.user,
            metadata__paypal_payment_id=payment_id,
            status=Payment.PaymentStatus.PENDING,
        )

        # Execute PayPal payment
        paypal_service = PayPalService()
        success, result = paypal_service.capture_order(payment_id)

        if success and result.get("status") == "COMPLETED":
            # Mark payment as completed
            payment.mark_completed(payment_id)

            # Process package purchase if applicable
            package_id = payment.metadata.get("package_id")
            if package_id:
                process_package_purchase(payment, package_id)

            # Process ad payment if applicable
            ad_id = payment.metadata.get("ad_id")
            if ad_id:
                process_ad_payment(payment)

            messages.success(request, _("تم الدفع بنجاح"))
            return redirect("main:payment_success", payment_id=payment.id)
        else:
            payment.mark_failed("PayPal execution failed")
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

            # Process ad payment if applicable
            ad_id = payment.metadata.get("ad_id")
            if ad_id:
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
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # Get upgrade data from payment metadata
    upgrade_data = payment.metadata

    payment_service = PaymentService()
    supported_providers = payment_service.get_supported_providers()

    context = {
        "payment": payment,
        "upgrade_data": upgrade_data,
        "supported_providers": supported_providers,
        "site_url": config.SITE_URL,
        "is_upgrade": True,
    }

    return render(request, "payments/payment_page.html", context)


@login_required
def ad_payment(request, ad_id):
    """Payment page for new ad with features"""
    from .models import ClassifiedAd
    from content.models import SiteConfiguration

    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)
    site_config = SiteConfiguration.get_solo()

    # Get payment details from session
    total_amount = Decimal(request.session.get("ad_payment_amount", "0"))
    base_fee = Decimal(request.session.get("ad_base_fee", "0"))
    features_cost = Decimal(request.session.get("ad_features_cost", "0"))
    features = request.session.get("ad_features", {})

    # If ad is already active or no payment needed, redirect
    if ad.status == ClassifiedAd.AdStatus.ACTIVE or total_amount == 0:
        messages.info(request, _("هذا الإعلان نشط بالفعل أو لا يحتاج إلى دفع"))
        return redirect("main:ad_detail", pk=ad.pk, slug=ad.slug)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "offline":
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
                    },
                )

            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                provider=Payment.PaymentProvider.BANK_TRANSFER,
                amount=total_amount,
                currency="EGP",
                status=Payment.PaymentStatus.PENDING,
                description=f"دفع إعلان: {ad.title}",
                offline_payment_receipt=receipt,
                metadata={
                    "ad_id": ad.id,
                    "features": features,
                    "base_fee": str(base_fee),
                    "features_cost": str(features_cost),
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
            ]:
                request.session.pop(key, None)

            return redirect("main:my_ads")

        elif payment_method in ["paymob", "paypal"]:
            # Create payment record for online payment
            payment = Payment.objects.create(
                user=request.user,
                provider=(
                    Payment.PaymentProvider.PAYMOB
                    if payment_method == "paymob"
                    else Payment.PaymentProvider.PAYPAL
                ),
                amount=total_amount,
                currency="EGP",
                status=Payment.PaymentStatus.PENDING,
                description=f"دفع إعلان: {ad.title}",
                metadata={
                    "ad_id": ad.id,
                    "features": features,
                    "base_fee": str(base_fee),
                    "features_cost": str(features_cost),
                },
            )

            # Redirect to online payment gateway
            # This would integrate with your existing payment service
            messages.info(request, _("جاري تحويلك إلى بوابة الدفع..."))
            return redirect("main:payment_page")  # Adjust to your payment page

    context = {
        "ad": ad,
        "total_amount": total_amount,
        "base_fee": base_fee,
        "features_cost": features_cost,
        "features": features,
        "site_config": site_config,
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
        ad.features_price = Decimal(payment.metadata.get("features_cost", "0"))

        # Change status from DRAFT to PENDING or ACTIVE
        if ad.status == ClassifiedAd.AdStatus.DRAFT:
            # Check if user is verified
            if ad.user.verification_status == User.VerificationStatus.VERIFIED:
                ad.status = ClassifiedAd.AdStatus.ACTIVE
                status_msg = _("نشط")
            else:
                ad.status = ClassifiedAd.AdStatus.PENDING
                status_msg = _("قيد المراجعة")

            # If user paid base fee (no package), check if they should get a package
            # Otherwise, deduct from their active package
            if base_fee == 0:
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
                message=_("تم تأكيد دفع إعلانك {} وتحويله إلى {}.").format(ad.title, status_msg),
                link=ad.get_absolute_url(),
            )

            logger.info(f"Ad {ad.id} status changed from DRAFT to {ad.status} after payment {payment.id}")
            return True
        else:
            logger.warning(f"Ad {ad.id} is not in DRAFT status, current status: {ad.status}")
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
    """Admin confirms offline ad payment"""
    from .models import ClassifiedAd, User

    if not request.user.is_staff:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)

    payment = get_object_or_404(Payment, id=payment_id)

    # Process the ad payment
    success = process_ad_payment(payment)

    if not success:
        return JsonResponse({"success": False, "message": _("فشل في معالجة دفع الإعلان")})

    # Mark payment as completed
    payment.mark_completed()

    return JsonResponse(
        {"success": True, "message": _("تم تأكيد الدفع وتفعيل الإعلان")}
    )


@login_required
def package_checkout(request, package_id):
    """Checkout page for package purchase with offline/online payment options"""
    from content.models import SiteConfiguration

    package = get_object_or_404(AdPackage, id=package_id, is_active=True)
    site_config = SiteConfiguration.get_solo()

    # Verify package is in session
    session_package_id = request.session.get("package_checkout_id")
    if not session_package_id or int(session_package_id) != package.id:
        messages.error(request, _("جلسة الدفع غير صالحة. يرجى المحاولة مرة أخرى."))
        return redirect("main:packages_list")

    total_amount = package.price

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method in ["offline", "instapay", "wallet"]:
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
                        "allow_offline_payment": allow_offline_payment,
                        "offline_payment_instructions": offline_payment_instructions,
                    },
                )

            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                provider=Payment.PaymentProvider.BANK_TRANSFER,
                amount=total_amount,
                currency="EGP",
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

        elif payment_method in ["paymob", "paypal", "card", "wallet", "instapay"]:
            # Determine provider based on payment method
            if payment_method == "paypal":
                provider = Payment.PaymentProvider.PAYPAL
            elif payment_method in ["paymob", "card", "wallet", "instapay"]:
                provider = Payment.PaymentProvider.PAYMOB
            else:
                provider = Payment.PaymentProvider.PAYMOB

            # Create payment record for online payment
            payment = Payment.objects.create(
                user=request.user,
                provider=provider,
                amount=total_amount,
                currency="EGP",
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

            # Create payment with provider
            result = payment_service.create_payment(
                payment_method,
                float(total_amount),
                "EGP",
                f"شراء باقة: {package.name}",
                user_data,
                payment_id=payment.id,
            )

            if result["success"]:
                payment.transaction_id = result.get("transaction_id")
                payment.payment_url = result.get("payment_url")
                payment.save()

                # Clear session
                request.session.pop("package_checkout_id", None)
                request.session.pop("package_checkout_amount", None)

                # Redirect to payment gateway
                return redirect(result["payment_url"])
            else:
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                messages.error(
                    request, _("فشل إنشاء الدفع: {}").format(result.get("message"))
                )

    context = {
        "package": package,
        "total_amount": total_amount,
        "site_config": site_config,
        "allow_offline_payment": site_config.allow_offline_payment,
        "offline_payment_instructions": site_config.offline_payment_instructions,
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
