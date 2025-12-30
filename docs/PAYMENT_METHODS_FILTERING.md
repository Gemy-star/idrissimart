# نظام فلترة وسائل الدفع حسب السياق
## Payment Methods Filtering System

## نظرة عامة | Overview

تم إنشاء نظام ذكي لفلترة وسائل الدفع المتاحة بناءً على **سياق الدفع**:
- **الدفع للمنصة** (User → Platform): الباقات، رسوم الإعلانات، المميزات المدفوعة
- **الدفع بين المستخدمين** (User → User): شراء المنتجات عبر السلة

A smart system for filtering available payment methods based on **payment context**:
- **Platform Payments** (User → Platform): Packages, ad fees, paid features
- **User-to-User Payments** (User → User): Product purchases via cart

---

## القواعد الأساسية | Core Rules

### 1. الدفع من المستخدم للمنصة | Platform Payments

**الوسائل المسموحة فقط:**
- ✅ **بطاقة فيزا/ماستركارد** (Visa/Mastercard)
- ✅ **محفظة إلكترونية** (E-Wallet)
- ✅ **إنستاباي** (InstaPay)

**الوسائل المحظورة:**
- ❌ **الدفع عند الاستلام** (Cash on Delivery - COD)
- ❌ **الدفع الجزئي** (Partial Payment)

**السبب:**
- الدفع للمنصة يتطلب تأكيد فوري وتحويل إلكتروني
- لا يمكن قبول الدفع عند الاستلام أو الدفع الجزئي للرسوم الإدارية

### 2. الدفع بين المستخدمين | Cart Purchases

**جميع الوسائل متاحة:**
- ✅ **بطاقة فيزا/ماستركارد** (Visa/Mastercard)
- ✅ **محفظة إلكترونية** (E-Wallet)
- ✅ **إنستاباي** (InstaPay)
- ✅ **الدفع عند الاستلام** (Cash on Delivery - COD)
- ✅ **الدفع الجزئي** (Partial Payment)

**السبب:**
- البيع بين المستخدمين يسمح بمرونة أكبر في طرق الدفع
- البائع والمشتري يتفقان على طريقة الدفع المناسبة

---

## الملفات الجديدة | New Files

### main/payment_utils.py

**الغرض:** ملف utility مركزي لفلترة وسائل الدفع

```python
"""Payment utilities for filtering allowed payment methods"""

from django.utils.translation import gettext_lazy as _


class PaymentContext:
    """Payment context types"""
    PLATFORM_PAYMENT = "platform"  # User paying to platform (packages, ad fees, features)
    CART_PURCHASE = "cart"  # User buying from another user via cart


def get_allowed_payment_methods(context=PaymentContext.PLATFORM_PAYMENT):
    """
    Get allowed payment methods based on payment context.

    Args:
        context: Payment context (platform or cart)

    Returns:
        List of tuples (value, label) for allowed payment methods
    """

    # All available payment methods
    ALL_METHODS = [
        ("visa", _("بطاقة فيزا/ماستركارد - Visa/Mastercard")),
        ("wallet", _("محفظة إلكترونية - E-Wallet")),
        ("instapay", _("إنستاباي - InstaPay")),
        ("cod", _("الدفع عند الاستلام - Cash on Delivery")),
        ("partial", _("دفع جزئي - Partial Payment")),
    ]

    if context == PaymentContext.PLATFORM_PAYMENT:
        # For platform payments: Only online methods allowed
        # User paying to platform for packages, ad fees, features
        return [
            ("visa", _("بطاقة فيزا/ماستركارد - Visa/Mastercard")),
            ("wallet", _("محفظة إلكترونية - E-Wallet")),
            ("instapay", _("إنستاباي - InstaPay")),
        ]

    elif context == PaymentContext.CART_PURCHASE:
        # For cart purchases: All methods allowed
        # User buying from another user
        return ALL_METHODS

    else:
        # Default: online methods only
        return [
            ("visa", _("بطاقة فيزا/ماستركارد - Visa/Mastercard")),
            ("wallet", _("محفظة إلكترونية - E-Wallet")),
            ("instapay", _("إنستاباي - InstaPay")),
        ]


def is_payment_method_allowed(payment_method, context=PaymentContext.PLATFORM_PAYMENT):
    """
    Check if a payment method is allowed for the given context.

    Args:
        payment_method: Payment method to check
        context: Payment context

    Returns:
        bool: True if allowed, False otherwise
    """
    allowed_methods = get_allowed_payment_methods(context)
    allowed_values = [method[0] for method in allowed_methods]
    return payment_method in allowed_values


def get_payment_method_display(payment_method):
    """Get display name for payment method"""
    all_methods = {
        "visa": _("بطاقة فيزا/ماستركارد"),
        "wallet": _("محفظة إلكترونية"),
        "instapay": _("إنستاباي"),
        "cod": _("الدفع عند الاستلام"),
        "partial": _("دفع جزئي"),
    }
    return all_methods.get(payment_method, payment_method)
```

