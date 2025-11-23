from django.urls import path

from main import views
from main import cart_wishlist_views
from main import chatbot_views

urlpatterns = [
    # Country selection
    path("set-country/", views.set_country, name="set_country"),
    # Cart management
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    # Wishlist management
    path("wishlist/add/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/", views.remove_from_wishlist, name="remove_from_wishlist"),
    # Bulk ads fetch for guest wishlist
    path("ads/bulk/", cart_wishlist_views.get_bulk_ads, name="get_bulk_ads"),
    # Chatbot API
    path("chatbot/", chatbot_views.chatbot_message, name="api_chatbot"),
]
