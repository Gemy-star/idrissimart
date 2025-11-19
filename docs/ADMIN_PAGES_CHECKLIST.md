# Admin Pages Testing Checklist

Use this checklist to verify all admin pages are working correctly with proper data display and theme support.

## Prerequisites
- [ ] Database has data (run seeding commands if needed)
- [ ] Superuser account exists
- [ ] Server is running

## Seeding Commands (Run if needed)
```bash
# Seed all data at once
python manage.py seed_payments --count 30
python manage.py seed_saved_searches
python manage.py init_chatbot
```

## Pages to Test

### 1. Main Dashboard - `/admin/dashboard/`
- [ ] Page loads without errors
- [ ] Statistics cards show numbers (not zeros)
- [ ] Charts display (ads last 7 days, users, categories)
- [ ] Recent ads table shows data
- [ ] Recent users table shows data
- [ ] Dark theme switches properly
- [ ] All hover effects work

**Expected Stats:**
- Total ads: Should match database count
- Active ads: Number of active ads
- Pending ads: Number pending review
- Premium members: Count of users with `is_premium=True`

### 2. Payments Dashboard - `/admin/payments/`
- [ ] Page loads without errors
- [ ] Stats cards show real numbers
- [ ] Revenue chart displays monthly data
- [ ] Recent transactions table has data
- [ ] Premium members table shows users
- [ ] Tabs work (Overview, Transactions, Members)
- [ ] Dark theme works
- [ ] Export buttons are visible

**Expected Data:**
- After running `seed_payments`, should show ~30 transactions
- Total revenue should be calculated from completed payments
- Premium members count should match active subscriptions

### 3. Users Management - `/admin/users/`
- [ ] Page loads without errors
- [ ] User list displays
- [ ] Search functionality works
- [ ] Role filter dropdown works
- [ ] Pagination works if >20 users
- [ ] User stats show correct counts
- [ ] Dark theme works
- [ ] Action buttons visible

**Expected:**
- Should show all users in database
- Stats should show: total users, verified users, publisher users

### 4. Categories Management - `/admin/categories/`
- [ ] Page loads without errors
- [ ] Categories grouped by section
- [ ] Subcategories displayed
- [ ] Ad counts shown per category
- [ ] Add/Edit modals work
- [ ] Dark theme works
- [ ] Drag & drop reordering works

**Expected:**
- Should show 80 categories organized by section
- Each category should show ad count

### 5. Custom Fields - `/admin/custom-fields/`
- [ ] Page loads without errors
- [ ] Custom fields list displays
- [ ] Grouped by category
- [ ] Add/Edit/Delete modals work
- [ ] Field type options visible
- [ ] Dark theme works
- [ ] Search works

**Expected:**
- May be empty initially (can create via UI)
- Should show fields grouped by category

### 6. Ads Management - `/admin/ads/`
- [ ] Page loads without errors
- [ ] Tabs work (Active, Pending, Expired, Hidden, Cart)
- [ ] Ads list displays with images
- [ ] Search functionality works
- [ ] Action buttons work (Edit, Delete, Toggle status)
- [ ] Dark theme works
- [ ] Pagination works

**Expected:**
- Should show 25 ads (from database)
- Images should load properly
- Ad cards should use `_ad_card_component.html`

### 7. Settings - `/admin/settings/`
- [ ] Page loads without errors
- [ ] All setting sections display
- [ ] Forms are populated with values
- [ ] Save buttons work
- [ ] Dark theme works
- [ ] Tabs switch properly

**Expected:**
- All settings show placeholder or actual values
- Settings organized in tabs

### 8. Chatbot Admin - `/chatbot/admin/`
- [ ] Page loads without errors
- [ ] Stats cards show numbers (after init_chatbot)
- [ ] Knowledge base list loads
- [ ] Quick actions list loads
- [ ] Recent conversations display
- [ ] Add/Edit buttons work
- [ ] Dark theme works
- [ ] Refresh buttons work

**Expected After `init_chatbot`:**
- 10 knowledge base entries
- 5 quick actions
- Stats should show conversation counts

### 9. Saved Searches - `/classifieds/saved-searches/`
- [ ] Page loads without errors
- [ ] Saved searches list displays (after seeding)
- [ ] Edit/Delete buttons work
- [ ] Email notification toggle works
- [ ] Dark theme works
- [ ] Admin tabs styling applied

**Expected After `seed_saved_searches`:**
- Admin user: 5-8 searches
- Publisher user: 5-8 searches
- Client user: 5-8 searches

## Dark Theme Testing

For each page, verify:
- [ ] Toggle theme switch in header
- [ ] Background changes to `#1a1a1a`
- [ ] Cards change to `#2d2d2d`
- [ ] Text remains readable (proper contrast)
- [ ] Borders are visible
- [ ] Buttons maintain styling
- [ ] Modals work in both themes
- [ ] Charts display correctly
- [ ] Tables are readable

## Common Issues & Solutions

### Issue: No data displays
**Solution**: Run seeding commands
```bash
python manage.py seed_payments
python manage.py seed_saved_searches
python manage.py init_chatbot
```

### Issue: "no content viewed"
**Causes**:
1. JavaScript not loading data
2. AJAX endpoints returning errors
3. No data in database

**Solutions**:
1. Check browser console for errors
2. Verify URL patterns are configured
3. Run seeding commands

### Issue: Encoding errors with Arabic text
**Solution**: All commands have been updated to remove problematic characters

### Issue: Charts not displaying
**Solutions**:
1. Check Chart.js is loaded
2. Verify data is being passed to template
3. Check console for JavaScript errors

## Test Users

Created by seeding commands:

1. **Admin User**
   - Username: `admin_user`
   - Password: `admin123`
   - Role: Superuser

2. **Publisher User**
   - Username: `publisher_user`
   - Password: `publisher123`
   - Role: Publisher

3. **Client User**
   - Username: `client_user`
   - Password: `client123`
   - Role: Client

## Verification Script

Quick check via Django shell:
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from main.models import *

User = get_user_model()

# Check counts
print(f"Users: {User.objects.count()}")
print(f"Premium Users: {User.objects.filter(is_premium=True).count()}")
print(f"Categories: {Category.objects.count()}")
print(f"Ads: {ClassifiedAd.objects.count()}")
print(f"Payments: {Payment.objects.count()}")
print(f"Saved Searches: {SavedSearch.objects.count()}")

# Check chatbot
from main.chatbot_models import ChatbotKnowledgeBase, ChatbotQuickAction
print(f"Chatbot Knowledge: {ChatbotKnowledgeBase.objects.count()}")
print(f"Chatbot Actions: {ChatbotQuickAction.objects.count()}")
```

## Success Criteria

All pages should:
✅ Load without 500/404 errors
✅ Display data (not empty states if seeded)
✅ Switch between light/dark themes smoothly
✅ Have functional search/filter
✅ Show proper loading states for AJAX
✅ Display charts where applicable
✅ Have working action buttons
✅ Show proper error messages for failed actions

## Documentation

See also:
- [ADMIN_PAGES_FIX_SUMMARY.md](./ADMIN_PAGES_FIX_SUMMARY.md) - Detailed fixes applied
- [SEEDING_COMMANDS.md](./SEEDING_COMMANDS.md) - Seeding command documentation
- [Z_INDEX_HIERARCHY.md](./Z_INDEX_HIERARCHY.md) - Z-index management
