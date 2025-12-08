# Cart & Wishlist System - Complete Reimplementation

## Overview
Complete rewrite of the cart and wishlist functionality with clean, maintainable code and proper separation of concerns.

## Changes Made

### 1. JavaScript - `static/js/cart-wishlist.js`
**Completely reimplemented with clean, modern code:**

#### Core Functions:
- `isUserAuthenticated()` - Check user authentication status
- `getCookie(name)` - Get CSRF token from cookies
- `updateHeaderCount(type, count)` - Update cart/wishlist count in header with animation
- `showNotification(message, type)` - Display toast notifications

#### Cart Functions:
- `addToCart(itemId, itemName)` - Add item to cart via AJAX
- `removeFromCart(itemId, itemName)` - Remove item from cart via AJAX
- `toggleCartCard(adId, button, itemName, price)` - Toggle cart button state

#### Wishlist Functions:
- `addToWishlist(itemId, itemName)` - Add item to wishlist via AJAX
- `removeFromWishlist(itemId, itemName)` - Remove item from wishlist via AJAX
- `toggleWishlistCard(adId, button, itemName)` - Toggle wishlist button state

#### Key Features:
✅ Authentication check before all operations
✅ Automatic redirect to login for unauthenticated users
✅ Count updates in header after each operation
✅ Custom events dispatched (`cartUpdated`, `wishlistUpdated`)
✅ Auto-refresh cart/wishlist pages when items change
✅ Proper error handling with user-friendly messages
✅ All functions exposed globally via `window` object

### 2. Template - `templates/partials/_ad_card_component.html`

#### Wishlist Button:
```html
<button class="ad-wishlist-btn wishlist-btn-card quick-action-btn {% if ad_in_wishlist %}active{% endif %}"
        onclick="toggleWishlistCard({{ ad.id }}, this, '{{ ad.title|escapejs }}')">
    <i class="{% if ad_in_wishlist %}fas{% else %}far{% endif %} fa-heart"></i>
</button>
```

#### Cart Button:
```html
<button class="ad-cart-btn cart-btn-card quick-action-btn {% if ad_in_cart %}active{% endif %}"
        onclick="toggleCartCard({{ ad.id }}, this, '{{ ad.title|escapejs }}', {{ ad.price|default:0 }})">
    <i class="fas fa-shopping-cart"></i>
</button>
```

**Key Changes:**
- Removed duplicate `data-in-cart` and `data-in-wishlist` attributes
- Simplified onclick handlers with proper parameters
- Icons change based on state (fas/far for heart, active class for cart)
- Proper Django template tag usage with `escapejs` filter

### 3. Base Template - `templates/base.html`

**Removed duplicates:**
- ❌ Removed duplicate `toggleWishlistCard` function
- ❌ Removed `toggleWishlistServerGlobal`
- ❌ Removed `toggleWishlistGuestGlobal`
- ❌ Removed `updateWishlistButtonGlobal`
- ❌ Removed duplicate `updateHeaderWishlistCount`
- ❌ Removed duplicate `updateHeaderCartCount`

**Kept:**
- ✅ `getCookie()` for CSRF token (used by other functions)
- ✅ Toast notification system
- ✅ Owner ad actions functions
- ✅ Newsletter subscription
- ✅ Initialization logging

**Single Source of Truth:**
All cart/wishlist logic now lives in `cart-wishlist.js` only.

### 4. Backend - No Changes Needed

The backend views are already correct:
- `add_to_cart` - Creates/updates CartItem, returns count
- `remove_from_cart` - Deletes CartItem, returns count
- `add_to_wishlist` - Creates WishlistItem, returns count
- `remove_from_wishlist` - Deletes WishlistItem, returns count

All views have proper logging already added.

### 5. Context Processor - Already Working

`main.context_processors.cart_wishlist_counts` provides:
- `cart_count` - Current cart item count
- `wishlist_count` - Current wishlist item count

These are available in all templates.

### 6. Template Tags - Already Working

- `{% is_in_cart ad.id as ad_in_cart %}`
- `{% is_in_wishlist ad.id as ad_in_wishlist %}`

These query the database to check item status.

## How It Works

### Adding to Cart:

1. User clicks cart button on ad card
2. `toggleCartCard(adId, button, itemName, price)` is called
3. Checks if item is already in cart (button has `active` class)
4. If not in cart:
   - Calls `addToCart(adId, itemName)`
   - Checks authentication → redirects to login if not authenticated
   - Sends AJAX POST to `/api/cart/add/`
   - Backend creates CartItem in database
   - Returns JSON with `{success: true, cart_count: X}`
   - Updates header count via `updateHeaderCount('cart', count)`
   - Shows success notification
   - Adds `active` class to button
   - Changes button title to "في السلة"
5. If already in cart:
   - Calls `removeFromCart(adId, itemName)`
   - Same flow but removes item
   - Removes `active` class
   - Changes button title to "إضافة للسلة"

### Adding to Wishlist:

1. User clicks heart icon on ad card
2. `toggleWishlistCard(adId, button, itemName)` is called
3. Checks if item is already in wishlist (button has `active` class)
4. If not in wishlist:
   - Calls `addToWishlist(adId, itemName)`
   - Checks authentication → redirects to login if not authenticated
   - Sends AJAX POST to `/api/wishlist/add/`
   - Backend creates WishlistItem in database
   - Returns JSON with `{success: true, wishlist_count: X}`
   - Updates header count via `updateHeaderCount('wishlist', count)`
   - Shows success notification
   - Adds `active` class to button
   - Changes icon from `far fa-heart` to `fas fa-heart` (filled)
   - Changes button title to "في المفضلة"
