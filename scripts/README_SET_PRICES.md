# Set Category Prices - Production Script

This script safely updates `ad_creation_price` for categories and subcategories on the **production database**.

## Features

- ✅ Automatically uses production settings (`idrissimart.settings.docker`)
- ✅ Shows current settings module, database, and DEBUG mode before running
- ✅ Defaults to **dry-run mode** for safety
- ✅ Requires explicit confirmation when modifying production data
- ✅ Displays preview table before making changes
- ✅ Supports filtering by section type and parent categories

---

## Quick Start

### 1. Dry Run (Preview Changes - SAFE)

```bash
cd /opt/WORK/idrissimart
./scripts/set_category_prices_production.sh
```

This will show what changes **would** be made without modifying the database.

### 2. Apply Changes (Modify Production Database)

```bash
./scripts/set_category_prices_production.sh --apply
```

You'll be prompted to type 'yes' to confirm.

---

## Usage Examples

### Set all subcategories to 300 (default)
```bash
./scripts/set_category_prices_production.sh --apply
```

### Set all subcategories to a different price (e.g., 500)
```bash
./scripts/set_category_prices_production.sh --apply --price 500
```

### Include root/parent categories
```bash
./scripts/set_category_prices_production.sh --apply --include-roots
```

### Filter by section type
```bash
./scripts/set_category_prices_production.sh --apply --section-type classified
```

### Combine multiple options
```bash
./scripts/set_category_prices_production.sh --apply --price 300 --include-roots --section-type classified
```

---

## Direct Command Usage

If you prefer to run the Django management command directly:

### Using Production Settings:
```bash
cd /opt/WORK/idrissimart
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=idrissimart.settings.docker
python manage.py set_all_category_prices --dry-run
```

### Using Local/Development Settings:
```bash
cd /opt/WORK/idrissimart
source .venv/bin/activate
python manage.py set_all_category_prices --dry-run
```

---

## Command Options

| Option | Description |
|--------|-------------|
| `--price AMOUNT` | Price to set (default: 300) |
| `--dry-run` | Preview changes without saving |
| `--include-roots` | Also update root/parent categories |
| `--section-type TYPE` | Filter by section type (classified, job, course, service, product) |

---

## Safety Features

1. **Dry-run by default**: Script runs in dry-run mode unless you explicitly use `--apply`
2. **Settings display**: Shows which database and settings module are being used
3. **Production confirmation**: Requires typing 'yes' when modifying production data
4. **Transaction safety**: All updates run in a database transaction (all-or-nothing)
5. **Preview table**: Shows all changes before applying them

---

## Output Example

```
=================================================
  Set Category Prices - PRODUCTION
=================================================

✓ Using production settings

================================================================================
Settings Module: idrissimart.settings.docker
Database: idrissimartdb
DEBUG Mode: False
================================================================================

⚠️  WARNING: Running on PRODUCTION database!
This will modify real data. Use --dry-run first to preview changes.

Are you sure you want to continue? Type 'yes' to proceed: yes

Setting ad_creation_price to 300 for subcategories only
Found 37 categories to update.

ID     Parent                         Category                               Current        New
-----------------------------------------------------------------------------------------------
191    New Survey Equipment           3d laser scanners                       150.00 →   300.00
174    New Survey Equipment           Accessories & Spare Parts               150.00 →   300.00
...

✓ Updated 37 categories, skipped 0 (already had target price)
```

---

## Troubleshooting

### "Virtual environment not found"
Make sure you're in the project root and `.venv` exists:
```bash
cd /opt/WORK/idrissimart
ls -la .venv/
```

### Wrong database being used
Check your environment variables:
```bash
echo $DJANGO_SETTINGS_MODULE
```
It should show `idrissimart.settings.docker` for production.

### Permission denied
Make the script executable:
```bash
chmod +x /opt/WORK/idrissimart/scripts/set_category_prices_production.sh
```

---

## Related Files

- Script: `/opt/WORK/idrissimart/scripts/set_category_prices_production.sh`
- Command: `/opt/WORK/idrissimart/main/management/commands/set_all_category_prices.py`
- Settings: `/opt/WORK/idrissimart/idrissimart/settings/docker.py`
