# Idrissimart API - Complete Endpoint Documentation

## Base URL
```
http://your-domain.com/api/
```

## Table of Contents
1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Countries](#countries)
4. [Categories](#categories)
5. [Classified Ads](#classified-ads)
6. [Blog](#blog)
7. [Chat / Messaging](#chat--messaging)
8. [Wishlist / Favorites](#wishlist--favorites)
9. [Notifications](#notifications)
10. [Packages & Payments](#packages--payments)
11. [FAQ](#faq)
12. [Safety Tips](#safety-tips)
13. [Contact Messages](#contact-messages)
14. [Home Page Content](#home-page-content)
15. [Site Configuration](#site-configuration)
16. [Static Pages](#static-pages)
17. [Custom Fields](#custom-fields)

---

## Authentication

### Obtain JWT Token
**Endpoint:** `POST /auth/token/`

**Description:** Get access and refresh tokens for authentication

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Refresh JWT Token
**Endpoint:** `POST /auth/token/refresh/`

**Description:** Refresh an expired access token using refresh token

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## User Management

### Register New User
**Endpoint:** `POST /users/`

**Description:** Register a new user account

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "mobile": "+1234567890",
  "profile_type": "individual",
  "rank": "private",
  "country": 1,
  "city": "New York"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "mobile": "+1234567890",
  "profile_type": "individual",
  "rank": "private",
  "country": 1,
  "city": "New York"
}
```

---

### List Users
**Endpoint:** `GET /users/`

**Description:** Get list of all users

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` (int): Page number
- `page_size` (int): Items per page
- `search` (string): Search by username, name

**Response (200 OK):**
```json
{
  "count": 100,
  "next": "http://domain.com/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "testuser",
      "first_name": "John",
      "last_name": "Doe",
      "profile_image": "http://domain.com/media/profiles/avatar.jpg",
      "verification_status": "verified",
      "average_rating": 4.5,
      "is_premium": true,
      "profile_type": "individual",
      "rank": "private"
    }
  ]
}
```

---

### Get User Detail
**Endpoint:** `GET /users/{id}/`

**Description:** Get detailed information about a specific user

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "mobile": "+1234567890",
  "whatsapp": "+1234567890",
  "profile_type": "individual",
  "rank": "private",
  "verification_status": "verified",
  "is_mobile_verified": true,
  "is_email_verified": true,
  "profile_image": "http://domain.com/media/profiles/avatar.jpg",
  "cover_image": "http://domain.com/media/profiles/cover.jpg",
  "bio": "Professional seller",
  "bio_ar": "بائع محترف",
  "company_name": "Company Inc",
  "company_name_ar": "الشركة",
  "country": 1,
  "city": "New York",
  "address": "123 Main St",
  "specialization": "Electronics",
  "years_of_experience": 5,
  "website": "https://example.com",
  "facebook": "https://facebook.com/user",
  "twitter": "https://twitter.com/user",
  "instagram": "https://instagram.com/user",
  "linkedin": "https://linkedin.com/in/user",
  "is_premium": true,
  "subscription_end": "2024-12-31T23:59:59Z",
  "average_rating": 4.5,
  "total_reviews": 20,
  "total_ads": 50,
  "active_ads": 30,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

---

### Get Current User Profile
**Endpoint:** `GET /users/me/`

**Description:** Get the profile of the authenticated user

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "currentuser",
  "email": "current@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  ...
}
```

---

### Update Current User Profile
**Endpoint:** `PATCH /users/update_profile/`

**Description:** Update the profile of the authenticated user

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1234567890",
  "mobile": "+1234567890",
  "bio": "Updated bio",
  "city": "Los Angeles"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1234567890",
  "mobile": "+1234567890",
  "bio": "Updated bio",
  "city": "Los Angeles"
}
```

---

### Update User
**Endpoint:** `PUT /users/{id}/` or `PATCH /users/{id}/`

**Description:** Update user details (own profile only)

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body (PATCH):**
```json
{
  "first_name": "Updated",
  "bio": "New bio"
}
```

---

### Get User's Ads
**Endpoint:** `GET /users/{id}/ads/`

**Description:** Get all active ads by a specific user

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "iPhone 15 Pro",
    "slug": "iphone-15-pro",
    "category": {...},
    "user": {...},
    "price": 999.99,
    "is_negotiable": true,
    "primary_image": "http://domain.com/media/ads/iphone.jpg",
    "city": "New York",
    "country": 1,
    "status": "active",
    "is_highlighted": true,
    "is_urgent": false,
    "is_favorited": false,
    "views_count": 150,
    "created_at": "2024-03-01T10:00:00Z",
    "expires_at": "2024-06-01T10:00:00Z"
  }
]
```

---

### Get User's Reviews
**Endpoint:** `GET /users/{id}/reviews/`

**Description:** Get all reviews for a specific user

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 2,
    "reviewer_name": "John Doe",
    "reviewer_image": "http://domain.com/media/profiles/reviewer.jpg",
    "rating": 5,
    "comment": "Great seller!",
    "created_at": "2024-03-01T10:00:00Z"
  }
]
```

---

## Countries

### List Countries
**Endpoint:** `GET /countries/`

**Description:** Get list of all active countries

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `search` (string): Search by country name or code
- `ordering` (string): Order by field (e.g., `order`, `name`)

**Response (200 OK):**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "الولايات المتحدة",
      "name_en": "United States",
      "code": "US",
      "flag_emoji": "🇺🇸",
      "phone_code": "+1",
      "currency": "USD",
      "cities": ["New York", "Los Angeles", "Chicago"],
      "is_active": true,
      "order": 1
    }
  ]
}
```

---

### Get Country Detail
**Endpoint:** `GET /countries/{id}/`

**Description:** Get detailed information about a specific country

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "الولايات المتحدة",
  "name_en": "United States",
  "code": "US",
  "flag_emoji": "🇺🇸",
  "phone_code": "+1",
  "currency": "USD",
  "cities": ["New York", "Los Angeles", "Chicago"],
  "is_active": true,
  "order": 1
}
```

---

## Categories

### List Categories
**Endpoint:** `GET /categories/`

**Description:** Get list of all categories

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `section_type` (string): Filter by section type
- `parent` (int): Filter by parent category ID
- `country` (int): Filter by country ID
- `search` (string): Search by name

**Response (200 OK):**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "إلكترونيات",
      "name_ar": "إلكترونيات",
      "slug": "electronics",
      "slug_ar": "الكترونيات",
      "section_type": "classified_ads",
      "icon": "fa-laptop",
      "image": "http://domain.com/media/categories/electronics.jpg",
      "parent": null,
      "subcategories_count": 5,
      "ads_count": 150,
      "allow_cart": true
    }
  ]
}
```

---

### Get Category Detail
**Endpoint:** `GET /categories/{id}/`

**Description:** Get detailed information about a category with subcategories

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "إلكترونيات",
  "name_ar": "إلكترونيات",
  "slug": "electronics",
  "slug_ar": "الكترونيات",
  "section_type": "classified_ads",
  "parent": null,
  "description": "Electronics category",
  "icon": "fa-laptop",
  "image": "http://domain.com/media/categories/electronics.jpg",
  "country": null,
  "countries": [1, 2, 3],
  "custom_field_schema": {},
  "allow_cart": true,
  "cart_instructions": "Add items to cart and checkout",
  "default_reservation_percentage": 10,
  "min_reservation_amount": 10.00,
  "max_reservation_amount": 1000.00,
  "subcategories": [
    {
      "id": 2,
      "name": "Phones",
      "name_ar": "هواتف",
      "slug": "phones",
      "slug_ar": "هواتف",
      "section_type": "classified_ads",
      "icon": "fa-mobile",
      "image": "http://domain.com/media/categories/phones.jpg",
      "parent": 1,
      "subcategories_count": 0,
      "ads_count": 50,
      "allow_cart": true
    }
  ],
  "custom_fields": [
    {
      "id": 1,
      "name": "brand",
      "label_ar": "العلامة التجارية",
      "label_en": "Brand",
      "field_type": "select",
      "is_required": true,
      "options": [...]
    }
  ]
}
```

---

### Get Category Ads
**Endpoint:** `GET /categories/{id}/ads/`

**Description:** Get all ads in a specific category

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `min_price` (decimal): Minimum price filter
- `max_price` (decimal): Maximum price filter
- `city` (string): Filter by city
- `page` (int): Page number

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://domain.com/api/categories/1/ads/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "iPhone 15 Pro",
      "slug": "iphone-15-pro",
      "category": {...},
      "user": {...},
      "price": 999.99,
      ...
    }
  ]
}
```

---

### Get Root Categories
**Endpoint:** `GET /categories/root_categories/`

**Description:** Get only root level categories (no parent)

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `section_type` (string): Filter by section type

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "إلكترونيات",
    "name_ar": "إلكترونيات",
    "slug": "electronics",
    "slug_ar": "الكترونيات",
    "section_type": "classified_ads",
    "icon": "fa-laptop",
    "image": "http://domain.com/media/categories/electronics.jpg",
    "parent": null,
    "subcategories_count": 5,
    "ads_count": 150,
    "allow_cart": true
  }
]
```

---

## Classified Ads

### List Ads
**Endpoint:** `GET /ads/`

**Description:** Get list of all active classified ads

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `category` (int): Filter by category ID
- `country` (int): Filter by country ID
- `city` (string): Filter by city
- `status` (string): Filter by status
- `is_highlighted` (boolean): Filter highlighted ads
- `is_urgent` (boolean): Filter urgent ads
- `is_pinned` (boolean): Filter pinned ads
- `min_price` (decimal): Minimum price
- `max_price` (decimal): Maximum price
- `search` (string): Search in title and description
- `ordering` (string): Order by field (e.g., `-created_at`, `price`)
- `page` (int): Page number

**Response (200 OK):**
```json
{
  "count": 200,
  "next": "http://domain.com/api/ads/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "iPhone 15 Pro",
      "slug": "iphone-15-pro",
      "category": {
        "id": 2,
        "name": "Phones",
        "name_ar": "هواتف",
        ...
      },
      "user": {
        "id": 1,
        "username": "seller",
        "first_name": "John",
        "last_name": "Doe",
        "profile_image": "http://domain.com/media/profiles/avatar.jpg",
        "verification_status": "verified",
        "average_rating": 4.5,
        "is_premium": true,
        "profile_type": "individual",
        "rank": "private"
      },
      "price": 999.99,
      "is_negotiable": true,
      "primary_image": "http://domain.com/media/ads/iphone.jpg",
      "city": "New York",
      "country": 1,
      "status": "active",
      "is_highlighted": true,
      "is_urgent": false,
      "is_favorited": false,
      "views_count": 150,
      "created_at": "2024-03-01T10:00:00Z",
      "expires_at": "2024-06-01T10:00:00Z"
    }
  ]
}
```

---

### Create Ad
**Endpoint:** `POST /ads/`

**Description:** Create a new classified ad

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
  "title": "iPhone 15 Pro",
  "category": 2,
  "description": "Brand new iPhone 15 Pro, 256GB",
  "price": "999.99",
  "is_negotiable": true,
  "country": 1,
  "city": "New York",
  "address": "Downtown Manhattan",
  "is_highlighted": false,
  "is_urgent": false,
  "custom_fields": {
    "brand": "Apple",
    "condition": "new",
    "storage": "256GB"
  },
  "is_cart_enabled": false,
  "video_url": "https://youtube.com/watch?v=xxx",
  "images": [<file1>, <file2>, <file3>]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "iPhone 15 Pro",
  "slug": "iphone-15-pro",
  "category": {
    "id": 2,
    "name": "Phones",
    ...
  },
  "user": {
    "id": 1,
    "username": "seller",
    ...
  },
  "description": "Brand new iPhone 15 Pro, 256GB",
  "price": 999.99,
  "is_negotiable": true,
  "images": [
    {
      "id": 1,
      "image": "http://domain.com/media/ads/img1.jpg",
      "order": 0
    }
  ],
  "city": "New York",
  "country": 1,
  "address": "Downtown Manhattan",
  "status": "active",
  "is_highlighted": false,
  "is_urgent": false,
  "is_pinned": false,
  "views_count": 0,
  "created_at": "2024-03-19T10:00:00Z",
  "updated_at": "2024-03-19T10:00:00Z",
  "expires_at": "2024-06-19T10:00:00Z",
  "reviews": [],
  "is_favorited": false,
  "custom_fields": {
    "brand": "Apple",
    "condition": "new",
    "storage": "256GB"
  },
  "is_cart_enabled": false,
  "video_url": "https://youtube.com/watch?v=xxx",
  "rating": 0,
  "rating_count": 0
}
```

---

### Get Ad Detail
**Endpoint:** `GET /ads/{id}/`

**Description:** Get detailed information about a specific ad (increments view count)

**Request Headers:**
```http
Content-Type: application/json
Authorization: Bearer {access_token} (optional)
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "iPhone 15 Pro",
  "slug": "iphone-15-pro",
  "category": {...},
  "user": {...},
  "description": "Brand new iPhone 15 Pro, 256GB",
  "price": 999.99,
  "is_negotiable": true,
  "images": [
    {
      "id": 1,
      "image": "http://domain.com/media/ads/img1.jpg",
      "order": 0
    },
    {
      "id": 2,
      "image": "http://domain.com/media/ads/img2.jpg",
      "order": 1
    }
  ],
  "city": "New York",
  "country": 1,
  "address": "Downtown Manhattan",
  "status": "active",
  "is_highlighted": true,
  "is_urgent": false,
  "is_pinned": false,
  "views_count": 151,
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-01T10:00:00Z",
  "expires_at": "2024-06-01T10:00:00Z",
  "reviews": [
    {
      "id": 1,
      "user": 2,
      "reviewer_name": "Jane Smith",
      "reviewer_image": "http://domain.com/media/profiles/jane.jpg",
      "rating": 5,
      "comment": "Great product!",
      "created_at": "2024-03-02T10:00:00Z"
    }
  ],
  "is_favorited": true,
  "custom_fields": {
    "brand": "Apple",
    "condition": "new",
    "storage": "256GB"
  },
  "is_cart_enabled": false,
  "video_url": "https://youtube.com/watch?v=xxx",
  "rating": 5.0,
  "rating_count": 1
}
```

---

### Update Ad
**Endpoint:** `PUT /ads/{id}/` or `PATCH /ads/{id}/`

**Description:** Update an existing ad (only by owner)

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (PATCH):**
```json
{
  "title": "iPhone 15 Pro - Updated",
  "price": "899.99"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "iPhone 15 Pro - Updated",
  "price": 899.99,
  ...
}
```

---

### Delete Ad
**Endpoint:** `DELETE /ads/{id}/`

**Description:** Delete an ad (only by owner)

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

---

### Toggle Favorite
**Endpoint:** `POST /ads/{id}/toggle_favorite/`

**Description:** Add or remove ad from user's favorites

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "status": "added",
  "message": "Ad added to favorites"
}
```

