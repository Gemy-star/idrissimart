from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from main import cart_wishlist_views
from main import views as main_views
from main import paid_ad_views
from main.sitemaps import sitemaps

# Sort models alphabetically within each app in the admin sidebar
_original_get_app_list = AdminSite.get_app_list


def _sorted_get_app_list(self, request, app_label=None):
    app_list = _original_get_app_list(self, request, app_label)
    for app in app_list:
        app["models"].sort(key=lambda m: m["name"].lower())
    return app_list


AdminSite.get_app_list = _sorted_get_app_list


# Inject stats into the Django admin index page
_original_index = AdminSite.index


def _stats_index(self, request, extra_context=None):
    extra_context = extra_context or {}
    try:
        from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        from main.models import ClassifiedAd, User

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        # Headline stats
        extra_context["idx_total_ads"] = ClassifiedAd.objects.count()
        extra_context["idx_pending_ads"] = ClassifiedAd.objects.filter(status="pending").count()
        extra_context["idx_active_ads"] = ClassifiedAd.objects.filter(status="active").count()
        extra_context["idx_total_users"] = User.objects.count()
        extra_context["idx_new_users_today"] = User.objects.filter(date_joined__date=today).count()
        extra_context["idx_new_ads_today"] = ClassifiedAd.objects.filter(created_at__date=today).count()

        # Ads-by-status for doughnut chart (JSON)
        import json
        ads_by_status = list(
            ClassifiedAd.objects.values("status")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")
        )
        extra_context["idx_ads_chart_labels"] = json.dumps([r["status"] for r in ads_by_status])
        extra_context["idx_ads_chart_data"] = json.dumps([r["cnt"] for r in ads_by_status])

        # Daily new ads last 7 days for line chart
        daily_ads = []
        daily_labels = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            daily_labels.append(str(d))
            daily_ads.append(ClassifiedAd.objects.filter(created_at__date=d).count())
        extra_context["idx_daily_labels"] = json.dumps(daily_labels)
        extra_context["idx_daily_ads"] = json.dumps(daily_ads)

        # Recent log entries — last 15, with readable action labels
        action_labels = {ADDITION: "أضاف", CHANGE: "عدّل", DELETION: "حذف"}
        action_colors = {ADDITION: "success", CHANGE: "warning", DELETION: "danger"}
        recent_logs = LogEntry.objects.select_related("user", "content_type").order_by("-action_time")[:15]
        extra_context["idx_recent_logs"] = [
            {
                "time": log.action_time,
                "user": log.user.get_full_name() or log.user.username,
                "action": action_labels.get(log.action_flag, "عملية"),
                "color": action_colors.get(log.action_flag, "secondary"),
                "model": (
                    log.content_type.model_class()._meta.verbose_name
                    if log.content_type.model_class()
                    else log.content_type.model
                ),
                "obj": log.object_repr,
                "url": log.get_admin_url() if not log.is_deletion else None,
            }
            for log in recent_logs
        ]
    except Exception:
        pass
    return _original_index(self, request, extra_context)


AdminSite.index = _stats_index

urlpatterns = [
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("i18n/", include("django.conf.urls.i18n")),
    # Cart & Wishlist APIs — BEFORE api/ include to avoid DRF router conflict
    # (DRF router matches wishlist/{pk}/ with pk="add" → 405 if placed after)
    path("api/category-price/<int:category_id>/", main_views.get_category_price_api, name="api_category_price"),
    path("api/admin/categories/", main_views.admin_category_api, name="api_admin_categories"),
    path("api/cart/add/", cart_wishlist_views.add_to_cart),
    path("api/cart/remove/", cart_wishlist_views.remove_from_cart),
    path("api/cart/update-quantity/", cart_wishlist_views.update_cart_quantity),
    path("api/cart/clear/", cart_wishlist_views.clear_cart),
    path("api/cart/count/", cart_wishlist_views.get_cart_count_view),
    path("api/wishlist/add/", cart_wishlist_views.add_to_wishlist),
    path("api/wishlist/remove/", cart_wishlist_views.remove_from_wishlist),
    path("api/wishlist/toggle/", cart_wishlist_views.toggle_wishlist),
    path("api/wishlist/count/", cart_wishlist_views.get_wishlist_count),
    path("api/wishlist/status/", cart_wishlist_views.check_wishlist_status),
    path("api/wishlist/clear/", cart_wishlist_views.clear_wishlist),
    # Country selection (no language prefix — JS fetches /api/set-country/ directly)
    path("api/set-country/", main_views.set_country, name="set_country"),
    # Paid ad tracking (no language prefix — templates fetch /api/paid-ads/{id}/view|click/)
    path("api/paid-ads/<int:ad_id>/view/", paid_ad_views.PaidAdViewTrackingView.as_view(), name="paid_ad_view_tracking"),
    path("api/paid-ads/<int:ad_id>/click/", paid_ad_views.PaidAdClickTrackingView.as_view(), name="paid_ad_click_tracking"),
    path("api/paid-ads/category/<int:category_id>/", paid_ad_views.get_category_paid_ads, name="get_category_paid_ads"),
    path("api/", include("api.urls", namespace="api")),  # Mobile API
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # CKEditor 5 URLs
]

urlpatterns += [
    # Rosetta MUST come before admin.site.urls to avoid catch_all_view intercepting it
    path("super-admin/translations/", include("rosetta.urls")),
    path("super-admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("", include("main.urls", namespace="main")),  # Your main app
    path("content/", include("content.urls", namespace="content")),  # Your content app
)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

# Custom error handlers
handler404 = 'main.views.custom_404'
handler500 = 'main.views.custom_500'
