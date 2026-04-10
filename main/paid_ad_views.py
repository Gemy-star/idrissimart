"""
Views for Paid Advertisement tracking and management
"""
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from main.models import PaidAdvertisement
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PaidAdViewTrackingView(View):
    """Track paid advertisement views"""

    def post(self, request, ad_id):
        try:
            ad = PaidAdvertisement.objects.get(id=ad_id)
            ad.increment_views()
            return JsonResponse({
                'success': True,
                'views_count': ad.views_count
            })
        except PaidAdvertisement.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Advertisement not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error tracking ad view: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PaidAdClickTrackingView(View):
    """Track paid advertisement clicks"""

    def post(self, request, ad_id):
        try:
            ad = PaidAdvertisement.objects.get(id=ad_id)
            ad.increment_clicks()
            return JsonResponse({
                'success': True,
                'clicks_count': ad.clicks_count,
                'ctr': ad.ctr
            })
        except PaidAdvertisement.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Advertisement not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error tracking ad click: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


def get_category_paid_ads(request, category_id):
    """
    API endpoint to get paid ads for a specific category
    """
    from main.models import Category

    try:
        # Validate category_id is a valid integer to prevent SQL injection attempts
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid category ID"}, status=400)

        category = Category.objects.get(id=category_id)
        selected_country = request.session.get("selected_country", "EG")

        ads = PaidAdvertisement.get_category_ads(category, selected_country)

        ads_data = []
        for ad in ads:
            ads_data.append({
                'id': ad.id,
                'title': ad.title_ar if request.LANGUAGE_CODE == 'ar' and ad.title_ar else ad.title,
                'image_url': ad.image.url if ad.image else None,
                'target_url': ad.target_url,
                'ad_type': ad.ad_type,
                'cta_text': ad.cta_text_ar if request.LANGUAGE_CODE == 'ar' and ad.cta_text_ar else ad.cta_text,
            })

        return JsonResponse({
            'success': True,
            'ads': ads_data,
            'count': len(ads_data)
        })
    except Category.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Category not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching category ads: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)