OR

```json
{
  "status": "removed",
  "message": "Ad removed from favorites"
}
```

---

### Add Review to Ad
**Endpoint:** `POST /ads/{id}/review/`

**Description:** Add a review/rating to an ad

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Excellent product and seller!"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user": 2,
  "reviewer_name": "Jane Smith",
  "reviewer_image": "http://domain.com/media/profiles/jane.jpg",
  "rating": 5,
  "comment": "Excellent product and seller!",
  "created_at": "2024-03-19T10:00:00Z"
}
```

---

### Get Featured Ads
**Endpoint:** `GET /ads/featured/`

**Description:** Get list of featured ads

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "iPhone 15 Pro",
    ...
  }
]
```

---

### Get Urgent Ads
**Endpoint:** `GET /ads/urgent/`

**Description:** Get list of urgent ads

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "title": "Quick Sale - MacBook Pro",
    ...
  }
]
```

---

### Get Recent Ads
**Endpoint:** `GET /ads/recent/`

**Description:** Get list of recent ads (last 20)

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "title": "New Samsung Galaxy",
    ...
  }
]
```

---

### Get My Ads
**Endpoint:** `GET /ads/my_ads/`

**Description:** Get current user's ads (all statuses)

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "iPhone 15 Pro",
      "status": "active",
      ...
    }
  ]
}
```

---

## Blog

### List Blog Categories
**Endpoint:** `GET /blog-categories/`

**Description:** Get list of all active blog categories

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Technology",
      "name_en": "Technology",
      "slug": "technology",
      "description": "Tech news and tips",
      "icon": "fa-laptop",
      "color": "#007bff",
      "order": 1,
      "is_active": true,
      "blogs_count": 25
    }
  ]
}
```

