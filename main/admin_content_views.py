"""
Admin views for content management (HomeSlider, etc.)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from content.models import HomeSlider, Country


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff


# ============================================
# HOME SLIDER MANAGEMENT
# ============================================


@login_required
@user_passes_test(is_admin)
def admin_home_sliders(request):
    """List all home sliders"""
    sliders = (
        HomeSlider.objects.select_related("country")
        .all()
        .order_by("order", "-created_at")
    )

    # Filter by country if specified
    country_filter = request.GET.get("country")
    if country_filter:
        sliders = sliders.filter(country__code=country_filter)

    # Pagination
    paginator = Paginator(sliders, 20)
    page = request.GET.get("page", 1)
    sliders_page = paginator.get_page(page)

    context = {
        "sliders": sliders_page,
        "total_sliders": sliders.count(),
        "active_sliders": sliders.filter(is_active=True).count(),
        "inactive_sliders": sliders.filter(is_active=False).count(),
        "countries": Country.objects.filter(is_active=True).order_by("order", "name"),
        "selected_country": country_filter,
    }

    return render(request, "admin_dashboard/home_sliders/list.html", context)


@login_required
@user_passes_test(is_admin)
def admin_home_slider_create(request):
    """Create new home slider"""
    if request.method == "POST":
        try:
            # Get country (optional)
            country_id = request.POST.get("country")
            country = None
            if country_id:
                country = get_object_or_404(Country, id=country_id)

            slider = HomeSlider.objects.create(
                country=country,
                title=request.POST.get("title", ""),
                title_ar=request.POST.get("title_ar", ""),
                subtitle=request.POST.get("subtitle", ""),
                subtitle_ar=request.POST.get("subtitle_ar", ""),
                description=request.POST.get("description", ""),
                description_ar=request.POST.get("description_ar", ""),
                button_text=request.POST.get("button_text", ""),
                button_text_ar=request.POST.get("button_text_ar", ""),
                button_url=request.POST.get("button_url", ""),
                background_color=request.POST.get("background_color", "#4B315E"),
                text_color=request.POST.get("text_color", "#FFFFFF"),
                order=int(request.POST.get("order", 0)),
                is_active=request.POST.get("is_active") == "on",
            )

            # Handle image upload
            if "image" in request.FILES:
                slider.image = request.FILES["image"]
                slider.save()

            messages.success(request, _("تم إنشاء الشريحة بنجاح"))
            return redirect("main:admin_home_sliders")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "action": "create",
        "countries": Country.objects.filter(is_active=True).order_by("order", "name"),
    }

    return render(request, "admin_dashboard/home_sliders/form.html", context)


@login_required
@user_passes_test(is_admin)
def admin_home_slider_edit(request, slider_id):
    """Edit home slider"""
    slider = get_object_or_404(HomeSlider, id=slider_id)

    if request.method == "POST":
        try:
            # Update country (optional)
            country_id = request.POST.get("country")
            if country_id:
                slider.country = get_object_or_404(Country, id=country_id)
            else:
                slider.country = None

            slider.title = request.POST.get("title", "")
            slider.title_ar = request.POST.get("title_ar", "")
            slider.subtitle = request.POST.get("subtitle", "")
            slider.subtitle_ar = request.POST.get("subtitle_ar", "")
            slider.description = request.POST.get("description", "")
            slider.description_ar = request.POST.get("description_ar", "")
            slider.button_text = request.POST.get("button_text", "")
            slider.button_text_ar = request.POST.get("button_text_ar", "")
            slider.button_url = request.POST.get("button_url", "")
            slider.background_color = request.POST.get("background_color", "#4B315E")
            slider.text_color = request.POST.get("text_color", "#FFFFFF")
            slider.order = int(request.POST.get("order", 0))
            slider.is_active = request.POST.get("is_active") == "on"

            # Handle image upload
            if "image" in request.FILES:
                slider.image = request.FILES["image"]

            slider.save()

            messages.success(request, _("تم تحديث الشريحة بنجاح"))
            return redirect("main:admin_home_sliders")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "slider": slider,
        "action": "edit",
        "countries": Country.objects.filter(is_active=True).order_by("order", "name"),
    }

    return render(request, "admin_dashboard/home_sliders/form.html", context)


@login_required
@user_passes_test(is_admin)
def admin_home_slider_delete(request, slider_id):
    """Delete home slider"""
    slider = get_object_or_404(HomeSlider, id=slider_id)

    if request.method == "POST":
        slider.delete()
        messages.success(request, _("تم حذف الشريحة بنجاح"))

    return redirect("main:admin_home_sliders")


@login_required
@user_passes_test(is_admin)
def admin_home_slider_toggle(request, slider_id):
    """Toggle slider active status"""
    slider = get_object_or_404(HomeSlider, id=slider_id)
    slider.is_active = not slider.is_active
    slider.save()

    status = _("مفعّل") if slider.is_active else _("معطّل")
    messages.success(request, f"تم تغيير حالة الشريحة إلى: {status}")

    return redirect("main:admin_home_sliders")
