"""
Test script to verify cart and wishlist database persistence
Run this with: python manage.py shell < test_cart_persistence.py
"""

from django.contrib.auth import get_user_model
from main.models import Cart, CartItem, Wishlist, WishlistItem, ClassifiedAd

User = get_user_model()

print("\n" + "=" * 80)
print("CART AND WISHLIST PERSISTENCE TEST")
print("=" * 80)

# Get a test user (change username as needed)
try:
    user = User.objects.first()
    if not user:
        print("❌ No users found in database. Please create a user first.")
        exit()

    print(f"\n✅ Testing with user: {user.username} (ID: {user.id})")

    # Get or create cart
    cart, cart_created = Cart.objects.get_or_create(user=user)
    print(f"\n📦 Cart ID: {cart.id}")
    print(f"   Created new: {cart_created}")
    print(f"   Current items count: {cart.get_items_count()}")

    # Get or create wishlist
    wishlist, wishlist_created = Wishlist.objects.get_or_create(user=user)
    print(f"\n💝 Wishlist ID: {wishlist.id}")
    print(f"   Created new: {wishlist_created}")
    print(f"   Current items count: {wishlist.get_items_count()}")

    # Get a test ad
    test_ad = ClassifiedAd.objects.filter(status="active").first()
    if not test_ad:
        print("\n❌ No active ads found. Cannot test cart/wishlist items.")
        exit()

    print(f"\n📰 Test Ad: {test_ad.title} (ID: {test_ad.id})")

    # Test cart item creation
    print("\n" + "-" * 80)
    print("TESTING CART ITEM CREATION")
    print("-" * 80)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, ad=test_ad)

    print(f"✅ CartItem ID: {cart_item.id}")
    print(f"   Created new: {item_created}")
    print(f"   Quantity: {cart_item.quantity}")
    print(f"   Cart: {cart_item.cart_id}")
    print(f"   Ad: {cart_item.ad_id}")

    # Verify cart count
    cart_count = cart.get_items_count()
    print(f"\n📊 Cart items count after add: {cart_count}")

    # Query directly from database
    db_cart_items = CartItem.objects.filter(cart=cart)
    print(f"   Direct DB query count: {db_cart_items.count()}")
    print(f"   Items in DB:")
    for item in db_cart_items:
        print(f"      - CartItem #{item.id}: Ad #{item.ad_id} (Qty: {item.quantity})")

    # Test wishlist item creation
    print("\n" + "-" * 80)
    print("TESTING WISHLIST ITEM CREATION")
    print("-" * 80)

    # Get a different ad for wishlist
    wishlist_test_ad = (
        ClassifiedAd.objects.filter(status="active").exclude(id=test_ad.id).first()
    )
    if not wishlist_test_ad:
        wishlist_test_ad = test_ad  # Use same ad if no other available

    wishlist_item, wl_item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist, ad=wishlist_test_ad
    )

    print(f"✅ WishlistItem ID: {wishlist_item.id}")
    print(f"   Created new: {wl_item_created}")
    print(f"   Wishlist: {wishlist_item.wishlist_id}")
    print(f"   Ad: {wishlist_item.ad_id}")

    # Verify wishlist count
    wishlist_count = wishlist.get_items_count()
    print(f"\n📊 Wishlist items count after add: {wishlist_count}")

    # Query directly from database
    db_wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
    print(f"   Direct DB query count: {db_wishlist_items.count()}")
    print(f"   Items in DB:")
    for item in db_wishlist_items:
        print(f"      - WishlistItem #{item.id}: Ad #{item.ad_id}")

    print("\n" + "=" * 80)
    print("✅ DATABASE PERSISTENCE TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nIf items are showing here but not in the web interface after refresh,")
    print("the issue is likely with:")
    print("  1. JavaScript not correctly updating the UI")
    print("  2. Template tags not querying correctly")
    print("  3. Context processor not being called")
    print("\nCheck the browser console for AJAX response logs.")
    print("=" * 80 + "\n")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