---

### List Blog Posts
**Endpoint:** `GET /blogs/`

**Description:** Get list of all published blog posts

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `category` (int): Filter by category ID
- `author` (int): Filter by author ID
- `search` (string): Search in title and content
- `ordering` (string): Order by field (e.g., `-published_date`, `-views_count`)
- `page` (int): Page number

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://domain.com/api/blogs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "10 Tips for Online Shopping Safety",
      "slug": "10-tips-online-shopping-safety",
      "author": {
        "id": 1,
        "username": "admin",
        ...
      },
      "category": {
        "id": 1,
        "name": "Safety Tips",
        ...
      },
      "image": "http://domain.com/media/blog/safety.jpg",
      "published_date": "2024-03-01T10:00:00Z",
      "views_count": 500,
      "likes_count": 45,
      "is_liked": false,
      "is_published": true
    }
  ]
}
```

---

### Get Blog Post Detail
**Endpoint:** `GET /blogs/{id}/`

**Description:** Get detailed blog post (increments view count)

**Request Headers:**
```http
Content-Type: application/json
Authorization: Bearer {access_token} (optional)
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "10 Tips for Online Shopping Safety",
  "slug": "10-tips-online-shopping-safety",
  "author": {...},
  "category": {...},
  "content": "<p>Full blog content here...</p>",
  "image": "http://domain.com/media/blog/safety.jpg",
  "published_date": "2024-03-01T10:00:00Z",
  "updated_date": "2024-03-02T10:00:00Z",
  "views_count": 501,
  "likes_count": 45,
  "is_liked": true,
  "is_published": true,
  "comments": [
    {
      "id": 1,
      "blog": 1,
      "author": {...},
      "body": "Great article!",
      "created_on": "2024-03-02T10:00:00Z",
      "active": true,
      "parent": null,
      "replies": []
    }
  ],
  "tags": ["shopping", "safety", "online"]
}
```

---

### Like/Unlike Blog Post
**Endpoint:** `POST /blogs/{id}/like/`

**Description:** Like or unlike a blog post

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "status": "liked",
  "likes_count": 46
}
```

