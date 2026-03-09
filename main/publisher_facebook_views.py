"""
Publisher views for Facebook Share Request management and payment
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView, View, TemplateView
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum
from django.utils import timezone
from decimal import Decimal

from .models import FacebookShareRequest, ClassifiedAd, Payment


class PublisherFacebookShareRequestsView(LoginRequiredMixin, ListView):
    """Publisher view for tracking their Facebook share requests"""

    model = FacebookShareRequest
    template_name = "classifieds/publisher_facebook_requests.html"
    context_object_name = "requests"
    paginate_by = 20

    def get_queryset(self):
        # Only show requests for ads owned by the current user
        queryset = FacebookShareRequest.objects.filter(
            ad__user=self.request.user
        ).select_related(
            'ad', 'ad__category', 'processed_by'
        ).order_by('-requested_at')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by payment status
        payment_status = self.request.GET.get('payment_status')
        if payment_status == 'paid':
            queryset = queryset.filter(payment_confirmed=True)
        elif payment_status == 'unpaid':
            queryset = queryset.filter(payment_confirmed=False)

        # Search by ad title
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(ad__title__icontains=search) |
                Q(ad__id__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Set active navigation
        context['active_nav'] = 'facebook_requests'

        # Statistics
        all_requests = FacebookShareRequest.objects.filter(ad__user=self.request.user)

        context['stats'] = {
            'total': all_requests.count(),
            'pending': all_requests.filter(status='pending').count(),
            'in_progress': all_requests.filter(status='in_progress').count(),
            'completed': all_requests.filter(status='completed').count(),
            'rejected': all_requests.filter(status='rejected').count(),
            'unpaid': all_requests.filter(payment_confirmed=False).count(),
            'total_amount': all_requests.filter(
                payment_confirmed=True
            ).aggregate(total=Sum('payment_amount'))['total'] or Decimal('0.00'),
        }

        # Get current filters
        context['current_status'] = self.request.GET.get('status', '')
        context['current_payment_status'] = self.request.GET.get('payment_status', '')
        context['search_query'] = self.request.GET.get('search', '')

        return context


class PublisherFacebookSharePaymentView(LoginRequiredMixin, TemplateView):
    """Publisher view for handling Facebook share request payment"""

    template_name = "classifieds/publisher_facebook_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Set active navigation
        context['active_nav'] = 'facebook_requests'

        request_id = kwargs.get('request_id')
        share_request = get_object_or_404(
            FacebookShareRequest,
            id=request_id,
            ad__user=self.request.user
        )

        context['share_request'] = share_request
        context['ad'] = share_request.ad

        # Get payment amount from constance or settings
        from constance import config
        payment_amount = getattr(config, 'FACEBOOK_SHARE_PRICE', Decimal('50.00'))
        context['payment_amount'] = payment_amount

        # Payment methods
        context['payment_methods'] = [
            {
                'id': 'bank_transfer',
                'name': _('تحويل بنكي'),
                'name_en': 'Bank Transfer',
                'icon': 'fas fa-university',
                'description': _('تحويل مباشر إلى الحساب البنكي'),
            },
            {
                'id': 'credit_card',
                'name': _('بطاقة ائتمان'),
                'name_en': 'Credit Card',
                'icon': 'fas fa-credit-card',
                'description': _('الدفع باستخدام بطاقة الائتمان'),
            },
            {
                'id': 'paypal',
                'name': _('PayPal'),
                'name_en': 'PayPal',
                'icon': 'fab fa-paypal',
                'description': _('الدفع عبر PayPal'),
            },
            {
                'id': 'cash',
                'name': _('دفع نقدي'),
                'name_en': 'Cash Payment',
                'icon': 'fas fa-money-bill-wave',
                'description': _('الدفع نقداً عند الاستلام'),
            },
        ]

        # Bank details from constance
        context['bank_details'] = {
            'bank_name': getattr(config, 'BANK_NAME', 'البنك الأهلي السعودي'),
            'account_name': getattr(config, 'BANK_ACCOUNT_NAME', 'إدريسي مارت'),
            'account_number': getattr(config, 'BANK_ACCOUNT_NUMBER', 'SA00 0000 0000 0000 0000'),
            'iban': getattr(config, 'BANK_IBAN', 'SA00 0000 0000 0000 0000'),
        }

        return context

    def post(self, request, *args, **kwargs):
        """Handle payment submission"""
        request_id = kwargs.get('request_id')
        share_request = get_object_or_404(
            FacebookShareRequest,
            id=request_id,
            ad__user=request.user
        )

        payment_method = request.POST.get('payment_method')
        payment_proof = request.FILES.get('payment_proof')
        notes = request.POST.get('notes', '')

        if not payment_method:
            messages.error(request, _('يرجى اختيار طريقة الدفع'))
            return redirect('main:publisher_facebook_payment', request_id=request_id)

        # Get payment amount
        from constance import config
        payment_amount = getattr(config, 'FACEBOOK_SHARE_PRICE', Decimal('50.00'))

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=payment_amount,
            currency='EGP',
            payment_method=payment_method,
            status='pending',
            description=f'Facebook Share Request for Ad: {share_request.ad.title}',
            metadata={
                'facebook_share_request_id': share_request.pk,
                'ad_id': share_request.ad.pk,
                'notes': notes,
            }
        )

        # Update share request
        share_request.payment_amount = payment_amount
        share_request.save()

        messages.success(
            request,
            _('تم إرسال طلب الدفع بنجاح. سيتم مراجعته من قبل الإدارة.')
        )

        return redirect('main:publisher_facebook_requests')


class CancelFacebookShareRequestView(LoginRequiredMixin, View):
    """View for publisher to cancel their Facebook share request"""

    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        share_request = get_object_or_404(
            FacebookShareRequest,
            id=request_id,
            ad__user=request.user
        )

        # Can only cancel pending requests
        if share_request.status != 'pending':
            return JsonResponse({
                'success': False,
                'message': _('لا يمكن إلغاء هذا الطلب')
            }, status=400)

        # Update ad
        share_request.ad.share_on_facebook = False
        share_request.ad.facebook_share_requested = False
        share_request.ad.save()

        # Delete the request
        share_request.delete()

        return JsonResponse({
            'success': True,
            'message': _('تم إلغاء الطلب بنجاح')
        })


class CreateFacebookShareRequestView(LoginRequiredMixin, View):
    """Form for publisher to select an ad and create a new Facebook share request"""

    template_name = "classifieds/publisher_facebook_create.html"

    def get(self, request, *args, **kwargs):
        from constance import config
        # Exclude ads that already have a pending/in-progress request
        existing_ad_ids = FacebookShareRequest.objects.filter(
            ad__user=request.user,
            status__in=['pending', 'in_progress']
        ).values_list('ad_id', flat=True)

        ads = ClassifiedAd.objects.filter(
            user=request.user,
            status='active'
        ).exclude(id__in=existing_ad_ids).order_by('-created_at')

        payment_amount = getattr(config, 'FACEBOOK_SHARE_PRICE', Decimal('50.00'))

        return render(request, self.template_name, {
            'ads': ads,
            'active_nav': 'facebook_requests',
            'payment_amount': payment_amount,
        })

    def post(self, request, *args, **kwargs):
        from constance import config
        ad_id = request.POST.get('ad_id')
        ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user, status='active')

        # Guard against duplicates
        if FacebookShareRequest.objects.filter(ad=ad, status__in=['pending', 'in_progress']).exists():
            messages.warning(request, _('يوجد طلب نشر نشط لهذا الإعلان بالفعل.'))
            return redirect('main:create_facebook_request')

        payment_amount = getattr(config, 'FACEBOOK_SHARE_PRICE', Decimal('50.00'))

        share_request = FacebookShareRequest.objects.create(
            ad=ad,
            user=request.user,
            payment_amount=payment_amount,
        )

        ad.facebook_share_requested = True
        ad.save(update_fields=['facebook_share_requested'])

        return redirect('main:publisher_facebook_payment', request_id=share_request.pk)


class FacebookShareRequestDetailView(LoginRequiredMixin, TemplateView):
    """Detailed view of a Facebook share request for publisher"""

    template_name = "classifieds/publisher_facebook_request_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Set active navigation
        context['active_nav'] = 'facebook_requests'

        request_id = kwargs.get('request_id')
        share_request = get_object_or_404(
            FacebookShareRequest,
            id=request_id,
            ad__user=self.request.user
        )

        context['share_request'] = share_request
        context['ad'] = share_request.ad

        # Get related payments
        context['payments'] = Payment.objects.filter(
            user=self.request.user,
            metadata__facebook_share_request_id=request_id
        ).order_by('-created_at')

        return context
