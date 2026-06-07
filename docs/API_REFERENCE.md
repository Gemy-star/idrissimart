# Idrissimart API Reference

Base URL: `/api/`  
Interactive docs: `/api/swagger/` · `/api/redoc/`

---

## Authentication

All protected endpoints require a JWT Bearer token:

```
Authorization: Bearer <access_token>
```

### Obtain token

```
POST /api/auth/token/
```

**Body**
```json
{ "username": "alice", "password": "secret" }
```

**Response**
```json
{ "access": "<jwt>", "refresh": "<jwt>" }
```

### Refresh token

```
POST /api/auth/token/refresh/
```

**Body**
```json
{ "refresh": "<refresh_token>" }
```

**Response**
```json
{ "access": "<new_jwt>" }
```

### Forgot password

```
POST /api/auth/forgot-password/
```

Always returns `200` (email enumeration prevention).

**Body**
```json
{ "email": "alice@example.com" }
```

### Reset password

```
POST /api/auth/reset-password/
```

**Body**
```json
{ "uid": "<uid>", "token": "<token>", "password": "newpass", "password_confirm": "newpass" }
```

### Send phone OTP

```
POST /api/auth/send-otp/
```

**Body**
```json
{ "phone": "+201012345678" }
```

### Verify phone OTP

```
POST /api/auth/verify-otp/
```

**Body**
```json
{ "phone": "+201012345678", "otp": "123456" }
```

---

## Users — `/api/users/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/users/` | Public | Register a new account |
| `GET` | `/api/users/{id}/` | Optional | Get public user profile |
| `PUT/PATCH` | `/api/users/{id}/` | Required (own account or staff) | Update user |
| `DELETE` | `/api/users/{id}/` | Required (own account or staff) | Delete account |
| `GET` | `/api/users/me/` | Required | Get own full profile |
| `PATCH` | `/api/users/update_profile/` | Required | Update own profile |
| `GET` | `/api/users/{id}/ads/` | Optional | Get user's active ads |
| `GET` | `/api/users/{id}/reviews/` | Optional | Get reviews on user's ads |

### Register

**Body**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret123",
  "password_confirm": "secret123",
  "first_name": "Alice",
  "last_name": "Smith",
  "phone": "+201012345678",
  "mobile": "+201012345678",
  "profile_type": "individual",
  "country": 1,
  "city": "Cairo"
}
```

`profile_type` values: `individual`, `company`, `real_estate`

### Update profile (`PATCH /api/users/update_profile/`)

Accepts any subset of:
```json
{
  "first_name": "Alice",
  "bio": "English bio",
  "bio_ar": "النبذة بالعربي",
  "company_name": "Acme",
  "company_name_ar": "أكمي",
  "profile_image": "<file>",
  "cover_image": "<file>",
  "website": "https://example.com",
  "facebook": "...",
  "twitter": "...",
  "instagram": "...",
  "linkedin": "..."
}
```

---

## Countries — `/api/countries/`

Public. Read-only.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/countries/` | List active countries |
| `GET` | `/api/countries/{id}/` | Country detail |

**Filters & search:** `?search=egypt` searches `name`, `name_en`, `code`.  
**Ordering:** `?ordering=order` or `?ordering=name`.

---

## Categories — `/api/categories/`