OR

```json
{
  "status": "unliked",
  "likes_count": 45
}
```

---

### Add Comment to Blog
**Endpoint:** `POST /blogs/{id}/comment/`

**Description:** Add a comment to a blog post

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "body": "Great article, very helpful!",
  "parent": null
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "blog": 1,
  "author": {
    "id": 2,
    "username": "commenter",
    ...
  },
  "body": "Great article, very helpful!",
  "created_on": "2024-03-19T10:00:00Z",
  "active": true,
  "parent": null,
  "replies": []
}
```

---

## Chat / Messaging

### List Chat Rooms
**Endpoint:** `GET /chat-rooms/`

**Description:** Get list of user's chat rooms

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "room_type": "publisher_client",
      "publisher": {
        "id": 1,
        "username": "seller",
        ...
      },
      "client": {
        "id": 2,
        "username": "buyer",
        ...
      },
      "ad": 1,
      "ad_title": "iPhone 15 Pro",
      "last_message": {
        "message": "Is this still available?",
        "sender": "buyer",
        "created_at": "2024-03-19T10:00:00Z"
      },
      "unread_count": 2,
      "created_at": "2024-03-15T10:00:00Z",
      "updated_at": "2024-03-19T10:00:00Z",
      "is_active": true
    }
  ]
}
```

