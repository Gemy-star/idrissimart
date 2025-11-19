# Data Seeding Management Commands

**Date:** 2025-11-19
**Status:** ✅ Complete

## Overview

Created two Django management commands to seed initial test data for the payments dashboard and saved searches features.

---

## Commands Available

### 1. seed_payments

Seeds payment transactions and premium user data for testing the `/admin/payments/` dashboard.

#### Usage

```bash
# Basic usage (30 payments, 10 premium users)
python manage.py seed_payments

# Custom count
python manage.py seed_payments --count 50 --premium-users 15

# Clear existing data first
python manage.py seed_payments --clear --count 30

# Help
python manage.py seed_payments --help
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--count` | int | 30 | Number of payments to create |
| `--premium-users` | int | 10 | Number of premium users to create |
| `--clear` | flag | False | Clear existing payment data before seeding |

#### What It Creates

**Test Users** (`test_user_1` to `test_user_N`):
- Username: `test_user_1`, `test_user_2`, etc.
- Email: `test_user_1@example.com`, etc.
- Password: `testpass123`

**Premium Users**:
- **Active Monthly**: Some users with 30-day subscriptions
- **Active Yearly**: Some users with 365-day subscriptions
- **Expired**: Some users with expired subscriptions

**Payments** (random distribution over 6 months):
- **Status Distribution**: ~70% completed, ~20% pending, ~10% failed
- **Package Types**:
  - Gold Package: 99 SAR
  - Platinum Package: 199 SAR
  - Featured Ad: 49 SAR
  - Urgent Ad: 29 SAR
- **Payment Providers**: PayPal, Paymob, Bank Transfer

#### Example Output

```
Starting payment data seeding...
Creating test users...
✓ Created/found 15 test users
Creating premium users...
✓ Created 10 premium users (7 active)
Creating payments...
✓ Created 30 payments

============================================================
✓ Payment Data Seeding Complete!
============================================================
  Premium Users Created: 10
  Payments Created: 30

  Payment Statistics:
    - Completed: 23
    - Pending: 5
    - Failed: 2
    - Total Revenue: 1957 SAR

✓ You can now view the data at /admin/payments/
```

---

### 2. seed_saved_searches

Seeds saved search queries for admin, publisher, and client users.

#### Usage

```bash
# Basic usage (5 searches per user type)
python manage.py seed_saved_searches

# Custom count
python manage.py seed_saved_searches --count 8

# Clear existing data first
python manage.py seed_saved_searches --clear --count 5

# Help
python manage.py seed_saved_searches --help
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--count` | int | 5 | Number of saved searches per user type |
| `--clear` | flag | False | Clear existing saved searches before seeding |

#### What It Creates

**User Accounts**:

1. **Admin User**
   - Username: `admin_user`
   - Email: `admin@example.com`
   - Password: `admin123`
   - Permissions: Staff, Superuser

2. **Publisher User**
   - Username: `publisher_user`
   - Email: `publisher@example.com`
   - Password: `publisher123`

3. **Client User**
   - Username: `client_user`
   - Email: `client@example.com`
   - Password: `client123`

**Saved Searches**:

**Admin Searches** (Management & Moderation):
1. Pending Ads Review - `status=pending&sort=-created_at`
2. Flagged Content - `is_flagged=true&sort=-updated_at`
3. High Value Listings - `min_price=10000&sort=-price`
4. New Users Ads - `days=7&sort=-created_at`
5. Premium Listings - `is_premium=true&sort=-views`
6. Expired Ads - `status=expired&sort=-expires_at`
7. Most Reported - `sort=-reports_count`
8. Verification Needed - `verification_status=pending`

**Publisher Searches** (Content Creation):
1. My Active Listings - `status=active&user=me&sort=-views`
2. Electronics Deals - `category=electronics&condition=new&sort=-created_at`
3. Real Estate Listings - `category=real-estate&sort=-price`
4. Vehicles Under 50k - `category=vehicles&max_price=50000&sort=-created_at`
5. Furniture in My City - `category=furniture&location=my_city&sort=-price`
6. Jobs in Tech - `category=jobs&keywords=technology,software&sort=-created_at`
7. Services Near Me - `category=services&radius=10km&sort=-rating`
8. Fashion & Accessories - `category=fashion&condition=new&sort=-created_at`

**Client Searches** (Browsing & Shopping):
1. Affordable Electronics - `category=electronics&max_price=1000&sort=price`
2. Apartments for Rent - `category=real-estate&listing_type=rent&sort=-created_at`
3. Used Cars - `category=vehicles&condition=used&max_price=30000&sort=price`
4. Home Appliances - `category=appliances&condition=new&sort=-created_at`
5. Remote Jobs - `category=jobs&keywords=remote,work-from-home&sort=-created_at`
6. Gaming Consoles - `category=electronics&keywords=playstation,xbox,nintendo&sort=price`
7. Books & Textbooks - `category=books&sort=price`
8. Sports Equipment - `category=sports&condition=new&sort=-created_at`

#### Example Output

```
Starting saved searches seeding...
Getting/creating admin user...
✓ Created admin user
Getting/creating publisher user...
✓ Created publisher user
Getting/creating client user...
✓ Created client user
Creating admin saved searches...
✓ Created 5 admin searches
Creating publisher saved searches...
✓ Created 5 publisher searches
Creating client saved searches...
✓ Created 5 client searches

============================================================
✓ Saved Searches Seeding Complete!
============================================================
  Admin Searches Created: 5
  Publisher Searches Created: 5
  Client Searches Created: 5
  Total: 15

✓ You can now view saved searches at /classifieds/saved-searches/
```

