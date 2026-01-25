# main/verification_views.py
"""Views for user verification system"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from constance import config

from .models import UserVerificationRequest, User
from .verification_forms import UserVerificationRequestForm


@login_required
def verification_request(request):
    """Page for users to request account verification"""

    user = request.user

    # Check if user is already verified
    if user.is_verified:
        messages.info(request, _("حسابك موثق بالفعل!"))
        return redirect("main:publisher_settings")

    # Check if there's a pending request
    pending_request = UserVerificationRequest.objects.filter(
        user=user, status=User.VerificationStatus.PENDING
    ).first()

    if pending_request:
        # Check if payment is required and not yet paid
        if pending_request.payment_required and pending_request.payment_status != "paid":
            messages.info(
                request,
                _(
                    "يرجى إكمال عملية الدفع لمتابعة طلب التوثيق."
                ),
            )
            return redirect("main:verification_payment", request_id=pending_request.id)

        messages.info(
            request,
            _(
                "لديك طلب توثيق قيد المراجعة. سنقوم بإشعارك عند مراجعة طلبك."
            ),
        )
        return render(
            request,
            "verification/verification_pending.html",
            {"verification_request": pending_request},
        )

    # Get user's latest verification request (if any)
    latest_request = (
        UserVerificationRequest.objects.filter(user=user).order_by("-created_at").first()
    )

    if request.method == "POST":
        form = UserVerificationRequestForm(request.POST, request.FILES)

        if form.is_valid():
            verification_request = form.save(commit=False)
            verification_request.user = user
            verification_request.status = User.VerificationStatus.PENDING

            # Check if payment is required from constance settings
            if config.VERIFICATION_FEE_ENABLED:
                verification_request.payment_required = True
                verification_request.payment_amount = config.VERIFICATION_FEE_AMOUNT
                verification_request.payment_status = "pending"

            verification_request.save()

            # If payment is required, redirect to payment page
            if verification_request.payment_required:
                messages.info(
                    request,
                    _(
                        "تم إنشاء طلب التوثيق. يرجى إكمال عملية الدفع."
                    ),
                )
                return redirect("main:verification_payment", request_id=verification_request.id)

            messages.success(
                request,
                _(
                    "تم إرسال طلب التوثيق بنجاح! سنقوم بمراجعة طلبك خلال 2-3 أيام عمل."
                ),
            )

            return redirect("main:verification_pending")

    else:
        form = UserVerificationRequestForm()

    # Get verification fee info from constance
    verification_fee_enabled = config.VERIFICATION_FEE_ENABLED
    verification_fee_amount = config.VERIFICATION_FEE_AMOUNT if verification_fee_enabled else 0
    verification_fee_currency = config.VERIFICATION_FEE_CURRENCY if verification_fee_enabled else "EGP"

    context = {
        "form": form,
        "latest_request": latest_request,
        "user": user,
        "verification_fee_enabled": verification_fee_enabled,
        "verification_fee_amount": verification_fee_amount,
        "verification_fee_currency": verification_fee_currency,
    }

    return render(request, "verification/verification_request.html", context)


@login_required
def verification_pending(request):
    """Page showing pending verification status"""

    user = request.user

    # Get pending verification request
    pending_request = UserVerificationRequest.objects.filter(
        user=user, status=User.VerificationStatus.PENDING
    ).first()

    if not pending_request:
        # Check if user is verified
        if user.is_verified:
            messages.info(request, _("حسابك موثق بالفعل!"))
            return redirect("main:publisher_settings")

        # No pending request, redirect to request page
        messages.info(request, _("ليس لديك طلب توثيق قيد المراجعة."))
        return redirect("main:verification_request")

    context = {
        "verification_request": pending_request,
        "user": user,
    }

    return render(request, "verification/verification_pending.html", context)


@login_required
def verification_status(request):
    """Page showing all user's verification requests and status"""

    user = request.user

    # Get all verification requests
    verification_requests = UserVerificationRequest.objects.filter(
        user=user
    ).order_by("-created_at")

    context = {
        "verification_requests": verification_requests,
        "user": user,
        "is_verified": user.is_verified,
    }

    return render(request, "verification/verification_status.html", context)


@login_required
def verification_payment(request, request_id):
    """Payment page for verification request"""

    user = request.user
    verification_request = get_object_or_404(
        UserVerificationRequest, id=request_id, user=user
    )

    # Check if payment is required
    if not verification_request.payment_required:
        messages.info(request, _("لا يتطلب هذا الطلب دفع رسوم."))
        return redirect("main:verification_pending")

    # Check if already paid
    if verification_request.payment_status == "paid":
        messages.info(request, _("تم الدفع بالفعل لهذا الطلب."))
        return redirect("main:verification_pending")

    context = {
        "verification_request": verification_request,
        "user": user,
    }

    return render(request, "verification/verification_payment.html", context)


