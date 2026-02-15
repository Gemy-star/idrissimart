#!/bin/bash

# =============================================================================
# Docker Quick Start Script for Idrissimart
# =============================================================================

set -e

echo "🐳 Starting Idrissimart Docker Setup..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Copying from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file. Please update it with your values.${NC}"
        echo -e "${YELLOW}Edit .env file and run this script again.${NC}"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Build images
echo -e "${GREEN}📦 Building Docker images...${NC}"
docker compose build

# Start services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker compose up -d

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 10

# Run migrations
echo -e "${GREEN}🔄 Running database migrations...${NC}"
docker compose exec -T web python manage.py migrate

# Collect static files
echo -e "${GREEN}📁 Collecting static files...${NC}"
docker compose exec -T web python manage.py collectstatic --noinput

# Create superuser (optional)
echo -e "${YELLOW}👤 Do you want to create a superuser? (y/n)${NC}"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    docker compose exec web python manage.py createsuperuser
fi

# Show status
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Services running:"
docker compose ps

echo ""
echo -e "${GREEN}🌐 Access your application:${NC}"
echo "   - Main site: http://localhost"
echo "   - Admin: http://localhost/admin/"
echo ""
echo -e "${GREEN}📝 Useful commands:${NC}"
echo "   - View logs: docker compose logs -f"
echo "   - Stop services: docker compose down"
echo "   - Restart: docker compose restart"
echo "   - Shell: docker compose exec web python manage.py shell"
