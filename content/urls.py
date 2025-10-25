from django.urls import path, re_path

from .views import BlogDetailView, BlogLikeView, BlogListView

app_name = "content"

urlpatterns = [
    path("", BlogListView.as_view(), name="blog_list"),
    re_path(
        r"^tag/(?P<tag_slug>[-\w]+)/$", BlogListView.as_view(), name="blog_list_by_tag"
    ),
    path("<slug:slug>/like/", BlogLikeView.as_view(), name="blog_like"),
    path("<slug:slug>/", BlogDetailView.as_view(), name="blog_detail"),
]
