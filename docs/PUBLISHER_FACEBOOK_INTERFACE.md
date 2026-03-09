# Publisher Facebook Share Interface Documentation

## Overview
Complete self-service interface for publishers to track and manage their Facebook share requests, make payments, and monitor the status of their shared ads.

## Features Implemented

### 1. Facebook Requests Dashboard
**URL:** `/publisher/facebook-requests/`
**View:** `PublisherFacebookShareRequestsView`
**Template:** `templates/classifieds/publisher_facebook_requests.html`

#### Features:
- **Statistics Cards:**
  - Total requests count
  - Pending requests count
  - Completed requests count
  - Unpaid requests count

- **Filtering:**
  - Filter by status (pending, in_progress, completed, rejected)
  - Filter by payment status (paid, unpaid)
  - Search by ad title or ID

- **Request Cards:**
  - Ad thumbnail preview
  - Ad title and category
  - Request date
  - Status badge (color-coded)
  - Payment status badge
  - Action buttons (contextual):
    - View details
    - Pay now (if unpaid/pending)
    - View post (if completed with post URL)
    - Cancel (if pending via AJAX)

- **Pagination:** 20 requests per page

#### Statistics:
```python
stats = {
    'total': Total count of all requests,
    'pending': Count of pending requests,
    'in_progress': Count of in-progress requests,
    'completed': Count of completed requests,
    'rejected': Count of rejected requests,
    'unpaid': Count of unpaid requests,
    'total_amount': Total amount paid
}
```

### 2. Payment Page
**URL:** `/publisher/facebook-requests/<request_id>/payment/`
**View:** `PublisherFacebookSharePaymentView`
**Template:** `templates/classifieds/publisher_facebook_payment.html`

#### Features:
- **Ad Summary:** Large preview with full ad details
- **Payment Amount Display:** Gradient box showing price from constance config
- **Payment Methods:**
  - Bank transfer (with expandable bank details)
  - Credit card
  - PayPal
  - Cash payment
- **Bank Details Display:**
  - Bank name
  - Account name
  - Account number
  - IBAN
  - Copy-to-clipboard buttons for each field
- **Payment Proof Upload:**
  - Drag-and-drop file upload
  - Image preview for uploaded files
  - Supports images and PDFs
- **Notes Field:** Optional notes for the payment

#### Payment Processing:
```python
payment = Payment.objects.create(
    user=request.user,
    amount=payment_amount,
    currency='SAR',
    payment_method=payment_method,
    status='pending',
    description=f'Facebook Share Request for Ad: {share_request.ad.title}',
    metadata={
        'facebook_share_request_id': share_request.pk,
        'ad_id': share_request.ad.pk,
        'notes': notes,
    }
)
```

### 3. Request Detail Page
**URL:** `/publisher/facebook-requests/<request_id>/`
**View:** `FacebookShareRequestDetailView`
**Template:** `templates/classifieds/publisher_facebook_request_detail.html`

#### Features:
- **Request Header:**
  - Request ID
  - Current status badge

- **Ad Information Section:**
  - Large ad thumbnail
  - Full ad details (category, price, location, publish date)
  - Link to view ad on site

- **Timeline View:**
  - Request creation milestone
  - Admin notes (if any)
  - Processing status update
  - Facebook post publication (if completed)
  - Visual timeline with color-coded icons

- **Payment History:**
  - List of all payment attempts
  - Payment status badges
  - Payment method display
  - Payment proof download links
  - Empty state with call-to-action if no payments

- **Action Buttons:**
  - Back to list
  - Pay now (if pending and unpaid)
  - Cancel request (if pending)
  - View Facebook post (if completed)

### 4. Cancel Request (AJAX)
**URL:** `/publisher/facebook-requests/<request_id>/cancel/`
**View:** `CancelFacebookShareRequestView`
**Method:** POST (AJAX)

#### Features:
- Validates request is in 'pending' status
- Updates ad flags (share_on_facebook, facebook_share_requested)
- Deletes the request
- Returns JSON response
- Shows confirmation dialog before canceling

#### Response:
```json
{
    "success": true,
    "message": "تم إلغاء الطلب بنجاح"
}
```

## Navigation Integration

### Publisher Dashboard Navigation
Added new navigation item in `templates/dashboard/partials/_publisher_nav.html`:

```html
<!-- Facebook Share Requests -->
<a href="{% url 'main:publisher_facebook_requests' %}"
   class="publisher-nav-item {% if active_nav == 'facebook_requests' %}active{% endif %}">
  <i class="fab fa-facebook-square"></i>
  <span>{% trans "طلبات فيسبوك" %}</span>
  {% if facebook_unpaid_count %}
  <span class="badge bg-danger rounded-pill ms-2">{{ facebook_unpaid_count }}</span>
  {% endif %}
</a>
```

Location: Between "رسائلي" (My Messages) and "حالة التوثيق" (Verification Status)

## URL Configuration

All routes added to `main/urls.py`:

