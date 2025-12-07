"""
Admin Order Management Views
Handles order CRUD operations in admin dashboard
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from main.models import Order, OrderItem


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff


# ============================================
# ADMIN ORDER MANAGEMENT
# ============================================


@login_required
@user_passes_test(is_admin)
def admin_orders_list(request):
    """List all orders for admin"""
    orders = Order.objects.select_related("user").prefetch_related("items").all()

    # Filter by status
    status_filter = request.GET.get("status")
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Filter by payment method
    payment_filter = request.GET.get("payment_method")
    if payment_filter:
        orders = orders.filter(payment_method=payment_filter)

    # Filter by payment status
    payment_status_filter = request.GET.get("payment_status")
    if payment_status_filter:
        orders = orders.filter(payment_status=payment_status_filter)

    # Search by order number, customer name, or phone
    search_query = request.GET.get("search", "")
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query)
            | Q(full_name__icontains=search_query)
            | Q(phone__icontains=search_query)
            | Q(user__username__icontains=search_query)
        )

    # Date filter
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)

    # Statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status="pending").count()
    processing_orders = orders.filter(status="processing").count()
    shipped_orders = orders.filter(status="shipped").count()
    delivered_orders = orders.filter(status="delivered").count()
    cancelled_orders = orders.filter(status="cancelled").count()

    total_revenue = (
        orders.filter(status__in=["processing", "shipped", "delivered"]).aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )

    # Pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get("page", 1)
    orders_page = paginator.get_page(page)

    # Get currency from selected country in session
    from content.models import Country
    from main.utils import get_selected_country_from_request

    currency = "SAR"  # Default
    currency_symbol = "ر.س"

    selected_country_code = get_selected_country_from_request(request, default="SA")
    try:
        country = Country.objects.get(code=selected_country_code)
        currency = country.currency or "SAR"
    except Country.DoesNotExist:
        pass

    # Currency symbols mapping
    currency_symbols = {
        "SAR": "ر.س",
        "EGP": "ج.م",
        "AED": "د.إ",
        "KWD": "د.ك",
        "QAR": "ر.ق",
        "BHD": "د.ب",
        "OMR": "ر.ع",
        "JOD": "د.أ",
    }
    currency_symbol = currency_symbols.get(currency, currency)

    context = {
        "orders": orders_page,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "processing_orders": processing_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": total_revenue,
        "status_filter": status_filter,
        "payment_filter": payment_filter,
        "search_query": search_query,
        "date_from": date_from,
        "date_to": date_to,
        "currency": currency,
        "currency_symbol": currency_symbol,
        "active_nav": "orders",
    }

    return render(request, "admin_dashboard/orders/list.html", context)


@login_required
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("items__ad__images"),
        id=order_id,
    )

    # Get currency from selected country
    from content.models import Country
    from main.utils import get_selected_country_from_request

    currency = "SAR"
    currency_symbol = "ر.س"

    selected_country_code = get_selected_country_from_request(request, default="SA")
    try:
        country = Country.objects.get(code=selected_country_code)
        currency = country.currency or "SAR"
    except Country.DoesNotExist:
        pass

    currency_symbols = {
        "SAR": "ر.س",
        "EGP": "ج.م",
        "AED": "د.إ",
        "KWD": "د.ك",
        "QAR": "ر.ق",
        "BHD": "د.ب",
        "OMR": "ر.ع",
        "JOD": "د.أ",
    }
    currency_symbol = currency_symbols.get(currency, currency)

    context = {
        "order": order,
        "currency": currency,
        "currency_symbol": currency_symbol,
        "active_nav": "orders",
    }

    return render(request, "admin_dashboard/orders/detail.html", context)


@login_required
@user_passes_test(is_admin)
def admin_order_update_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, _("تم تحديث حالة الطلب بنجاح"))
        else:
            messages.error(request, _("حالة غير صالحة"))

        return redirect("main:admin_order_detail", order_id=order.id)

    return redirect("main:admin_orders_list")


@login_required
@user_passes_test(is_admin)
def admin_order_delete(request, order_id):
    """Delete order"""
    order = get_object_or_404(Order, id=order_id)
    order_number = order.order_number
    order.delete()
    messages.success(request, f"تم حذف الطلب {order_number} بنجاح")
    return redirect("main:admin_orders_list")


@login_required
@user_passes_test(is_admin)
def admin_orders_statistics(request):
    """Orders statistics dashboard"""
    # Date range - default last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if date_from:
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
    if date_to:
        end_date = datetime.strptime(date_to, "%Y-%m-%d")

    orders = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)

    # Overall statistics
    total_orders = orders.count()
    total_revenue = (
        orders.filter(status__in=["processing", "shipped", "delivered"]).aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )

    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # Orders by status
    status_stats = {}
    for status, label in Order.STATUS_CHOICES:
        status_stats[status] = {
            "label": label,
            "count": orders.filter(status=status).count(),
        }

    # Orders by payment method
    payment_stats = {}
    for method, label in Order.PAYMENT_METHOD_CHOICES:
        payment_stats[method] = {
            "label": label,
            "count": orders.filter(payment_method=method).count(),
        }

    # Daily orders
    daily_orders = (
        orders.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(count=Count("id"), revenue=Sum("total_amount"))
        .order_by("date")
    )

    # Top customers
    top_customers = (
        orders.values("user__username", "user__first_name", "user__last_name")
        .annotate(order_count=Count("id"), total_spent=Sum("total_amount"))
        .order_by("-total_spent")[:10]
    )

    # Get currency from selected country
    from content.models import Country
    from main.utils import get_selected_country_from_request

    currency = "SAR"
    currency_symbol = "ر.س"

    selected_country_code = get_selected_country_from_request(request, default="SA")
    try:
        country = Country.objects.get(code=selected_country_code)
        currency = country.currency or "SAR"
    except Country.DoesNotExist:
        pass

    currency_symbols = {
        "SAR": "ر.س",
        "EGP": "ج.م",
        "AED": "د.إ",
        "KWD": "د.ك",
        "QAR": "ر.ق",
        "BHD": "د.ب",
        "OMR": "ر.ع",
        "JOD": "د.أ",
    }
    currency_symbol = currency_symbols.get(currency, currency)

    context = {
        "statistics": {
            "total_revenue": total_revenue,
            "pending_orders": status_stats.get("pending", {}).get("count", 0),
            "processing_orders": status_stats.get("processing", {}).get("count", 0),
            "shipped_orders": status_stats.get("shipped", {}).get("count", 0),
            "delivered_orders": status_stats.get("delivered", {}).get("count", 0),
            "cancelled_orders": status_stats.get("cancelled", {}).get("count", 0),
            "daily_orders": daily_orders,
            "top_customers": top_customers,
        },
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "status_stats": status_stats,
        "payment_stats": payment_stats,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "currency": currency,
        "currency_symbol": currency_symbol,
        "active_nav": "orders",
    }

    return render(request, "admin_dashboard/orders/statistics.html", context)


# ============================================
# PUBLISHER ORDER MANAGEMENT
# ============================================


@login_required
def publisher_orders_list(request):
    """List orders for items published by current user"""
    # Get orders that contain items from this publisher's ads
    orders = (
        Order.objects.filter(items__ad__user=request.user)
        .distinct()
        .select_related("user")
        .prefetch_related("items__ad")
    )

    # Filter by status
    status_filter = request.GET.get("status")
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Search
    search_query = request.GET.get("search", "")
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query)
            | Q(full_name__icontains=search_query)
        )

    # Statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status="pending").count()
    delivered_orders = orders.filter(status="delivered").count()

    # Calculate revenue from publisher's items only
    publisher_items = OrderItem.objects.filter(
        ad__user=request.user, order__status__in=["processing", "shipped", "delivered"]
    )
    total_revenue = sum(item.get_total_price() for item in publisher_items)

    # Pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get("page", 1)
    orders_page = paginator.get_page(page)

    context = {
        "orders": orders_page,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "total_revenue": total_revenue,
        "status_filter": status_filter,
        "search_query": search_query,
        "active_nav": "orders",
    }

    return render(request, "publisher_dashboard/orders/list.html", context)


@login_required
def publisher_order_detail(request, order_id):
    """View order details for publisher"""
    # Ensure order contains items from this publisher
    order = get_object_or_404(
        Order.objects.filter(items__ad__user=request.user)
        .distinct()
        .select_related("user")
        .prefetch_related("items__ad__images"),
        id=order_id,
    )

    # Get only this publisher's items from the order
    publisher_items = order.items.filter(ad__user=request.user)

    # Calculate publisher revenue from this order
    publisher_revenue = sum(item.get_total_price() for item in publisher_items)

    context = {
        "order": order,
        "publisher_items": publisher_items,
        "publisher_revenue": publisher_revenue,
        "active_nav": "orders",
    }

    return render(request, "publisher_dashboard/orders/detail.html", context)
