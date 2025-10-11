from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # Country selection
    path("api/set-country/", views.set_country, name="set_country"),
    # Cart management
    path("api/cart/add/", views.add_to_cart, name="add_to_cart"),
    path("api/cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    # Wishlist management
    path("api/wishlist/add/", views.add_to_wishlist, name="add_to_wishlist"),
    path(
        "api/wishlist/remove/", views.remove_from_wishlist, name="remove_from_wishlist"
    ),
]
