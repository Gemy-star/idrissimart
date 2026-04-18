# Advertising Space & Swiper Carousel Feature

## Overview
This feature enables multiple advertisers to purchase the same advertising space (مساحة الاعلانية), with their ads displayed in a rotating carousel using Swiper.js.

## Key Changes

### 1. Database Model Updates

#### New Field: `advertising_space`
- **Location**: `main/models.py` - `PaidAdvertisement` model
- **Type**: `CharField(max_length=100, blank=True, null=True)`
- **Purpose**: Groups multiple ads together to share the same display slot
- **Arabic Label**: "المساحة الإعلانية"
- **Help Text**: "معرف المساحة الإعلانية - يمكن لعدة معلنين شراء نفس المساحة وسيتم عرضهم بالتناوب"

#### Migration
- **File**: `main/migrations/1007_add_advertising_space_field.py`
- **Command to Apply**: `python manage.py migrate main`

### 2. Model Methods

#### `get_ads_grouped_by_space()`
```python
PaidAdvertisement.get_ads_grouped_by_space(
    country_code=None,
    placement_type=None,
    category=None,
    ad_type=None
)
```
- Returns ads grouped by `advertising_space` and `ad_type`
- Ads with the same `advertising_space` are grouped together for carousel display
- Ads without an `advertising_space` are treated as individual items

#### `get_category_ads_grouped()`
```python
PaidAdvertisement.get_category_ads_grouped(category, country_code)
```
- Convenience method for fetching category-specific ads grouped by space
- Returns dictionary with ad_type keys containing lists of ad groups

### 3. Template Updates

All three ad component templates have been updated to support both single ads and multiple ads (carousel):

#### Banner Template (`templates/components/paid_ads/banner.html`)
- **Usage**: `{% include 'components/paid_ads/banner.html' with ads=ad_list %}`
- **Features**:
  - Automatic Swiper carousel when multiple ads provided
  - Navigation arrows and pagination dots
  - 5-second autoplay interval
  - Responsive design for mobile/desktop

#### Sidebar Template (`templates/components/paid_ads/sidebar.html`)
- **Usage**: `{% include 'components/paid_ads/sidebar.html' with ads=ad_list %}`
- **Features**:
  - Vertical carousel format
  - Pagination dots only (no arrows)
  - 6-second autoplay interval
  - Card-based design

#### Featured Box Template (`templates/components/paid_ads/featured_box.html`)
- **Usage**: `{% include 'components/paid_ads/featured_box.html' with ads=ad_list %}`
- **Features**:
  - Full-width featured carousel
  - Navigation arrows and pagination
  - 7-second autoplay interval
  - Two-column layout (image + content)

### 4. View Updates

#### Category Detail View (`main/views.py`)
Updated to use the new grouping methods:

```python
category_paid_ads_grouped = PaidAdvertisement.get_category_ads_grouped(
    category=self.category,
    country_code=selected_country
)

# Organized by ad type
category_paid_ads = {
    'banner': [...],      # List of all banner ads
    'sidebar': [...],     # List of all sidebar ads
    'featured_box': [...], # List of all featured box ads
    'popup': [...]        # List of all popup ads
}
```

#### Subcategory Detail View
Same structure as category view, ensuring consistent behavior across all category pages.

### 5. Admin Interface

#### Updated Fields
- **List Display**: Added `advertising_space` column to see which ads share slots
- **Fieldsets**: Added `advertising_space` field in "Placement & Targeting" section
- **Description**: Added help text explaining the carousel feature in Arabic

#### How Admins Use This Feature
1. Create multiple paid advertisements
2. Assign the same `advertising_space` identifier to ads that should rotate
3. Example: Set `advertising_space = "homepage-banner-1"` for 3 different advertisers
4. All 3 ads will display in a carousel in the same slot

### 6. API Updates

#### Serializers (`api/serializers.py`)
- Added `advertising_space` field to `PaidAdvertisementSerializer` (read)
- Added `advertising_space` field to `PaidAdvertisementCreateSerializer` (write)
- Publishers can now specify advertising_space when creating ads via API

## How It Works

### Single Ad Display
```django
{% if category_paid_ads.banner %}
    {% include 'components/paid_ads/banner.html' with ads=category_paid_ads.banner %}
{% endif %}
```
- If only one ad exists: displays static ad (no carousel)
- If multiple ads exist: displays Swiper carousel with all ads

### Multiple Advertisers on Same Space

