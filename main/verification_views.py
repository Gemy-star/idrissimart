# main/verification_views.py
"""Views for user verification system"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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
            verification_request.save()

            messages.success(
                request,
                _(
                    "تم إرسال طلب التوثيق بنجاح! سنقوم بمراجعة طلبك خلال 2-3 أيام عمل."
                ),
            )

            return redirect("main:verification_pending")

    else:
        form = UserVerificationRequestForm()

    context = {
        "form": form,
        "latest_request": latest_request,
        "user": user,
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
