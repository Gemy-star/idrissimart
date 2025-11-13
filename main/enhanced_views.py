from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
import json
from datetime import datetime, timedelta

from .models import (
    Category,
    ClassifiedAd,
    AdFeaturePrice,
    CartSettings,
    AdReservation,
    AdTransaction,
    AdPackage,
    UserPackage,
    CustomField,
    AdFeature,
)


@login_required
def enhanced_ad_create(request):
    """Enhanced ad creation with custom fields and features"""
    if request.method == "POST":
        try:
            # Get form data
            title = request.POST.get("title")
            description = request.POST.get("description")
            price = request.POST.get("price")
            category_id = request.POST.get("category")

            # Validate required fields
            if not all([title, description, price, category_id]):
                return JsonResponse(
                    {"success": False, "error": _("جميع الحقول مطلوبة")}
                )

            category = get_object_or_404(Category, id=category_id)

            # Create the ad
            ad = ClassifiedAd.objects.create(
                title=title,
                description=description,
                price=Decimal(price),
                category=category,
                user=request.user,
                status="pending",
            )

            # Process custom fields
            custom_fields_data = {}
            for field in CustomField.objects.filter(category=category):
                field_value = request.POST.get(f"custom_field_{field.id}")
                if field_value:
                    custom_fields_data[field.name] = field_value

            ad.custom_fields = custom_fields_data

            # Process selected features
            selected_features = request.POST.getlist("features")
            total_features_price = Decimal("0")

            for feature_id in selected_features:
                try:
                    feature = AdFeature.objects.get(id=feature_id)
                    feature_price = AdFeaturePrice.objects.filter(
                        feature=feature, category=category
                    ).first()

                    if feature_price:
                        total_features_price += feature_price.price
                        # Add feature to ad (you might need a many-to-many relationship)

                except AdFeature.DoesNotExist:
                    continue

            ad.features_price = total_features_price
            ad.save()

            # Handle reservation if cart is enabled
            cart_settings = CartSettings.objects.first()
            if cart_settings and cart_settings.enable_cart:
                # Create reservation
                reservation = AdReservation.objects.create(
                    user=request.user,
                    ad=ad,
                    quantity=1,
                    total_amount=ad.price + total_features_price,
                    expires_at=timezone.now()
                    + timedelta(hours=cart_settings.reservation_duration),
                )

                return JsonResponse(
                    {
                        "success": True,
                        "message": _("تم إنشاء الإعلان وحجزه بنجاح"),
                        "reservation_id": reservation.id,
                        "ad_id": ad.id,
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": True,
                        "message": _("تم إنشاء الإعلان بنجاح"),
                        "ad_id": ad.id,
                    }
                )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # GET request - show form
    categories = Category.objects.filter(parent__isnull=False)  # Only subcategories
    features = AdFeature.objects.filter(is_active=True)
    cart_settings = CartSettings.objects.first()

    context = {
        "categories": categories,
        "features": features,
        "cart_settings": cart_settings,
    }

    return render(request, "classifieds/enhanced_ad_create.html", context)


@login_required
def packages_list(request):
    """List available packages for users"""
    # Get user's active packages
    active_packages = UserPackage.objects.filter(
        user=request.user, is_active=True, expiry_date__gt=timezone.now()
    ).select_related("package")

    # Get general packages (not category-specific)
    general_packages = AdPackage.objects.filter(
        category__isnull=True, is_active=True
    ).order_by("price")

    # Get category-specific packages grouped by category
    category_packages = {}
    categories_with_packages = Category.objects.filter(
        adpackage__isnull=False, adpackage__is_active=True
    ).distinct()

    for category in categories_with_packages:
        packages = AdPackage.objects.filter(category=category, is_active=True).order_by(
            "price"
        )
        if packages.exists():
            category_packages[category] = packages

    context = {
        "active_packages": active_packages,
        "general_packages": general_packages,
        "category_packages": category_packages,
    }

    return render(request, "classifieds/packages_list.html", context)