---

## الملفات المعدلة | Modified Files

### 1. main/payment_views.py

#### package_checkout View

**التغييرات:**

```python
@login_required
def package_checkout(request, package_id):
    """Checkout page for package purchase with offline/online payment options"""
    from content.models import SiteConfiguration
    from .payment_utils import get_allowed_payment_methods, PaymentContext  # ← NEW

    package = get_object_or_404(AdPackage, id=package_id, is_active=True)
    site_config = SiteConfiguration.get_solo()

    # ... session verification ...

    total_amount = package.price

    # Get allowed payment methods for platform payments ← NEW
    allowed_payment_methods = get_allowed_payment_methods(PaymentContext.PLATFORM_PAYMENT)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # Validate payment method is allowed for platform payments ← NEW
        from .payment_utils import is_payment_method_allowed
        if not is_payment_method_allowed(payment_method, PaymentContext.PLATFORM_PAYMENT):
            messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
            return redirect("main:package_checkout", package_id=package.id)

        # Handle instapay and wallet (online methods with receipt) ← UPDATED
        if payment_method in ["instapay", "wallet"]:
            # ... handle receipt upload ...

        # Handle visa/card (online payment gateway) ← UPDATED
        elif payment_method in ["paymob", "paypal", "visa", "card"]:
            # ... redirect to payment gateway ...

    context = {
        "package": package,
        "total_amount": total_amount,
        "site_config": site_config,
        "allowed_payment_methods": allowed_payment_methods,  # ← NEW
        "allow_offline_payment": site_config.allow_offline_payment,
        "offline_payment_instructions": site_config.offline_payment_instructions,
    }

    return render(request, "payments/package_checkout.html", context)
```

#### ad_payment View

**التغييرات المشابهة:**

```python
@login_required
def ad_payment(request, ad_id):
    """Payment page for new ad with features"""
    from .models import ClassifiedAd
    from content.models import SiteConfiguration
    from .payment_utils import get_allowed_payment_methods, PaymentContext  # ← NEW

    ad = get_object_or_404(ClassifiedAd, id=ad_id, user=request.user)
    site_config = SiteConfiguration.get_solo()

    # ... get payment details from session ...

    # Get allowed payment methods for platform payments ← NEW
    allowed_payment_methods = get_allowed_payment_methods(PaymentContext.PLATFORM_PAYMENT)

    # ... same validation and payment processing as package_checkout ...

    context = {
        "ad": ad,
        "total_amount": total_amount,
        "base_fee": base_fee,
        "features_cost": features_cost,
        "features": features,
        "site_config": site_config,
        "allowed_payment_methods": allowed_payment_methods,  # ← NEW
    }

    return render(request, "payments/ad_payment.html", context)
```

### 2. templates/payments/package_checkout.html

**التغييرات:**

