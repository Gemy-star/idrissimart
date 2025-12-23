# Ad Features & Payment System Implementation

## Overview
Implemented a comprehensive ad features system with fees and payment integration. Users can now add premium features to their ads (featured, urgent, pinned) with appropriate pricing. The system handles free ads, calculates costs, and supports both online and offline payment methods.

## Key Features Implemented

### 1. Feature Pricing System
**Location:** `content/site_config.py`

Added new fields to `SiteConfiguration` model:
- `ad_base_fee`: Base fee for posting an ad (default: 0 = free)
- `featured_ad_price`: Cost to make ad highlighted (default: 50 EGP)
- `urgent_ad_price`: Cost to add urgent badge (default: 30 EGP)
- `pinned_ad_price`: Cost to pin ad to top (default: 100 EGP)

### 2. Payment Receipt Support
**Location:** `main/models.py`

Added to `Payment` model:
- `offline_payment_receipt`: ImageField for uploading transaction photos
- Supports offline payment verification workflow

### 3. Ad Creation Form Enhancement
**Location:** `templates/classifieds/ad_form.html`

**Features Added:**
- Feature selection cards in Step 2 (Price & Location)
- Real-time price calculation
- Visual feedback for selected features
- Price summary breakdown showing:
  - Base posting fee
  - Selected features cost
  - Free ads discount (if applicable)
  - Total cost

**JavaScript Features:**
- Automatic price calculation when features selected
- Feature card styling (selected/unselected states)
- Integration with free ads count from user's package

### 4. Payment Flow
**Location:** `main/classifieds_views.py`, `main/payment_views.py`

**ClassifiedAdCreateView Changes:**
```python
- Detects selected features from form
- Calculates total cost (base fee + features)
- Checks if user has free ads available
- If cost > 0: Saves ad as DRAFT and redirects to payment
- If cost = 0: Publishes ad immediately (or pending review)
- Stores payment details in session for processing
```

**New Views:**
- `ad_payment()`: Payment page for new ads with features
- `confirm_ad_payment()`: Admin endpoint to confirm offline payments

### 5. Payment Page
**Location:** `templates/payments/ad_payment.html`

**Features:**
- Ad details display
- Price breakdown with features list
- Payment method selection:
  - **Offline Payment:** InstaPay QR code / Wallet link + receipt upload
  - **Online Payment:** PayMob / PayPal integration
- Receipt upload for offline payments
- Payment instructions in Arabic

### 6. Admin Dashboard Integration
**Location:** `templates/admin_dashboard/edit_siteconfig.html`

Added section for "Ad Posting & Feature Pricing":
- Base ad posting fee
- Featured ad price
- Urgent ad price
- Pinned ad price

All editable through Site Configuration page.

## Workflow

### For Users with Free Ads:
1. User creates ad and selects features
2. Base fee = 0 (covered by package)
3. Features cost = sum of selected features
4. If features selected → redirects to payment
5. If no features → ad published directly

### For Users without Free Ads:
1. User creates ad and selects features
2. Base fee = `site_config.ad_base_fee`
3. Features cost = sum of selected features
4. Total = base fee + features cost
5. Redirects to payment page

### Payment Process:
1. **Offline Payment:**
   - User sees QR code / wallet link
   - User makes payment
   - User uploads receipt photo
   - Ad saved as DRAFT
   - Admin confirms payment via dashboard
   - Ad status changes to ACTIVE/PENDING

2. **Online Payment:**
   - User redirected to payment gateway
   - Payment processed automatically
   - On success: Ad activated with features

### Admin Confirmation:
- Admin views pending offline payments
- Reviews receipt photo
- Confirms or rejects payment
- On confirm: Ad features applied and activated
- User receives notification

## Database Changes

### Migrations Created:
1. `content/migrations/0017_add_feature_pricing.py`
   - Added pricing fields to SiteConfiguration

2. `main/migrations/0035_add_payment_receipt.py`
   - Added offline_payment_receipt to Payment model

## URLs Added
**Location:** `main/urls.py`

```python
path("payment/ad/<int:ad_id>/", payment_views.ad_payment, name="ad_payment")
path("payment/ad/confirm/<int:payment_id>/", payment_views.confirm_ad_payment, name="confirm_ad_payment")
```

## Configuration

### Default Pricing:
- Ad base fee: 0 EGP (free)
- Featured ad: 50 EGP
- Urgent ad: 30 EGP
- Pinned ad: 100 EGP

### To Change Pricing:
1. Go to: `/admin/site-content/siteconfig/edit/`
2. Scroll to "Ad Posting & Feature Pricing" section
3. Update values
4. Save

## Testing Checklist

### User Flow:
- [ ] User with free ads can post without payment
- [ ] User with free ads + features redirected to payment
- [ ] User without free ads redirected to payment
- [ ] Feature selection updates price in real-time
- [ ] Price summary shows correct calculations

### Offline Payment:
- [ ] QR code displays correctly
- [ ] Wallet link opens properly
- [ ] Receipt upload works
- [ ] Payment pending status set correctly
- [ ] Admin can view and confirm payments
- [ ] Ad activated after confirmation
- [ ] User receives notification

### Online Payment:
- [ ] Redirects to payment gateway
- [ ] Payment amount correct
- [ ] Success callback activates ad
- [ ] Features applied correctly

## Files Modified

1. `content/site_config.py` - Added pricing fields
2. `main/models.py` - Added receipt field to Payment
3. `templates/classifieds/ad_form.html` - Added feature selection UI
4. `main/classifieds_views.py` - Updated ClassifiedAdCreateView
5. `main/payment_views.py` - Added ad_payment and confirm_ad_payment
6. `templates/payments/ad_payment.html` - Created payment page
7. `templates/admin_dashboard/edit_siteconfig.html` - Added pricing fields
8. `main/enhanced_views.py` - Updated SiteConfigForm
9. `main/urls.py` - Added payment URLs

## Features & Benefits

### For Site Owners:
- ✅ Flexible pricing control
- ✅ Revenue from ad features
- ✅ Offline payment support
- ✅ Manual payment verification
- ✅ Free ad packages still work

### For Users:
- ✅ Clear pricing display
- ✅ Optional features
- ✅ Multiple payment methods
- ✅ Free ads honored
- ✅ Visual feature selection

### For Admins:
- ✅ Easy pricing management
- ✅ Payment verification workflow
- ✅ Receipt viewing
- ✅ One-click confirmation

## Future Enhancements

Possible additions:
1. Auto-confirm online payments
2. Feature duration (7/14/30 days)
3. Bulk feature purchases
4. Feature packages
5. Discount codes
6. Refund system
7. Payment analytics

## Notes

- All existing features (is_highlighted, is_urgent, is_pinned) already exist in ClassifiedAd model
- features_price field already exists to store total features cost
- System integrates seamlessly with existing package system
- Free ads from packages take priority over base fee
- Features always require payment (not covered by packages)
