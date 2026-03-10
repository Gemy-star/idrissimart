#!/bin/bash

# Idrissimart API Setup Script
# This script installs all required dependencies for the API

echo "=========================================="
echo "Idrissimart API Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found${NC}"
echo ""

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Warning: You are not in a virtual environment${NC}"
    echo "It's recommended to use a virtual environment"
    echo ""
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Installing API dependencies..."
echo ""

# Install using pip
if [ -f "requirements_api.txt" ]; then
    echo -e "${YELLOW}Installing from requirements_api.txt...${NC}"
    pip install -r requirements_api.txt

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
    else
        echo -e "${RED}✗ Failed to install dependencies${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}requirements_api.txt not found. Installing packages individually...${NC}"

    # Install packages individually
    pip install "djangorestframework>=3.16.1,<4.0.0"
    pip install "djangorestframework-simplejwt>=5.3.0,<6.0.0"
    pip install "django-cors-headers>=4.9.0,<5.0.0"
    pip install "django-filter>=25.1,<26.0"
    pip install "markdown>=3.9,<4.0"
    pip install "drf-yasg[validation]>=1.21.11,<2.0.0"
    pip install "inflection>=0.5.1"
    pip install "ruamel.yaml>=0.17.0"
    pip install "uritemplate>=4.1.1"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
    else
        echo -e "${RED}✗ Failed to install some dependencies${NC}"
        exit 1
    fi
fi

echo ""
echo "Verifying installations..."
echo ""

# Verify each package
packages=("rest_framework" "rest_framework_simplejwt" "corsheaders" "drf_yasg" "django_filters")
all_installed=true

for package in "${packages[@]}"; do
    python -c "import $package" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $package${NC}"
    else
        echo -e "${RED}✗ $package (failed)${NC}"
        all_installed=false
    fi
done

echo ""

if [ "$all_installed" = true ]; then
    echo -e "${GREEN}=========================================="
    echo "Installation completed successfully! ✓"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Run: python manage.py migrate"
    echo "2. Run: python manage.py runserver"
    echo "3. Visit: http://localhost:8000/api/swagger/"
    echo ""
    echo "Documentation:"
    echo "- Swagger UI: http://localhost:8000/api/swagger/"
    echo "- ReDoc: http://localhost:8000/api/redoc/"
    echo ""
    echo "For more information, see:"
    echo "- docs/API_SETUP_GUIDE.md"
    echo "- docs/SWAGGER_REDOC_GUIDE.md"
    echo "- docs/API_SETUP_CHECKLIST.md"
    echo ""
else
    echo -e "${RED}=========================================="
    echo "Installation completed with errors"
    echo "=========================================="
    echo ""
    echo "Some packages failed to install."
    echo "Please check the error messages above and try again."
    echo ""
    exit 1
fi
