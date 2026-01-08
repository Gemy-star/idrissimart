#!/bin/bash
# =============================================================================
# Database Integrity Fix - Quick Run Script
# =============================================================================
# This script fixes invalid country_id values in the users table
# before running Django migrations
# =============================================================================

echo "============================================================"
echo "🔧 Database Integrity Fix - Starting..."
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "fix_db_integrity.py" ]; then
    echo -e "${RED}❌ Error: fix_db_integrity.py not found!${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Error: Poetry not found!${NC}"
    echo "Please install Poetry first."
    exit 1
fi

# Backup database (for MySQL/MariaDB)
echo -e "${YELLOW}📦 Creating database backup...${NC}"
if command -v mysqldump &> /dev/null; then
    # Get database info from Django settings
    DB_NAME=$(poetry run python -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])" 2>/dev/null)
    DB_USER=$(poetry run python -c "from django.conf import settings; print(settings.DATABASES['default']['USER'])" 2>/dev/null)

    if [ ! -z "$DB_NAME" ]; then
        BACKUP_FILE="backup_before_fix_$(date +%Y%m%d_%H%M%S).sql"
        mysqldump -u "$DB_USER" -p "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not create backup (optional)${NC}"
        fi
    fi
fi

echo ""

# Run the fix script
echo -e "${YELLOW}🔄 Running database integrity fix...${NC}"
echo ""

poetry run python fix_db_integrity.py

FIX_STATUS=$?

echo ""

if [ $FIX_STATUS -eq 0 ]; then
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}✅ Database integrity fix completed successfully!${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run migrations: poetry run python manage.py migrate"
    echo "2. Verify system: poetry run python manage.py check"
else
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}❌ Database integrity fix failed!${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo "Please check the error messages above."
    echo "You may need to:"
    echo "1. Check database connection settings"
    echo "2. Ensure at least one active country exists"
    echo "3. Verify database permissions"
    exit 1
fi

echo ""
read -p "Do you want to run migrations now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}🔄 Running migrations...${NC}"
    poetry run python manage.py migrate

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Migrations completed successfully!${NC}"

        echo ""
        echo -e "${YELLOW}🔍 Running system check...${NC}"
        poetry run python manage.py check
    else
        echo ""
        echo -e "${RED}❌ Migration failed!${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ All done!${NC}"
echo -e "${GREEN}============================================================${NC}"
