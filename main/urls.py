from django.urls import path

from . import auth_views, classifieds_views, views
from . import enhanced_views

app_name = "main"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("login/", auth_views.CustomLoginView.as_view(), name="login"),
    path("register/", auth_views.RegisterView.as_view(), name="register"),
    path("logout/", auth_views.logout_view, name="logout"),
    # Temporary category detail URL (you can implement the view later)
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    # Subcategory detail URL
    path(
        "subcategory/<slug:slug>/",
        views.SubcategoryDetailView.as_view(),
        name="subcategory_detail",
    ),
    # Classified Ads URLs
    path(
        "classifieds/",
        classifieds_views.ClassifiedAdListView.as_view(),
        name="ad_list",
    ),
    path(
        "classifieds/my-ads/",
        classifieds_views.MyClassifiedAdsView.as_view(),
        name="my_ads",
    ),
    path(
        "classifieds/create/",
        classifieds_views.ClassifiedAdCreateView.as_view(),
        name="ad_create",
    ),
    path(
        "classifieds/<int:pk>/edit/",
        classifieds_views.ClassifiedAdUpdateView.as_view(),
        name="ad_update",
    ),
    path(
        "classifieds/create/success/<int:pk>/",
        classifieds_views.ClassifiedAdCreateSuccessView.as_view(),
        name="ad_create_success",
    ),
    path(
        "classifieds/<int:pk>/",
        classifieds_views.ClassifiedAdDetailView.as_view(),
        name="ad_detail",
    ),
    # Saved Searches URLs
    path(
        "classifieds/save-search/",
        classifieds_views.SaveSearchView.as_view(),
        name="save_search",
    ),
    path(
        "classifieds/saved-searches/",
        classifieds_views.UserSavedSearchesView.as_view(),
        name="saved_searches",
    ),
    path(
        "classifieds/saved-searches/<int:pk>/delete/",
        classifieds_views.DeleteSavedSearchView.as_view(),
        name="delete_saved_search",
    ),
    path(
        "classifieds/unsubscribe/<uuid:token>/",
        classifieds_views.UnsubscribeFromSearchView.as_view(),
        name="unsubscribe_from_search",
    ),
    # Notifications URL
    path(
        "notifications/",
        classifieds_views.NotificationListView.as_view(),
        name="notification_list",
    ),
    # AJAX endpoint for subcategories
    path(
        "ajax/subcategories/",
        views.get_subcategories,
        name="ajax_subcategories",
    ),
    # AJAX endpoint for category statistics
    path(
        "ajax/category-stats/",
        views.get_category_stats,
        name="ajax_category_stats",
    ),
    # AJAX endpoint for categories page filtering
    path(
        "ajax/filter-categories/",
        views.filter_categories_ajax,
        name="ajax_filter_categories",
    ),
    # Enhanced Classified Ads URLs
    path(
        "classifieds/enhanced/create/",
        views.enhanced_ad_create_view,
        name="enhanced_ad_create",
    ),
    path(
        "classifieds/creation-success/<int:ad_id>/",
        views.enhanced_ad_creation_success_view,
        name="ad_creation_success",
    ),
    path(
        "ajax/subcategories/<int:category_id>/",
        views.get_subcategories_ajax,
        name="ajax_get_subcategories",
    ),
    path(
        "classifieds/packages/",
        enhanced_views.packages_list,
        name="packages_list",
    ),
    path(
        "classifieds/reservations/",
        enhanced_views.reservation_management,
        name="reservation_management",
    ),
    # AJAX endpoints for enhanced features
    path(
        "ajax/get-custom-fields/",
        enhanced_views.get_custom_fields,
        name="ajax_get_custom_fields",
    ),
    path(
        "ajax/get-features/",
        enhanced_views.get_features,
        name="ajax_get_features",
    ),
    path(
        "ajax/calculate-features-price/",
        enhanced_views.calculate_features_price,
        name="ajax_calculate_features_price",
    ),
    path(
        "ajax/create-reservation/",
        enhanced_views.create_reservation,
        name="ajax_create_reservation",
    ),
    path(
        "ajax/activate-package/",
        enhanced_views.activate_package,
        name="ajax_activate_package",
    ),
    path(
        "ajax/reservation-details/<int:reservation_id>/",
        enhanced_views.reservation_details,
        name="ajax_reservation_details",
    ),
    path(
        "ajax/update-reservation-status/",
        enhanced_views.update_reservation_status,
        name="ajax_update_reservation_status",
    ),
    path(
        "ajax/delete-reservation/",
        enhanced_views.delete_reservation,
        name="ajax_delete_reservation",
    ),
    path(
        "ajax/send-reservation-notification/",
        enhanced_views.send_reservation_notification,
        name="ajax_send_reservation_notification",
    ),
    path(
        "ajax/add-reservation/",
        enhanced_views.add_reservation,
        name="ajax_add_reservation",
    ),
    path(
        "ajax/get-users/",
        enhanced_views.get_users,
        name="ajax_get_users",
    ),
    path(
        "ajax/get-ads/",
        enhanced_views.get_ads,
        name="ajax_get_ads",
    ),
    # Dashboard URLs
    path(
        "dashboard/",
        views.PublisherDashboardView.as_view(),
        name="dashboard",
    ),
    path(
        "dashboard/ad/<int:ad_id>/toggle-status/",
        views.dashboard_ad_toggle_status,
        name="dashboard_ad_toggle_status",
    ),
    path(
        "dashboard/ad/<int:ad_id>/delete/",
        views.dashboard_ad_delete,
        name="dashboard_ad_delete",
    ),
    path(
        "dashboard/ad/<int:ad_id>/details/",
        views.dashboard_get_ad_details,
        name="dashboard_ad_details",
    ),
    # Admin Dashboard URLs
    path(
        "admin/dashboard/",
        views.AdminDashboardView.as_view(),
        name="admin_dashboard",
    ),
    path(
        "admin/categories/",
        views.AdminCategoriesView.as_view(),
        name="admin_categories",
    ),
    path(
        "admin/ads/",
        views.AdminAdsManagementView.as_view(),
        name="admin_ads",
    ),
    path(
        "admin/settings/",
        views.AdminSettingsView.as_view(),
        name="admin_settings",
    ),
    path(
        "admin/payments/",
        views.AdminPaymentsView.as_view(),
        name="admin_payments",
    ),
    path(
        "admin/ads/tab/<str:tab>/",
        views.admin_get_ads_by_tab,
        name="admin_ads_by_tab",
    ),
    path(
        "admin/ads/<int:ad_id>/status/",
        views.admin_ad_status_change,
        name="admin_ad_status_change",
    ),
    path(
        "admin/ads/<int:ad_id>/delete/",
        views.admin_ad_delete,
        name="admin_ad_delete",
    ),
    # Admin Settings AJAX URLs
    path(
        "admin/settings/get/",
        views.admin_settings_get,
        name="admin_settings_get",
    ),
    path(
        "admin/settings/publishing/",
        views.admin_settings_publishing,
        name="admin_settings_publishing",
    ),
    path(
        "admin/settings/delivery/",
        views.admin_settings_delivery,
        name="admin_settings_delivery",
    ),
    path(
        "admin/settings/cart/",
        views.admin_settings_cart,
        name="admin_settings_cart",
    ),
    path(
        "admin/settings/notifications/",
        views.admin_settings_notifications,
        name="admin_settings_notifications",
    ),
]