```python
# Publisher Facebook Share Requests
path(
    "publisher/facebook-requests/",
    publisher_facebook_views.PublisherFacebookShareRequestsView.as_view(),
    name="publisher_facebook_requests",
),
path(
    "publisher/facebook-requests/<int:request_id>/",
    publisher_facebook_views.FacebookShareRequestDetailView.as_view(),
    name="publisher_facebook_request_detail",
),
path(
    "publisher/facebook-requests/<int:request_id>/payment/",
    publisher_facebook_views.PublisherFacebookSharePaymentView.as_view(),
    name="publisher_facebook_payment",
),
path(
    "publisher/facebook-requests/<int:request_id>/cancel/",
    publisher_facebook_views.CancelFacebookShareRequestView.as_view(),
    name="cancel_facebook_request",
),
```

## Configuration Requirements

### Constance Settings:
```python
FACEBOOK_SHARE_PRICE = Decimal('50.00')  # Price per share request
BANK_NAME = 'البنك الأهلي السعودي'
BANK_ACCOUNT_NAME = 'إدريسي مارت'
BANK_ACCOUNT_NUMBER = 'SA00 0000 0000 0000 0000'
BANK_IBAN = 'SA00 0000 0000 0000 0000'
```

## Security

### Authentication & Authorization:
- All views use `LoginRequiredMixin`
- All querysets filtered by `ad__user=self.request.user`
- Only ad owners can view/manage their requests
- Cancel is restricted to 'pending' status only

## User Flow

### Happy Path:
1. Publisher creates ad with "Share on Facebook" checkbox
2. Publisher navigates to "طلبات فيسبوك" in dashboard
3. Views list of all their requests with statistics
4. Clicks "دفع الآن" (Pay Now) button
5. Completes payment form with preferred method
6. Uploads payment proof (optional)
7. Submits payment
8. Request status updated to 'pending' with payment_confirmed=False
9. Admin reviews and processes payment
10. Admin shares ad on Facebook
11. Publisher can view post via "عرض المنشور" button

### Cancel Flow:
1. Publisher views requests list
2. Clicks "إلغاء" (Cancel) on pending request
3. Confirms in dialog
4. AJAX request sent to cancel endpoint
5. Ad flags updated, request deleted
6. Page refreshes with updated list

## Styling

### Color Scheme:
- **Facebook Blue:** `#1877f2` (gradients with `#0d5dbf`)
- **Success:** `#10b981` (green)
- **Warning:** `#f59e0b` (orange)
- **Danger:** `#ef4444` (red)
- **Info:** `#3b82f6` (blue)

### Key CSS Classes:
- `.facebook-gradient-header` - Header with Facebook branding
- `.stat-card` - Statistics cards with hover effects
- `.request-card` - Individual request cards
- `.payment-method` - Payment method selection cards
- `.timeline` - Vertical timeline for request history

## AJAX Features

### Cancel Request:
```javascript
fetch('/publisher/facebook-requests/' + requestId + '/cancel/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
    }
})
```

### Copy to Clipboard:
```javascript
navigator.clipboard.writeText(text).then(() => {
    // Show success toast
});
```

## Testing Checklist

### Listing Page:
- [ ] Statistics display correctly
- [ ] Filters work (status, payment_status, search)
- [ ] Pagination works
- [ ] Action buttons show contextually
- [ ] Cancel AJAX works for pending requests
- [ ] Empty state displays when no requests

### Payment Page:
- [ ] Ad summary displays correctly
- [ ] Payment amount from config
- [ ] Payment methods selectable
- [ ] Bank details show for bank transfer
- [ ] File upload works (drag-and-drop + click)
- [ ] Image preview shows for uploaded images
- [ ] Copy to clipboard works
- [ ] Form submission creates Payment record
- [ ] Redirect to requests list after payment

### Detail Page:
- [ ] Request header shows status
- [ ] Ad information complete
- [ ] Timeline shows all milestones
- [ ] Payment history displays
- [ ] Action buttons show contextually
- [ ] Facebook post link works (if completed)
- [ ] Cancel button works (if pending)

### Navigation:
- [ ] Tab shows in publisher dashboard
- [ ] Active state works on all pages
- [ ] Badge shows unpaid count (if implemented)

## Future Enhancements

### Potential Additions:
1. **Real-time Notifications:** WebSocket notifications when status changes
2. **Payment Gateway Integration:** Direct credit card processing
3. **Bulk Requests:** Select multiple ads for Facebook sharing
4. **Analytics:** Track post performance (likes, shares, clicks)
5. **Scheduled Sharing:** Choose specific date/time for sharing
6. **Auto-renewal:** Automatically renew share requests for popular ads
7. **Share Templates:** Preview how ad will look on Facebook
8. **A/B Testing:** Test different post formats

## Related Files

### Views:
- `main/publisher_facebook_views.py` (242 lines)

### Templates:
- `templates/classifieds/publisher_facebook_requests.html` (listing)
- `templates/classifieds/publisher_facebook_payment.html` (payment form)
- `templates/classifieds/publisher_facebook_request_detail.html` (detail view)
- `templates/dashboard/partials/_publisher_nav.html` (navigation)

### Configuration:
- `main/urls.py` (URL routing)

### Models Used:
- `FacebookShareRequest` (main/models.py)
- `ClassifiedAd` (main/models.py)
- `Payment` (main/models.py)

## Support

For issues or questions:
1. Check error logs in Django admin
2. Verify constance settings are configured
3. Ensure Payment model has metadata field
4. Check user permissions and ad ownership
5. Verify Facebook post URLs are valid
