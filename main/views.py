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
    """AJAX endpoint to set user's country"""
    country_code = request.POST.get('country_code')

    if country_code and Country.objects.filter(code=country_code, is_active=True).exists():
        request.session['selected_country'] = country_code
        return JsonResponse({
            'success': True,
            'message': _('Country updated successfully')
        })

    return JsonResponse({
        'success': False,
        'message': _('Invalid country code')
    }, status=400)


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
