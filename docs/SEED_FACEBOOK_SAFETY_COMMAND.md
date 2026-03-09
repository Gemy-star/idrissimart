# Seed Facebook & Safety Tips Data - Management Command

## Overview
Custom Django management command to populate the database with test data for Facebook Share Requests and Safety Tips.

## Command File
`main/management/commands/seed_facebook_safety.py`

## Usage

### Basic Usage
```bash
# Seed with default values (20 Facebook requests, 15 safety tips)
python manage.py seed_facebook_safety
```

### Custom Counts
```bash
# Specify custom counts
python manage.py seed_facebook_safety --facebook-requests=50 --safety-tips=30
```

### Clear Existing Data
```bash
# Clear existing Facebook requests before seeding
python manage.py seed_facebook_safety --clear-facebook

# Clear existing safety tips before seeding
python manage.py seed_facebook_safety --clear-tips

# Clear all existing data before seeding
python manage.py seed_facebook_safety --clear-all
```

### Complete Example
```bash
# Clear all data and seed with custom counts
python manage.py seed_facebook_safety --clear-all --facebook-requests=100 --safety-tips=25
```

## Command Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--facebook-requests` | Integer | 20 | Number of Facebook share requests to create |
| `--safety-tips` | Integer | 15 | Number of safety tips to create |
| `--clear-facebook` | Flag | False | Clear existing Facebook share requests before seeding |
| `--clear-tips` | Flag | False | Clear existing safety tips before seeding |
| `--clear-all` | Flag | False | Clear all existing data before seeding |

## Prerequisites

The command requires existing data in the database:
1. **Active Ads** - At least one active classified ad
2. **Categories** - At least one category
3. **Superuser** - At least one superuser account

If any of these are missing, the command will display an error message.

## What Gets Created

### Facebook Share Requests

#### Statuses Distribution:
- **30%** Pending
- **20%** In Progress
- **40%** Completed
- **10%** Rejected

#### Features:
- Random payment amounts: 50.00, 75.00, or 100.00 SAR
- Payment confirmation status (varies by status)
- Request dates spanning last 90 days
- Processed requests include:
  - Processing date (1-5 days after request)
  - Processed by (random superuser)
  - Admin notes (status-specific)
  - Facebook post URL (for completed requests)

#### Example Data:
```python
FacebookShareRequest:
    ad: Random active ad
    status: 'completed'
    payment_amount: 75.00
    payment_confirmed: True
    requested_at: 30 days ago
    processed_at: 32 days ago
    processed_by: Admin user
    facebook_post_url: "https://facebook.com/idrissimart/posts/12345"
    admin_notes: "تم النشر بنجاح على الصفحة الرسمية"
```

### Safety Tips

#### 15 Pre-defined Templates:
1. Verify Seller Identity
2. Meet in Public Places
3. Inspect Before Payment
4. Avoid Advance Transfers
5. Use Secure Payment Methods
6. Beware of Very Low Prices
7. Don't Share Personal Info
8. Document Agreement in Writing
9. Bring Someone With You
10. Check Warranty
11. Review Official Documents
12. Trust Your Instincts
13. Use Internal Messaging
14. Verify Product Ownership
15. Research the Product

#### Features:
- Bilingual content (Arabic & English)
- Random color themes: blue, green, red, yellow, purple, orange
- Random Font Awesome icons
- 50% general tips, 50% category-specific
- 75% active, 25% inactive
- 30% chance of being assigned to multiple categories
- Sequential ordering (0, 10, 20, ...)

#### Example Data:
```python
SafetyTip:
    title: "تحقق من هوية البائع"
    title_en: "Verify Seller Identity"
    description: "تأكد دائماً من هوية البائع..."
    description_en: "Always verify the seller's identity..."
    icon_class: "fas fa-shield-alt"
    color_theme: "tip-blue"
    category: Electronics (or None for general)
    categories: [Electronics, Vehicles]  # Maybe multiple
    is_active: True
    order: 10
```

## Output Example

