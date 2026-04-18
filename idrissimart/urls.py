from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import include, path
from main import cart_wishlist_views
from main import views as main_views

# Sort models alphabetically within each app in the admin sidebar
_original_get_app_list = AdminSite.get_app_list


def _sorted_get_app_list(self, request, app_label=None):
    app_list = _original_get_app_list(self, request, app_label)
    for app in app_list:
        app["models"].sort(key=lambda m: m["name"].lower())
    return app_list


AdminSite.get_app_list = _sorted_get_app_list

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    # Cart & Wishlist APIs — BEFORE api/ include to avoid DRF router conflict
    # (DRF router matches wishlist/{pk}/ with pk="add" → 405 if placed after)
    path("api/category-price/<int:category_id>/", main_views.get_category_price_api, name="api_category_price"),
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