```html
<!-- OLD: Conditional display based on allow_offline_payment -->
{% if allow_offline_payment %}
    <!-- instapay, wallet -->
{% else %}
    <!-- card, paymob, paypal -->
{% endif %}

<!-- NEW: Always show only platform-allowed methods -->
<!-- Visa/Card Payment -->
<div class="payment-method-card" data-payment="visa" onclick="selectPaymentMethod('visa')">
    <div class="d-flex align-items-center">
        <input type="radio" name="payment_method" value="visa" id="visa" style="margin-left: 15px;">
        <div class="flex-grow-1">
            <h5 class="mb-1">
                <i class="fas fa-credit-card me-2 text-info"></i>
                {% trans "بطاقة فيزا/ماستركارد" %}
            </h5>
            <p class="text-muted small mb-0">{% trans "الدفع الإلكتروني عبر بطاقة Visa أو Mastercard" %}</p>
        </div>
    </div>
</div>

<!-- Wallet Payment -->
<div class="payment-method-card" data-payment="wallet" onclick="selectPaymentMethod('wallet')">
    <!-- ... wallet with receipt upload ... -->
</div>

<!-- Instapay Payment -->
<div class="payment-method-card" data-payment="instapay" onclick="selectPaymentMethod('instapay')">
    <!-- ... instapay with receipt upload ... -->
</div>

<!-- Notice about payment methods -->
<div class="alert alert-info mt-3">
    <i class="fas fa-info-circle me-2"></i>
    {% trans "للدفع من المستخدم للمنصة، الطرق المتاحة هي: بطاقة فيزا/ماستركارد، محفظة إلكترونية، أو إنستاباي فقط." %}
</div>
```

**JavaScript Updates:**

```javascript
function selectPaymentMethod(method) {
    // Remove selected class from all cards
    document.querySelectorAll('.payment-method-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add selected class to clicked card
    event.currentTarget.classList.add('selected');

    // Hide all offline payment details
    const instapayDetails = document.getElementById('instapayDetails');
    const walletDetails = document.getElementById('walletDetails');

    // Hide all receipt fields first and make them not required
    document.querySelectorAll('.payment-receipt').forEach(field => {
        field.required = false;
    });

    // Handle each payment method
    if (method === 'instapay') {
        if (instapayDetails) {
            instapayDetails.style.display = 'block';
            document.getElementById('instapay_receipt').required = true;
        }
        if (walletDetails) walletDetails.style.display = 'none';
        document.getElementById('instapay').checked = true;
    } else if (method === 'wallet') {
        if (walletDetails) {
            walletDetails.style.display = 'block';
            document.getElementById('wallet_receipt').required = true;
        }
        if (instapayDetails) instapayDetails.style.display = 'none';
        document.getElementById('wallet').checked = true;
    } else if (method === 'visa') {
        if (instapayDetails) instapayDetails.style.display = 'none';
        if (walletDetails) walletDetails.style.display = 'none';
        document.getElementById('visa').checked = true;
    }
}
```

---

## منطق تحويل حالة الإعلان | Ad Status Workflow

