# Home Page API Endpoint

## Overview

The `/api/home/` endpoint returns all data needed to render the home page in a **single request**. It aggregates hero content, sliders, categories grouped by section, latest ads, featured ads, and latest blog posts — mirroring exactly what the server-side `HomeView` provides to the template.

---

## Endpoint

```
GET /api/home/
```

---

## Request Headers

```http
Content-Type: application/json
```

> Authentication is **not required**. This is a public endpoint.

---

## Query Parameters

| Parameter            | Type   | Default                      | Description                                                                   |
|----------------------|--------|------------------------------|-------------------------------------------------------------------------------|
| `country`            | string | Session/middleware (e.g. EG) | Country code to filter ads, sliders, and categories (e.g. `EG`, `US`, `SA`). |
| `latest_ads_limit`   | int    | `20`                         | Maximum number of latest ads to return.                                       |
| `featured_ads_limit` | int    | `20`                         | Maximum number of featured ads to return.                                     |
| `blogs_limit`        | int    | `10`                         | Maximum number of latest published blog posts to return.                      |

### Example Request

```http
GET /api/home/?country=EG&latest_ads_limit=10&featured_ads_limit=6&blogs_limit=5
```

---

## Response Body

**Status: `200 OK`**

```json
{
  "home_page": { ... },
  "sliders": [ ... ],
  "categories_by_section": [ ... ],
  "latest_ads": [ ... ],
  "featured_ads": [ ... ],
  "latest_blogs": [ ... ]
}
```

---

### `home_page` object

Contains the hero section, statistics, "Why Choose Us" config, and section visibility flags.

