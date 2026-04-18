# Paid Advertisement Seed Commands

This document explains how to use the seed commands to populate your database with sample paid advertisements for testing and demonstration.

## Available Commands

### 1. `seed_paid_ads` - Full Featured Seed Command

Creates comprehensive paid advertisement data with optional placeholder images from the internet.

#### Basic Usage

```bash
python manage.py seed_paid_ads
```

#### Options

- `--ads N` - Number of ads to create (default: 20)
- `--clear` - Clear all existing paid advertisements before seeding
- `--no-images` - Skip downloading images (faster, but ads won't have images)

#### Examples

```bash
# Create 20 ads with images from placeholder service
python manage.py seed_paid_ads

# Create 30 ads without images (faster)
python manage.py seed_paid_ads --ads 30 --no-images

# Clear existing ads and create 15 new ones
python manage.py seed_paid_ads --ads 15 --clear

# Create 50 ads without images, clearing old data
python manage.py seed_paid_ads --ads 50 --clear --no-images
```

#### What It Creates

- **5 advertiser users** (advertiser_1 through advertiser_5)
- **Shared advertising spaces** for carousel demonstration:
  - `homepage-hero-banner` - 3 banner ads
  - `homepage-sidebar-top` - 2 sidebar ads
  - `homepage-featured-middle` - 3 featured box ads
  - `category-tech-banner` - 2 category banner ads
  - `category-fashion-sidebar` - 2 category sidebar ads
- **Unique ads** - Remaining ads without shared spaces
- **Realistic data** including:
  - Arabic and English titles
  - Company names and contact info
  - Various ad types and placements
  - Random views and clicks analytics
  - Paid status with payment references

---

### 2. `quick_seed_ads` - Fast Local Seed Command

Creates ads with locally generated colored images. No internet required, faster execution.

#### Basic Usage

```bash
python manage.py quick_seed_ads
```

#### Options

- `--count N` - Number of ads to create (default: 20)
- `--clear` - Clear existing ads first

#### Examples

```bash
# Create 20 ads with locally generated images
python manage.py quick_seed_ads

# Create 10 ads, clearing old data
python manage.py quick_seed_ads --count 10 --clear

# Create 50 ads quickly
python manage.py quick_seed_ads --count 50
```

#### What It Creates

- **1 demo advertiser user** (demo_advertiser)
- **Shared advertising spaces**:
  - `homepage-main-banner` - 3 banner ads (different colors)
  - `homepage-sidebar` - 2 sidebar ads
  - `homepage-featured` - 3 featured box ads
  - `category-banner` - 2 category banner ads (if categories exist)
- **Simple colored images** - Locally generated, no download needed
- **Quick execution** - Much faster than downloading images

---

## Which Command Should I Use?

### Use `seed_paid_ads` when:
- ✅ You want realistic-looking placeholder images
- ✅ You have internet connection
- ✅ You're setting up a demo/staging environment
- ✅ You need diverse sample data with multiple advertisers

### Use `quick_seed_ads` when:
- ✅ You want fast seeding (no internet downloads)
- ✅ You're doing local development
- ✅ You need to test quickly
- ✅ You don't care about realistic images

---

## Testing the Carousel Feature

After running either seed command, you'll have multiple ads sharing the same `advertising_space`. To see the carousel in action:

### 1. Check the Homepage

Visit your homepage to see:
- Banner carousel at the top (3 rotating ads)
- Sidebar carousel (2 rotating ads)
- Featured box carousel (3 rotating ads)

### 2. Check Category Pages

Visit any category page to see category-specific carousels.

### 3. Admin Interface

Go to Django Admin → Paid Advertisements to:
- View all seeded ads
- See which ads share the same `advertising_space`
- Edit or manage the ads
- View analytics (views, clicks, CTR)

---

## Seed Data Structure

Both commands create ads with the following advertising spaces:

| Space Name | Ad Type | Placement | Count | Purpose |
|------------|---------|-----------|-------|---------|
| `homepage-hero-banner` | BANNER | GENERAL | 3 | Main homepage banner carousel |
| `homepage-sidebar-top` | SIDEBAR | GENERAL | 2 | Homepage sidebar carousel |
| `homepage-featured-middle` | FEATURED_BOX | GENERAL | 3 | Featured content carousel |
| `category-tech-banner` | BANNER | CATEGORY | 2 | Tech category banner carousel |
| `category-fashion-sidebar` | SIDEBAR | CATEGORY | 2 | Fashion category sidebar carousel |

---

## Cleaning Up

To remove all seeded data:

```bash
# Using either command with --clear
python manage.py seed_paid_ads --clear --ads 0
# or
python manage.py quick_seed_ads --clear --count 0
```

Or use Django shell:

```bash
python manage.py shell
>>> from main.models import PaidAdvertisement
>>> PaidAdvertisement.objects.all().delete()
```

---

## Sample Credentials

### Advertisers Created by `seed_paid_ads`:
- **Usernames**: advertiser_1, advertiser_2, advertiser_3, advertiser_4, advertiser_5
- **Password**: testpass123
- **Email**: advertiser_N@example.com

### Advertiser Created by `quick_seed_ads`:
- **Username**: demo_advertiser
- **Password**: demo123
- **Email**: advertiser@example.com

---

## Troubleshooting

### "No countries found!"
**Solution**: Run the country population command first:
```bash
python manage.py populate_countries
```

### "No categories found" warning
**Solution**: This is just a warning. The command will create general placement ads. To add categories:
```bash
python manage.py populate_categories
```

### Images not showing
**Causes**:
1. Used `--no-images` flag with `seed_paid_ads`
2. Internet connection failed during image download
3. Media files not properly configured

**Solutions**:
- Use `quick_seed_ads` for locally generated images
- Run `seed_paid_ads` without `--no-images` flag
- Check your MEDIA_ROOT and MEDIA_URL settings

---

## Advanced Usage

### Create ads for specific testing scenarios

```bash
# Scenario 1: Test carousel with many ads
python manage.py quick_seed_ads --count 30 --clear

# Scenario 2: Test with realistic diverse data
python manage.py seed_paid_ads --ads 40 --clear

# Scenario 3: Quick test without images
python manage.py seed_paid_ads --ads 10 --no-images --clear
```

### Verify created ads

```bash
python manage.py shell
>>> from main.models import PaidAdvertisement
>>>
>>> # Check total ads
>>> PaidAdvertisement.objects.count()
>>>
>>> # Check carousel ads
>>> PaidAdvertisement.objects.filter(advertising_space='homepage-hero-banner').count()
>>>
>>> # Check unique ads
>>> PaidAdvertisement.objects.filter(advertising_space__isnull=True).count()
```

---

## Related Documentation

- [ADVERTISING_SPACE_SWIPER_FEATURE.md](./ADVERTISING_SPACE_SWIPER_FEATURE.md) - Technical documentation
- [ADVERTISING_SPACE_ADMIN_GUIDE_AR.md](./ADVERTISING_SPACE_ADMIN_GUIDE_AR.md) - Arabic admin guide

---

**Last Updated**: April 18, 2026
