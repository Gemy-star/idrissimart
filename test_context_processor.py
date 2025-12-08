"""
Test to verify context processor is working
Run with: python manage.py shell
Then paste this code
"""

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from main.context_processors import cart_wishlist_counts
from main.models import Cart, Wishlist, CartItem, WishlistItem, ClassifiedAd

User = get_user_model()

# Get a user
user = User.objects.first()
if not user:
    print("❌ No users found")
    exit()

print(f"\n✅ Testing context processor for user: {user.username}")

# Create a mock request
factory = RequestFactory()
request = factory.get("/")
request.user = user

# Call context processor
context = cart_wishlist_counts(request)

print(f"\n📊 Context Processor Results:")
print(f"   cart_count: {context['cart_count']}")
print(f"   wishlist_count: {context['wishlist_count']}")

# Check actual database
cart, _ = Cart.objects.get_or_create(user=user)
wishlist, _ = Wishlist.objects.get_or_create(user=user)

print(f"\n🔍 Direct Database Query:")
print(f"   Cart items: {cart.get_items_count()}")
print(f"   Wishlist items: {wishlist.get_items_count()}")

# List items
print(f"\n📦 Cart Items:")
for item in CartItem.objects.filter(cart=cart):
    print(f"   - Ad #{item.ad_id}: {item.ad.title} (Qty: {item.quantity})")

print(f"\n💝 Wishlist Items:")
for item in WishlistItem.objects.filter(wishlist=wishlist):
    print(f"   - Ad #{item.ad_id}: {item.ad.title}")

if context["cart_count"] != cart.get_items_count():
    print("\n❌ WARNING: Context processor count doesn't match database!")
else:
    print("\n✅ Context processor is working correctly!")