```json
{
  "hero_title": "Welcome to Idrissimart",
  "hero_title_ar": "مرحباً بك في إدريسي مارت",
  "hero_subtitle": "<p>The best marketplace in the region</p>",
  "hero_subtitle_ar": "<p>أفضل سوق في المنطقة</p>",
  "hero_image": "http://domain.com/media/homepage/hero/banner.jpg",
  "hero_button_text": "Get Started",
  "hero_button_text_ar": "ابدأ الآن",
  "hero_button_url": "/ads/",

  "show_why_choose_us": true,
  "why_choose_us_title": "Why Choose Us?",
  "why_choose_us_title_ar": "لماذا إدريسي مارت؟",
  "why_choose_us_subtitle": "Trusted by thousands of buyers and sellers.",
  "why_choose_us_subtitle_ar": "موثوق به من قِبل آلاف المشترين والبائعين.",
  "why_choose_us_features": [
    {
      "id": 1,
      "title": "Secure Transactions",
      "title_ar": "معاملات آمنة",
      "description": "All transactions are fully protected.",
      "description_ar": "جميع المعاملات محمية بالكامل.",
      "icon": "fas fa-shield-alt",
      "order": 1,
      "is_active": true
    }
  ],

  "show_featured_categories": true,
  "show_featured_ads": true,
  "show_statistics": true,

  "stat1_value": 15,
  "stat1_title": "Active Advertisers",
  "stat1_title_ar": "معلنين نشطين",
  "stat1_subtitle": "Offices, Engineers & Companies",
  "stat1_subtitle_ar": "مكاتب، مهندسين، وشركات",
  "stat1_icon": "fas fa-user-friends",

  "stat2_value": 150,
  "stat2_title": "Published Ads",
  "stat2_title_ar": "إعلانات منشورة",
  "stat2_subtitle": "Services, Equipment & Job Opportunities",
  "stat2_subtitle_ar": "خدمات، معدات، وفرص عمل",
  "stat2_icon": "fas fa-bullhorn",

  "stat3_value": 500,
  "stat3_title": "Monthly Visits",
  "stat3_title_ar": "زيارات شهرية",
  "stat3_subtitle": "Interested in Surveying Field",
  "stat3_subtitle_ar": "مهتمون بالمجال المساحي",
  "stat3_icon": "fas fa-chart-line",

  "stat4_value": 250,
  "stat4_title": "Supported Specializations",
  "stat4_title_ar": "تخصصات مدعومة",
  "stat4_subtitle": "Surveying - Engineering - GIS",
  "stat4_subtitle_ar": "مساحة – هندسة – GIS",
  "stat4_icon": "fas fa-th-large"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `hero_title` / `hero_title_ar` | string | Hero section heading (EN / AR) |
| `hero_subtitle` / `hero_subtitle_ar` | HTML string | Hero sub-heading rich text |
| `hero_image` | URL \| null | Hero banner image URL |
| `hero_button_text` / `hero_button_text_ar` | string | CTA button label |
| `hero_button_url` | string | CTA button link path |
| `show_why_choose_us` | boolean | Whether to render the "Why Choose Us" section |
| `why_choose_us_features` | array | List of feature items (see below) |
| `show_featured_categories` | boolean | Whether to render the categories section |
| `show_featured_ads` | boolean | Whether to render the featured ads section |
| `show_statistics` | boolean | Whether to render the statistics section |
| `stat1_value` … `stat4_value` | int | Numeric value for each stat counter |
| `stat1_title` … `stat4_title` | string | Stat label (EN) |
| `stat1_title_ar` … `stat4_title_ar` | string | Stat label (AR) |
| `stat1_subtitle` … `stat4_subtitle` | string | Stat sub-label (EN) |
| `stat1_subtitle_ar` … `stat4_subtitle_ar` | string | Stat sub-label (AR) |
| `stat1_icon` … `stat4_icon` | string | FontAwesome class (e.g. `fas fa-user-friends`) |

---

### `sliders` array

Active home page sliders filtered by the requested country (global sliders with no country assigned are always included).

```json
[
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
```

---

### `categories_by_section` array

Root-level categories (level 0) grouped by their `section_type`, each with nested subcategories and custom fields. Only categories active for the requested country are included.

```json
[
  {
    "section_type": "classified_ads",
    "section_name": "Classified Ads",
    "categories": [
      {
        "id": 1,
        "name": "إلكترونيات",
        "name_ar": "إلكترونيات",
        "slug": "electronics",
        "slug_ar": "الكترونيات",
        "section_type": "classified_ads",
        "parent": null,
        "description": "Electronics and devices",
        "icon": "fa-laptop",
        "image": "http://domain.com/media/categories/electronics.jpg",
        "country": null,
        "countries": [1, 2],
        "custom_field_schema": {},
        "allow_cart": true,
        "cart_instructions": "",
        "default_reservation_percentage": 10,
        "min_reservation_amount": "10.00",
        "max_reservation_amount": "1000.00",
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
            "options": [
              { "id": 1, "label_ar": "أبل", "label_en": "Apple", "value": "apple", "order": 1, "is_active": true }
            ]
          }
        ]
      }
    ]
  }
]
```

---

### `latest_ads` array

Most recent active ads for the requested country, ordered by: pinned → urgent → highlighted → newest. Respects `latest_ads_limit`.

```json
[
  {
    "id": 1,
    "title": "iPhone 15 Pro",
    "slug": "iphone-15-pro",
    "category": {
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
    },
    "user": {
      "id": 1,
      "username": "seller",
      "first_name": "Ahmed",
      "last_name": "Hassan",
      "profile_image": "http://domain.com/media/profiles/avatar.jpg",
      "verification_status": "verified",
      "average_rating": 4.5,
      "is_premium": true,
      "profile_type": "individual",
      "rank": "private"
    },
    "price": "999.99",
    "is_negotiable": true,
    "primary_image": "http://domain.com/media/ads/iphone.jpg",
    "city": "Cairo",
    "country": 1,
    "status": "active",
    "is_highlighted": true,
    "is_urgent": false,
    "is_favorited": false,
    "views_count": 150,
    "created_at": "2026-03-01T10:00:00Z",
    "expires_at": "2026-06-01T10:00:00Z"
  }
]
```

> `is_favorited` is always `false` for unauthenticated requests.

---

### `featured_ads` array

Highlighted or featured ads for the requested country. Falls back to latest ads if no featured ads exist. Respects `featured_ads_limit`. Same structure as `latest_ads`.

---

### `latest_blogs` array

Most recently published blog posts. Respects `blogs_limit`.

```json
[
  {
    "id": 1,
    "title": "10 Tips for Online Shopping Safety",
    "slug": "10-tips-online-shopping-safety",
    "author": {
      "id": 1,
      "username": "admin",
      "first_name": "Admin",
      "last_name": "User",
      "profile_image": null,
      "verification_status": "verified",
      "average_rating": 0,
      "is_premium": false,
      "profile_type": "individual",
      "rank": "private"
    },
    "category": {
      "id": 1,
      "name": "Safety",
      "name_en": "Safety",
      "slug": "safety",
      "description": "",
      "icon": "fa-shield",
      "color": "#28a745",
      "order": 1,
      "is_active": true,
      "blogs_count": 5
    },
    "image": "http://domain.com/media/blog/safety.jpg",
    "published_date": "2026-03-01T10:00:00Z",
    "views_count": 500,
    "likes_count": 45,
    "is_liked": false,
    "is_published": true
  }
]
```

---

## Error Responses

### `400 Bad Request`
Returned when an invalid non-integer value is passed for a limit parameter (the server silently falls back to defaults, so this will not normally occur).

### `500 Internal Server Error`
```json
{
  "detail": "An unexpected error occurred."
}
```

---

## Usage Examples

### Fetch home page for Egypt (default)
```http
GET /api/home/
```

### Fetch home page for Saudi Arabia with custom limits
```http
GET /api/home/?country=SA&latest_ads_limit=12&featured_ads_limit=8&blogs_limit=6
```

### JavaScript (fetch)
```js
const response = await fetch('http://domain.com/api/home/?country=EG');
const data = await response.json();

const { home_page, sliders, categories_by_section, latest_ads, featured_ads, latest_blogs } = data;
```

### Axios
```js
const { data } = await axios.get('/api/home/', {
  params: {
    country: 'EG',
    latest_ads_limit: 10,
    featured_ads_limit: 6,
    blogs_limit: 5,
  },
});
```

### React Native (fetch)
```js
const res = await fetch(`${BASE_URL}/api/home/?country=EG&latest_ads_limit=10`);
const json = await res.json();
```

---

## Notes

- **No authentication required.** The endpoint is fully public.
- **`is_favorited`** in ads is always `false` for unauthenticated users. Authenticated users will see accurate favorites status if a valid `Authorization: Bearer {token}` header is provided.
- **Country fallback:** If `country` is omitted, the server uses the country stored in the session/cookie (set by the country-selector middleware). For API clients with no session, pass `country` explicitly to get predictable results.
- **Featured ads fallback:** If no featured/highlighted ads exist for the country, `featured_ads` returns the same content as `latest_ads`.
- **Slider country filter:** Sliders with no country assigned are always included regardless of the `country` parameter.
