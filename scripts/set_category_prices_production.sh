#!/bin/bash
#
# Script to set category prices on PRODUCTION database
# Usage: ./scripts/set_category_prices_production.sh [OPTIONS]
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}  Set Category Prices - PRODUCTION${NC}"
echo -e "${YELLOW}=================================================${NC}"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo -e "${RED}Error: Virtual environment not found at .venv/${NC}"
        exit 1
    fi
fi

# Set production settings
export DJANGO_SETTINGS_MODULE=idrissimart.settings.docker

echo -e "${GREEN}✓ Using production settings${NC}"
echo ""

# Parse command line arguments, default to dry-run if no args provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}No arguments provided, running in DRY-RUN mode${NC}"
    echo -e "${YELLOW}To apply changes, run: $0 --apply${NC}"
    echo ""
    ARGS="--dry-run"
elif [ "$1" = "--apply" ]; then
    shift  # Remove --apply from args
    ARGS="$@"
    echo -e "${RED}⚠️  WARNING: This will modify PRODUCTION data!${NC}"
else
    ARGS="$@"
fi

# Run the management command
python manage.py set_all_category_prices $ARGS

echo ""
echo -e "${GREEN}Done!${NC}"
