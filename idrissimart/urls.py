from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from main import cart_wishlist_views

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/", include("api.urls", namespace="api")),  # Mobile API
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # CKEditor 5 URLs
    # Cart & Wishlist APIs — outside i18n_patterns to prevent POST→GET redirect
    path("api/cart/add/", cart_wishlist_views.add_to_cart),
    path("api/cart/remove/", cart_wishlist_views.remove_from_cart),
    path("api/cart/update-quantity/", cart_wishlist_views.update_cart_quantity),
    path("api/cart/count/", cart_wishlist_views.get_cart_count_view),
    path("api/wishlist/add/", cart_wishlist_views.add_to_wishlist),
    path("api/wishlist/remove/", cart_wishlist_views.remove_from_wishlist),
    path("api/wishlist/toggle/", cart_wishlist_views.toggle_wishlist),
    path("api/wishlist/count/", cart_wishlist_views.get_wishlist_count),
    path("api/wishlist/status/", cart_wishlist_views.check_wishlist_status),
]

urlpatterns += i18n_patterns(
    path("", include("main.urls", namespace="main")),  # Your main app
    path("super-admin/", admin.site.urls),
    path("super-admin/translations/", include("rosetta.urls")),  # Translation manager
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
