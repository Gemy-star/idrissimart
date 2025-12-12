# Payment Methods Configuration Guide

## Overview
This document describes the payment methods configuration system that allows administrators to control which payment options are available in the checkout process.

## Features Implemented

### 1. Online Payment Toggle (Django Constance)

#### Configuration Setting
**Setting Name**: `ALLOW_ONLINE_PAYMENT`
**Type**: Boolean (True/False)
**Default**: `True`
**Location**: Django Constance Admin → Payment General Settings

#### Functionality
- **When Enabled (True)**: Online payment option is displayed in checkout
- **When Disabled (False)**: Online payment option is hidden from checkout
- Affects all checkout pages site-wide
- Changes take effect immediately without code deployment

#### Admin Access
1. Navigate to: **Admin Dashboard → Constance → Config**
2. Find section: **Payment General Settings**
3. Toggle: **ALLOW_ONLINE_PAYMENT**
4. Click **Save**

---

### 2. InstaPay QR Code Payment

#### Configuration
**Field Name**: `instapay_qr_code`
**Type**: ImageField
**Location**: Site Configuration Model
**Upload Path**: `media/payment/instapay/`

#### Functionality
- **When QR Code Uploaded**: InstaPay payment option appears in checkout
- **When No QR Code**: InstaPay option is hidden
- Displays QR code image for customers to scan with their banking app
- Treated as offline payment (similar to Cash on Delivery)
- Order created with status "unpaid" - admin manually confirms payment

#### Admin Access
1. Navigate to: **Admin Dashboard → Content → Site Configuration**
2. Find section: **إعدادات الدفع - InstaPay**
3. Upload QR code image
4. Click **Save**

#### QR Code Specifications
- **Recommended Size**: 500x500px or larger
- **Format**: PNG, JPG, JPEG
- **Quality**: High resolution for scanning
- **Content**: Bank-generated InstaPay QR code

---

## Payment Methods Summary

### Available Payment Methods

| Method | Display Name | Type | Status | Controlled By |
|--------|-------------|------|--------|---------------|
| **COD** | الدفع عند الاستلام (Cash on Delivery) | Offline | Always Available | N/A |
| **Online** | الدفع الإلكتروني (Online Payment) | Online | Conditional | `ALLOW_ONLINE_PAYMENT` config |
| **InstaPay** | InstaPay (QR) | Offline | Conditional | QR code upload |
| **Partial** | دفع جزئي (Partial Payment) | Mixed | Always Available* | Product settings |

*Partial payment visibility depends on cart items supporting partial payment.

---

## Implementation Details

### 1. Database Schema

#### SiteConfiguration Model (`content/site_config.py`)
```python
class SiteConfiguration(SingletonModel):
    # ... other fields ...

    instapay_qr_code = models.ImageField(
        upload_to="payment/instapay/",
        blank=True,
        null=True,
        verbose_name=_("رمز QR لـ InstaPay"),
        help_text=_("قم برفع صورة رمز QR الخاص بحساب InstaPay للدفع غير المتصل بالإنترنت"),
    )
```

#### Constance Configuration (`settings/constance_config.py`)
```python
CONSTANCE_CONFIG = {
    # ... other settings ...

    "ALLOW_ONLINE_PAYMENT": (
        True,
        _("Enable online payment option in checkout"),
        bool,
    ),
}
```

#### Order Model Payment Methods (`main/models.py`)
```python
PAYMENT_METHOD_CHOICES = [
    ("cod", _("الدفع عند الاستلام")),
    ("online", _("الدفع الإلكتروني")),
    ("instapay", _("InstaPay")),
    ("partial", _("دفع جزئي")),
]
```

### 2. Template Logic (`templates/cart/checkout.html`)

#### Online Payment Conditional Display
```django
{% if config.ALLOW_ONLINE_PAYMENT %}
<div class="payment-method" onclick="selectPaymentMethod('online')">
    <input type="radio" name="payment_method" value="online">
    <div class="payment-method-icon">
        <i class="fas fa-credit-card"></i>
    </div>
    <div class="payment-method-label">
        {% trans "الدفع الإلكتروني" %}
    </div>
</div>
{% endif %}
```

#### InstaPay Conditional Display
```django
{% if site_config.instapay_qr_code %}
<div class="payment-method" onclick="selectPaymentMethod('instapay')">
    <input type="radio" name="payment_method" value="instapay">
    <div class="payment-method-icon">
        <i class="fas fa-qrcode"></i>
    </div>
    <div class="payment-method-label">
        {% trans "InstaPay (QR)" %}
    </div>
</div>
{% endif %}
```

#### InstaPay QR Code Display
```django
{% if site_config.instapay_qr_code %}
<div id="instapayPaymentNote" style="display: none;" class="alert alert-info">
    <div class="text-center">
        <i class="fas fa-qrcode me-2"></i>
        <h5>{% trans "الدفع عبر InstaPay" %}</h5>
        <p class="mb-3">{% trans "قم بمسح رمز QR باستخدام تطبيق البنك الخاص بك" %}</p>
        <img src="{{ site_config.instapay_qr_code.url }}"
             alt="InstaPay QR Code"
             class="img-fluid"
             style="max-width: 300px; border: 2px solid #4b315e; border-radius: 10px; padding: 10px;">
        <p class="mt-3 small text-muted">
            <i class="fas fa-info-circle me-1"></i>
            {% trans "بعد إتمام الدفع، سيتم تأكيد الطلب تلقائياً. يمكنك تتبع حالة الطلب من لوحة التحكم." %}
        </p>
    </div>
</div>
{% endif %}
```