5. If already in wishlist:
   - Calls `removeFromWishlist(adId, itemName)`
   - Same flow but removes item
   - Removes `active` class
   - Changes icon from `fas fa-heart` to `far fa-heart` (outline)
   - Changes button title to "إضافة للمفضلة"

### Page Refresh:

1. User refreshes page
2. Context processor runs: `cart_wishlist_counts(request)`
3. Queries database for user's cart/wishlist items
4. Returns counts to template context
5. Header displays: `{{ cart_count }}` and `{{ wishlist_count }}`
6. Template tags run: `{% is_in_cart ad.id %}` and `{% is_in_wishlist ad.id %}`
7. Buttons render with correct state:
   - If in cart/wishlist → `active` class added
   - If in wishlist → `fas fa-heart` icon
   - If not in wishlist → `far fa-heart` icon

## Testing

### Test 1: Add to Cart
1. Login to your account
2. Go to homepage or category page
3. Find an ad with cart enabled
4. Click the cart icon
5. ✅ Should see success notification
6. ✅ Cart count in header should increase
7. ✅ Button should become active
8. Refresh page (F5)
9. ✅ Cart count should stay the same
10. ✅ Button should still be active

### Test 2: Remove from Cart
1. Click the active cart button
2. ✅ Should see removal notification
3. ✅ Cart count should decrease
4. ✅ Button should become inactive
5. Refresh page
6. ✅ Cart count should stay decreased
7. ✅ Button should be inactive

### Test 3: Add to Wishlist
1. Click the heart icon (outline)
2. ✅ Should see success notification
3. ✅ Wishlist count should increase
4. ✅ Heart should become filled (solid)
5. ✅ Button should have active class
6. Refresh page
7. ✅ Wishlist count should stay the same
8. ✅ Heart should still be filled

### Test 4: Remove from Wishlist
1. Click the filled heart icon
2. ✅ Should see removal notification
3. ✅ Wishlist count should decrease
4. ✅ Heart should become outline
5. Refresh page
6. ✅ Wishlist count should stay decreased
7. ✅ Heart should be outline

### Test 5: Unauthenticated User
1. Logout
2. Try to add to cart/wishlist
3. ✅ Should see "يجب تسجيل الدخول" error
4. ✅ Should redirect to login page after 1.5 seconds

### Test 6: Multiple Items
1. Login
2. Add 3 different items to cart
3. ✅ Cart count should show 3
4. Add 2 items to wishlist
5. ✅ Wishlist count should show 2
6. Refresh page
7. ✅ Both counts should persist

## Browser Console Logs

When system is working correctly, you should see:

```
[Cart/Wishlist] System initialized
[Cart/Wishlist] User authenticated: true
[Cart/Wishlist] Cart count: 0
[Cart/Wishlist] Wishlist count: 0
```

When adding to cart:
```
Cart updated: {action: 'add', itemId: '24', count: 1}
```

When adding to wishlist:
```
Wishlist updated: {action: 'add', itemId: '24', count: 1}
```

## Files Modified

1. ✅ `static/js/cart-wishlist.js` - Complete rewrite
2. ✅ `templates/partials/_ad_card_component.html` - Simplified button handlers
3. ✅ `templates/base.html` - Removed duplicates, cleaned up
4. ℹ️ `main/cart_wishlist_views.py` - Already has debug logging
5. ℹ️ `main/context_processors.py` - Already has debug logging
6. ℹ️ `main/templatetags/idrissimart_tags.py` - Already working

## Architecture

```
User Action (Click button)
    ↓
JavaScript Function (toggleCartCard/toggleWishlistCard)
    ↓
Authentication Check
    ↓
AJAX Request to Backend (/api/cart/add/, etc.)
    ↓
Django View (add_to_cart, add_to_wishlist)
    ↓
Database Operation (CartItem.objects.get_or_create)
    ↓
JSON Response {success: true, count: X}
    ↓
Update UI (header count, button state, notification)
    ↓
Dispatch Custom Event (for other listeners)

On Page Refresh:
    ↓
Context Processor (cart_wishlist_counts)
    ↓
Query Database (Cart.get_items_count())
    ↓
Template Context {cart_count: X, wishlist_count: Y}
    ↓
Template Tags (is_in_cart, is_in_wishlist)
    ↓
Render Buttons with Correct State
```

## Key Improvements

1. **Single Source of Truth** - All logic in cart-wishlist.js
2. **No Duplication** - Removed all duplicate functions
3. **Clean Code** - Modern async/await, clear function names
4. **Proper Error Handling** - Try/catch with user feedback
5. **Authentication First** - Always check before operations
6. **Event System** - Custom events for extensibility
7. **Auto Refresh** - Cart/wishlist pages reload on changes
8. **Consistent Naming** - All functions follow same pattern
9. **Global Access** - Functions available via window object
10. **Database Persistence** - Everything saved to DB, survives refresh

## Troubleshooting

If items still don't persist after refresh:

1. **Check Console** - Should show initialization logs
2. **Check Network Tab** - AJAX should return 200 with JSON
3. **Check Django Logs** - Should show database operations
4. **Clear Browser Cache** - Hard refresh with Ctrl+F5
5. **Check Database** - Run: `python manage.py shell < test_cart_persistence.py`
6. **Check Authentication** - Console should show `User authenticated: true`
7. **Check Context Processor** - Verify it's in settings TEMPLATES
8. **Check Template Tags** - Verify `{% load idrissimart_tags %}`

## Success Criteria

✅ Add to cart/wishlist works
✅ Remove from cart/wishlist works
✅ Counts update immediately
✅ Counts persist after refresh
✅ Button states persist after refresh
✅ Unauthenticated users redirected to login
✅ Notifications show for all actions
✅ No console errors
✅ No duplicate functions
✅ Clean, maintainable code
