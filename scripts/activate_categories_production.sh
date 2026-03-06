#!/bin/bash

# Activate Inactive Categories - Production Script
# This script activates inactive categories in the production database

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}======================================${NC}"
echo -e "${YELLOW}  Activate Categories - Production${NC}"
echo -e "${YELLOW}======================================${NC}"
echo ""

# Set production settings
export DJANGO_SETTINGS_MODULE=idrissimart.settings.docker

# Default to dry-run for safety
DRY_RUN="--dry-run"
SECTION_TYPE="classified"
ROOTS_ONLY=""
AUTO_YES=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --apply)
            DRY_RUN=""
            shift
            ;;
        --section-type)
            SECTION_TYPE="$2"
            shift 2
            ;;
        --roots-only)
            ROOTS_ONLY="--roots-only"
            shift
            ;;
        --yes)
            AUTO_YES="--yes"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--apply] [--section-type TYPE] [--roots-only] [--yes]"
            exit 1
            ;;
    esac
done

# Show what we're doing
if [ -z "$DRY_RUN" ]; then
    echo -e "${RED}⚠️  PRODUCTION MODE - Will modify database${NC}"
else
    echo -e "${GREEN}✓ DRY RUN MODE - No changes will be made${NC}"
fi

echo -e "Section type: ${YELLOW}$SECTION_TYPE${NC}"
if [ -n "$ROOTS_ONLY" ]; then
    echo -e "Filter: ${YELLOW}Root categories only${NC}"
fi
echo ""

# Run the management command
python manage.py activate_categories \
    $DRY_RUN \
    --section-type "$SECTION_TYPE" \
    $ROOTS_ONLY \
    $AUTO_YES

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Command completed successfully${NC}"
else
    echo -e "${RED}✗ Command failed with exit code $EXIT_CODE${NC}"
fi

echo ""
echo -e "${YELLOW}Usage Examples:${NC}"
echo "  # Dry run (default - safe):"
echo "  ./scripts/activate_categories_production.sh"
echo ""
echo "  # Actually activate categories (requires confirmation):"
echo "  ./scripts/activate_categories_production.sh --apply"
echo ""
echo "  # Activate only root categories:"
echo "  ./scripts/activate_categories_production.sh --apply --roots-only"
echo ""
echo "  # Activate without confirmation (use with caution):"
echo "  ./scripts/activate_categories_production.sh --apply --yes"
echo ""

exit $EXIT_CODE
