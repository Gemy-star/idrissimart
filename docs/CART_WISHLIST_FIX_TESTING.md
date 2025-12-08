# Cart & Wishlist Fix - Testing Guide

## Changes Made

### 1. Template Tags Enhancement
**File**: `templates/partials/_ad_card_component.html`

Added debug HTML comments and data attributes to track button states:
- Added `data-in-cart` attribute to cart buttons
- Added `data-in-wishlist` attribute to wishlist buttons
- Added HTML comment showing template tag values for debugging

### 2. JavaScript Debug Logging
**File**: `templates/base.html`

Added comprehensive initialization logging on page load:
- Logs initial cart/wishlist counts from header
- Logs all cart button states (active class vs data attribute)
- Logs all wishlist button states (active class vs data attribute)
- Helps identify if template tags are working correctly

### 3. Backend Debug Logging
**Files**:
- `main/cart_wishlist_views.py` - Logs all cart/wishlist operations
- `main/context_processors.py` - Logs count retrieval on each page load

### 4. Frontend Debug Logging
**File**: `static/js/cart-wishlist.js`

Logs all AJAX operations:
- Item ID being added/removed
- Response status codes
- Full response data from server

## How to Test

### Step 1: Clear Browser Cache
1. Press `Ctrl+Shift+Delete`
2. Clear cached images and files
3. Or use incognito mode

### Step 2: Open Developer Tools
1. Press `F12` to open DevTools
2. Go to **Console** tab
3. Keep it open during testing

### Step 3: Test Adding to Cart/Wishlist

1. **Login** to your account
2. Navigate to a page with ads (homepage, category page, etc.)
3. **Check Console** - You should see logs like:
   ```
   [INIT] Page loaded - Cart count: 0
   [INIT] Page loaded - Wishlist count: 0
   [INIT] User authenticated: true
   [INIT] Cart button - Ad 24: Active=false, Data=false
   [INIT] Wishlist button - Ad 24: Active=false, Data=false
   ```

4. **Click wishlist heart icon** on an ad
5. **Check Console** - You should see:
   ```
   Adding to wishlist: 24
   Response status: 200
   Wishlist add response: {success: true, message: "...", wishlist_count: 1}
   ```

6. **Check Django Server Console** - You should see:
   ```
   [ADD_TO_WISHLIST] User: admin, Authenticated: True
   [ADD_TO_WISHLIST] Ad ID: 24
   [ADD_TO_WISHLIST] Wishlist: 1, User: 1
   [ADD_TO_WISHLIST] Created wishlist item: 4
   [ADD_TO_WISHLIST] Final wishlist count: 1
   ```

7. **Check Header** - Wishlist count should update to `1`

8. **Refresh Page** (Press `F5`)

9. **Check Console Again** - You should now see:
   ```
   [INIT] Page loaded - Wishlist count: 1
   [INIT] Wishlist button - Ad 24: Active=true, Data=true
   [CONTEXT_PROCESSOR] User: admin, Wishlist: 1, Count: 1, Created: False
   ```

10. **Check Button State**:
    - Heart icon should be solid (filled)
    - Button should have `active` class
    - Tooltip should say "في المفضلة" (In Wishlist)

### Step 4: Test Cart (Same Process)

1. Click cart icon on an ad with cart enabled
2. Follow same verification steps as above
3. Check cart count updates and persists

### Step 5: Verify Database Directly

Run this command to check database:

```powershell
Get-Content test_cart_persistence.py | python manage.py shell
```

Expected output:
```
✅ Database persistence test completed successfully
   Cart items: 1
   Wishlist items: 1
```

## Expected Behavior (Working Correctly)

### On First Add:
1. ✅ Button becomes active (filled icon)
2. ✅ Header count increases
3. ✅ Success notification appears
4. ✅ Console shows success response
5. ✅ Django logs show database write

### After Page Refresh:
1. ✅ Header count stays the same (not 0)
2. ✅ Button stays active (filled icon)
3. ✅ Console shows `Active=true, Data=true`
4. ✅ Context processor logs show correct count
5. ✅ Can click to remove item

## Troubleshooting

### Issue: Count shows 0 after refresh

**Check Django server console for:**
```
[CONTEXT_PROCESSOR] User: admin, Cart: 1, Count: 0
```

If count is 0 but database has items:
- Run `python manage.py migrate` to ensure migrations are up to date
- Check if items are being deleted somewhere
- Verify user is logged in (check session)

### Issue: Button not active after refresh

**Check browser console for:**
```
[INIT] Cart button - Ad 24: Active=false, Data=true
```

If `Data=true` but `Active=false`:
- Template is receiving correct value
- Button class is not being set
- Check HTML comment in source: `<!-- Debug: Ad 24 - In Cart: True -->`

If both are `false` but database has items:
- Template tags not working
- Check if `{% load idrissimart_tags %}` is present
- Verify user is authenticated

### Issue: AJAX returns 302 or 403

**Check browser console:**
```
Response status: 302
```

This means:
- User is not authenticated
- Session expired
- CSRF token issue

**Solution:**
- Log out and log back in
- Clear cookies
- Check `window.isAuthenticated` in console (should be `true`)

### Issue: Database test shows items but web doesn't

This means:
- Items ARE being saved
- Problem is with template rendering or context processor
- Check if hard refresh works (`Ctrl+F5`)
- Disable browser cache in DevTools

## Files Modified

1. `templates/partials/_ad_card_component.html` - Added data attributes
2. `templates/base.html` - Added debug logging on page load
3. `static/js/cart-wishlist.js` - Added AJAX logging
4. `main/cart_wishlist_views.py` - Added backend logging
5. `main/context_processors.py` - Added context processor logging

## Next Steps

1. **Test the flow** following the steps above
2. **Share console output** if issues persist:
   - Browser console logs
   - Django server console logs
3. **Check HTML source** - Look for debug comments showing template tag values
4. **Verify database** using the test script

## Success Criteria

✅ Items persist after page refresh
✅ Header counts stay accurate
✅ Button states (active/inactive) match database
✅ Can add and remove items multiple times
✅ Console logs show correct flow
✅ Django logs confirm database writes
