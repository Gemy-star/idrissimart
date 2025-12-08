# Cart and Wishlist Persistence Debugging Guide

## Problem Description
Items can be added to cart/wishlist (count updates), but they disappear after page refresh. This suggests a database persistence issue.

## What Has Been Fixed

### 1. Frontend Enhancements (JavaScript)
**File**: `static/js/cart-wishlist.js`

Added comprehensive logging to all cart/wishlist functions:
- `addToCart()` - Logs item ID, response status, full response data
- `removeFromCart()` - Similar logging
- `addToWishlist()` - Logs item ID, response status, full response data
- `removeFromWishlist()` - Similar logging
- Changed unauthenticated errors from 'warning' to 'error'
- Added auto-redirect to login page for unauthenticated users

### 2. Backend Enhancements (Django)
**File**: `main/cart_wishlist_views.py`

Added debug logging to views:
- `add_to_cart()` - Logs user, ad ID, cart creation, item creation, quantity updates, final count
- `add_to_wishlist()` - Logs user, ad ID, wishlist creation, item creation, final count
- All database operations are now traced

**File**: `main/context_processors.py`

Added logging to context processor:
- Logs cart/wishlist retrieval on every page load
- Shows counts being passed to templates
- Catches and logs any errors

### 3. Database Test Script
**File**: `test_cart_persistence.py`

Created a standalone test script to verify database persistence independently from web interface.

## How to Debug

### Step 1: Test Database Persistence Directly

Run the test script to verify database is working:

```powershell
python manage.py shell < test_cart_persistence.py
```

**Expected Output:**
- ✅ Shows user, cart, and wishlist IDs
- ✅ Creates test cart and wishlist items
- ✅ Shows item counts from database
- ✅ Confirms items are actually saved

**If this fails:** Database configuration issue or model constraint problem.

### Step 2: Check Django Server Logs

Start/restart the development server and watch the console:

```powershell
python manage.py runserver
```

**When adding item to cart, you should see:**
```
[ADD_TO_CART] User: username, Authenticated: True
[ADD_TO_CART] Ad ID: 123
[ADD_TO_CART] Cart: 45, User: 67
[ADD_TO_CART] CartItem: 89, Created: True, Quantity: 1
[ADD_TO_CART] Created new cart item
[ADD_TO_CART] Final cart count: 1
```

**If you don't see these logs:**
- AJAX request is not reaching the backend
- User is not authenticated (check login status)
- @login_required is redirecting instead of executing view

### Step 3: Check Browser Console Logs

Open browser DevTools (F12) → Console tab, then add item to cart:

**Expected Console Output:**
```
Adding to cart: 123
Response status: 200
Cart add response: {success: true, message: "...", cart_count: 1, item_id: "123"}
```

**If you see different output:**

| Console Log | Meaning | Solution |
|------------|---------|----------|
| `Response status: 302` | Login required redirect | User not authenticated, check `window.isAuthenticated` |
| `Response status: 403` | CSRF token issue | Check CSRF token is being sent |
| `Response status: 500` | Server error | Check Django server logs for Python exception |
| `success: false` | Business logic error | Check the `message` field for details |
| No logs at all | JavaScript not executing | Check if `cart-wishlist.js` is loaded |

### Step 4: Check Network Tab

Open DevTools (F12) → Network tab, then add item:

1. Look for POST request to `/api/cart/add/`
2. Click on the request
3. Check **Response** tab

**Expected Response:**
```json
{
  "success": true,
  "message": "تمت إضافة ... إلى السلة",
  "cart_count": 1,
  "item_id": "123"
}
```

**If response is HTML instead of JSON:**
- @login_required is redirecting to login page
- User is not authenticated

### Step 5: Check Context Processor Logs

After adding item and refreshing page, check Django server logs for:

```
[CONTEXT_PROCESSOR] User: username, Cart: 45, Count: 1, Created: False
[CONTEXT_PROCESSOR] User: username, Wishlist: 67, Count: 0, Created: False
```

**If count is 0 after adding:**
- Database write may have rolled back
- Context processor is querying wrong user
- Items were saved but then deleted

### Step 6: Verify Database Directly

Check database directly (use Django shell or database client):

```python
python manage.py shell
```

Then:
```python
from django.contrib.auth import get_user_model
from main.models import Cart, CartItem

User = get_user_model()
user = User.objects.get(username='your_username')  # Change to your username

# Check cart
cart = Cart.objects.get(user=user)
print(f"Cart ID: {cart.id}")
print(f"Items count: {cart.get_items_count()}")

# List all cart items
for item in cart.items.all():
    print(f"  - CartItem #{item.id}: Ad #{item.ad_id}, Qty: {item.quantity}")
```

**If items are in database but not showing in UI:**
- Context processor not working
- Template tags not querying correctly
- JavaScript count update failing

## Common Issues and Solutions

### Issue 1: "Response status: 302" in console

**Problem:** User not authenticated, @login_required redirecting

**Solution:**
1. Verify user is logged in: Check Django admin or session
2. Check `window.isAuthenticated` in console (should be `true`)
3. Verify session cookie is set (DevTools → Application → Cookies)

### Issue 2: Items show in database but not in UI

**Problem:** Context processor or template tags not working

**Solution:**
1. Verify context processor is registered in settings:
   ```python
   # In idrissimart/settings/common.py
   "main.context_processors.cart_wishlist_counts"
   ```
2. Check template is using `{{ cart_count }}` and `{{ wishlist_count }}`
3. Verify template tags are loaded: `{% load idrissimart_tags %}`

### Issue 3: Count updates but resets on refresh

**Problem:** Database write not committing or being rolled back

**Solution:**
1. Check `ATOMIC_REQUESTS` setting (should be `True`)
2. Look for middleware that might rollback transactions
3. Check for duplicate database saves causing unique constraint violations
4. Verify no exception is being raised after save

### Issue 4: CSRF token error

**Problem:** CSRF token missing or invalid

**Solution:**
1. Verify `csrftoken` is defined in JavaScript (check cart-wishlist.js)
2. Check cookie is set: `document.cookie` should show csrftoken
3. Verify CSRF middleware is enabled in settings

## Next Steps

1. **Run database test first** (`python manage.py shell < test_cart_persistence.py`)
2. **Add item to cart with DevTools open** - check Console and Network tabs
3. **Compare logs** - Django server logs vs browser console logs
4. **Check database directly** - Verify items are actually saved
5. **Report findings** - Share the logs to identify root cause

## Files Modified

1. `static/js/cart-wishlist.js` - Added console logging
2. `main/cart_wishlist_views.py` - Added backend logging
3. `main/context_processors.py` - Added context processor logging
4. `test_cart_persistence.py` - New database test script

## Expected Behavior

When working correctly:

1. User clicks "Add to Cart"
2. JavaScript sends AJAX POST to `/api/cart/add/`
3. Backend creates/updates CartItem in database
4. Backend returns JSON with `success: true` and new `cart_count`
5. JavaScript updates header count
6. On page refresh:
   - Context processor queries database
   - Returns current count to template
   - Header shows correct count
   - Template tags show correct button states

If any step fails, items won't persist.