```
🌱 Starting Facebook & Safety Tips data seeding...

Clearing existing Facebook share requests...
✓ Cleared Facebook requests

Clearing existing safety tips...
✓ Cleared safety tips

Creating 50 Facebook share requests...
✓ Created 50 Facebook share requests

Creating 25 safety tips...
✓ Created 25 safety tips

🎉 Seeding completed successfully!
```

## Use Cases

### 1. Development Testing
```bash
# Quick test data for development
python manage.py seed_facebook_safety --facebook-requests=10 --safety-tips=5
```

### 2. Design/UI Testing
```bash
# Populate with lots of data to test UI/pagination
python manage.py seed_facebook_safety --facebook-requests=100 --safety-tips=30
```

### 3. Fresh Start
```bash
# Clear everything and start fresh
python manage.py seed_facebook_safety --clear-all --facebook-requests=20 --safety-tips=15
```

### 4. Testing Filters
```bash
# Create many requests to test status/payment filters
python manage.py seed_facebook_safety --facebook-requests=50
```

### 5. Testing Admin Features
```bash
# Seed data then test admin bulk actions, processing, etc.
python manage.py seed_facebook_safety --clear-all --facebook-requests=30
```

## Tips

1. **Run after migrations**: Ensure all migrations are applied before running
2. **Create base data first**: Have at least one ad, category, and superuser
3. **Use --clear flags carefully**: They will delete all existing data
4. **Realistic data**: The command creates realistic test data with proper relationships
5. **Idempotent**: Can be run multiple times to add more data (without clear flags)

## Troubleshooting

### Error: "No active ads found"
**Solution**: Create at least one active classified ad
```bash
python manage.py populate_ads  # If you have this command
# Or create an ad through the admin/frontend
```

### Error: "No categories found"
**Solution**: Create categories first
```bash
python manage.py populate_categories  # Or populate_categories_simple
```

### Error: "No superusers found"
**Solution**: Create a superuser
```bash
python manage.py createsuperuser
```

### Too much data created
**Solution**: Clear and re-seed with lower counts
```bash
python manage.py seed_facebook_safety --clear-all --facebook-requests=5 --safety-tips=5
```

## Integration with Other Commands

### Complete Setup Flow
```bash
# 1. Run migrations
python manage.py migrate

# 2. Create superuser
python manage.py createsuperuser

# 3. Populate categories
python manage.py populate_categories_simple

# 4. Create some ads (or do manually)
python manage.py populate_ads --count=20

# 5. Seed Facebook & Safety Tips data
python manage.py seed_facebook_safety --facebook-requests=30 --safety-tips=20
```

## Code Structure

```python
class Command(BaseCommand):
    def add_arguments(parser):
        # Define command-line arguments

    def handle(*args, **options):
        # Main command logic
        # 1. Clear data (if requested)
        # 2. Get existing data (ads, categories, users)
        # 3. Seed Facebook requests
        # 4. Seed safety tips

    def _seed_facebook_requests(count, ads, superusers):
        # Create Facebook share requests with:
        # - Random status distribution
        # - Payment details
        # - Processing information

    def _seed_safety_tips(count, categories):
        # Create safety tips from templates with:
        # - Bilingual content
        # - Random styling
        # - Category associations
```

## Future Enhancements

Possible improvements to this command:
1. Add `--dry-run` flag to preview what would be created
2. Add `--only-facebook` or `--only-tips` flags
3. Allow custom status distributions via arguments
4. Import tips from CSV/JSON file
5. Add progress bars for large datasets
6. Generate random post URLs with more variety
7. Create related Payment records for Facebook requests
8. Add more tip templates or load from external source

## Related Files

- Models: `main/models.py` (FacebookShareRequest, SafetyTip)
- Admin Views: `main/facebook_share_admin_views.py`, `main/safety_tip_admin_views.py`
- Publisher Views: `main/publisher_facebook_views.py`
- Templates: `templates/admin/`, `templates/classifieds/`
- Documentation: `docs/PUBLISHER_FACEBOOK_INTERFACE.md`, `docs/SAFETY_TIPS_SYSTEM.md`
