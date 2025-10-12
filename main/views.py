from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from content.models import Country


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get user's selected country from session
        selected_country = self.request.session.get('selected_country', 'SA')
        # Get cart and wishlist counts from session
        cart_count = len(self.request.session.get('cart', []))
        wishlist_count = len(self.request.session.get('wishlist', []))
        context["selected_country"] = selected_country
        context["cart_count"] = cart_count
        context["wishlist_count"] = wishlist_count
        context["page_title"] = _("الرئيسية - إدريسي مارت")
        context["meta_description"] = _("منصة تجمع سوق واحد للمختصصين والحرفيين والجمهور العام")

        return context


@require_POST
def set_country(request):
    """
    API endpoint to set user's selected country
    """
    try:
        country_code = request.POST.get('country_code')

        if not country_code:
            return JsonResponse({
                'success': False,
                'message': _('لم يتم تحديد البلد')
            }, status=400)

        # Validate country exists and is active
        try:
            country = Country.objects.get(code=country_code, is_active=True)
        except Country.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': _('البلد المحدد غير متاح')
            }, status=404)

        # Store in session
        request.session['selected_country'] = country_code
        request.session['selected_country_name'] = country.name

        # Optional: Store in user profile if authenticated
        if request.user.is_authenticated:
            request.user.profile.country = country
            request.user.profile.save()

        return JsonResponse({
            'success': True,
            'message': _('تم تغيير البلد بنجاح'),
            'country_code': country_code,
            'country_name': country.name
        })

    except Exception:
        return JsonResponse({
            'success': False,
            'message': _('حدث خطأ في تغيير البلد')
        }, status=500)




@require_POST
def add_to_cart(request):
    """Add item to cart"""
    item_id = request.POST.get('item_id')

    if not item_id:
        return JsonResponse({'success': False, 'message': _('Item ID required')}, status=400)

    cart = request.session.get('cart', [])

    if item_id not in cart:
        cart.append(item_id)
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item added to cart'),
            'cart_count': len(cart)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item already in cart')
    })


@require_POST
def add_to_wishlist(request):
    """Add item to wishlist"""
    item_id = request.POST.get('item_id')

    if not item_id:
        return JsonResponse({'success': False, 'message': _('Item ID required')}, status=400)

    wishlist = request.session.get('wishlist', [])

    if item_id not in wishlist:
        wishlist.append(item_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item added to wishlist'),
            'wishlist_count': len(wishlist)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item already in wishlist')
    })


@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    item_id = request.POST.get('item_id')
    cart = request.session.get('cart', [])

    if item_id in cart:
        cart.remove(item_id)
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item removed from cart'),
            'cart_count': len(cart)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item not in cart')
    })


@require_POST
def remove_from_wishlist(request):
    """Remove item from wishlist"""
    item_id = request.POST.get('item_id')
    wishlist = request.session.get('wishlist', [])

    if item_id in wishlist:
        wishlist.remove(item_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item removed from wishlist'),
            'wishlist_count': len(wishlist)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item not in wishlist')
    })