@login_required
def verification_payment_process(request, request_id):
    """Process verification payment"""
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    from django.views.decorators.csrf import csrf_exempt

    user = request.user
    verification_request = get_object_or_404(
        UserVerificationRequest, id=request_id, user=user
    )

    if request.method == "POST":
        # Here you would integrate with your payment gateway
        # For now, we'll simulate a successful payment
        payment_method = request.POST.get("payment_method", "card")
        transaction_id = request.POST.get("transaction_id", "")

        # Update payment status
        verification_request.payment_status = "paid"
        verification_request.payment_method = payment_method
        verification_request.payment_transaction_id = transaction_id
        verification_request.paid_at = timezone.now()

        # Auto-approve if enabled in settings
        if config.VERIFICATION_AUTO_APPROVE_ON_PAYMENT:
            verification_request.status = User.VerificationStatus.VERIFIED
            verification_request.user.verification_status = User.VerificationStatus.VERIFIED
            verification_request.user.verified_at = timezone.now()
            verification_request.user.save()
            verification_request.reviewed_at = timezone.now()

        verification_request.save()

        messages.success(
            request,
            _("تم الدفع بنجاح! سيتم مراجعة طلبك قريباً.")
        )

        return redirect("main:verification_pending")

    return redirect("main:verification_payment", request_id=request_id)


# Admin Views
from .decorators import superadmin_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse


@superadmin_required
def admin_verification_requests(request):
    """Admin view to manage verification requests"""

    # Get filter parameters
    status_filter = request.GET.get("status", "")
    payment_status_filter = request.GET.get("payment_status", "")
    search = request.GET.get("search", "")

    # Base queryset
    verification_requests = UserVerificationRequest.objects.select_related(
        "user", "reviewed_by"
    ).order_by("-created_at")

    # Apply filters
    if status_filter:
        verification_requests = verification_requests.filter(status=status_filter)

    if payment_status_filter:
        verification_requests = verification_requests.filter(
            payment_status=payment_status_filter
        )

    if search:
        verification_requests = verification_requests.filter(
            user__username__icontains=search
        ) | verification_requests.filter(user__email__icontains=search)

    # Pagination
    from django.core.paginator import Paginator

    paginator = Paginator(verification_requests, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Get statistics
    stats = {
        "pending": UserVerificationRequest.objects.filter(
            status=User.VerificationStatus.PENDING
        ).count(),
        "approved": UserVerificationRequest.objects.filter(
            status=User.VerificationStatus.VERIFIED
        ).count(),
        "rejected": UserVerificationRequest.objects.filter(
            status=User.VerificationStatus.REJECTED
        ).count(),
        "payment_pending": UserVerificationRequest.objects.filter(
            payment_required=True, payment_status="pending"
        ).count(),
    }

    context = {
        "verification_requests": page_obj,
        "stats": stats,
        "status_filter": status_filter,
        "payment_status_filter": payment_status_filter,
        "search": search,
    }

    return render(request, "admin_dashboard/verification_requests.html", context)


@superadmin_required
def admin_verification_detail(request, request_id):
    """Admin view for verification request details"""

    verification_request = get_object_or_404(
        UserVerificationRequest.objects.select_related("user", "reviewed_by"),
        id=request_id,
    )

    context = {
        "verification_request": verification_request,
    }

    return render(request, "admin_dashboard/verification_detail.html", context)


@superadmin_required
@require_POST
def admin_verification_approve(request, request_id):
    """Admin action to approve verification request"""

    verification_request = get_object_or_404(UserVerificationRequest, id=request_id)

    # Check if payment is required and not paid
    if (
        verification_request.payment_required
        and verification_request.payment_status != "paid"
    ):
        return JsonResponse(
            {
                "success": False,
                "message": _("لا يمكن الموافقة على الطلب قبل إتمام الدفع"),
            },
            status=400,
        )

    # Update verification request
    verification_request.status = User.VerificationStatus.VERIFIED
    verification_request.reviewed_by = request.user
    verification_request.reviewed_at = timezone.now()
    verification_request.admin_notes = request.POST.get("admin_notes", "")
    verification_request.save()

    # Update user status
    user = verification_request.user
    user.verification_status = User.VerificationStatus.VERIFIED
    user.verified_at = timezone.now()
    user.save()

    messages.success(
        request,
        _("تم الموافقة على طلب التوثيق بنجاح")
    )

    return JsonResponse(
        {
            "success": True,
            "message": _("تم الموافقة على طلب التوثيق بنجاح"),
        }
    )


@superadmin_required
@require_POST
def admin_verification_reject(request, request_id):
    """Admin action to reject verification request"""

    verification_request = get_object_or_404(UserVerificationRequest, id=request_id)

    # Update verification request
    verification_request.status = User.VerificationStatus.REJECTED
    verification_request.reviewed_by = request.user
    verification_request.reviewed_at = timezone.now()
    verification_request.admin_notes = request.POST.get("admin_notes", "")
    verification_request.save()

    # Update user status
    user = verification_request.user
    user.verification_status = User.VerificationStatus.REJECTED
    user.save()

    messages.success(
        request,
        _("تم رفض طلب التوثيق")
    )

    return JsonResponse(
        {
            "success": True,
            "message": _("تم رفض طلب التوثيق"),
        }
    )

