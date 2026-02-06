from django.urls import path, re_path

from .views import (
    BlogDetailView,
    BlogLikeView,
    BlogListView,
    get_cities,
    get_cities_by_id,
    payment_methods_config,
)

app_name = "content"

urlpatterns = [
    path("", BlogListView.as_view(), name="blog_list"),
    # Cities API endpoints
    path("api/cities/<str:country_code>/", get_cities, name="get_cities"),
    path(
        "api/countries/<int:country_id>/cities/",
        get_cities_by_id,
        name="get_cities_by_id",
    ),
    # Payment Methods Configuration (Admin only)
    path(
        "admin/payment-methods/",
        payment_methods_config,
        name="payment_methods_config",
    ),
    # Tag filter MUST come before blog detail to avoid conflicts (supports Arabic)
    re_path(
        r"^tag/(?P<tag_slug>[\w\-\u0600-\u06FF]+)/$",
        BlogListView.as_view(),
        name="blog_list_by_tag",
    ),
    # Category filter (supports Arabic)
    re_path(
        r"^category/(?P<category_slug>[\w\-\u0600-\u06FF]+)/$",
        BlogListView.as_view(),
        name="blog_list_by_category",
    ),
    # Like endpoint with specific path
    re_path(
        r"^(?P<slug>[\w\-\u0600-\u06FF]+)/like/$",
        BlogLikeView.as_view(),
        name="blog_like",
    ),
    # Blog detail - should be last
    re_path(
        r"^(?P<slug>[\w\-\u0600-\u06FF]+)/$",
        BlogDetailView.as_view(),
        name="blog_detail",
    ),
]