Public. Read-only.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/categories/` | List active categories |
| `GET` | `/api/categories/{id}/` | Category detail with subcategories and custom fields |
| `GET` | `/api/categories/{id}/ads/` | Ads inside a category |
| `GET` | `/api/categories/root_categories/` | Top-level categories only |

**Query params**

| Param | Example | Description |
|-------|---------|-------------|
| `section_type` | `?section_type=classifieds` | Filter by section |
| `parent` | `?parent=5` | Filter by parent category ID |
| `country` | `?country=1` | Filter by country |
| `search` | `?search=cars` | Search `name` / `name_ar` |
| `ordering` | `?ordering=order` | Sort by `name` or `order` |

For `ads` action, extra params: `?min_price=100&max_price=5000&city=Cairo`

---

## Classified Ads — `/api/ads/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/ads/` | Public | List active ads |
| `POST` | `/api/ads/` | Required | Create ad |
| `GET` | `/api/ads/{id}/` | Public | Ad detail (increments view count) |
| `PUT/PATCH` | `/api/ads/{id}/` | Required (owner) | Update ad |
| `DELETE` | `/api/ads/{id}/` | Required (owner) | Delete ad |
| `GET` | `/api/ads/featured/` | Public | Highlighted ads (up to 10) |
| `GET` | `/api/ads/urgent/` | Public | Urgent ads (up to 10) |
| `GET` | `/api/ads/recent/` | Public | Most recent ads (up to 20) |
| `GET` | `/api/ads/my_ads/` | Required | Own ads (all statuses) |
| `POST` | `/api/ads/{id}/toggle_favorite/` | Required | Add/remove from favourites |
| `POST` | `/api/ads/{id}/review/` | Required | Submit a review |

**Filters**

| Param | Example | Description |
|-------|---------|-------------|
| `category` | `?category=3` | Category ID |
| `country` | `?country=1` | Country ID |
| `city` | `?city=Cairo` | City string |
| `status` | `?status=active` | `active`, `pending`, `expired` |
| `is_highlighted` | `?is_highlighted=true` | Featured ads |
| `is_urgent` | `?is_urgent=true` | Urgent ads |
| `is_pinned` | `?is_pinned=true` | Pinned ads |
| `min_price` | `?min_price=100` | Minimum price |
| `max_price` | `?max_price=5000` | Maximum price |
| `search` | `?search=toyota` | Full-text search on title + description |
| `ordering` | `?ordering=-created_at` | `created_at`, `price`, `views_count` |

### Create ad

`Content-Type: multipart/form-data`

```
title          string       required
category       int (ID)     required
description    string       required
price          decimal      required
is_negotiable  bool         optional
country        int (ID)     optional
city           string       optional
address        string       optional
is_highlighted bool         optional
is_urgent      bool         optional
custom_fields  json object  optional  e.g. {"color": "red", "year": "2020"}
video_url      string       optional
images         file[]       optional  (first image becomes primary)
```

### Review an ad (`POST /api/ads/{id}/review/`)

```json
{ "rating": 5, "comment": "Great seller!" }
```

---

## Blogs — `/api/blogs/`

Public. Read-only.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/blogs/` | Public | List published posts |
| `GET` | `/api/blogs/{id}/` | Public | Post detail + comments (increments views) |
| `POST` | `/api/blogs/{id}/like/` | Required | Toggle like |
| `POST` | `/api/blogs/{id}/comment/` | Required | Add comment |

**Blog categories:** `GET /api/blog-categories/` — list/retrieve blog categories.

**Filters:** `?category=2&author=5`  
**Search:** `?search=market`  
**Ordering:** `?ordering=-published_date` or `?ordering=views_count`

### Add comment

```json
{ "body": "Great article!", "parent": null }
```

Set `"parent": <comment_id>` to reply to an existing comment.

---

## Chat — `/api/chat-rooms/`

All endpoints require authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/chat-rooms/` | List user's chat rooms |
| `GET` | `/api/chat-rooms/{id}/` | Room detail with full message history |
| `POST` | `/api/chat-rooms/create_or_get/` | Get or create room for an ad |
| `POST` | `/api/chat-rooms/{id}/send_message/` | Send a message |
| `POST` | `/api/chat-rooms/{id}/mark_read/` | Mark all messages in room as read |

### Create or get room

```json
{ "ad_id": 42 }
```

Returns a `ChatRoomDetail` object including all messages.

### Send message

`Content-Type: multipart/form-data`

```
message     string   required (text content)
attachment  file     optional
```

---

## Wishlist — `/api/wishlist/`

Requires authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/wishlist/` | Get wishlist metadata |
| `GET` | `/api/wishlist/items/` | Get all favourited ads |

To add/remove an ad use `POST /api/ads/{id}/toggle_favorite/`.

---

## Notifications — `/api/notifications/`

Requires authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/notifications/` | List notifications (newest first) |
| `GET` | `/api/notifications/{id}/` | Single notification |
| `POST` | `/api/notifications/{id}/mark_read/` | Mark one as read |
| `POST` | `/api/notifications/mark_all_read/` | Mark all as read |
| `GET` | `/api/notifications/unread_count/` | `{ "count": 3 }` |

---

## Ad Packages — `/api/ad-packages/`

Public. Read-only. Lists available posting packages users can purchase.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ad-packages/` | List active packages |
| `GET` | `/api/ad-packages/{id}/` | Package detail |

---

