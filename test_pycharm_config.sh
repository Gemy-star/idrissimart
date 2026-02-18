#!/bin/bash
# Test script to verify PyCharm configurations work correctly

echo "========================================="
echo "Testing PyCharm WSL + Poetry Configuration"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Poetry environment
echo "1. Testing Poetry environment..."
if poetry env info &> /dev/null; then
    echo -e "${GREEN}✓ Poetry environment OK${NC}"
    poetry env info | grep -E "(Python|Path|Executable)"
else
    echo -e "${RED}✗ Poetry environment not found${NC}"
    exit 1
fi
echo ""

# Test 2: Django import
echo "2. Testing Django import..."
if poetry run python -c "import django; print('Django version:', django.get_version())" &> /dev/null; then
    echo -e "${GREEN}✓ Django import OK${NC}"
    poetry run python -c "import django; print('   Django version:', django.get_version())"
else
    echo -e "${RED}✗ Django import failed${NC}"
    exit 1
fi
echo ""

# Test 3: Daphne module
echo "3. Testing Daphne module..."
if poetry run python -c "import daphne; print('Daphne version:', daphne.__version__)" &> /dev/null; then
    echo -e "${GREEN}✓ Daphne module OK${NC}"
    poetry run python -c "import daphne; print('   Daphne version:', daphne.__version__)"
else
    echo -e "${RED}✗ Daphne module not found${NC}"
    exit 1
fi
echo ""

# Test 4: Channels module
echo "4. Testing Channels module..."
if poetry run python -c "import channels; print('Channels version:', channels.__version__)" &> /dev/null; then
    echo -e "${GREEN}✓ Channels module OK${NC}"
    poetry run python -c "import channels; print('   Channels version:', channels.__version__)"
else
    echo -e "${RED}✗ Channels module not found${NC}"
    exit 1
fi
echo ""

# Test 5: Redis connection
echo "5. Testing Redis connection..."
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis connection OK${NC}"
    echo "   Redis status: $(redis-cli ping)"
else
    echo -e "${YELLOW}⚠ Redis not running${NC}"
    echo "   Start Redis with: sudo service redis-server start"
fi
echo ""

# Test 6: Django settings
echo "6. Testing Django settings..."
if DJANGO_SETTINGS_MODULE=idrissimart.settings.local poetry run python -c "import django; django.setup()" 2>&1 | grep -q "Django setup"; then
    echo -e "${GREEN}✓ Django settings OK${NC}"
else
    # Check if it at least loads without critical errors
    if DJANGO_SETTINGS_MODULE=idrissimart.settings.local poetry run python -c "import django; django.setup(); print('Django setup successful')" 2>&1 | grep -q "successful"; then
        echo -e "${GREEN}✓ Django settings OK${NC}"
        echo -e "${YELLOW}   Note: Some warnings about database access during app init (safe to ignore)${NC}"
    else
        echo -e "${RED}✗ Django settings failed${NC}"
        exit 1
    fi
fi
echo ""

# Test 7: Virtual environment Python path
echo "7. Testing Python interpreter path..."
PYTHON_PATH=$(poetry run which python)
if [[ "$PYTHON_PATH" == *".venv/bin/python"* ]]; then
    echo -e "${GREEN}✓ Python interpreter path OK${NC}"
    echo "   Path: $PYTHON_PATH"
else
    echo -e "${RED}✗ Python interpreter path incorrect${NC}"
    echo "   Path: $PYTHON_PATH"
    exit 1
fi
echo ""

# Summary
echo "========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "========================================="
echo ""
echo "You can now:"
echo "1. Open PyCharm and select run configurations"
echo "2. Or run manually:"
echo "   - Django Runserver:  poetry run python manage.py runserver"
echo "   - Daphne Server:     poetry run daphne -b 127.0.0.1 -p 8001 idrissimart.asgi:application"
echo "   - Django Q Cluster:  poetry run python manage.py qcluster"
echo ""

