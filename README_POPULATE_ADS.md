# Populate Ads Command - Usage Guide

## Overview
This management command creates surveying engineering classified ads with images for testing and development purposes.

## Features
- ✅ Creates realistic surveying equipment ads
- ✅ Automatically adds images from `static/images/ads/`
- ✅ Supports multiple categories (used equipment, rental, maintenance, books)
- ✅ Can update existing ads without images
- ✅ Randomizes ad properties (urgency, highlighting, views, etc.)

## Usage

### Create New Ads with Images

```bash
# Create 50 new ads for Egypt
python manage.py populate_ads 50 --country_code=EG

# Create 100 new ads for Saudi Arabia
python manage.py populate_ads 100 --country_code=SA
```

### Update Existing Ads (Add Images)

```bash
# Update all existing ads that don't have images
python manage.py populate_ads 0 --update_existing
```

## Image Requirements

The command looks for images in: `static/images/ads/`

**Supported formats:**
- `.jpg`
- `.png`

**Current images:**
- `ad-1.jpg`
- `ad-2.jpg`

**How it works:**
- Each ad gets 1-3 random images from the available images
- Images are copied to `media/ads/images/` with unique names
- Images are ordered (order: 1, 2, 3)

## Ad Categories

The command creates ads for these surveying categories:

1. **Used Equipment** (معدات مستعملة)
   - Total stations
   - GPS receivers
   - Laser levels
   - Theodolites

2. **Rental** (إيجار)
   - Total stations
   - 3D laser scanners
   - Survey drones

3. **Maintenance** (صيانة)
   - Calibration services
   - GPS calibration
   - Equipment repair

4. **Books & Software** (كتب وبرامج)
   - Technical books
   - Software licenses
   - Training materials

## Custom Fields

Each ad includes realistic custom fields based on category:

**For Equipment:**
- Brand
- Model
- Condition
- Year purchased
- Usage hours
- Warranty remaining

**For Rental:**
- Rental period
- Hourly/daily/monthly rates
- Deposit required
- Delivery available

**For Services:**
- Service type
- Brands supported
- Turnaround time
- Certification provided
- Warranty period

## Examples

### Full Workflow

```bash
# 1. Activate virtual environment
& C:/WORK/idrissimart/.venv/Scripts/Activate.ps1

# 2. Create 30 new ads with images
python manage.py populate_ads 30

# 3. Check created ads in admin dashboard
# Visit: http://localhost:8000/admin/dashboard

# 4. Later, if you add more images to static/images/ads/
# Update existing ads without images:
python manage.py populate_ads 0 --update_existing
```

### Add More Sample Images

To add more variety:

1. Place images in `static/images/ads/`
2. Name them descriptively (e.g., `surveying-equipment-1.jpg`)
3. Run the command again

The system will automatically use all available images.

## Tips

- **Start small:** Test with 5-10 ads first
- **Check images:** Ensure images exist in `static/images/ads/`
- **Update mode:** Use `--update_existing` to add images to old ads
- **Clean up:** Delete test ads from admin dashboard when done

## Troubleshooting

**No images added?**
- Check if `static/images/ads/` exists
- Ensure images are `.jpg` or `.png` format
- Check console output for warnings

**Command fails?**
- Ensure countries are populated first: `python manage.py populate_countries`
- Ensure users exist: `python manage.py populate_users`
- Ensure categories exist: `python manage.py populate_categories`

**Images not showing?**
- Run `python manage.py collectstatic`
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings
- Verify file permissions