#### Example Scenario:
1. **Advertiser A**: Creates banner ad with `advertising_space = "category-tech-banner"`
2. **Advertiser B**: Creates banner ad with `advertising_space = "category-tech-banner"`
3. **Advertiser C**: Creates banner ad with `advertising_space = "category-tech-banner"`

**Result**: All 3 ads rotate in a carousel in the same banner slot on the Technology category page.

### Benefits
- **Revenue**: Multiple advertisers can share premium placement slots
- **Fair Distribution**: All advertisers get equal visibility through rotation
- **User Experience**: Fresh, rotating content keeps pages dynamic
- **Analytics**: Each ad tracks its own views and clicks independently

## Technical Details

### Swiper Configuration

#### Banner Swiper
```javascript
{
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    autoplay: { delay: 5000 },
    pagination: { clickable: true },
    navigation: { nextEl, prevEl }
}
```

#### Sidebar Swiper
```javascript
{
    slidesPerView: 1,
    spaceBetween: 15,
    loop: true,
    autoplay: { delay: 6000 },
    pagination: { clickable: true }
}
```

#### Featured Box Swiper
```javascript
{
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    autoplay: { delay: 7000 },
    pagination: { clickable: true },
    navigation: { nextEl, prevEl }
}
```

### Analytics Tracking
- Each ad tracks views and clicks independently
- View tracking fires on page load for all ads in carousel
- Click tracking fires when user clicks on any slide
- CTR (Click-Through Rate) calculated per ad

## Migration Steps

1. **Backup Database**
   ```bash
   python manage.py dumpdata main.PaidAdvertisement > paid_ads_backup.json
   ```

2. **Apply Migration**
   ```bash
   python manage.py migrate main
   ```

3. **Verify**
   - Check admin interface for new `advertising_space` field
   - Test creating ads with same `advertising_space` value
   - Verify carousel displays on category pages

## Usage Examples

### Admin: Creating Shared Advertising Space

```python
# In Django Admin, create 3 banner ads:

Ad 1:
- Title: "Spring Sale - Company A"
- advertising_space: "homepage-main-banner"
- ad_type: "banner"

Ad 2:
- Title: "New Products - Company B"
- advertising_space: "homepage-main-banner"
- ad_type: "banner"

Ad 3:
- Title: "Limited Offer - Company C"
- advertising_space: "homepage-main-banner"
- ad_type: "banner"
```

Result: All 3 ads display in rotating carousel at the same homepage banner position.

### API: Creating Ad via REST API

```json
POST /api/paid-ads/
{
    "title": "Summer Promotion",
    "advertising_space": "category-electronics-banner",
    "ad_type": "banner",
    "placement_type": "category",
    "category": 5,
    "country": 1,
    "image": "...",
    "target_url": "https://example.com",
    "start_date": "2026-04-18T00:00:00Z",
    "end_date": "2026-05-18T23:59:59Z"
}
```

## Troubleshooting

### Issue: Carousel Not Showing, Only Single Ad
**Cause**: Only one active ad exists for that space
**Solution**: Verify multiple ads have:
- Same `advertising_space` value
- Same `ad_type`
- `status = ACTIVE`
- `is_active = True`
- Current date within `start_date` and `end_date` range

### Issue: Swiper Not Loading
**Cause**: Missing Swiper CSS/JS
**Solution**: Verify `base.html` includes Swiper imports:
```html
<link rel="stylesheet" href="/static/node_modules/swiper/swiper-bundle.min.css">
```

### Issue: Ads from Different Categories Mixing
**Cause**: View not filtering by category properly
**Solution**: Check view implementation ensures category filtering:
```python
category_paid_ads_grouped = PaidAdvertisement.get_category_ads_grouped(
    category=self.category,  # Ensure correct category
    country_code=selected_country
)
```

## Future Enhancements

- [ ] Add admin action to bulk assign advertising_space
- [ ] Create predefined advertising_space choices for consistency
- [ ] Add rotation statistics per advertising_space
- [ ] Implement weighted rotation based on payment tier
- [ ] Add A/B testing capabilities for ad performance

## Related Documentation

- [AD_PRICING_SYSTEM.md](./AD_PRICING_SYSTEM.md)
- [AD_FEATURES_PAYMENT_SYSTEM.md](./AD_FEATURES_PAYMENT_SYSTEM.md)
- [ADMIN_PACKAGES_SUBSCRIPTIONS_MANAGEMENT.md](./ADMIN_PACKAGES_SUBSCRIPTIONS_MANAGEMENT.md)

---

**Last Updated**: April 18, 2026
**Author**: GitHub Copilot
**Version**: 1.0
