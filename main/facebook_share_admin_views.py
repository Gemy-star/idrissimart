"""
Custom admin views for Facebook Share Request management
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, View
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.utils import timezone

from .models import FacebookShareRequest, ClassifiedAd


class AdminFacebookShareRequestsView(LoginRequiredMixin, ListView):
    """Admin view for managing Facebook share requests"""

    model = FacebookShareRequest
    template_name = "admin/facebook_share_requests.html"
    context_object_name = "requests"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
            return redirect("main:home")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = FacebookShareRequest.objects.select_related(
            'ad', 'ad__user', 'ad__category', 'processed_by'
        ).order_by('-requested_at')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by payment confirmation
        payment_confirmed = self.request.GET.get('payment_confirmed')
        if payment_confirmed == 'true':
            queryset = queryset.filter(payment_confirmed=True)
        elif payment_confirmed == 'false':
            queryset = queryset.filter(payment_confirmed=False)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(ad__title__icontains=search) |
                Q(ad__user__username__icontains=search) |
                Q(admin_notes__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Set active navigation
        context['active_nav'] = 'facebook_share_requests'

        # Statistics
        context['stats'] = {
            'total': FacebookShareRequest.objects.count(),
            'pending': FacebookShareRequest.objects.filter(status='pending').count(),
            'in_progress': FacebookShareRequest.objects.filter(status='in_progress').count(),
            'completed': FacebookShareRequest.objects.filter(status='completed').count(),
            'rejected': FacebookShareRequest.objects.filter(status='rejected').count(),
            'payment_pending': FacebookShareRequest.objects.filter(
                status='pending',
                payment_confirmed=False
            ).count(),
        }

        # Filters
        context['current_status'] = self.request.GET.get('status', '')
        context['current_payment'] = self.request.GET.get('payment_confirmed', '')
        context['search_query'] = self.request.GET.get('search', '')

        return context


class PublisherFacebookShareRequestsView(LoginRequiredMixin, ListView):
    """Publisher view for tracking their Facebook share requests"""

    model = FacebookShareRequest
    template_name = "publisher/facebook_share_requests.html"
    context_object_name = "requests"
    paginate_by = 10

    def get_queryset(self):
        # Get requests for ads owned by the current user
        return FacebookShareRequest.objects.filter(
            ad__user=self.request.user
        ).select_related(
            'ad', 'ad__category', 'processed_by'
        ).order_by('-requested_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics for user's requests
        user_requests = FacebookShareRequest.objects.filter(ad__user=self.request.user)
        context['stats'] = {
            'total': user_requests.count(),
            'pending': user_requests.filter(status='pending').count(),
            'in_progress': user_requests.filter(status='in_progress').count(),
            'completed': user_requests.filter(status='completed').count(),
            'rejected': user_requests.filter(status='rejected').count(),
        }

        return context


class FacebookShareRequestDetailView(LoginRequiredMixin, View):
    """Get details of a specific request"""

    def get(self, request, request_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"},
                status=403
            )

        try:
            fb_request = FacebookShareRequest.objects.select_related(
                'ad', 'ad__user', 'ad__category', 'processed_by'
            ).get(id=request_id)

            data = {
                'success': True,
                'id': fb_request.pk,
                'ad_id': fb_request.ad.pk,
                'ad_title': fb_request.ad.title,
                'ad_user': fb_request.ad.user.username,
                'status': fb_request.status,
                'payment_confirmed': fb_request.payment_confirmed,
                'payment_amount': str(fb_request.payment_amount),
                'requested_at': fb_request.requested_at.isoformat(),
                'processed_at': fb_request.processed_at.isoformat() if fb_request.processed_at else None,
                'processed_by': fb_request.processed_by.username if fb_request.processed_by else None,
                'facebook_post_url': fb_request.facebook_post_url or '',
                'admin_notes': fb_request.admin_notes or '',
            }
            return JsonResponse(data)
        except FacebookShareRequest.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Request not found"},
                status=404
            )


class FacebookShareRequestProcessView(LoginRequiredMixin, View):
    """Process a Facebook share request (mark as completed/rejected)"""

    def post(self, request):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"},
                status=403
            )

        request_id = request.POST.get('request_id')
        action = request.POST.get('action')  # 'complete', 'reject', 'in_progress', 'confirm_payment'
        facebook_post_url = request.POST.get('facebook_post_url', '')
        admin_notes = request.POST.get('admin_notes', '')

        try:
            fb_request = FacebookShareRequest.objects.get(id=request_id)

            if action == 'confirm_payment':
                fb_request.payment_confirmed = True
                fb_request.save()
                message = _("تم تأكيد الدفع بنجاح")

            elif action == 'in_progress':
                fb_request.status = 'in_progress'
                fb_request.save()
                message = _("تم تحديث الحالة إلى 'جاري التنفيذ'")

            elif action == 'complete':
                fb_request.mark_as_completed(
                    facebook_post_url=facebook_post_url,
                    admin=request.user
                )
                message = _("تم إكمال الطلب بنجاح")

            elif action == 'reject':
                fb_request.mark_as_rejected(
                    reason=admin_notes,
                    admin=request.user
                )
                message = _("تم رفض الطلب")

            else:
                return JsonResponse(
                    {"success": False, "message": "Invalid action"},
                    status=400
                )

            # Update admin notes if provided
            if admin_notes and action != 'reject':
                fb_request.admin_notes = admin_notes
                fb_request.save()

            return JsonResponse({"success": True, "message": message})

        except FacebookShareRequest.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Request not found"},
                status=404
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": str(e)},
                status=500
            )


class FacebookShareRequestBulkActionView(LoginRequiredMixin, View):
    """Bulk actions for Facebook share requests"""

    def post(self, request):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"},
                status=403
            )

        action = request.POST.get('action')
        request_ids = request.POST.getlist('request_ids[]')

        try:
            requests_qs = FacebookShareRequest.objects.filter(id__in=request_ids)

            if action == 'confirm_payment':
                count = requests_qs.update(payment_confirmed=True)
                message = _(f"تم تأكيد الدفع لـ {count} طلب")

            elif action == 'mark_in_progress':
                count = requests_qs.update(status='in_progress')
                message = _(f"تم تحديث {count} طلب إلى 'جاري التنفيذ'")

            elif action == 'delete':
                count = requests_qs.count()
                requests_qs.delete()
                message = _(f"تم حذف {count} طلب")

            else:
                return JsonResponse(
                    {"success": False, "message": "Invalid action"},
                    status=400
                )

            return JsonResponse({"success": True, "message": message})

        except Exception as e:
            return JsonResponse(
                {"success": False, "message": str(e)},
                status=500
            )
