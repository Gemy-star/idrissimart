# Cart and Wishlist Database Handling

## Overview
This document explains how cart and wishlist items are stored and synchronized between the database and frontend in the IdrissiMart application.

## Database Structure

### 1. Cart System

#### Cart Model (`carts` table)
```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```
- **One-to-One relationship**: Each user has exactly one cart
- **Auto-created**: Cart is created automatically when user first adds an item
- **Persistent**: Cart persists across sessions

#### CartItem Model (`cart_items` table)
```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    ad = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["cart", "ad"]]
```
- **Unique constraint**: One ad can only appear once per cart
- **Quantity tracking**: Supports multiple quantities of the same item
- **Timestamp**: Tracks when item was added

### 2. Wishlist System

#### Wishlist Model (`wishlists` table)
```python
class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```
- **One-to-One relationship**: Each user has exactly one wishlist
- **Auto-created**: Wishlist is created when user first adds an item
- **Persistent**: Wishlist persists across sessions

#### WishlistItem Model (`wishlist_items` table)
```python
class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    ad = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["wishlist", "ad"]]
```
- **Unique constraint**: One ad can only appear once per wishlist
- **No quantity**: Wishlist doesn't support quantities
- **Timestamp**: Tracks when item was added

## Backend API Endpoints

### Cart Endpoints

#### 1. Add to Cart
```
POST /api/cart/add/
Parameters: item_id (ad ID)
```
**Process:**
1. Check user authentication
2. Verify ad exists and is active
3. Check if cart is enabled for this ad
4. Get or create user's cart
5. Get or create CartItem (if exists, increment quantity)
6. Return success with updated cart count

**Database Operations:**
```python
cart, created = Cart.objects.get_or_create(user=request.user)
cart_item, created = CartItem.objects.get_or_create(cart=cart, ad=ad)
if not created:
    cart_item.quantity += 1
    cart_item.save()
```

#### 2. Remove from Cart
```
POST /api/cart/remove/
Parameters: item_id (ad ID)
```
**Process:**
1. Get user's cart
2. Find CartItem
3. Delete CartItem
4. Return success with updated cart count

**Database Operations:**
```python
cart = get_or_create_cart(request.user)
cart_item = CartItem.objects.get(cart=cart, ad_id=ad_id)
cart_item.delete()
```

### Wishlist Endpoints

#### 1. Add to Wishlist
```
POST /api/wishlist/add/
Parameters: item_id (ad ID)
```
**Process:**
1. Check user authentication
2. Verify ad exists and is active
3. Get or create user's wishlist
4. Create WishlistItem (IntegrityError if already exists)
5. Return success with updated wishlist count

**Database Operations:**
```python
wishlist, created = Wishlist.objects.get_or_create(user=request.user)
try:
    wishlist_item = WishlistItem.objects.create(wishlist=wishlist, ad=ad)
except IntegrityError:
    # Item already in wishlist
    return error response
```

#### 2. Remove from Wishlist
```
POST /api/wishlist/remove/
Parameters: item_id (ad ID)
```
**Process:**
1. Get user's wishlist
2. Find WishlistItem
3. Delete WishlistItem
4. Return success with updated wishlist count

**Database Operations:**
```python
wishlist = get_or_create_wishlist(request.user)
wishlist_item = WishlistItem.objects.get(wishlist=wishlist, ad_id=ad_id)
wishlist_item.delete()
```

## Frontend-Backend Synchronization

### 1. Initial Page Load

**Template Tags Check Database:**
```django
{% load idrissimart_tags %}
{% is_in_cart ad.id as ad_in_cart %}
{% is_in_wishlist ad.id as ad_in_wishlist %}
```

**These tags query the database:**
```python
# is_in_cart
cart, _ = Cart.objects.get_or_create(user=request.user)
return CartItem.objects.filter(cart=cart, ad_id=ad_id).exists()

# is_in_wishlist
wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
return WishlistItem.objects.filter(wishlist=wishlist, ad_id=ad_id).exists()
```

**Rendered HTML:**
```html
<!-- Cart button with active class if in DB -->
<button class="cart-btn-card {% if ad_in_cart %}active{% endif %}"
        data-ad-id="{{ ad.id }}"
        onclick="toggleCartCard({{ ad.id }}, this)">
    <i class="fas fa-shopping-cart"></i>
</button>

<!-- Wishlist button with active class and fas icon if in DB -->
<button class="wishlist-btn-card {% if ad_in_wishlist %}active{% endif %}"
        data-ad-id="{{ ad.id }}"
        onclick="toggleWishlistCard({{ ad.id }}, this)">
    <i class="{% if ad_in_wishlist %}fas{% else %}far{% endif %} fa-heart"></i>
</button>
```

### 2. User Actions (Add/Remove)

**Frontend JavaScript Flow:**
```javascript
// User clicks cart button
async function toggleCartCard(adId, button) {
    const isInCart = button.classList.contains('active');

    if (isInCart) {
        // Remove from cart
        const result = await window.removeFromCart(adId);
        if (result.success) {
            button.classList.remove('active');
            // Database: CartItem deleted
        }
    } else {
        // Add to cart
        const result = await window.addToCart(adId);
        if (result.success) {
            button.classList.add('active');
            // Database: CartItem created or quantity incremented
        }
    }
}
```