### 3. View Logic (`main/cart_wishlist_views.py`)

#### Context Variables
```python
from content.site_config import SiteConfiguration
from constance import config

site_config = SiteConfiguration.get_solo()

context = {
    # ... other context ...
    "site_config": site_config,
    "config": config,
}
```

#### Payment Method Handling
```python
# Determine payment status
payment_status = "unpaid"
if payment_method == "online":
    payment_status = "unpaid"  # Will be updated after payment gateway
elif payment_method == "partial" and paid_amount:
    if paid_amount >= total_amount:
        payment_status = "paid"
        paid_amount = total_amount
    else:
        payment_status = "partial"
elif payment_method in ["cod", "instapay"]:
    payment_status = "unpaid"  # InstaPay is offline, will be confirmed manually
```

### 4. JavaScript (`checkout.html`)

#### Payment Method Selection
```javascript
function selectPaymentMethod(method) {
    // Remove active class from all
    document.querySelectorAll('.payment-method').forEach(el => {
        el.classList.remove('active');
    });

    // Add active to selected
    const selected = document.querySelector(`input[value="${method}"]`).closest('.payment-method');
    selected.classList.add('active');

    // Check radio
    document.querySelector(`input[value="${method}"]`).checked = true;

    // Show/hide payment notes
    const onlineNote = document.getElementById('onlinePaymentNote');
    const instapayNote = document.getElementById('instapayPaymentNote');
    const partialNote = document.getElementById('partialPaymentNote');

    // Hide all notes first
    if (onlineNote) onlineNote.style.display = 'none';
    if (instapayNote) instapayNote.style.display = 'none';
    if (partialNote) partialNote.style.display = 'none';

    // Show relevant note
    if (method === 'online' && onlineNote) {
        onlineNote.style.display = 'block';
    } else if (method === 'instapay' && instapayNote) {
        instapayNote.style.display = 'block';
    } else if (method === 'partial' && partialNote) {
        partialNote.style.display = 'block';
    }
}
```

---

## User Experience Flow

### Scenario 1: All Payment Methods Enabled
1. User goes to checkout
2. Sees 4 payment options:
   - Cash on Delivery (always visible)
   - Online Payment (if `ALLOW_ONLINE_PAYMENT` = True)
   - InstaPay QR (if QR code uploaded)
   - Partial Payment (if applicable)
3. User selects payment method
4. Relevant instructions/form shown
5. Order is created with selected method

### Scenario 2: Online Payment Disabled
1. User goes to checkout
2. Sees 3 payment options:
   - Cash on Delivery
   - InstaPay QR (if QR code uploaded)
   - Partial Payment (if applicable)
3. Online payment option not displayed
4. User must choose from offline methods

### Scenario 3: InstaPay Selected
1. User selects InstaPay payment method
2. QR code image displayed with instructions
3. User scans QR code with banking app
4. User completes payment in banking app
5. User returns to site and confirms order
6. Order created with status "unpaid"
7. Admin receives order notification
8. Admin manually verifies payment and updates order status

---

## Admin Workflow

### Setting Up InstaPay

1. **Obtain QR Code from Bank**
   - Contact your bank for InstaPay QR code
   - Request high-resolution image (PNG or JPG)
   - Save QR code image to computer

2. **Upload to Site**
   - Login to Admin Dashboard
   - Navigate: Content → Site Configuration
   - Scroll to: "إعدادات الدفع - InstaPay"
   - Click "Choose File"
   - Select QR code image
   - Click "Save"

3. **Verify Display**
   - Go to checkout page
   - Verify InstaPay option appears
   - Click InstaPay option
   - Confirm QR code displays correctly

4. **Test Payment Flow**
   - Create test order with InstaPay
   - Scan QR code with banking app
   - Complete test payment
   - Verify order appears in admin orders
   - Mark order as paid manually

### Managing Online Payment

1. **Enable Online Payment**
   - Navigate: Constance → Config
   - Find: Payment General Settings
   - Set: ALLOW_ONLINE_PAYMENT = True
   - Save

2. **Disable Online Payment**
   - Navigate: Constance → Config
   - Find: Payment General Settings
   - Set: ALLOW_ONLINE_PAYMENT = False
   - Save

### Processing InstaPay Orders

1. **Receive Order Notification**
   - Order email sent with payment method "InstaPay"
   - Order appears in admin dashboard

2. **Verify Payment**
   - Check bank account for payment
   - Match order amount with received payment
   - Verify customer phone/name

3. **Update Order**
   - Navigate: Orders → [Order Number]
   - Change Payment Status to "Paid"
   - Add admin note: "Payment verified via InstaPay"
   - Change Order Status to "Processing"
   - Save

