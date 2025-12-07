"""
Cart and Wishlist Views
Handles all cart and wishlist functionality including AJAX endpoints
"""

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
import json

from main.models import Cart, CartItem, ClassifiedAd, Wishlist, WishlistItem


def get_or_create_cart(user):
    """Get or create cart for authenticated user"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def get_session_cart(request):
    """Get cart items from session for guest users"""
    return request.session.get("cart", {})


def save_session_cart(request, cart_data):
    """Save cart items to session for guest users"""
    request.session["cart"] = cart_data
    request.session.modified = True


def get_cart_count(request):
    """Get cart items count for both authenticated and guest users"""
    if request.user.is_authenticated:
        cart = get_or_create_cart(request.user)
        return cart.get_items_count()
    else:
        session_cart = get_session_cart(request)
        return sum(item["quantity"] for item in session_cart.values())


def get_or_create_wishlist(user):
    """Get or create wishlist for user"""
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    return wishlist


# ============================================
# Cart Views
# ============================================


@require_POST
@login_required
def add_to_cart(request):
    """Add item to cart via AJAX - only for authenticated users"""
    try:
        ad_id = request.POST.get("item_id")
        if not ad_id:
            return JsonResponse(
                {"success": False, "message": _("معرف الإعلان مفقود")}, status=400
            )

        ad = get_object_or_404(
            ClassifiedAd, id=ad_id, status=ClassifiedAd.AdStatus.ACTIVE
        )

        # Check if cart is enabled for this ad
        if not ad.cart_enabled_by_admin:
            return JsonResponse(
                {
                    "success": False,
                    "message": _("السلة غير مفعلة لهذا الإعلان"),
                },
                status=400,
            )

        # Authenticated user - use database cart
        cart = get_or_create_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, ad=ad)

        if not created:
            cart_item.quantity += 1
            cart_item.save()
            message = _("تم زيادة الكمية في السلة")
        else:
            message = _("تمت إضافة {} إلى السلة").format(ad.title)

        cart_count = cart.get_items_count()

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "cart_count": cart_count,
                "item_id": ad_id,
            }
        )

    except ClassifiedAd.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("الإعلان غير موجود")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@require_POST
@login_required
def remove_from_cart(request):
    """Remove item from cart via AJAX - only for authenticated users"""
    try:
        ad_id = request.POST.get("item_id")
        if not ad_id:
            return JsonResponse(
                {"success": False, "message": _("معرف الإعلان مفقود")}, status=400
            )

        # Authenticated user - use database cart
        cart = get_or_create_cart(request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, ad_id=ad_id)
        ad_title = cart_item.ad.title
        cart_item.delete()
        cart_count = cart.get_items_count()

        return JsonResponse(
            {
                "success": True,
                "message": _("تمت إزالة {} من السلة").format(ad_title),
                "cart_count": cart_count,
                "item_id": ad_id,
            }
        )

    except CartItem.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("العنصر غير موجود في السلة")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@require_POST
@login_required
def update_cart_quantity(request):
    """Update cart item quantity via AJAX - only for authenticated users"""
    try:
        ad_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity")

        if not ad_id or not quantity:
            return JsonResponse(
                {"success": False, "message": _("البيانات غير مكتملة")}, status=400
            )

        quantity = int(quantity)
        if quantity < 1:
            return JsonResponse(
                {"success": False, "message": _("الكمية يجب أن تكون أكبر من صفر")},
                status=400,
            )

        # Authenticated user - use database cart
        cart = get_or_create_cart(request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, ad_id=ad_id)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse(
            {
                "success": True,
                "message": _("تم تحديث الكمية"),
                "cart_count": cart.get_items_count(),
                "item_total": float(cart_item.get_total_price()),
                "cart_total": float(cart.get_total_amount()),
            }
        )

    except CartItem.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("العنصر غير موجود في السلة")}, status=404
        )
    except ValueError:
        return JsonResponse(
            {"success": False, "message": _("الكمية غير صحيحة")}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


def get_cart_count_view(request):
    """Get cart items count via AJAX - supports both authenticated and guest users"""
    try:
        if request.user.is_authenticated:
            cart = get_or_create_cart(request.user)
            count = cart.get_items_count()
        else:
            session_cart = get_session_cart(request)
            count = sum(item["quantity"] for item in session_cart.values())

        return JsonResponse({"success": True, "cart_count": count})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@login_required
def cart_view(request):
    """Display cart page - only for authenticated users"""
    # Authenticated user - use database cart
    cart = get_or_create_cart(request.user)
    cart_items = (
        cart.items.select_related("ad", "ad__user", "ad__category")
        .prefetch_related("ad__images")
        .all()
    )
    total_amount = cart.get_total_amount()
    is_guest = False

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "total_amount": total_amount,
        "is_guest": is_guest,
    }

    return render(request, "cart/cart.html", context)


@login_required
def check_partial_payment_eligibility(request):
    """Check if cart items allow partial payment"""
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.select_related("ad").all()

    # Check if all ads allow partial payment
    all_allow_partial = all(item.ad.allow_partial_payment for item in cart_items)

    # Get list of ads that don't allow partial payment
    ads_not_allowing = [
        {"id": item.ad.id, "title": item.ad.title}
        for item in cart_items
        if not item.ad.allow_partial_payment
    ]

    return JsonResponse(
        {
            "allowed": all_allow_partial,
            "ads_not_allowing": ads_not_allowing,
            "total_items": cart_items.count(),
        }
    )


@login_required
def checkout_view(request):
    """Display checkout page"""
    cart = get_or_create_cart(request.user)
    cart_items = (
        cart.items.select_related("ad", "ad__user", "ad__category")
        .prefetch_related("ad__images")
        .all()
    )

    if not cart_items.exists():
        from django.contrib import messages

        messages.warning(request, _("السلة فارغة"))
        return redirect("main:cart_view")

    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        # Handle order placement
        try:
            from main.models import Order, OrderItem
            from django.db import transaction

            # Get form data
            full_name = request.POST.get("full_name")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            city = request.POST.get("city")
            postal_code = request.POST.get("postal_code", "")
            notes = request.POST.get("notes", "")
            payment_method = request.POST.get("payment_method", "cod")

            # Validate partial payment eligibility
            if payment_method == "partial":
                # Check if all ads in cart allow partial payment
                ads_not_allowing_partial = cart_items.filter(
                    ad__allow_partial_payment=False
                ).select_related("ad")

                if ads_not_allowing_partial.exists():
                    ad_titles = [item.ad.title for item in ads_not_allowing_partial[:3]]
                    return JsonResponse(
                        {
                            "success": False,
                            "message": _(
                                "بعض المنتجات في السلة لا تدعم الدفع الجزئي: {ads}"
                            ).format(ads=", ".join(ad_titles)),
                        },
                        status=400,
                    )

            # Get partial payment amount if applicable
            paid_amount = None
            if payment_method == "partial":
                paid_amount = request.POST.get("paid_amount")
                if paid_amount:
                    try:
                        paid_amount = Decimal(paid_amount)
                    except (ValueError, TypeError):
                        return JsonResponse(
                            {
                                "success": False,
                                "message": _("المبلغ المدفوع غير صحيح"),
                            },
                            status=400,
                        )

            # Calculate total
            total_amount = cart.get_total_amount()

            # Create order atomically
            with transaction.atomic():
                # Determine payment status
                payment_status = "unpaid"
                if payment_method == "online":
                    payment_status = "unpaid"  # Will be updated after payment gateway
                elif payment_method == "partial" and paid_amount:
                    if paid_amount >= total_amount:
                        payment_status = "paid"
                        paid_amount = total_amount
                    else:
                        payment_status = "partial"
                elif payment_method == "cod":
                    payment_status = "unpaid"

                # Create order
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    notes=notes,
                    payment_method=payment_method,
                    payment_status=payment_status,
                    paid_amount=paid_amount or Decimal("0.00"),
                    total_amount=total_amount,
                    status="pending",
                )

                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        ad=cart_item.ad,
                        quantity=cart_item.quantity,
                        price=cart_item.ad.price,
                    )

                # Clear cart
                cart_items.delete()

            # Return success response
            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم تأكيد الطلب بنجاح"),
                    "order_id": order.id,
                    "redirect_url": f"/{request.LANGUAGE_CODE}/",
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    total_amount = cart.get_total_amount()

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "total_amount": total_amount,
    }

    return render(request, "cart/checkout.html", context)


# ============================================
# Wishlist Views
# ============================================


@login_required
@require_POST
def add_to_wishlist(request):
    """Add item to wishlist via AJAX"""
    try:
        ad_id = request.POST.get("item_id")
        if not ad_id:
            return JsonResponse(
                {"success": False, "message": _("معرف الإعلان مفقود")}, status=400
            )

        ad = get_object_or_404(
            ClassifiedAd, id=ad_id, status=ClassifiedAd.AdStatus.ACTIVE
        )
        wishlist = get_or_create_wishlist(request.user)

        # Try to create wishlist item
        try:
            wishlist_item = WishlistItem.objects.create(wishlist=wishlist, ad=ad)
            message = _("تمت إضافة {} إلى المفضلة").format(ad.title)
            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "wishlist_count": wishlist.get_items_count(),
                    "item_id": ad_id,
                    "is_in_wishlist": True,
                }
            )
        except IntegrityError:
            # Item already in wishlist
            return JsonResponse(
                {
                    "success": False,
                    "message": _("هذا الإعلان موجود بالفعل في المفضلة"),
                    "wishlist_count": wishlist.get_items_count(),
                },
                status=400,
            )

    except ClassifiedAd.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("الإعلان غير موجود")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@login_required
@require_POST
def remove_from_wishlist(request):
    """Remove item from wishlist via AJAX"""
    try:
        ad_id = request.POST.get("item_id")
        if not ad_id:
            return JsonResponse(
                {"success": False, "message": _("معرف الإعلان مفقود")}, status=400
            )

        wishlist = get_or_create_wishlist(request.user)
        wishlist_item = get_object_or_404(WishlistItem, wishlist=wishlist, ad_id=ad_id)

        ad_title = wishlist_item.ad.title
        wishlist_item.delete()

        return JsonResponse(
            {
                "success": True,
                "message": _("تمت إزالة {} من المفضلة").format(ad_title),
                "wishlist_count": wishlist.get_items_count(),
                "item_id": ad_id,
                "is_in_wishlist": False,
            }
        )

    except WishlistItem.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("العنصر غير موجود في المفضلة")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@login_required
@require_POST
def toggle_wishlist(request):
    """Toggle item in wishlist (add if not exists, remove if exists) via AJAX"""
    try:
        ad_id = request.POST.get("item_id")
        if not ad_id:
            return JsonResponse(
                {"success": False, "message": _("معرف الإعلان مفقود")}, status=400
            )

        ad = get_object_or_404(
            ClassifiedAd, id=ad_id, status=ClassifiedAd.AdStatus.ACTIVE
        )
        wishlist = get_or_create_wishlist(request.user)

        # Check if item exists in wishlist
        wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, ad=ad).first()

        if wishlist_item:
            # Remove from wishlist
            wishlist_item.delete()
            message = _("تمت إزالة {} من المفضلة").format(ad.title)
            is_in_wishlist = False
        else:
            # Add to wishlist
            WishlistItem.objects.create(wishlist=wishlist, ad=ad)
            message = _("تمت إضافة {} إلى المفضلة").format(ad.title)
            is_in_wishlist = True

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "wishlist_count": wishlist.get_items_count(),
                "item_id": ad_id,
                "is_in_wishlist": is_in_wishlist,
            }
        )

    except ClassifiedAd.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": _("الإعلان غير موجود")}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@login_required
def get_wishlist_count(request):
    """Get wishlist items count via AJAX"""
    try:
        wishlist = get_or_create_wishlist(request.user)
        return JsonResponse(
            {"success": True, "wishlist_count": wishlist.get_items_count()}
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@login_required
def check_wishlist_status(request):
    """Check if items are in wishlist via AJAX"""
    try:
        ad_ids = request.GET.getlist("ad_ids[]")
        if not ad_ids:
            return JsonResponse(
                {"success": False, "message": _("معرفات الإعلانات مفقودة")},
                status=400,
            )

        wishlist = get_or_create_wishlist(request.user)
        wishlist_ad_ids = list(
            WishlistItem.objects.filter(
                wishlist=wishlist, ad_id__in=ad_ids
            ).values_list("ad_id", flat=True)
        )

        return JsonResponse(
            {
                "success": True,
                "wishlist_ad_ids": wishlist_ad_ids,
                "wishlist_count": wishlist.get_items_count(),
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": _("حدث خطأ: {}").format(str(e))}, status=500
        )


@login_required
def wishlist_view(request):
    """Display wishlist page - only for authenticated users"""
    wishlist = get_or_create_wishlist(request.user)
    wishlist_items = wishlist.items.select_related(
        "ad", "ad__user", "ad__category", "ad__country"
    ).all()

    context = {
        "wishlist": wishlist,
        "wishlist_items": wishlist_items,
        "is_guest": False,
    }

    return render(request, "wishlist/wishlist.html", context)


def get_bulk_ads(request):
    """
    Fetch multiple ads by IDs for guest wishlist rendering
    Returns ad data with rendered HTML cards
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Method not allowed"}, status=405
        )

    try:
        data = json.loads(request.body)
        ad_ids = data.get("ad_ids", [])

        if not ad_ids or not isinstance(ad_ids, list):
            return JsonResponse(
                {"success": False, "message": "Invalid ad_ids"}, status=400
            )

        # Limit to 50 ads max to prevent abuse
        ad_ids = ad_ids[:50]

        # Fetch ads
        ads = (
            ClassifiedAd.objects.filter(
                id__in=ad_ids, status=ClassifiedAd.AdStatus.ACTIVE
            )
            .select_related("user", "category", "country")
            .prefetch_related("images")
        )

        # Render each ad card
        ads_data = []
        for ad in ads:
            try:
                html = render_to_string(
                    "partials/_ad_card_component.html",
                    {
                        "ad": ad,
                        "user": request.user,
                        "LANGUAGE_CODE": request.LANGUAGE_CODE,
                    },
                )
                ads_data.append(
                    {
                        "id": ad.id,
                        "html": html,
                    }
                )
            except Exception as e:
                # Skip ads that fail to render
                print(f"Error rendering ad {ad.id}: {e}")
                continue

        return JsonResponse({"success": True, "ads": ads_data, "count": len(ads_data)})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
