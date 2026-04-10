"""
Custom admin views for Safety Tips management
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import ListView, View
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.utils import timezone

from .models import SafetyTip, Category


class AdminSafetyTipsView(LoginRequiredMixin, ListView):
    """Admin view for managing safety tips with preview"""

    model = SafetyTip
    template_name = "admin/safety_tips.html"
    context_object_name = "tips"
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
            return redirect("main:home")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = SafetyTip.objects.select_related('category').prefetch_related('categories').order_by('order', 'id')

        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)

        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(
                Q(category_id=category_id) | Q(categories__id=category_id)
            ).distinct()

        # Filter by color theme
        color = self.request.GET.get('color')
        if color:
            queryset = queryset.filter(color_theme=color)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(title_en__icontains=search) |
                Q(description__icontains=search) |
                Q(description_en__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Set active navigation
        context['active_nav'] = 'safety_tips'

        # Statistics
        context['stats'] = {
            'total': SafetyTip.objects.count(),
            'active': SafetyTip.objects.filter(is_active=True).count(),
            'inactive': SafetyTip.objects.filter(is_active=False).count(),
            'general': SafetyTip.objects.filter(category__isnull=True).count(),
        }

        # Categories for filters and forms
        context['all_categories'] = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')

        # Current filters
        context['current_status'] = self.request.GET.get('is_active', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_color'] = self.request.GET.get('color', '')
        context['search_query'] = self.request.GET.get('search', '')

        # Color themes for dropdown
        context['color_themes'] = SafetyTip.ColorTheme.choices

        return context


class SafetyTipDetailView(LoginRequiredMixin, View):
    """Get details of a specific safety tip"""

    def get(self, request, tip_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"},
                status=403
            )

        try:
            tip = SafetyTip.objects.prefetch_related('categories').get(id=tip_id)

            data = {
                'success': True,
                'id': tip.pk,
                'title': tip.title,
                'title_en': tip.title_en,
                'description': tip.description,
                'description_en': tip.description_en,
                'icon_class': tip.icon_class,
                'color_theme': tip.color_theme,
                'category': tip.category.pk if tip.category else None,
                'categories': list(tip.categories.values_list('id', flat=True)),
                'is_active': tip.is_active,
                'order': tip.order,
            }
            return JsonResponse(data)
        except SafetyTip.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Tip not found"},
                status=404
            )


class SafetyTipSaveView(LoginRequiredMixin, View):
    """Save (create/update) safety tip"""

    def post(self, request):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"},
                status=403
            )

        tip_id = request.POST.get('tip_id')
        title = request.POST.get('title')
        title_en = request.POST.get('title_en', '')
        description = request.POST.get('description')
        description_en = request.POST.get('description_en', '')
        icon_class = request.POST.get('icon_class', 'fas fa-info-circle')
        color_theme = request.POST.get('color_theme', 'tip-blue')
        category_id = request.POST.get('category')
        category_ids = request.POST.getlist('categories[]')
        is_active = request.POST.get('is_active') == 'on'
        order = request.POST.get('order', 0)

        try:
            if tip_id:
                # Update existing tip
                tip = SafetyTip.objects.get(id=tip_id)
                action = "updated"
            else:
                # Create new tip
                tip = SafetyTip()
                action = "created"

            tip.title = title
            tip.title_en = title_en
            tip.description = description
            tip.description_en = description_en
            tip.icon_class = icon_class
            tip.color_theme = color_theme
            tip.category = Category.objects.get(pk=category_id) if category_id else None
            tip.is_active = is_active
            tip.order = int(order)

            tip.save()

            # Handle multiple categories
            if category_ids:
                tip.categories.set(category_ids)
            else:
                tip.categories.clear()

            message = _("تم حفظ النصيحة بنجاح") if action == "created" else _("تم تحديث النصيحة بنجاح")
            return JsonResponse({
                "success": True,
                "message": message,
                "tip_id": tip.pk
            })

        except SafetyTip.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Tip not found"},
                status=404
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": str(e)},
                status=500
            )


class SafetyTipDeleteView(LoginRequiredMixin, View):
    """Delete a safety tip"""

    def post(self, request, tip_id):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"},
                status=403
            )

        try:
            tip = SafetyTip.objects.get(id=tip_id)
            tip.delete()

            return JsonResponse({
                "success": True,
                "message": _("تم حذف النصيحة بنجاح")
            })

        except SafetyTip.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Tip not found"},
                status=404
            )


class SafetyTipBulkActionView(LoginRequiredMixin, View):
    """Bulk actions for safety tips"""

    def post(self, request):
        if not request.user.is_superuser:
            return JsonResponse(
                {"success": False, "message": "Permission denied"},
                status=403
            )

        action = request.POST.get('action')
        tip_ids = request.POST.getlist('tip_ids[]')

        try:
            tips_qs = SafetyTip.objects.filter(id__in=tip_ids)

            if action == 'activate':
                count = tips_qs.update(is_active=True)
                message = _(f"تم تفعيل {count} نصيحة")

            elif action == 'deactivate':
                count = tips_qs.update(is_active=False)
                message = _(f"تم إلغاء تفعيل {count} نصيحة")

            elif action == 'delete':
                count = tips_qs.count()
                tips_qs.delete()
                message = _(f"تم حذف {count} نصيحة")

            elif action == 'duplicate':
                count = 0
                for tip in tips_qs:
                    tip.pk = None
                    tip.title = f"{tip.title} (نسخة)"
                    tip.is_active = False
                    tip.save()
                    count += 1
                message = _(f"تم تكرار {count} نصيحة")

            else:
                return JsonResponse(
                    {"success": False, "message": "Invalid action"},
                    status=400
                )

            return JsonResponse({"success": True, "message": message})

        except Exception as e:
            return JsonResponse(
                {"success": False, "message": str(e)},
                status=500
            )


class SafetyTipPreviewView(LoginRequiredMixin, View):
    """Preview safety tips by category"""

    def get(self, request):
        if not request.user.is_superuser:
            messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
            return redirect("main:home")

        # Get filters
        tip_id = request.GET.get('tip_id')
        category_id = request.GET.get('category')

        # Get categories for dropdown
        categories = Category.objects.filter(parent__isnull=True)

        # Get tips to preview
        if tip_id:
            tips = SafetyTip.objects.filter(id=tip_id, is_active=True)
        elif category_id:
            try:
                # Validate category_id is a valid integer to prevent SQL injection attempts
                category_id = int(category_id)
                category = Category.objects.get(id=category_id)
                tips = SafetyTip.get_tips_for_category(category)
            except (ValueError, TypeError, Category.DoesNotExist):
                tips = SafetyTip.objects.filter(is_active=True).order_by('order')[:8]
        else:
            tips = SafetyTip.objects.filter(is_active=True).order_by('order')[:8]

        context = {
            'tips': tips,
            'categories': categories,
            'selected_category': category_id,
        }

        return render(request, "admin/safety_tip_preview.html", context)