### السير الكامل | Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│  المستخدم ينشئ إعلان جديد                                   │
│  User creates new ad                                        │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │  حالة: DRAFT        │
                    │  Status: DRAFT      │
                    └──────────┬──────────┘
                               ↓
                ┌──────────────────────────────┐
                │ هل يوجد تكلفة للإعلان؟       │
                │ Is there a cost for the ad?  │
                └──────┬───────────────┬────────┘
                       ↓               ↓
                   نعم (Yes)       لا (No - Free)
                       ↓               ↓
        ┌──────────────────────┐      ↓
        │ تحويل لصفحة الدفع     │      ↓
        │ Redirect to payment  │      ↓
        └──────┬───────────────┘      ↓
               ↓                      ↓
        ┌──────────────────┐          ↓
        │ اختيار وسيلة دفع  │          ↓
        │ Select payment   │          ↓
        │ (Visa/Wallet/    │          ↓
        │  InstaPay ONLY)  │          ↓
        └──────┬───────────┘          ↓
               ↓                      ↓
        ┌──────────────────┐          ↓
        │ إتمام الدفع      │          ↓
        │ Complete payment │          ↓
        └──────┬───────────┘          ↓
               ↓                      ↓
        ┌──────────────────┐          ↓
        │ تأكيد الدفع      │          ↓
        │ Payment confirmed│          ↓
        └──────┬───────────┘          ↓
               ↓                      ↓
        ┌──────────────────────────────┴──────┐
        │ هل المستخدم موثق؟                   │
        │ Is user verified?                   │
        └──────┬──────────────────┬────────────┘
               ↓                  ↓
           نعم (Yes)          لا (No)
               ↓                  ↓
     ┌─────────────────┐  ┌──────────────────┐
     │ حالة: ACTIVE    │  │ حالة: PENDING    │
     │ Status: ACTIVE  │  │ Status: PENDING  │
     │                 │  │                  │
     │ نشط مباشرة      │  │ قيد المراجعة     │
     │ Active directly │  │ Under review     │
     └─────────────────┘  └────────┬─────────┘
                                   ↓
                          ┌────────────────────┐
                          │ مراجعة المحتوى     │
                          │ Content review     │
                          └────────┬───────────┘
                                   ↓
                          ┌────────────────────┐
                          │ موافقة الإدارة     │
                          │ Admin approval     │
                          └────────┬───────────┘
                                   ↓
                          ┌─────────────────┐
                          │ حالة: ACTIVE    │
                          │ Status: ACTIVE  │
                          └─────────────────┘
```

### الكود المسؤول | Responsible Code

**في** `main/classifieds_views.py` → `ClassifiedAdCreateView.form_valid()`:

```python
# Line 378
# Always save ad as DRAFT first
form.instance.status = ClassifiedAd.AdStatus.DRAFT

# ... save ad ...

if total_cost > 0:
    # There's a cost - redirect to payment
    return redirect("main:ad_payment", ad_id=self.object.pk)
else:
    # Free ad - process immediately
    if self.request.user.verification_status == User.VerificationStatus.VERIFIED:
        self.object.status = ClassifiedAd.AdStatus.ACTIVE
    else:
        self.object.status = ClassifiedAd.AdStatus.PENDING
    self.object.save()
```

**في** `main/payment_views.py` → `process_ad_payment()`:

```python
# Lines 496-503
# Change status from DRAFT to PENDING or ACTIVE
if ad.status == ClassifiedAd.AdStatus.DRAFT:
    # Check if user is verified
    if ad.user.verification_status == User.VerificationStatus.VERIFIED:
        ad.status = ClassifiedAd.AdStatus.ACTIVE
        status_msg = _("نشط")
    else:
        ad.status = ClassifiedAd.AdStatus.PENDING
        status_msg = _("قيد المراجعة")

    ad.save()

    # Send notification to user
    Notification.objects.create(
        user=ad.user,
        notification_type=Notification.NotificationType.GENERAL,
        title=_("تم تأكيد الدفع"),
        message=_("تم تأكيد دفع إعلانك {} وتحويله إلى {}.").format(ad.title, status_msg),
        link=ad.get_absolute_url(),
    )