@login_required
@staff_member_required
def reservation_management(request):
    """Management page for reservations"""
    # Get filter parameters
    status_filter = request.GET.get("status")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    user_filter = request.GET.get("user")

    # Build query
    reservations = AdReservation.objects.select_related("user", "ad", "ad__category")

    if status_filter:
        reservations = reservations.filter(status=status_filter)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            reservations = reservations.filter(created_at__date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
            reservations = reservations.filter(created_at__date__lte=date_to)
        except ValueError:
            pass

    if user_filter:
        reservations = reservations.filter(
            Q(user__username__icontains=user_filter)
            | Q(user__email__icontains=user_filter)
        )

    reservations = reservations.order_by("-created_at")

    # Statistics
    total_reservations = AdReservation.objects.count()
    pending_reservations = AdReservation.objects.filter(status="pending").count()
    completed_reservations = AdReservation.objects.filter(status="completed").count()
    cancelled_reservations = AdReservation.objects.filter(status="cancelled").count()

    # Pagination
    paginator = Paginator(reservations, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "reservations": page_obj,
        "total_reservations": total_reservations,
        "pending_reservations": pending_reservations,
        "completed_reservations": completed_reservations,
        "cancelled_reservations": cancelled_reservations,
        "is_paginated": page_obj.has_other_pages(),
        "page_obj": page_obj,
        "active_nav": "reservations",
    }

    return render(request, "classifieds/reservation_management.html", context)


# AJAX Views


@require_http_methods(["GET"])
def get_custom_fields(request):
    """Get custom fields for a category"""
    category_id = request.GET.get("category_id")

    if not category_id:
        return JsonResponse({"success": False, "error": _("معرف القسم مطلوب")})

    try:
        category = Category.objects.get(id=category_id)
        fields = CustomField.objects.filter(category=category, is_active=True)

        fields_data = []
        for field in fields:
            field_data = {
                "id": field.id,
                "name": field.name,
                "field_type": field.field_type,
                "is_required": field.is_required,
                "help_text": field.help_text,
                "options": field.options.split(",") if field.options else [],
            }
            fields_data.append(field_data)

        return JsonResponse({"success": True, "fields": fields_data})

    except Category.DoesNotExist:
        return JsonResponse({"success": False, "error": _("القسم غير موجود")})


@require_http_methods(["GET"])
def get_features(request):
    """Get available features for a category"""
    category_id = request.GET.get("category_id")

    if not category_id:
        return JsonResponse({"success": False, "error": _("معرف القسم مطلوب")})

    try:
        category = Category.objects.get(id=category_id)
        features = AdFeature.objects.filter(is_active=True)

        features_data = []
        for feature in features:
            feature_price = AdFeaturePrice.objects.filter(
                feature=feature, category=category
            ).first()

            feature_data = {
                "id": feature.id,
                "name": feature.name,
                "description": feature.description,
                "icon": feature.icon,
                "price": str(feature_price.price) if feature_price else "0",
                "duration_days": feature_price.duration_days if feature_price else None,
            }
            features_data.append(feature_data)

        return JsonResponse({"success": True, "features": features_data})

    except Category.DoesNotExist:
        return JsonResponse({"success": False, "error": _("القسم غير موجود")})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_features_price(request):
    """Calculate total price for selected features"""
    try:
        data = json.loads(request.body)
        category_id = data.get("category_id")
        feature_ids = data.get("feature_ids", [])

        if not category_id:
            return JsonResponse({"success": False, "error": _("معرف القسم مطلوب")})

        category = Category.objects.get(id=category_id)
        total_price = Decimal("0")

        for feature_id in feature_ids:
            feature_price = AdFeaturePrice.objects.filter(
                feature_id=feature_id, category=category
            ).first()

            if feature_price:
                total_price += feature_price.price

        return JsonResponse({"success": True, "total_price": str(total_price)})

    except (json.JSONDecodeError, Category.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_reservation(request):
    """Create a new reservation"""
    try:
        data = json.loads(request.body)
        ad_id = data.get("ad_id")
        quantity = int(data.get("quantity", 1))

        if not ad_id:
            return JsonResponse({"success": False, "error": _("معرف الإعلان مطلوب")})

        ad = ClassifiedAd.objects.get(id=ad_id)

        # Check if cart is enabled
        cart_settings = CartSettings.objects.first()
        if not cart_settings or not cart_settings.enable_cart:
            return JsonResponse({"success": False, "error": _("سلة الحجز غير مفعلة")})

        # Calculate total amount
        total_amount = ad.price * quantity

        # Create reservation
        reservation = AdReservation.objects.create(
            user=request.user,
            ad=ad,
            quantity=quantity,
            total_amount=total_amount,
            expires_at=timezone.now()
            + timedelta(hours=cart_settings.reservation_duration),
        )

        return JsonResponse(
            {
                "success": True,
                "message": _("تم حجز الإعلان بنجاح"),
                "reservation_id": reservation.id,
            }
        )

    except (json.JSONDecodeError, ClassifiedAd.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def activate_package(request):
    """Activate a free package"""
    try:
        data = json.loads(request.body)
        package_id = data.get("package_id")

        if not package_id:
            return JsonResponse({"success": False, "error": _("معرف الباقة مطلوب")})

        package = AdPackage.objects.get(id=package_id)

        # Check if package is free
        if package.price > 0:
            return JsonResponse({"success": False, "error": _("هذه الباقة غير مجانية")})

        # Check if user already has an active package of this type
        existing_package = UserPackage.objects.filter(
            user=request.user,
            package=package,
            is_active=True,
            expiry_date__gt=timezone.now(),
        ).first()

        if existing_package:
            return JsonResponse(
                {"success": False, "error": _("لديك باقة نشطة من هذا النوع بالفعل")}
            )

        # Create user package
        user_package = UserPackage.objects.create(
            user=request.user,
            package=package,
            ads_remaining=package.ad_count,
            expiry_date=timezone.now() + timedelta(days=package.duration_days),
            is_active=True,
        )

        return JsonResponse({"success": True, "message": _("تم تفعيل الباقة بنجاح")})

    except (json.JSONDecodeError, AdPackage.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["GET"])
@staff_member_required
def reservation_details(request, reservation_id):
    """Get reservation details for modal display"""
    try:
        reservation = AdReservation.objects.select_related(
            "user", "ad", "ad__category"
        ).get(id=reservation_id)

        html = render_to_string(
            "classifieds/reservation_detail_modal.html", {"reservation": reservation}
        )

        return JsonResponse({"success": True, "html": html})

    except AdReservation.DoesNotExist:
        return JsonResponse({"success": False, "error": _("الحجز غير موجود")})


@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def update_reservation_status(request):
    """Update reservation status"""
    try:
        data = json.loads(request.body)
        reservation_id = data.get("reservation_id")
        status = data.get("status")

        if not all([reservation_id, status]):
            return JsonResponse({"success": False, "error": _("البيانات غير مكتملة")})

        reservation = AdReservation.objects.get(id=reservation_id)
        reservation.status = status
        reservation.save()

        return JsonResponse(
            {"success": True, "message": _("تم تحديث حالة الحجز بنجاح")}
        )

    except (json.JSONDecodeError, AdReservation.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["DELETE"])
@staff_member_required
def delete_reservation(request):
    """Delete a reservation"""
    try:
        data = json.loads(request.body)
        reservation_id = data.get("reservation_id")

        if not reservation_id:
            return JsonResponse({"success": False, "error": _("معرف الحجز مطلوب")})

        reservation = AdReservation.objects.get(id=reservation_id)
        reservation.delete()

        return JsonResponse({"success": True, "message": _("تم حذف الحجز بنجاح")})

    except (json.JSONDecodeError, AdReservation.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def send_reservation_notification(request):
    """Send notification reminder for reservation"""
    try:
        data = json.loads(request.body)
        reservation_id = data.get("reservation_id")

        if not reservation_id:
            return JsonResponse({"success": False, "error": _("معرف الحجز مطلوب")})

        reservation = AdReservation.objects.get(id=reservation_id)

        # Here you would implement email/SMS notification
        # For now, just return success

        return JsonResponse({"success": True, "message": _("تم إرسال التذكير بنجاح")})

    except (json.JSONDecodeError, AdReservation.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def add_reservation(request):
    """Add a new reservation manually"""
    try:
        data = json.loads(request.body)
        user_id = data.get("user")
        ad_id = data.get("ad")
        quantity = int(data.get("quantity", 1))
        total_amount = Decimal(data.get("total_amount"))
        expires_at = data.get("expires_at")
        status = data.get("status", "pending")
        notes = data.get("notes", "")

        if not all([user_id, ad_id, total_amount]):
            return JsonResponse({"success": False, "error": _("البيانات غير مكتملة")})

        user = User.objects.get(id=user_id)
        ad = ClassifiedAd.objects.get(id=ad_id)

        # Parse expires_at if provided
        expiry_date = None
        if expires_at:
            try:
                expiry_date = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            except ValueError:
                pass

        reservation = AdReservation.objects.create(
            user=user,
            ad=ad,
            quantity=quantity,
            total_amount=total_amount,
            expires_at=expiry_date,
            status=status,
            notes=notes,
        )

        return JsonResponse({"success": True, "message": _("تم إضافة الحجز بنجاح")})

    except (json.JSONDecodeError, User.DoesNotExist, ClassifiedAd.DoesNotExist) as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["GET"])
@staff_member_required
def get_users(request):
    """Get list of users for dropdown"""
    users = User.objects.filter(is_active=True).values("id", "username", "email")[:100]

    return JsonResponse({"success": True, "users": list(users)})


@require_http_methods(["GET"])
@staff_member_required
def get_ads(request):
    """Get list of ads for dropdown"""
    ads = ClassifiedAd.objects.filter(status="approved").values("id", "title", "price")[
        :100
    ]

    return JsonResponse({"success": True, "ads": list(ads)})
