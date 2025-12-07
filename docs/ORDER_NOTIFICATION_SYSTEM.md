# Order Notification System Implementation

## Overview
Comprehensive email and SMS notification system for order transactions, integrated with the enhanced Order model that supports partial payments.

## Date
2025-01-XX

---

## Features Implemented

### 1. **Order Creation Notifications**
When a new order is created from the cart:

#### Customer Notifications:
- ✅ **In-app Notification**: Created in the user's notification center
- ✅ **Email Notification**: Professional HTML email with order details
  - Order number and date
  - Payment status (unpaid/partial/paid)
  - Payment method
  - List of items ordered
  - Total amount breakdown
  - Partial payment details (if applicable)
  - Link to view order details
- ✅ **SMS Notification**: Quick confirmation message with order number and total

#### Admin Notifications:
- ✅ **In-app Notification**: Alert for all superusers
  - Shows customer name and order total
  - Direct link to admin order detail page

#### Publisher Notifications:
- ✅ **In-app Notification**: For publishers whose items are in the order
  - Shows their revenue from the order
  - Link to publisher order detail page

### 2. **Order Status Change Notifications**
When order status changes (pending → processing → shipped → delivered):

#### Customer Notifications:
- ✅ **In-app Notification**: Status update message
- ✅ **SMS Notification**: For important status changes (shipped, delivered)
  - Customized messages per status:
    - `processing`: "طلبك قيد المعالجة"
    - `shipped`: "تم شحن طلبك"
    - `delivered`: "تم تسليم طلبك بنجاح"
    - `cancelled`: "تم إلغاء طلبك"
    - `refunded`: "تم استرداد مبلغ طلبك"

### 3. **Payment Status Change Notifications**
When payment status changes (unpaid → partial → paid):

#### Full Payment:
- ✅ **In-app Notification**: Payment confirmation
- ✅ **SMS Notification**: "تم استلام الدفع الكامل لطلبك"

#### Partial Payment:
- ✅ **In-app Notification**: Shows paid amount and remaining balance

### 4. **Partial Payment Support in Checkout**
Enhanced checkout form with partial payment option:

#### UI Enhancements:
- ✅ **New Payment Method**: "دفع جزئي" option added
- ✅ **Paid Amount Input**: Field to enter partial payment amount
- ✅ **Validation**:
  - Ensures paid amount > 0
  - Ensures paid amount ≤ total amount
  - Shows total amount for reference

#### Backend Logic:
- ✅ Automatically calculates payment status
- ✅ Sets `paid_amount` field
- ✅ Auto-calculates `remaining_amount` in model save()
- ✅ If partial payment ≥ total, marks as fully paid

---

## Technical Implementation

### Signal Handlers (main/signals.py)

#### 1. Order Creation Signal
```python
@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs)
```
**Triggers on**: Order creation (`created=True`)

**Actions**:
1. Creates in-app notification for customer
2. Sends HTML email using `email_service.py`
3. Sends SMS using `sms_service.py`
4. Notifies all superusers
5. Notifies publishers whose items are in the order

#### 2. Order Status Tracking Signal
```python
@receiver(pre_save, sender=Order)
def track_order_status_changes(sender, instance, **kwargs)
```
**Triggers on**: Order update (before save)

**Actions**:
- Detects status changes and sets flags:
  - `instance._status_changed = True`
  - `instance._old_status = old_status`
- Detects payment status changes and sets flags:
  - `instance._payment_status_changed = True`
  - `instance._old_payment_status = old_payment_status`

#### 3. Order Status Change Notification Signal
```python
@receiver(post_save, sender=Order)
def send_order_status_notifications(sender, instance, created, **kwargs)
```
**Triggers on**: Order update (`created=False`)

**Actions**:
- If status changed: Sends notification + SMS
- If payment status changed to 'paid': Sends payment confirmation
- If payment status changed to 'partial': Sends partial payment notification

### Email Template (templates/emails/order_created.html)

**Features**:
- Professional RTL Arabic design
- Gradient header with success icon
- Order information cards
- Payment status badges (colored)
- Responsive items table
- Total amount breakdown
- Partial payment details section
- Call-to-action button
- Mobile-friendly

**Styling**:
- Uses inline CSS for email client compatibility
- Color-coded payment statuses:
  - 🟢 Paid: Green background
  - 🟡 Partial: Yellow background
  - 🔴 Unpaid: Red background

### Checkout View Updates (main/cart_wishlist_views.py)