```

---

## سيناريوهات الاستخدام | Use Cases

### سيناريو 1: مستخدم جديد يشتري باقة

```
1. User: يذهب إلى /packages/
2. User: يختار باقة (مثلاً: "باقة القياسية - 10 إعلانات")
3. System: Redirect to /packages/checkout/5/
4. System: يعرض فقط: Visa, Wallet, InstaPay
5. User: يختار "Visa"
6. System: Redirect to payment gateway (Paymob)
7. User: يدفع بنجاح
8. System: Payment confirmed → creates UserPackage
9. System: Notification sent to user
10. User: يمكنه الآن نشر 10 إعلانات مجاناً
```

### سيناريو 2: مستخدم يحاول استخدام COD للباقة

```
1. User: في صفحة checkout للباقة
2. User: يحاول اختيار "COD" (لكن الخيار غير موجود!)
3. System: فقط Visa, Wallet, InstaPay متاحة
4. Alternative: User يحاول POST request يدوي مع payment_method=cod
5. System: Validation fails
6. System: Error message: "طريقة الدفع المختارة غير متاحة للدفع للمنصة."
7. System: Redirect back to checkout page
```

### سيناريو 3: مستخدم موثق ينشر إعلان بدفع

```
1. User: (verified user) creates new ad
2. System: No active package → redirect to pricing
3. User: Chooses "Post Ad Now" (pay per ad)
4. System: Redirect to /classifieds/create/?pay_per_ad=true
5. User: Fills form, selects features
6. System: Total cost = 57.50 SAR (base + tax + features)
7. System: Save ad as DRAFT → redirect to /payments/ad/123/
8. System: Shows only Visa, Wallet, InstaPay
9. User: Selects "InstaPay" → uploads receipt
10. System: Creates Payment (status=PENDING)
11. Admin: Confirms payment in admin dashboard
12. System: process_ad_payment() called
13. System: User is VERIFIED → ad.status = ACTIVE
14. System: Notification: "تم تأكيد دفع إعلانك وتحويله إلى نشط."
15. User: Ad is LIVE immediately
```

### سيناريو 4: مستخدم غير موثق ينشر إعلان بدفع

```
(Same as Scenario 3, but:)

13. System: User is NOT VERIFIED → ad.status = PENDING
14. System: Notification: "تم تأكيد دفع إعلانك وتحويله إلى قيد المراجعة."
15. Admin: Reviews ad content
16. Admin: Approves ad → status = ACTIVE
17. User: Receives notification → ad is LIVE
```

### سيناريو 5: شراء منتج من سلة (Cart Purchase)

```
1. User: Adds products to cart
2. User: Proceeds to checkout
3. System: Context = CART_PURCHASE
4. System: Shows ALL payment methods:
   - Visa
   - Wallet
   - InstaPay
   - COD ← AVAILABLE for cart!
   - Partial Payment ← AVAILABLE for cart!
5. User: Selects "COD" → order created
6. System: Seller receives order notification
7. Seller: Prepares and ships product
8. User: Pays on delivery
```

---

## الأمان | Security

### 1. Server-Side Validation

```python
# ALWAYS validate on server-side
if not is_payment_method_allowed(payment_method, PaymentContext.PLATFORM_PAYMENT):
    messages.error(request, _("طريقة الدفع المختارة غير متاحة للدفع للمنصة."))
    return redirect(...)
```

**Why:**
- المستخدم يمكنه تعديل HTML/JavaScript
- POST requests يمكن إرسالها يدوياً
- Server-side validation هي الضمان الوحيد

### 2. Payment Method Mapping

```python
# Map payment method to provider
if payment_method in ["paymob", "visa", "card"]:
    provider = Payment.PaymentProvider.PAYMOB
elif payment_method == "paypal":
    provider = Payment.PaymentProvider.PAYPAL
```

### 3. Payment Confirmation

```python
# Only process_ad_payment if payment is COMPLETED
payment.mark_completed(transaction_id)
success = process_ad_payment(payment)
```

---

## الاختبار | Testing

### Test Case 1: Package Checkout with Visa

```bash
# Test as regular user
1. Login as user without package
2. Go to /packages/
3. Select "Standard Package"
4. Choose "Visa" payment method
5. Verify redirect to Paymob gateway
6. Complete payment
7. Verify UserPackage created
8. Verify notification sent
```

### Test Case 2: Package Checkout with COD (Should Fail)

```bash
# Test server-side validation
1. Login as regular user
2. Go to /packages/checkout/5/
3. Inspect HTML and add:
   <input type="radio" name="payment_method" value="cod" id="cod">
