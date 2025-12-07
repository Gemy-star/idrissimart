# Populate Dummy Data Command

This document explains how to use the `populate_dummy_data` management command to generate test data for your IdrissiMart application.

## Overview

The command creates dummy data for:
- **AdReview**: User reviews and ratings for classified ads
- **AdReport**: Reports for ads or users (spam, fraud, inappropriate content, etc.)
- **UserPackage**: User package purchases with payment records
- **AdReservation**: Ad reservations/bookings (الحجوزات) with payment amounts and delivery details

## Prerequisites

Before running this command, ensure you have:
1. **Users** in the database (use `populate_users` command if needed)
2. **Classified Ads** (use `populate_ads` command if needed)
3. **Ad Packages** for creating user packages

## Usage

### Basic Usage

Create specific numbers of each type:

```bash
python manage.py populate_dummy_data --reviews 50 --reports 30 --packages 20 --reservations 40
```

### Create All Types Equally

Use `--all` to create the same number of each type:

```bash
python manage.py populate_dummy_data --all 100
```

This creates 100 reviews, 100 reports, 100 packages, and 100 reservations.

### Individual Options

```bash
# Create only reviews
python manage.py populate_dummy_data --reviews 50

# Create only reports
python manage.py populate_dummy_data --reports 30

# Create only packages
python manage.py populate_dummy_data --packages 20

# Create only reservations
python manage.py populate_dummy_data --reservations 40
```

## Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--reviews N` | Number of ad reviews to create | `--reviews 50` |
| `--reports N` | Number of ad reports to create | `--reports 30` |
| `--packages N` | Number of user packages to create | `--packages 20` |
| `--reservations N` | Number of ad reservations to create | `--reservations 40` |
| `--all N` | Create N of each type (overrides individual counts) | `--all 100` |

## Generated Data Details

### AdReview (Reviews)
- Random ratings from 1-5 stars (weighted towards higher ratings: 40% for 5 stars)
- Mix of Arabic and English comments
- 90% approved, 10% not approved
- Random creation dates within the last 180 days
- Respects unique constraint (one review per user per ad)

### AdReport (Reports)
- All report types: `ad_content`, `fraud`, `spam`, `wrong_category`, `user_behavior`, `fake_info`, `other`
- 70% ad reports, 30% user reports
- Status distribution:
  - 40% pending
  - 30% reviewing
  - 20% resolved
  - 10% rejected
- Resolved/rejected reports include admin notes and reviewer assignment
- Mix of Arabic and English descriptions
- Random creation dates within the last 90 days

### UserPackage (Packages)
- Random purchase dates within the last year
- Automatic expiry date calculation based on package duration
- Random ads used/remaining counts
- 80% include payment records with completed status
- Payment includes Paymob provider and transaction IDs
- Mix of active and expired packages

### AdReservation (Reservations/الحجوزات)
- Reservation amount is 10-50% of full ad price
- Full amount based on actual ad price (or generated if not available)
- Delivery fees between 0-100 SAR
- Status distribution:
  - 30% pending
  - 40% confirmed
  - 15% completed
  - 10% cancelled
  - 5% refunded
- 50% include Arabic notes (customer requests)
- 70% include delivery addresses (Saudi cities)
- Automatic expiry calculation (48 hours for pending/confirmed)
- Random creation dates within the last 60 days
- Realistic amounts and delivery information

## Examples

### Quick Test Setup
```bash
# Small test dataset
python manage.py populate_dummy_data --all 10
```

### Development Environment
```bash
# Moderate dataset for development
python manage.py populate_dummy_data --reviews 50 --reports 25 --packages 30 --reservations 40
```

### Staging/Demo Environment
```bash
# Larger dataset for realistic testing
python manage.py populate_dummy_data --all 200
```

### Focus on Reservations
```bash
# Create many reservations for testing booking system
python manage.py populate_dummy_data --reservations 100
```

## Verification

Check the created data:

```bash
python manage.py shell -c "from main.models import AdReview, AdReport, UserPackage, AdReservation; print(f'Reviews: {AdReview.objects.count()}'); print(f'Reports: {AdReport.objects.count()}'); print(f'Packages: {UserPackage.objects.count()}'); print(f'Reservations: {AdReservation.objects.count()}')"
```

Check reservation statuses:

```bash
python manage.py shell -c "from main.models import AdReservation; print(f'Pending: {AdReservation.objects.filter(status=\"pending\").count()}'); print(f'Confirmed: {AdReservation.objects.filter(status=\"confirmed\").count()}'); print(f'Completed: {AdReservation.objects.filter(status=\"completed\").count()}')"
```

## Notes

1. The command will skip creation if required data doesn't exist (users, ads, packages)
2. Some records may be skipped due to constraints (e.g., duplicate reviews)
3. Arabic text is safely handled for Windows console environments
4. All timestamps are randomized to simulate realistic historical data
5. Payment records are automatically created for most user packages
6. Reservations include realistic Saudi addresses and Arabic customer notes
7. Reservation amounts are calculated as percentages of ad prices for realism

## Related Commands

- `populate_users` - Create dummy users
- `populate_ads` - Create dummy classified ads
- `populate_categories` - Create ad categories
- `seed_payments` - Create payment records

## Troubleshooting

### No users found
```bash
python manage.py populate_users 20
```

### No ads found
```bash
python manage.py populate_ads 50
```

### No packages found
Check that AdPackage records exist in your database through the admin panel or create them manually.
