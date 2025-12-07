"""
API views for ad owner actions (toggle visibility, mark as sold, delete)
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from .models import ClassifiedAd


@login_required
@require_POST
def toggle_ad_visibility(request, ad_id):
    """Toggle ad visibility (is_active status)"""
    ad = get_object_or_404(ClassifiedAd, id=ad_id)

    # Check if user is the owner
    if ad.user != request.user:
        return JsonResponse({
            'success': False,
            'message': _('ليس لديك صلاحية لتعديل هذا الإعلان')
        }, status=403)

    # Toggle is_active
    ad.is_active = not ad.is_active
    ad.save()

    status_message = _('تم إظهار الإعلان') if ad.is_active else _('تم إخفاء الإعلان')

    return JsonResponse({
        'success': True,
        'message': status_message,
        'is_active': ad.is_active
    })


@login_required
@require_POST
def mark_ad_as_sold(request, ad_id):
    """Mark ad as sold"""
    ad = get_object_or_404(ClassifiedAd, id=ad_id)

    # Check if user is the owner
    if ad.user != request.user:
        return JsonResponse({
            'success': False,
            'message': _('ليس لديك صلاحية لتعديل هذا الإعلان')
        }, status=403)

    # Check if SOLD status exists
    if hasattr(ClassifiedAd, 'AdStatus') and hasattr(ClassifiedAd.AdStatus, 'SOLD'):
        ad.status = ClassifiedAd.AdStatus.SOLD
        ad.save()

        return JsonResponse({
            'success': True,
            'message': _('تم تحديد الإعلان كـ "تم البيع"')
        })
    else:
        # Fallback: just deactivate the ad
        ad.is_active = False
        ad.save()

        return JsonResponse({
            'success': True,
            'message': _('تم إخفاء الإعلان')
        })


@login_required
@require_POST
def delete_ad(request, ad_id):
    """Delete ad (soft delete by deactivating or hard delete based on business rules)"""
    ad = get_object_or_404(ClassifiedAd, id=ad_id)

    # Check if user is the owner
    if ad.user != request.user:
        return JsonResponse({
            'success': False,
            'message': _('ليس لديك صلاحية لحذف هذا الإعلان')
        }, status=403)

    try:
        # Hard delete the ad
        ad.delete()

        return JsonResponse({
            'success': True,
            'message': _('تم حذف الإعلان بنجاح')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _('حدث خطأ أثناء حذف الإعلان')
        }, status=500)
