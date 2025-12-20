"""
Offline Payment Transaction Handlers
Handles manual payment confirmation for offline transactions
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from main.models import Payment, Order
from decimal import Decimal
import json


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
@require_POST
def confirm_offline_payment(request):
    """
    Confirm an offline payment transaction
    Used for bank transfers and cash payments
    """
    try:
        data = json.loads(request.body)
        payment_id = data.get("payment_id")
        transaction_reference = data.get("transaction_reference", "")
        admin_notes = data.get("admin_notes", "")

        payment = get_object_or_404(Payment, id=payment_id)

        # Check if payment is already completed
        if payment.status == Payment.PaymentStatus.COMPLETED:
            return JsonResponse(
                {"success": False, "error": _("هذه الدفعة مكتملة بالفعل")}, status=400
            )

        # Update payment status
        payment.status = Payment.PaymentStatus.COMPLETED
        payment.completed_at = timezone.now()

        if transaction_reference:
            payment.provider_transaction_id = transaction_reference

        # Update metadata with admin notes
        if not payment.metadata:
            payment.metadata = {}
        payment.metadata["admin_confirmed"] = True
        payment.metadata["confirmed_by"] = request.user.username
        payment.metadata["confirmed_at"] = timezone.now().isoformat()
        if admin_notes:
            payment.metadata["admin_notes"] = admin_notes

        payment.save()

        # If this payment is linked to a user package, activate it
        if "package_id" in payment.metadata:
            from main.models import UserPackage

            try:
                package = UserPackage.objects.get(id=payment.metadata["package_id"])
                if not package.is_paid:
                    package.is_paid = True
                    package.purchase_date = timezone.now()
                    package.save()
            except UserPackage.DoesNotExist:
                pass

        # If this payment is linked to premium subscription, activate it
        if "subscription_type" in payment.metadata:
            user = payment.user
            user.is_premium = True
            if not user.subscription_start:
                user.subscription_start = timezone.now().date()
            # Extend subscription by duration in metadata
            duration_days = payment.metadata.get("duration_days", 30)
            from datetime import timedelta

            if user.subscription_end and user.subscription_end > timezone.now().date():
                user.subscription_end = user.subscription_end + timedelta(
                    days=duration_days
                )
            else:
                user.subscription_end = timezone.now().date() + timedelta(
                    days=duration_days
                )
            user.save()

        return JsonResponse(
            {
                "success": True,
                "message": _("تم تأكيد الدفعة بنجاح"),
                "payment": {
                    "id": payment.id,
                    "status": payment.status,
                    "status_display": payment.get_status_display(),
                    "completed_at": (
                        payment.completed_at.strftime("%Y-%m-%d %H:%M")
                        if payment.completed_at
                        else None
                    ),
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": _("بيانات غير صالحة")}, status=400
        )
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error confirming offline payment: {str(e)}")
        return JsonResponse(
            {"success": False, "error": _("حدث خطأ أثناء تأكيد الدفعة")}, status=500
        )


@login_required
@user_passes_test(is_admin)
@require_POST
def confirm_offline_order_payment(request):
    """
    Confirm offline payment for an order
    Used for bank transfers and cash on delivery
    """
    try:
        data = json.loads(request.body)
        order_id = data.get("order_id")
        transaction_reference = data.get("transaction_reference", "")
        admin_notes = data.get("admin_notes", "")

        order = get_object_or_404(Order, id=order_id)

        # Check if order payment is already confirmed
        if order.payment_status == "paid":
            return JsonResponse(
                {"success": False, "error": _("الدفعة مؤكدة بالفعل لهذا الطلب")},
                status=400,
            )

        # Update order payment status
        order.payment_status = "paid"

        # If order status is pending, move it to processing
        if order.status == "pending":
            order.status = "processing"

        # Update metadata with admin notes
        if not hasattr(order, "metadata") or not order.metadata:
            order.metadata = {}
        order.metadata["payment_confirmed_by"] = request.user.username
        order.metadata["payment_confirmed_at"] = timezone.now().isoformat()
        if transaction_reference:
            order.metadata["payment_reference"] = transaction_reference
        if admin_notes:
            order.metadata["admin_payment_notes"] = admin_notes

        order.save()

        # Create or update payment record
        payment, created = Payment.objects.get_or_create(
            user=order.user,
            provider_transaction_id=f"ORDER-{order.order_number}",
            defaults={
                "provider": Payment.PaymentProvider.BANK_TRANSFER,
                "amount": order.total_amount,
                "currency": "SAR",  # You can customize this
                "status": Payment.PaymentStatus.COMPLETED,
                "description": f"Payment for Order #{order.order_number}",
                "completed_at": timezone.now(),
                "metadata": {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "confirmed_by": request.user.username,
                },
            },
        )

        if not created:
            payment.status = Payment.PaymentStatus.COMPLETED
            payment.completed_at = timezone.now()
            payment.save()

        return JsonResponse(
            {
                "success": True,
                "message": _("تم تأكيد دفعة الطلب بنجاح"),
                "order": {
                    "id": order.id,
                    "order_number": order.order_number,
                    "payment_status": order.payment_status,
                    "status": order.status,
                    "status_display": order.get_status_display(),
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": _("بيانات غير صالحة")}, status=400
        )
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error confirming order payment: {str(e)}")
        return JsonResponse(
            {"success": False, "error": _("حدث خطأ أثناء تأكيد دفعة الطلب")}, status=500
        )


@login_required
@user_passes_test(is_admin)
@require_POST
def reject_offline_payment(request):
    """
    Reject an offline payment transaction
    """
    try:
        data = json.loads(request.body)
        payment_id = data.get("payment_id")
        rejection_reason = data.get("rejection_reason", "")

        payment = get_object_or_404(Payment, id=payment_id)

        # Update payment status
        payment.status = Payment.PaymentStatus.FAILED

        # Update metadata with rejection info
        if not payment.metadata:
            payment.metadata = {}
        payment.metadata["rejected_by"] = request.user.username
        payment.metadata["rejected_at"] = timezone.now().isoformat()
        if rejection_reason:
            payment.metadata["rejection_reason"] = rejection_reason

        payment.save()

        return JsonResponse(
            {
                "success": True,
                "message": _("تم رفض الدفعة"),
                "payment": {
                    "id": payment.id,
                    "status": payment.status,
                    "status_display": payment.get_status_display(),
                },
            }
        )

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error rejecting payment: {str(e)}")
        return JsonResponse(
            {"success": False, "error": _("حدث خطأ أثناء رفض الدفعة")}, status=500
        )
