from django.urls import path

from . import auth_views, views

app_name = "main"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("login/", auth_views.login_view, name="login"),
    path("register/", auth_views.register_view, name="register"),
    path("logout/", auth_views.logout_view, name="logout"),
]