---

### Get Chat Room Detail
**Endpoint:** `GET /chat-rooms/{id}/`

**Description:** Get detailed chat room with all messages

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "room_type": "publisher_client",
  "publisher": {...},
  "client": {...},
  "ad": {
    "id": 1,
    "title": "iPhone 15 Pro",
    ...
  },
  "messages": [
    {
      "id": 1,
      "room": 1,
      "sender": {...},
      "message": "Is this still available?",
      "attachment": null,
      "created_at": "2024-03-19T09:00:00Z",
      "is_read": true,
      "read_at": "2024-03-19T09:05:00Z"
    },
    {
      "id": 2,
      "room": 1,
      "sender": {...},
      "message": "Yes, it is!",
      "attachment": null,
      "created_at": "2024-03-19T10:00:00Z",
      "is_read": false,
      "read_at": null
    }
  ],
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2024-03-19T10:00:00Z",
  "is_active": true
}
```

---

### Create or Get Chat Room
**Endpoint:** `POST /chat-rooms/create_or_get/`

**Description:** Create a new chat room or get existing one for an ad

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "ad_id": 1
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "room_type": "publisher_client",
  "publisher": {...},
  "client": {...},
  "ad": {...},
  "messages": [],
  "created_at": "2024-03-19T10:00:00Z",
  "updated_at": "2024-03-19T10:00:00Z",
  "is_active": true
}
```

---

### Send Message
**Endpoint:** `POST /chat-rooms/{id}/send_message/`

**Description:** Send a message in a chat room

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body:**
```json
{
  "message": "Hello, is this still available?",
  "attachment": <file> (optional)
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "room": 1,
  "sender": {
    "id": 2,
    "username": "buyer",
    ...
  },
  "message": "Hello, is this still available?",
  "attachment": null,
  "created_at": "2024-03-19T10:00:00Z",
  "is_read": false,
  "read_at": null
}
```

---

### Mark Chat as Read
**Endpoint:** `POST /chat-rooms/{id}/mark_read/`

**Description:** Mark all messages in a chat room as read

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "status": "success"
}
```

---

## Wishlist / Favorites

### Get Wishlist Items
**Endpoint:** `GET /wishlist/items/`

**Description:** Get all items in user's wishlist

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "ad": {
      "id": 1,
      "title": "iPhone 15 Pro",
      ...
    },
    "added_at": "2024-03-15T10:00:00Z"
  },
  {
    "id": 2,
    "ad": {
      "id": 5,
      "title": "MacBook Pro",
      ...
    },
    "added_at": "2024-03-18T10:00:00Z"
  }
]
```

---

## Notifications

### List Notifications
**Endpoint:** `GET /notifications/`