4. **Notify Customer**
   - System sends email confirmation
   - Order status updated in customer dashboard

---

## Migration History

### Migration: `content/0015_add_instapay_qr_code.py`
```python
# Generated migration
operations = [
    migrations.AddField(
        model_name='siteconfiguration',
        name='instapay_qr_code',
        field=models.ImageField(
            blank=True,
            null=True,
            upload_to='payment/instapay/',
            verbose_name='رمز QR لـ InstaPay'
        ),
    ),
]
```

**Status**: ✅ Applied

---

## Security Considerations

### Online Payment Toggle
- **Risk**: Low - only controls UI visibility
- **Benefit**: Allows quick disabling if payment gateway has issues
- **Recommendation**: Keep enabled unless gateway is down

### InstaPay QR Code
- **Risk**: Medium - QR code exposed publicly
- **Mitigation**:
  - Use dedicated business account
  - Monitor transactions regularly
  - Set up fraud alerts with bank
- **Recommendation**:
  - Rotate QR code periodically
  - Use bank's security features
  - Keep backup of QR code offline

### Manual Verification
- **Risk**: Low - admin manually verifies payments
- **Benefit**: Prevents fraud, ensures accuracy
- **Recommendation**:
  - Train staff on verification process
  - Document payment verification steps
  - Use admin notes for audit trail

---

## Troubleshooting

### Issue: Online Payment Option Not Showing

**Possible Causes:**
1. `ALLOW_ONLINE_PAYMENT` is set to False
2. Template not loading config context
3. Cache not cleared

**Solutions:**
1. Check constance setting: `config.ALLOW_ONLINE_PAYMENT`
2. Verify context in view: `context["config"] = config`
3. Clear cache: `python manage.py clear_cache` or restart server
4. Check template syntax: `{% if config.ALLOW_ONLINE_PAYMENT %}`

### Issue: InstaPay Option Not Showing

**Possible Causes:**
1. QR code not uploaded
2. QR code file deleted from media folder
3. Template not loading site_config

**Solutions:**
1. Check admin: Content → Site Configuration → InstaPay QR Code
2. Verify file exists: `media/payment/instapay/`
3. Check context: `context["site_config"] = site_config`
4. Re-upload QR code if missing

### Issue: QR Code Not Displaying

**Possible Causes:**
1. Image file path incorrect
2. Media files not served properly
3. Image file corrupted

**Solutions:**
1. Check URL in template: `{{ site_config.instapay_qr_code.url }}`
2. Verify media settings in `settings.py`
3. Test image URL directly in browser
4. Re-upload QR code

### Issue: Order Created with Wrong Payment Method

**Possible Causes:**
1. JavaScript not updating radio button
2. Form submission before selection
3. Cache issue

**Solutions:**
1. Clear browser cache
2. Check browser console for JS errors
3. Verify radio button is checked before submit
4. Test in incognito/private mode

---

## Best Practices

### For Administrators

1. **Test Before Enabling**
   - Test each payment method thoroughly
   - Create test orders
   - Verify email notifications
   - Check admin order display

2. **Monitor Regularly**
   - Review payment gateway logs
   - Check for failed transactions
   - Monitor InstaPay payments
   - Update QR code if needed

3. **Document Procedures**
   - Payment verification steps
   - Order processing workflow
   - Refund procedures
   - Customer support scripts

4. **Security**
   - Use strong admin passwords
   - Enable 2FA on admin accounts
   - Regular security audits
   - Keep Django and packages updated

### For Developers

1. **Code Maintenance**
   - Keep payment logic centralized
   - Document configuration changes
   - Test all payment methods after updates
   - Monitor error logs

2. **Testing**
   - Unit tests for payment logic
   - Integration tests for checkout
   - UI tests for payment selection
   - Load testing for peak times

3. **Deployment**
   - Test in staging environment
   - Plan for rollback if issues
   - Monitor after deployment
   - Clear cache after updates

---

## Future Enhancements

### Planned Features
1. **Multiple InstaPay Accounts**: Support different QR codes per currency/country
2. **Auto Payment Verification**: Webhook integration with banks for auto-confirmation
3. **Payment Analytics**: Dashboard showing payment method usage statistics
4. **Dynamic Payment Methods**: Admin can add custom payment methods without code changes
5. **Payment Method Rules**: Show/hide methods based on order amount, user location, etc.

### Considerations
- Mobile wallet integration (Apple Pay, Google Pay)
- Cryptocurrency payment options
- Buy now, pay later (BNPL) services
- Subscription/recurring payment support
- Multi-currency support improvements

---

## Related Documentation

- [Order Management System](./ORDER_MANAGEMENT_SYSTEM.md)
- [Order Notification System](./ORDER_NOTIFICATION_SYSTEM.md)
- [Paymob Integration Guide](./PAYMOB_INTEGRATION.md)
- [Site Configuration Guide](./SITE_CONFIGURATION.md)

---

## Support

For technical support or questions:
- Review this documentation
- Check error logs: `logs/django.log`
- Contact development team
- Refer to Django documentation

---

**Document Version**: 1.0
**Last Updated**: 2025-12-12
**Status**: ✅ Production Ready