4. Select "COD" and submit
5. Expected: Error message + redirect
6. Verify no payment created
7. Verify no package created
```

### Test Case 3: Ad Payment for Verified User

```bash
# Test ad workflow for verified user
1. Login as verified user (verification_status=VERIFIED)
2. Create new ad without package
3. Add features (highlighted, urgent)
4. Submit form
5. Verify ad status = DRAFT
6. Complete payment with Wallet
7. Admin confirms payment
8. Verify ad status = ACTIVE (skip PENDING)
9. Verify notification sent
```

### Test Case 4: Ad Payment for Unverified User

```bash
# Test ad workflow for unverified user
1. Login as unverified user
2. Create new ad without package
3. Submit form
4. Complete payment with InstaPay
5. Admin confirms payment
6. Verify ad status = PENDING (not ACTIVE)
7. Admin reviews and approves
8. Verify ad status = ACTIVE
9. Verify notifications sent at each step
```

### Test Case 5: Cart Purchase with COD

```bash
# Test cart purchase allows COD
1. Browse products
2. Add to cart
3. Proceed to checkout
4. Verify "COD" option is AVAILABLE
5. Select COD
6. Submit order
7. Verify order created with payment_method=cod
8. Verify seller notified
```

---

## ملاحظات التطوير | Development Notes

### Future Enhancements

1. **Dynamic Payment Methods:**
   ```python
   # Could be configured per-category or per-package
   category.allowed_payment_methods = ["visa", "wallet"]
   package.allowed_payment_methods = ["visa", "instapay"]
   ```

2. **Payment Method Fees:**
   ```python
   # Different fees for different payment methods
   visa_fee = 2.5%  # Gateway fee
   wallet_fee = 1.0%  # Lower fee
   instapay_fee = 0.5%  # Lowest fee
   ```

3. **Geographic Restrictions:**
   ```python
   # Limit payment methods by user location
   if user.country == "EG":
       allowed_methods.append("instapay")
   if user.country == "SA":
       allowed_methods.append("mada")
   ```

4. **Subscription-Based Access:**
   ```python
   # Premium users get access to all payment methods
   if user.is_premium:
       return ALL_METHODS
   ```

### Migration Guide

إذا كنت تريد تطبيق هذا النظام على موقع موجود:

1. **Create payment_utils.py:**
   ```bash
   cp payment_utils.py main/
   ```

2. **Update Views:**
   ```python
   # In each payment view, add:
   from .payment_utils import get_allowed_payment_methods, PaymentContext
   allowed_payment_methods = get_allowed_payment_methods(PaymentContext.PLATFORM_PAYMENT)
   ```

3. **Update Templates:**
   ```html
   <!-- Replace hardcoded payment methods with filtered list -->
   {% for method in allowed_payment_methods %}
       <div class="payment-method-card">...</div>
   {% endfor %}
   ```

4. **Add Validation:**
   ```python
   # In POST handler:
   if not is_payment_method_allowed(payment_method, context):
       # Reject request
   ```

5. **Test Thoroughly:**
   ```bash
   python manage.py test main.tests.test_payment_filtering
   ```

---

## الخلاصة | Summary

✅ **تم التنفيذ:**
1. نظام فلترة وسائل الدفع حسب السياق
2. فصل كامل بين الدفع للمنصة والدفع بين المستخدمين
3. Server-side validation لجميع طرق الدفع
4. منطق تحويل الإعلان من DRAFT → PENDING/ACTIVE
5. تكامل كامل مع نظام التوثيق (Verified Users)

✅ **الفوائد:**
- أمان أعلى في المعاملات المالية
- تجربة مستخدم أفضل (خيارات واضحة)
- مرونة في إضافة وسائل دفع جديدة
- سهولة الصيانة والتطوير

✅ **ملفات جديدة:**
- `main/payment_utils.py` (81 lines)

✅ **ملفات معدلة:**
- `main/payment_views.py` (package_checkout, ad_payment)
- `templates/payments/package_checkout.html`
- منطق تحويل الإعلان موجود بالفعل في `process_ad_payment()`

---

**تاريخ الإنشاء | Creation Date:** 2025-12-30
**الإصدار | Version:** 1.0
**الحالة | Status:** ✅ مكتمل | Completed