**Description:** Get list of user's notifications

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` (int): Page number

**Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://domain.com/api/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "notification_type": "new_message",
      "title": "New Message",
      "message": "You have a new message from John Doe",
      "link": "/chat/1/",
      "is_read": false,
      "created_at": "2024-03-19T10:00:00Z"
    }
  ]
}
```

---

### Mark Notification as Read
**Endpoint:** `POST /notifications/{id}/mark_read/`

**Description:** Mark a specific notification as read

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "status": "success"
}
```

---

### Mark All Notifications as Read
**Endpoint:** `POST /notifications/mark_all_read/`

**Description:** Mark all notifications as read

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "status": "success"
}
```

---

### Get Unread Count
**Endpoint:** `GET /notifications/unread_count/`

**Description:** Get count of unread notifications

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 5
}
```

---

## Packages & Payments

### List Ad Features
**Endpoint:** `GET /ad-features/`

**Description:** Get list of all active ad features

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "ad": 1,
      "feature_type": "pinned",
      "feature_type_display": "Pinned",
      "start_date": "2024-03-19T00:00:00Z",
      "end_date": "2024-04-19T00:00:00Z",
      "is_active": true
    }
  ]
}
```

---

### List Ad Packages
**Endpoint:** `GET /ad-packages/`

**Description:** Get list of all available ad packages

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "الباقة الأساسية",
      "name_en": "Basic Package",
      "description": "باقة مناسبة للبداية",
      "description_en": "Perfect starter package",
      "price": "29.99",
      "ad_count": 5,
      "ad_duration_days": 30,
      "duration_days": 30,
      "feature_pinned_price": "10.00",
      "feature_urgent_price": "5.00",
      "feature_highlighted_price": "8.00",
      "feature_contact_for_price": "3.00",
      "feature_auto_refresh_price": "7.00",
      "feature_add_video_price": "5.00",
      "is_active": true,
      "is_recommended": false,
      "is_default": true
    },
    {
      "id": 2,
      "name": "الباقة المميزة",
      "name_en": "Premium Package",
      "description": "باقة للمعلنين المحترفين",
      "description_en": "For professional advertisers",
      "price": "99.99",
      "ad_count": 20,
      "ad_duration_days": 60,
      "duration_days": 90,
      "feature_pinned_price": "8.00",
      "feature_urgent_price": "4.00",
      "feature_highlighted_price": "6.00",
      "feature_contact_for_price": "2.00",
      "feature_auto_refresh_price": "5.00",
      "feature_add_video_price": "3.00",
      "is_active": true,
      "is_recommended": true,
      "is_default": false
    }
  ]
}
```

---

### List Payments
**Endpoint:** `GET /payments/`

**Description:** Get list of user's payments

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {...},
      "provider": "stripe",
      "provider_transaction_id": "ch_1234567890",
      "amount": "29.99",
      "currency": "USD",
      "status": "completed",
      "description": "Basic Package Purchase",
      "metadata": {},
      "offline_payment_receipt": null,
      "created_at": "2024-03-19T10:00:00Z",
      "updated_at": "2024-03-19T10:05:00Z",
      "completed_at": "2024-03-19T10:05:00Z"
    }
  ]
}
```

---

### Create Payment
**Endpoint:** `POST /payments/`

**Description:** Create a new payment

**Request Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "provider": "stripe",
  "amount": "29.99",
  "currency": "USD",
  "description": "Basic Package Purchase",
  "metadata": {
    "package_id": 1
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user": {...},
  "provider": "stripe",
  "provider_transaction_id": null,
  "amount": "29.99",
  "currency": "USD",
  "status": "pending",
  "description": "Basic Package Purchase",
  "metadata": {
    "package_id": 1
  },
  "offline_payment_receipt": null,
  "created_at": "2024-03-19T10:00:00Z",
  "updated_at": "2024-03-19T10:00:00Z",
  "completed_at": null
}
```

---

### List User Packages
**Endpoint:** `GET /user-packages/`

**Description:** Get list of user's purchased packages

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "package": {
        "id": 1,
        "name": "الباقة الأساسية",
        "name_en": "Basic Package",
        ...
      },
      "payment": 1,
      "purchase_date": "2024-03-01T10:00:00Z",
      "expiry_date": "2024-03-31T10:00:00Z",
      "ads_remaining": 3,
      "ads_used": 2,
      "is_active": true
    }
  ]
}
```

---

## FAQ

### List FAQ Categories
**Endpoint:** `GET /faq-categories/`

