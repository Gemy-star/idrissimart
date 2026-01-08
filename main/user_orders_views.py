# main/user_orders_views.py
"""
User Orders Views - Show user's own orders (as a buyer)
عرض طلبات العضو الخاصة (كمشتري)
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils.translation import gettext as _

from .models import Order, OrderItem


@login_required
def my_orders_list(request):
    """
    عرض طلبات العضو (مشتريات السلة)
    Display user's own orders (purchases from cart)
    """
    # Get orders where user is the buyer
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__ad__images", "items__ad__user")
        .order_by("-created_at")
    )

    # Filter by status
    status_filter = request.GET.get("status")
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Filter by payment status
    payment_status_filter = request.GET.get("payment_status")
    if payment_status_filter:
        orders = orders.filter(payment_status=payment_status_filter)

    # Search by order number
    search_query = request.GET.get("search", "")
    if search_query:
        orders = orders.filter(Q(order_number__icontains=search_query))

    # Statistics
    all_orders = Order.objects.filter(user=request.user)
    stats = {
        "total_orders": all_orders.count(),
        "pending": all_orders.filter(status="pending").count(),
        "processing": all_orders.filter(status="processing").count(),
        "shipped": all_orders.filter(status="shipped").count(),
        "delivered": all_orders.filter(status="delivered").count(),
        "cancelled": all_orders.filter(status="cancelled").count(),
        "total_spent": all_orders.filter(payment_status="paid").aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0,
        "unpaid": all_orders.filter(payment_status="unpaid").count(),
        "partially_paid": all_orders.filter(payment_status="partial").count(),
    }

    # Pagination
    paginator = Paginator(orders, 10)
    page = request.GET.get("page", 1)
    orders_page = paginator.get_page(page)

    context = {
        "orders": orders_page,
        "stats": stats,
        "status_filter": status_filter,
        "payment_status_filter": payment_status_filter,
        "search_query": search_query,
        "active_nav": "my_orders",
        "page_title": _("طلباتي"),
    }

    return render(request, "dashboard/my_orders_list.html", context)


@login_required
def my_order_detail(request, order_id):
    """
    عرض تفاصيل الطلب
    Display order details
    """
    order = get_object_or_404(
        Order.objects.filter(user=request.user)
        .prefetch_related("items__ad__images", "items__ad__user")
        .select_related("country"),
        id=order_id,
    )

    context = {
        "order": order,
        "active_nav": "my_orders",
        "page_title": _("تفاصيل الطلب") + f" #{order.order_number}",
    }

    return render(request, "dashboard/my_order_detail.html", context)