---

## File Structure

```
main/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── seed_payments.py          # Payment & premium users seeding
│       └── seed_saved_searches.py    # Saved searches seeding
```

---

## Database Models Used

### Payment Model

```python
# main/models.py:1706
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    provider_transaction_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='SAR')
    status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

### User Model (Premium Fields)

```python
# main/models.py:317-339
is_premium = models.BooleanField(default=False)
subscription_start = models.DateField(null=True, blank=True)
subscription_end = models.DateField(null=True, blank=True)
subscription_type = models.CharField(
    max_length=20,
    choices=[
        ("monthly", "شهري - Monthly"),
        ("yearly", "سنوي - Yearly"),
    ],
    blank=True,
)
```

### SavedSearch Model

```python
# main/models.py:1837
class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_searches")
    name = models.CharField(max_length=100)
    query_params = models.TextField()
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    unsubscribe_token = models.UUIDField(editable=False, unique=True, db_index=True)
```

---

## Testing the Data

### 1. Test Payments Dashboard

```bash
# Access as superuser
http://localhost:8000/admin/payments/
```

**Expected Results**:
- ✅ Statistics cards show real numbers
- ✅ Transaction table populated
- ✅ Revenue chart displays monthly data
- ✅ Package subscriber counts shown
- ✅ Premium members list populated

### 2. Test Saved Searches

```bash
# Login as each user type:
# admin_user / admin123
# publisher_user / publisher123
# client_user / client123

http://localhost:8000/classifieds/saved-searches/
```

**Expected Results**:
- ✅ Each user sees their own saved searches
- ✅ Email notification toggles work
- ✅ View Results buttons work
- ✅ Delete functionality works
- ✅ Search names are relevant to user type

---

## Cleanup Commands

### Clear All Seeded Data

```bash
# Clear payments and premium users
python manage.py seed_payments --clear

# Clear saved searches
python manage.py seed_saved_searches --clear
```

### Clear Specific Users

```python
# Django shell
python manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()

# Delete test users
User.objects.filter(username__startswith='test_user_').delete()

# Delete seeded accounts
User.objects.filter(username__in=['admin_user', 'publisher_user', 'client_user']).delete()
```

---

## Common Issues

### 1. IntegrityError: Duplicate Names

**Problem**: Saved search with same name already exists for user

**Solution**: Use `--clear` flag to remove existing data first

```bash
python manage.py seed_saved_searches --clear
```

### 2. No Data Appearing

**Problem**: Commands run but data not showing

**Troubleshooting**:
1. Check if you're logged in as the correct user
2. Verify database connection
3. Check command output for errors
4. Inspect database directly:

```python
python manage.py shell

from main.models import Payment, SavedSearch
print(f"Payments: {Payment.objects.count()}")
print(f"Saved Searches: {SavedSearch.objects.count()}")
```

### 3. Permission Denied

**Problem**: Cannot create admin user

**Solution**: Ensure proper database permissions

---

## Integration with Application

### Payment Dashboard

The seeded data integrates with:
- [views.py:2626-2742](../main/views.py#L2626-L2742) - `AdminPaymentsView`
- [templates/admin_dashboard/payments.html](../templates/admin_dashboard/payments.html)
- [docs/PAYMENTS_PAGE_DATA_FIX.md](PAYMENTS_PAGE_DATA_FIX.md)

### Saved Searches

The seeded data integrates with:
- Saved searches view and template
- [templates/classifieds/saved_searches.html](../templates/classifieds/saved_searches.html)
- Email notification system

---

## Future Enhancements

### For Payment Seeding

1. **Add transaction history**: Link payments to specific ads
2. **Create refunds**: Add refunded payment records
3. **Generate invoices**: Create PDF invoices for completed payments
4. **Add payment methods**: Include credit card, wallet, etc.

### For Saved Searches Seeding

1. **Add search results**: Link to actual matching ads
2. **Create notifications**: Generate notification records
3. **Add search frequency**: Track how often searches are used
4. **Create alerts**: Set up alert conditions

---

## Production Considerations

⚠️ **WARNING**: These commands are for **development/testing only**

**Never run in production** without modification because:
1. Creates users with weak passwords
2. Generates fake transaction data
3. Uses predictable usernames and emails
4. May conflict with real user data

**For production setup**:
1. Use proper user creation flows
2. Import real transaction data
3. Let users create their own saved searches
4. Use secure password policies

---

## Related Documentation

- [Payment Model](../main/models.py#L1706-L1788)
- [SavedSearch Model](../main/models.py#L1837-L1873)
- [User Model](../main/models.py#L1-L600)
- [Payments Page Fix](PAYMENTS_PAGE_DATA_FIX.md)
- [Admin Dashboard CSS](../static/css/admin-dashboard.css)

---

## Conclusion

✅ **Successfully created seeding commands** for payments and saved searches.

**Benefits**:
- 🚀 Quick test data generation
- 🎯 Realistic data patterns
- 🔧 Easy to customize
- 🧹 Simple cleanup
- 📊 Supports dashboard testing
- 👥 Multiple user types

**Command Summary**:
```bash
# Seed everything
python manage.py seed_payments --count 30 --premium-users 10
python manage.py seed_saved_searches --count 5

# Test URLs
/admin/payments/
/classifieds/saved-searches/
```

All commands run successfully and populate the database with realistic test data!