## Ad Features — `/api/ad-features/`

Public. Read-only. Lists upgrade features (highlight, pin, etc.).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ad-features/` | List active features |
| `GET` | `/api/ad-features/{id}/` | Feature detail |

---

## User Packages — `/api/user-packages/`

Requires authentication. Returns only non-expired packages with remaining ads.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/user-packages/` | Own active packages |
| `GET` | `/api/user-packages/{id}/` | Package detail |

---

## Payments — `/api/payments/`

Requires authentication (unless noted).

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/payments/` | Required | Own payment history |
| `GET` | `/api/payments/{id}/` | Required | Payment detail |
| `GET` | `/api/payments/methods/` | Required | Available payment methods |
| `POST` | `/api/payments/initiate/` | Required | Initiate a payment |
| `POST` | `/api/payments/{id}/upload_receipt/` | Required | Upload offline receipt |
| `POST` | `/api/payments/{id}/capture_paypal/` | Required | Capture approved PayPal order |
| `POST` | `/api/payments/paymob/callback/` | Public | Paymob webhook (internal use) |

### Available methods (`GET /api/payments/methods/`)

```
?context=ad_posting         # default
?context=ad_upgrade
?context=package_purchase
?context=paid_banner
```

Response: `[{ "code": "paymob", "label": "Card" }, ...]`

Possible codes: `paymob`, `paypal`, `bank_transfer`, `mobile_wallet`, `instapay`

### Initiate payment (`POST /api/payments/initiate/`)

```json
{
  "provider": "paymob",
  "amount": "199.00",
  "currency": "EGP",
  "context": "ad_posting",
  "description": "optional note",
  "metadata": {}
}
```

For `context = paid_banner` also include:
```json
{ "paid_ad_id": 7 }
```

**Paymob response** — redirect user to `checkout_url`:
```json
{ "payment_id": 1, "checkout_url": "https://accept.paymob.com/..." }
```

**PayPal response** — redirect user to `approval_url`:
```json
{ "payment_id": 1, "approval_url": "https://paypal.com/..." }
```

**Offline providers** (bank_transfer / mobile_wallet / instapay) — upload receipt after:
```json
{ "payment_id": 1, "status": "pending", "message": "Upload your receipt to confirm." }
```

### Upload receipt (`POST /api/payments/{id}/upload_receipt/`)

`Content-Type: multipart/form-data`

```
receipt   file   required   (image or PDF of payment proof)
```

### Capture PayPal (`POST /api/payments/{id}/capture_paypal/`)

```json
{ "order_id": "<paypal_order_id>" }
```

---

## FAQs

### Categories — `/api/faq-categories/`

Public. `GET /api/faq-categories/` and `GET /api/faq-categories/{id}/`.

### Questions — `/api/faqs/`

Public.

| Param | Example | Description |
|-------|---------|-------------|
| `category` | `?category=2` | Filter by FAQ category |
| `search` | `?search=shipping` | Search question/answer in Arabic and English |

---

## Safety Tips — `/api/safety-tips/`

Public. Read-only list/retrieve.

---

## Contact Messages — `/api/contact-messages/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/contact-messages/` | Public | Submit a contact form |
| `GET` | `/api/contact-messages/` | Required | Own submitted messages (staff sees all) |
| `GET` | `/api/contact-messages/{id}/` | Required | Single message |

### Submit contact form

```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "subject": "Inquiry",
  "message": "Hello..."
}
```

---

## Home Content — `/api/home/`

Single endpoint that returns everything needed to render the home page.

```
GET /api/home/
```

**Query params**

| Param | Default | Description |
|-------|---------|-------------|
| `country` | `EG` | Country code to scope ads, categories, sliders |
| `latest_ads_limit` | `20` | Number of latest ads |
| `featured_ads_limit` | `20` | Number of featured ads |
| `blogs_limit` | `10` | Number of latest blog posts |

**Response shape**
```json
{
  "home_page": { "...site copy fields..." },
  "sliders": [ { "id": 1, "image": "...", "title": "..." } ],
  "categories_by_section": [
    {
      "section_type": "classifieds",
      "section_name": "إعلانات",
      "categories": [ { "..." } ]
    }
  ],
  "latest_ads": [ { "..." } ],
  "featured_ads": [ { "..." } ],
  "latest_blogs": [ { "..." } ]
}
```

---

## Home Sliders — `/api/home-sliders/`

Public. Read-only.

`?country=<id>` — returns sliders for that country plus global (country-less) sliders.

---

## Why Choose Us — `/api/why-choose-us/`

Public. Read-only list of feature highlights shown on the home page.

---

## Site Configuration — `/api/site-config/`

Public. Read-only. Returns platform settings (name, logo, contact info, social links, etc.).

---

## Static Pages

Public. Read-only. Each endpoint returns the singleton page content.

| Endpoint | Description |
|----------|-------------|
| `GET /api/about-page/` | About page content |
| `GET /api/contact-page/` | Contact page content |
| `GET /api/terms-page/` | Terms and conditions |
| `GET /api/privacy-page/` | Privacy policy |

---

## Custom Fields — `/api/custom-fields/`

Public. Read-only.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/custom-fields/` | All custom fields |
| `GET` | `/api/custom-fields/{id}/` | Field detail with options |
| `GET` | `/api/custom-fields/by_category/?category_id=3` | Fields for a specific category |