**Backend Database Operations:**
```python
# Add to Cart
def add_to_cart(request):
    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, ad=ad)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    # Database now contains: CartItem(cart=cart, ad=ad, quantity=n)

# Remove from Cart
def remove_from_cart(request):
    cart = get_or_create_cart(request.user)
    cart_item = CartItem.objects.get(cart=cart, ad_id=ad_id)
    cart_item.delete()
    # Database now: CartItem no longer exists
```

### 3. Header Count Updates

**JavaScript updates all count badges:**
```javascript
function updateHeaderCount(type, count) {
    const selectors = {
        'cart': '.cart-count',
        'wishlist': '.wishlist-count'
    };

    const elements = document.querySelectorAll(selectors[type]);
    elements.forEach(element => {
        element.textContent = count;  // Updates from DB response
    });
}
```

**Backend returns count from database:**
```python
# Cart count
cart.get_items_count()  # Returns cart.items.count()

# Wishlist count
wishlist.get_items_count()  # Returns wishlist.items.count()
```

### 4. Cross-Page Synchronization

**Global Events Keep All Instances in Sync:**
```javascript
// When cart updated, notify all listeners
document.dispatchEvent(new CustomEvent('cartUpdated', {
    detail: { action: 'add', itemId: adId, count: cart_count }
}));

// All cart buttons for this ad update
document.querySelectorAll(`[data-ad-id="${adId}"].cart-btn-card`).forEach(btn => {
    btn.classList.add('active');  // Reflects DB state
});
```

### 5. Page Reload Ensures Consistency

**On specific pages, reload to resync with DB:**
```javascript
document.addEventListener('cartUpdated', (e) => {
    // If on cart page, reload to show updated DB state
    if (window.location.pathname.includes('/cart/')) {
        location.reload();  // Re-renders with fresh DB query
    }
});
```

## Data Flow Diagram

```
User Action (Click Add to Cart)
        ↓
JavaScript (toggleCartCard)
        ↓
AJAX Request (/api/cart/add/)
        ↓
Django View (add_to_cart)
        ↓
Database Operation (CartItem.objects.create or update)
        ↓
JSON Response {success: true, cart_count: 5}
        ↓
JavaScript Updates UI (button.classList.add('active'))
        ↓
Event Dispatched (cartUpdated)
        ↓
Header Count Updated (from DB response)
        ↓
All Instances Synced (via event listeners)
```

## Key Features

### 1. Automatic Cart/Wishlist Creation
```python
cart, created = Cart.objects.get_or_create(user=request.user)
```
- User doesn't need to explicitly create cart/wishlist
- Created on first add action
- Persists permanently

### 2. Duplicate Prevention
```python
class Meta:
    unique_together = [["cart", "ad"]]
```
- Database constraint prevents duplicate entries
- Frontend handles gracefully with quantity increment (cart)
- Frontend shows "already in wishlist" message (wishlist)

### 3. Cascade Deletion
```python
cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
```
- If user deleted → cart deleted → all cart items deleted
- If ad deleted → all cart/wishlist items for that ad deleted
- Maintains database integrity

### 4. Authentication Required
```python
@login_required
@require_POST
def add_to_cart(request):
```
- All cart/wishlist operations require authentication
- Guest users redirected to login
- No session-based cart (only database)

## Testing Cart/Wishlist State

### Check Current State in Database
```python
# Django Shell
from main.models import Cart, CartItem, Wishlist, WishlistItem
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='testuser')

# Check cart
cart = Cart.objects.get(user=user)
cart_items = CartItem.objects.filter(cart=cart)
for item in cart_items:
    print(f"Ad: {item.ad.title}, Quantity: {item.quantity}")

# Check wishlist
wishlist = Wishlist.objects.get(user=user)
wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
for item in wishlist_items:
    print(f"Ad: {item.ad.title}")
```

### Verify Frontend Matches Database
1. Open browser
2. Check button states (active class)
3. Compare with database query
4. Should match exactly

## Common Issues and Solutions

### Issue: Button shows "active" but item not in database
**Solution:**
- Check template tag is called correctly
- Verify user is authenticated
- Check database constraints

### Issue: Database has item but button not active
**Solution:**
- Clear browser cache
- Check template rendering
- Verify JavaScript loaded
- Call syncButtonStates() manually

### Issue: Count mismatch between header and database
**Solution:**
- Check updateHeaderCount() is called
- Verify cart_count in API response
- Reload page to resync

### Issue: Adding same item multiple times
**Solution:**
- For cart: Quantity incremented (correct behavior)
- For wishlist: IntegrityError caught, shows message
- Both prevent duplicates at database level

## Best Practices

1. **Always use global functions** from cart-wishlist.js
2. **Never bypass database** - always use API endpoints
3. **Trust the database** as source of truth
4. **Reload on critical pages** (cart, wishlist) to ensure sync
5. **Use template tags** for initial state on page load
6. **Handle errors gracefully** - show user-friendly messages
7. **Keep counts updated** - use updateHeaderCount()
8. **Dispatch events** - allow cross-component updates

## Summary

The cart and wishlist system maintains perfect synchronization between frontend and database through:

1. **Database Models** - Single source of truth
2. **Template Tags** - Server-side rendering with DB queries
3. **API Endpoints** - All mutations go through backend
4. **JavaScript Events** - Keep all UI instances in sync
5. **Global Functions** - Centralized logic in cart-wishlist.js
6. **Unique Constraints** - Database-level duplicate prevention
7. **Cascade Rules** - Automatic cleanup on deletions

This ensures that regardless of where the user interacts with cart/wishlist (ad cards, detail pages, cart page, wishlist page), the state is always consistent and persisted to the database.