**New Logic**:
```python
# Handle partial payment
if payment_method == "partial":
    paid_amount = Decimal(request.POST.get("paid_amount"))

    if paid_amount >= total_amount:
        payment_status = "paid"
        paid_amount = total_amount
    else:
        payment_status = "partial"
```

**Order Creation**:
- Sets `payment_status` based on payment method
- Sets `paid_amount` for partial payments
- Model automatically calculates `remaining_amount`

### Checkout Template Updates (templates/cart/checkout.html)

**New UI Elements**:
```html
<!-- Partial Payment Option -->
<div class="payment-method" onclick="selectPaymentMethod('partial')">
    <input type="radio" name="payment_method" value="partial">
    <div class="payment-method-icon">
        <i class="fas fa-percentage"></i>
    </div>
    <div class="payment-method-label">دفع جزئي</div>
</div>

<!-- Partial Payment Input -->
<div id="partialPaymentNote">
    <input type="number" name="paid_amount" id="paidAmount"
           min="0" step="0.01" class="form-control">
</div>
```

**JavaScript Updates**:
- `selectPaymentMethod()`: Shows/hides partial payment note
- `placeOrder()`: Validates partial payment amount

---

## Configuration Requirements

### Email Service (SendGrid)
**File**: `main/services/email_service.py`

**Required Settings**:
```python
SENDGRID_API_KEY = 'your-sendgrid-api-key'
DEFAULT_FROM_EMAIL = 'noreply@idrissimart.com'
```

**Check if enabled**:
```python
EmailService.is_enabled()  # Returns True if configured
```

### SMS Service (Twilio)
**File**: `main/services/sms_service.py`

**Required Settings**:
```python
TWILIO_ACCOUNT_SID = 'your-twilio-sid'
TWILIO_AUTH_TOKEN = 'your-twilio-token'
TWILIO_PHONE_NUMBER = '+966XXXXXXXXX'
```

**Features**:
- Auto-formats Saudi phone numbers to +966 format
- Development mode for testing without sending actual SMS
- Error logging for failed deliveries

**Check if enabled**:
```python
SMSService.is_enabled()  # Returns True if configured
```

---

## Order Model Fields (Enhanced)

### Payment-Related Fields
```python
payment_status = models.CharField(
    choices=[
        ('unpaid', 'غير مدفوع'),
        ('partial', 'دفع جزئي'),
        ('paid', 'مدفوع'),
        ('refunded', 'مسترد'),
    ]
)
paid_amount = models.DecimalField(default=Decimal("0.00"))
payment_method = models.CharField(
    choices=[
        ('cod', 'الدفع عند الاستلام'),
        ('online', 'الدفع الإلكتروني'),
        ('partial', 'دفع جزئي'),
    ]
)
```

### Auto-Calculated Properties
```python
@property
def remaining_amount(self):
    return self.total_amount - self.paid_amount

def get_payment_percentage(self):
    if self.total_amount > 0:
        return (self.paid_amount / self.total_amount) * 100
    return 0
```

---

## Notification Flow Examples

### Example 1: New Order with COD
```
1. User completes checkout with COD
2. Order created with payment_status='unpaid'
3. Signals triggered:
   ✓ In-app notification created for customer
   ✓ Email sent to customer (order_created.html)
   ✓ SMS sent: "تم إنشاء طلبك ORD-20250115-001 بنجاح..."
   ✓ Admin notified in-app
   ✓ Publishers notified of their revenue
```

### Example 2: New Order with Partial Payment
```
1. User selects "دفع جزئي"
2. User enters paid amount: 500 SAR (total: 1000 SAR)
3. Order created with:
   - payment_status='partial'
   - paid_amount=500
   - remaining_amount=500 (auto-calculated)
4. Customer receives:
   ✓ Email showing partial payment breakdown
   ✓ SMS confirmation
   ✓ In-app notification
```

### Example 3: Order Status Update
```
1. Admin changes order status: pending → shipped
2. pre_save signal: Sets _status_changed flag
3. post_save signal:
   ✓ Customer gets in-app notification: "تم شحن طلبك"
   ✓ Customer gets SMS: "طلبك ORD-001: تم شحن طلبك"
```

### Example 4: Payment Completion
```
1. Admin updates payment: partial → paid
2. pre_save signal: Sets _payment_status_changed flag
3. post_save signal:
   ✓ Customer gets in-app: "تم استلام الدفع الكامل"
   ✓ Customer gets SMS: "تم استلام الدفع الكامل لطلبك ORD-001"
```

---

## Testing Checklist

### Cart to Order Integration
- [ ] Add items to cart
- [ ] Proceed to checkout
- [ ] Verify all payment methods visible
- [ ] Test COD order creation
- [ ] Test online payment order creation
- [ ] Test partial payment order creation