**Description:** Get list of all active FAQ categories

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Getting Started",
      "name_ar": "البداية",
      "icon": "fa-rocket",
      "order": 1,
      "is_active": true
    }
  ]
}
```

---

### List FAQs
**Endpoint:** `GET /faqs/`

**Description:** Get list of all active FAQs

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `category` (int): Filter by category ID
- `search` (string): Search in question and answer

**Response (200 OK):**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "category": {
        "id": 1,
        "name": "Getting Started",
        ...
      },
      "question": "How do I create an account?",
      "question_ar": "كيف أنشئ حساب؟",
      "answer": "To create an account, click on the Sign Up button...",
      "answer_ar": "لإنشاء حساب، اضغط على زر التسجيل...",
      "order": 1,
      "is_active": true,
      "is_popular": true
    }
  ]
}
```

---

## Safety Tips

### List Safety Tips
**Endpoint:** `GET /safety-tips/`

**Description:** Get list of all active safety tips

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Meet in Public Places",
      "title_en": "Meet in Public Places",
      "description": "Always meet buyers/sellers in public locations",
      "description_en": "Always meet buyers/sellers in public locations",
      "icon_class": "fa-users",
      "order": 1,
      "is_active": true
    }
  ]
}
```

---

## Contact Messages

### Create Contact Message
**Endpoint:** `POST /contact-messages/`

**Description:** Submit a contact form message

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "subject": "General Inquiry",
  "message": "I have a question about your platform..."
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "subject": "General Inquiry",
  "message": "I have a question about your platform...",
  "status": "pending",
  "created_at": "2024-03-19T10:00:00Z",
  "replied_at": null
}
```

---

### List Contact Messages
**Endpoint:** `GET /contact-messages/`

**Description:** Get list of contact messages (admin only)

**Request Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "subject": "General Inquiry",
      "message": "I have a question...",
      "status": "pending",
      "created_at": "2024-03-19T10:00:00Z",
      "replied_at": null
    }
  ]
}
```

---

## Home Page Content

### List Home Sliders
**Endpoint:** `GET /home-sliders/`

**Description:** Get list of all active home page sliders

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `country` (int): Filter by country ID

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Welcome to Idrissimart",
      "title_ar": "مرحبا بكم في إدريسي مارت",
      "subtitle": "Buy and Sell with Confidence",
      "subtitle_ar": "اشتري وبيع بثقة",
      "description": "The best marketplace in the region",
      "description_ar": "أفضل سوق في المنطقة",
      "image": "http://domain.com/media/sliders/slide1.jpg",
      "button_text": "Get Started",
      "button_text_ar": "ابدأ الآن",
      "button_url": "/register",
      "country": 1,
      "background_color": "#007bff",
      "text_color": "#ffffff",
      "is_active": true,
      "order": 1
    }
  ]
}
```

---

### List Why Choose Us Features
**Endpoint:** `GET /why-choose-us/`

**Description:** Get list of "Why Choose Us" features

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Secure Transactions",
      "title_ar": "معاملات آمنة",
      "description": "All transactions are protected",
      "description_ar": "جميع المعاملات محمية",
      "icon": "fa-shield-alt",
      "order": 1,
      "is_active": true
    }
  ]
}
```

---

## Site Configuration

### Get Site Configuration
**Endpoint:** `GET /site-config/`

**Description:** Get site configuration settings

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "meta_keywords": "classified ads, marketplace",
      "meta_keywords_ar": "إعلانات مبوبة، سوق",
      "footer_text": "Your trusted marketplace",
      "footer_text_ar": "سوقك الموثوق",
      "copyright_text": "© 2024 Idrissimart. All rights reserved.",
      "logo": "http://domain.com/media/logo.png",
      "logo_light": "http://domain.com/media/logo-light.png",
      "logo_dark": "http://domain.com/media/logo-dark.png",
      "logo_mini": "http://domain.com/media/logo-mini.png",
      "require_email_verification": true,
      "require_phone_verification": false,
      "require_verification_for_services": true,
      "allow_online_payment": true,
      "allow_offline_payment": true
    }
  ]
}
```

---

## Static Pages

### Get About Page
**Endpoint:** `GET /about-page/`

**Description:** Get about page content

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "content": "<p>About us content...</p>",
      "content_ar": "<p>محتوى من نحن...</p>",
      "sections": [
        {
          "id": 1,
          "tab_title": "Our Mission",
          "tab_title_ar": "مهمتنا",
          "icon": "fa-bullseye",
          "content": "<p>Mission content...</p>",
          "content_ar": "<p>محتوى المهمة...</p>",
          "order": 1,
          "is_active": true
        }
      ]
    }
  ]
}
```

---

### Get Contact Page
**Endpoint:** `GET /contact-page/`

**Description:** Get contact page content and settings

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Contact Us",
      "title_ar": "اتصل بنا",
      "description": "Get in touch with us",
      "description_ar": "تواصل معنا",
      "enable_contact_form": true,
      "notification_email": "support@idrissimart.com",
      "show_phone": true,
      "show_address": true,
      "show_office_hours": true,
      "show_map": true,
      "office_hours": "Mon-Fri: 9AM-6PM",
      "office_hours_ar": "الإثنين-الجمعة: 9ص-6م",
      "map_embed_code": "<iframe src='...'></iframe>"
    }
  ]
}
```

