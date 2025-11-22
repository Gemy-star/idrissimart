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
        payment_service = PaymentService()
        success, result = payment_service.paypal.execute_payment(payment_id, payer_id)

        if success and result.get("status") == "approved":
            # Mark payment as completed
            payment.mark_completed(payment_id)

            # Process package purchase if applicable
            package_id = payment.metadata.get("package_id")
            if package_id:
                process_package_purchase(payment, package_id)

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

    context = {"payments": payments}

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