Use `by_category` to build the dynamic form when creating an ad in a category that has extra fields.

---

## Paid Banners — `/api/paid-ads/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/paid-ads/` | Public | Currently active banners |
| `POST` | `/api/paid-ads/` | Required | Create a paid banner (publisher) |
| `GET` | `/api/paid-ads/{id}/` | Public | Banner detail |
| `PUT/PATCH` | `/api/paid-ads/{id}/` | Required (owner) | Update banner |
| `DELETE` | `/api/paid-ads/{id}/` | Required (owner) | Delete banner |
| `GET` | `/api/paid-ads/my_ads/` | Required | Own banners |
| `GET` | `/api/paid-ads/active/` | Public | Active banners with filters |
| `GET` | `/api/paid-ads/pricing/` | Public | Full pricing matrix |
| `GET` | `/api/paid-ads/pricing_simple/` | Public | Simple pricing (general placement) |
| `POST` | `/api/paid-ads/{id}/track_click/` | Public | Increment click counter |

### Active banners (`GET /api/paid-ads/active/`)

| Param | Values | Description |
|-------|--------|-------------|
| `placement_type` | `general`, `category`, `subcategory` | Placement scope |
| `ad_type` | `banner`, `sidebar`, `popup`, `featured_box` | Display format |
| `country` | `<id>` | Country ID |
| `category` | `<id>` | Category ID |

### Pricing matrix (`GET /api/paid-ads/pricing/`)

```json
{
  "banner": { "general": "150.00", "category": "100.00", "subcategory": "75.00" },
  "sidebar": { "general": "100.00", "category": "75.00", "subcategory": "50.00" },
  "popup": { "..." },
  "featured_box": { "..." }
}
```

### Create a paid banner (`POST /api/paid-ads/`)

```json
{
  "title": "My Ad",
  "ad_type": "banner",
  "placement_type": "general",
  "image": "<file>",
  "link_url": "https://example.com",
  "country": 1,
  "category": null,
  "start_date": "2026-06-10T00:00:00Z",
  "end_date": "2026-07-10T00:00:00Z"
}
```

After creation, pay via `POST /api/payments/initiate/` with `context: "paid_banner"` and `paid_ad_id: <id>`.

---

## Pagination

All list endpoints support cursor/page pagination. Default response envelope:

```json
{
  "count": 120,
  "next": "https://api.example.com/api/ads/?page=2",
  "previous": null,
  "results": [ { "..." } ]
}
```

Default page size: **20**. Override with `?page_size=50` (max 100).

---

## Error Responses

| Status | Meaning |
|--------|---------|
| `400` | Validation error — body contains `{ "field": ["message"] }` |
| `401` | Missing or invalid token |
| `403` | Authenticated but not authorised (e.g. editing another user's ad) |
| `404` | Resource not found |
| `429` | Rate limit exceeded |
| `503` | Payment gateway not configured |

---

## Bilingual Fields

All content fields come in two languages. Arabic is the primary locale.

| English field | Arabic field |
|---------------|--------------|
| `name` | `name_ar` |
| `title` | `title_ar` |
| `description` | `description_ar` |
| `question` | `question_ar` |
| `answer` | `answer_ar` |
| `bio` | `bio_ar` |
| `company_name` | `company_name_ar` |

Use the language that matches the user's locale. Fall back to the other if the preferred one is empty.