---

### Get Terms Page
**Endpoint:** `GET /terms-page/`

**Description:** Get terms and conditions page content

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "content": "<p>Terms and conditions content...</p>",
      "content_ar": "<p>محتوى الشروط والأحكام...</p>"
    }
  ]
}
```

---

### Get Privacy Page
**Endpoint:** `GET /privacy-page/`

**Description:** Get privacy policy page content

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "content": "<p>Privacy policy content...</p>",
      "content_ar": "<p>محتوى سياسة الخصوصية...</p>"
    }
  ]
}
```

---

## Custom Fields

### List Custom Fields
**Endpoint:** `GET /custom-fields/`

**Description:** Get list of all custom fields

**Request Headers:**
```http
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "brand",
      "label_ar": "العلامة التجارية",
      "label_en": "Brand",
      "field_type": "select",
      "is_required": true,
      "help_text": "Select the brand",
      "placeholder": "Choose a brand",
      "default_value": "",
      "min_length": null,
      "max_length": null,
      "min_value": null,
      "max_value": null,
      "validation_regex": "",
      "is_active": true,
      "options": [
        {
          "id": 1,
          "label_ar": "أبل",
          "label_en": "Apple",
          "value": "apple",
          "order": 1,
          "is_active": true
        },
        {
          "id": 2,
          "label_ar": "سامسونج",
          "label_en": "Samsung",
          "value": "samsung",
          "order": 2,
          "is_active": true
        }
      ]
    }
  ]
}
```

---

### Get Custom Fields by Category
**Endpoint:** `GET /custom-fields/by_category/?category_id={id}`

**Description:** Get custom fields for a specific category

**Request Headers:**
```http
Content-Type: application/json
```

**Query Parameters:**
- `category_id` (int, required): Category ID

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "brand",
    "label_ar": "العلامة التجارية",
    "label_en": "Brand",
    "field_type": "select",
    "is_required": true,
    "options": [...]
  },
  {
    "id": 2,
    "name": "condition",
    "label_ar": "الحالة",
    "label_en": "Condition",
    "field_type": "select",
    "is_required": true,
    "options": [
      {
        "id": 5,
        "label_ar": "جديد",
        "label_en": "New",
        "value": "new",
        "order": 1,
        "is_active": true
      },
      {
        "id": 6,
        "label_ar": "مستعمل",
        "label_en": "Used",
        "value": "used",
        "order": 2,
        "is_active": true
      }
    ]
  }
]
```

---

## Error Responses

### Common Error Codes

#### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

OR

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred. Please try again later."
}
```

---

## Pagination

All list endpoints support pagination with the following parameters:

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://domain.com/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering and Search

Many list endpoints support filtering and search:

**Query Parameters:**
- `search` (string): Full-text search in specified fields
- `ordering` (string): Order results by field (prefix with `-` for descending)
- Various filter fields specific to each endpoint (see endpoint documentation)

**Example:**
```
GET /api/ads/?category=2&min_price=100&max_price=1000&search=iphone&ordering=-created_at
```

---

## Rate Limiting

API requests are rate-limited:
- **Authenticated users**: 100 requests per minute
- **Unauthenticated users**: 20 requests per minute

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1616161616
```

When rate limit is exceeded:
```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

---

## Best Practices

1. **Authentication**: Always include the Bearer token in the Authorization header for protected endpoints
2. **Content-Type**: Use `application/json` for JSON data, `multipart/form-data` for file uploads
3. **Error Handling**: Always check the HTTP status code and handle errors appropriately
4. **Pagination**: Use pagination for list endpoints to avoid large responses
5. **Caching**: Cache static content like countries, categories, and configuration
6. **Image Upload**: When uploading images, use multipart/form-data and send files as form fields
7. **Search Optimization**: Use specific filters instead of broad searches when possible
8. **Token Refresh**: Implement token refresh logic to handle expired access tokens

---

## Support

For API support and questions:
- Email: support@idrissimart.com
- Documentation: http://domain.com/api/swagger/
- API Explorer: http://domain.com/api/redoc/
