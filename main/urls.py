from django.urls import path

from . import auth_views, classifieds_views, views

app_name = "main"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("login/", auth_views.login_view, name="login"),
    path("register/", auth_views.register_view, name="register"),
    path("logout/", auth_views.logout_view, name="logout"),
    # Temporary category detail URL (you can implement the view later)
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
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
]
