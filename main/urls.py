from django.urls import path

from . import views
from . import auth_views
from . import classifieds_views
from . import payment_views
from . import chatbot_views
from . import enhanced_views
from . import cart_wishlist_views
from . import chat_views
from django.contrib.auth import views as dj_auth_views


app_name = "main"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("social/", views.SocialMediaView.as_view(), name="social"),
    path("privacy/", views.PrivacyPolicyView.as_view(), name="privacy"),
    path("terms/", views.TermsConditionsView.as_view(), name="terms"),
    path(
        "login/",
        auth_views.CustomLoginView.as_view(),
        name="login",
    ),
    path(
        "register/",
        auth_views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "send-phone-code/",
        auth_views.send_phone_verification_code,
        name="send_phone_code",
    ),
    path(
        "verify-phone-code/",
        auth_views.verify_phone_code,
        name="verify_phone_code",
    ),
    path("logout/", auth_views.logout_view, name="logout"),
    path(
        "password_reset/",
        dj_auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        dj_auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        dj_auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        dj_auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
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
    # Ad Upgrade URLs
    path(
        "classifieds/<int:pk>/upgrade/",
        classifieds_views.AdUpgradeCheckoutView.as_view(),
        name="ad_upgrade_checkout",
    ),
    path(
        "classifieds/<int:pk>/upgrade/process/",
        classifieds_views.AdUpgradeProcessView.as_view(),
        name="ad_upgrade_process",
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
        classifieds_views.PackageListView.as_view(),
        name="packages_list",
    ),
    path(
        "classifieds/package/<int:package_id>/purchase/",
        classifieds_views.PackagePurchaseView.as_view(),
        name="package_purchase",
    ),
    # Admin Categories Management (AJAX endpoints)
    path(
        "admin/categories/save/",
        classifieds_views.CategorySaveView.as_view(),
        name="admin_category_save",
    ),
    path(
        "admin/categories/<int:category_id>/",
        classifieds_views.CategoryGetView.as_view(),
        name="admin_category_get",
    ),
    path(
        "admin/categories/<int:category_id>/delete/",
        views.admin_category_delete,
        name="admin_category_delete",
    ),
    path(
        "admin/categories/reorder/",
        views.admin_category_reorder,
        name="admin_category_reorder",
    ),
    path(
        "admin/categories/<int:category_id>/custom-fields/",
        views.AdminCategoryCustomFieldsView.as_view(),
        name="admin_category_custom_fields",
    ),
    path(
        "admin/custom-fields/",
        views.AdminCustomFieldsView.as_view(),
        name="admin_custom_fields",
    ),
    path(
        "admin/custom-fields/<int:field_id>/get/",
        views.AdminCustomFieldGetView.as_view(),
        name="admin_custom_field_get",
    ),
    path(
        "admin/custom-fields/save/",
        views.AdminCustomFieldSaveView.as_view(),
        name="admin_custom_field_save",
    ),
    path(
        "admin/custom-fields/<int:field_id>/delete/",
        views.AdminCustomFieldDeleteView.as_view(),
        name="admin_custom_field_delete",
    ),
    path(
        "admin/users/",
        views.AdminUsersManagementView.as_view(),
        name="admin_users",
    ),
    path(
        "admin/users/<int:user_id>/",
        views.admin_user_detail,
        name="admin_user_detail",
    ),
    path(
        "admin/users/<int:user_id>/update/",
        views.admin_user_update,
        name="admin_user_update",
    ),
    # TODO: Implement AdminPackagesView and AdminTransactionsView
    # path(
    #     "admin/packages/",
    #     views.AdminPackagesView.as_view(),
    #     name="admin_packages",
    # ),
    # path(
    #     "admin/transactions/",
    #     views.AdminTransactionsView.as_view(),
    #     name="admin_transactions",
    # ),
    path(
        "admin/ads/<int:ad_id>/toggle-hide/",
        classifieds_views.ToggleAdHideView.as_view(),
        name="toggle_ad_hide",
    ),
    path(
        "admin/ads/<int:ad_id>/enable-cart/",
        classifieds_views.EnableAdCartView.as_view(),
        name="enable_ad_cart",
    ),
    path(
        "admin/ads/<int:ad_id>/delete/",
        classifieds_views.DeleteAdView.as_view(),
        name="delete_ad",
    ),
    path(
        "admin/ads/<int:ad_id>/publisher/",
        views.ad_publisher_detail,
        name="ad_publisher_detail",
    ),
    path(
        "admin/users/<int:user_id>/action/",
        views.admin_user_action,
        name="admin_user_action",
    ),
    path(
        "compare/",
        views.ComparisonView.as_view(),
        name="compare_ads",
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
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
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
    # Mobile Verification URLs
    path(
        "ajax/send-mobile-verification/",
        views.send_mobile_verification,
        name="send_mobile_verification",
    ),
    path(
        "ajax/verify-mobile-otp/",
        views.verify_mobile_otp,
        name="verify_mobile_otp",
    ),
    # Payment URLs
    path(
        "payment/",
        payment_views.payment_page,
        name="payment_page",
    ),
    path(
        "payment/<int:package_id>/",
        payment_views.payment_page,
        name="payment_page_package",
    ),
    path(
        "payment/upgrade/<int:payment_id>/",
        payment_views.payment_page_upgrade,
        name="payment_page_upgrade",
    ),
    path(
        "payment/create/",
        payment_views.create_payment,
        name="create_payment",
    ),
    path(
        "payment/paypal/success/",
        payment_views.paypal_success,
        name="paypal_success",
    ),
    path(
        "payment/paypal/cancel/",
        payment_views.paypal_cancel,
        name="paypal_cancel",
    ),
    path(
        "payment/paymob/callback/",
        payment_views.paymob_callback,
        name="paymob_callback",
    ),
    path(
        "payment/success/<int:payment_id>/",
        payment_views.payment_success,
        name="payment_success",
    ),
    path(
        "payment/failed/",
        payment_views.payment_failed,
        name="payment_failed",
    ),
    path(
        "payment/history/",
        payment_views.payment_history,
        name="payment_history",
    ),
    # Chatbot URLs
    path(
        "chatbot/",
        chatbot_views.ChatbotView.as_view(),
        name="chatbot",
    ),
    path(
        "chatbot/message/",
        chatbot_views.chatbot_message,
        name="chatbot_message",
    ),
    path(
        "chatbot/rate/",
        chatbot_views.chatbot_rate,
        name="chatbot_rate",
    ),
    path(
        "chatbot/history/",
        chatbot_views.chatbot_history,
        name="chatbot_history",
    ),
    path(
        "chatbot/widget-data/",
        chatbot_views.chatbot_widget_data,
        name="chatbot_widget_data",
    ),
    path(
        "chatbot/admin/",
        chatbot_views.ChatbotAdminView.as_view(),
        name="chatbot_admin",
    ),
    path(
        "chatbot/manage/knowledge/",
        chatbot_views.manage_knowledge,
        name="manage_knowledge",
    ),
    path(
        "chatbot/manage/actions/",
        chatbot_views.manage_actions,
        name="manage_actions",
    ),
    # Admin Dashboard URLs
    path(
        "admin/dashboard/",  # This will be the main admin dashboard
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
        "admin/translations/",
        views.AdminTranslationsView.as_view(),
        name="admin_translations",
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
    # Admin Settings - Constance
    path(
        "admin/settings/constance/get/",
        views.admin_settings_constance_get,
        name="admin_settings_constance_get",
    ),
    path(
        "admin/settings/constance/save/",
        views.admin_settings_constance_save,
        name="admin_settings_constance_save",
    ),
    # Cart URLs
    path("api/cart/add/", cart_wishlist_views.add_to_cart, name="cart_add"),
    path("api/cart/remove/", cart_wishlist_views.remove_from_cart, name="cart_remove"),
    path(
        "api/cart/update-quantity/",
        cart_wishlist_views.update_cart_quantity,
        name="cart_update_quantity",
    ),
    path("api/cart/count/", cart_wishlist_views.get_cart_count, name="cart_count"),
    path("cart/", cart_wishlist_views.cart_view, name="cart_view"),
    # Wishlist URLs
    path("api/wishlist/add/", cart_wishlist_views.add_to_wishlist, name="wishlist_add"),
    path(
        "api/wishlist/remove/",
        cart_wishlist_views.remove_from_wishlist,
        name="wishlist_remove",
    ),
    path(
        "api/wishlist/toggle/",
        cart_wishlist_views.toggle_wishlist,
        name="wishlist_toggle",
    ),
    path(
        "api/wishlist/count/",
        cart_wishlist_views.get_wishlist_count,
        name="wishlist_count",
    ),
    path(
        "api/wishlist/status/",
        cart_wishlist_views.check_wishlist_status,
        name="wishlist_status",
    ),
    path("wishlist/", cart_wishlist_views.wishlist_view, name="wishlist_view"),
    # Chat URLs - User to User Messaging
    path("chat/", chat_views.chat_list, name="chat_list"),
    path("chat/room/<int:room_id>/", chat_views.chat_room, name="chat_room"),
    path("chat/room/", chat_views.chat_room, name="chat_room_new"),
    path(
        "chat/room/<int:room_id>/send/",
        chat_views.send_message,
        name="chat_send_message",
    ),
    path(
        "chat/room/<int:room_id>/messages/",
        chat_views.get_messages,
        name="chat_get_messages",
    ),
    path(
        "chat/room/<int:room_id>/mark-read/",
        chat_views.mark_read,
        name="chat_mark_read",
    ),
    path("chat/admin-panel/", chat_views.admin_chat_panel, name="admin_chat_panel"),
    # Chat URLs (Django Channels WebSocket endpoints - Legacy)
    path(
        "publisher/chats/",
        views.PublisherChatsView.as_view(),
        name="publisher_chats",
    ),
    path(
        "publisher/support/",
        views.PublisherSupportChatView.as_view(),
        name="publisher_support_chat",
    ),
    path(
        "admin/support-chats/",
        views.AdminSupportChatsView.as_view(),
        name="admin_support_chats",
    ),
    path(
        "chat/publisher/<int:ad_id>/",
        views.ChatWithPublisherView.as_view(),
        name="chat_with_publisher",
    ),
]