### Notification Delivery
- [ ] Verify in-app notification created
- [ ] Check email received (check spam folder)
- [ ] Verify SMS sent (if Twilio configured)
- [ ] Confirm admin receives notification
- [ ] Confirm publisher receives notification

### Partial Payment
- [ ] Enter partial amount = 0 → validation error
- [ ] Enter partial amount > total → validation error
- [ ] Enter partial amount = total → payment_status = 'paid'
- [ ] Enter partial amount < total → payment_status = 'partial'
- [ ] Verify remaining_amount calculated correctly

### Status Changes
- [ ] Change status to 'processing' → notification sent
- [ ] Change status to 'shipped' → notification + SMS sent
- [ ] Change status to 'delivered' → notification + SMS sent
- [ ] Change status to 'cancelled' → notification sent

### Payment Updates
- [ ] Update payment: unpaid → partial → notification sent
- [ ] Update payment: partial → paid → notification + SMS sent
- [ ] Verify revenue calculations for publishers

---

## Files Modified

### Backend Files
1. **main/signals.py** (320 lines)
   - Added Order import
   - Added SMSService import
   - Added 3 new signal handlers (130+ lines)

2. **main/cart_wishlist_views.py** (625 lines)
   - Added Decimal import
   - Enhanced checkout_view() with partial payment logic
   - Added payment status calculation

### Template Files
1. **templates/emails/order_created.html** (NEW)
   - Professional order confirmation email
   - 200+ lines of HTML/CSS

2. **templates/cart/checkout.html** (564 lines)
   - Added partial payment option
   - Added paid amount input field
   - Enhanced JavaScript validation

### Documentation
1. **docs/ORDER_NOTIFICATION_SYSTEM.md** (THIS FILE)

---

## Dependencies

### Python Packages
```
django>=4.2
sendgrid>=6.9
twilio>=8.0
```

### External Services
- **SendGrid**: Email delivery service
- **Twilio**: SMS delivery service

### Django Apps
- `main` (Order, Cart, User models)
- `content` (Notification model)

---

## Notification Types Summary

| Event | In-App | Email | SMS |
|-------|--------|-------|-----|
| Order Created | ✅ | ✅ | ✅ |
| Status: Processing | ✅ | ❌ | ❌ |
| Status: Shipped | ✅ | ❌ | ✅ |
| Status: Delivered | ✅ | ❌ | ✅ |
| Status: Cancelled | ✅ | ❌ | ❌ |
| Payment: Partial | ✅ | ❌ | ❌ |
| Payment: Full | ✅ | ❌ | ✅ |
| Admin: New Order | ✅ | ❌ | ❌ |
| Publisher: Revenue | ✅ | ❌ | ❌ |

---

## Error Handling

All notification sending is wrapped in try-except blocks to ensure order creation never fails due to notification errors:

```python
try:
    # Send notification
    email_service.send_email(...)
except Exception as e:
    logger.error(f"Failed to send email: {str(e)}")
    # Order creation continues normally
```

**Logged Errors**:
- Email delivery failures
- SMS delivery failures
- Notification creation failures
- Payment status change errors

---

## Future Enhancements

### Potential Additions:
1. **WhatsApp Notifications** (via Twilio API)
2. **Email Templates for Status Changes** (currently only in-app + SMS)
3. **Push Notifications** (for mobile apps)
4. **Notification Preferences** (let users choose which notifications to receive)
5. **Scheduled Payment Reminders** (for partial payments)
6. **Delivery Tracking Integration** (SMS updates from courier)
7. **Payment Gateway Integration** (for online payments)
8. **Invoice Generation** (PDF attached to email)

---

## Related Documentation

- [Order Management System](ORDER_MANAGEMENT_SYSTEM.md)
- [Admin Dashboard Updates](ADMIN_DASHBOARD_UPDATES.md)
- [Free Ad System](FREE_AD_SYSTEM.md)
- [Scheduled Tasks](03_scheduled_tasks.md)

---

## Support

For issues or questions about the notification system:
1. Check logs: `logger.error()` messages
2. Verify SendGrid/Twilio configuration
3. Test with development mode (SMS)
4. Check email spam folder

**Common Issues**:
- **No emails received**: Check SendGrid API key, verify email not in spam
- **No SMS received**: Check Twilio credentials, verify phone number format
- **Notifications not sent**: Check signal registration in `apps.py`
- **Partial payment validation fails**: Check JavaScript console, verify input field

---

**Status**: ✅ Fully Implemented and Ready for Testing
**Last Updated**: 2025-01-XX
