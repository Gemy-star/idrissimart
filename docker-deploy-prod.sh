#!/bin/bash

# =============================================================================
# Docker Production Deployment Script
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Idrissimart Production Docker Deployment          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  This script should be run with sudo for production setup${NC}"
    echo -e "${YELLOW}Continue anyway? (y/n)${NC}"
    read -r answer
    if [ "$answer" != "y" ]; then
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
        echo -e "${YELLOW}⚠️  Please configure .env with production values!${NC}"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found!${NC}"
        exit 1
    fi
fi

# Create required directories
echo -e "${BLUE}📁 Creating required directories...${NC}"
sudo mkdir -p /var/lib/idrissimart/mariadb
sudo mkdir -p ./backups
sudo mkdir -p ./docker/nginx/ssl
sudo chown -R $USER:$USER /var/lib/idrissimart
sudo chown -R $USER:$USER ./backups

# Pull latest code
echo -e "${BLUE}📥 Pulling latest code...${NC}"
if [ -d .git ]; then
    git pull
else
    echo -e "${YELLOW}⚠️  Not a git repository, skipping pull${NC}"
fi

# Backup database if exists
if docker ps -a | grep -q idrissimart_mariadb_prod; then
    echo -e "${BLUE}💾 Creating database backup...${NC}"
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
    docker compose -f docker compose.prod.yml exec -T db mysqldump \
        -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} > $BACKUP_FILE 2>/dev/null || true
    if [ -f "$BACKUP_FILE" ]; then
        echo -e "${GREEN}✓ Backup saved to: $BACKUP_FILE${NC}"
    fi
fi

# Build images
echo -e "${BLUE}🔨 Building Docker images...${NC}"
docker compose -f docker compose.prod.yml build --no-cache

# Stop existing containers
echo -e "${BLUE}⏹️  Stopping existing containers...${NC}"
docker compose -f docker compose.prod.yml down

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
docker compose -f docker compose.prod.yml up -d

# Wait for services
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 20

# Check service health
echo -e "${BLUE}🏥 Checking service health...${NC}"
docker compose -f docker compose.prod.yml ps

# Run migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
docker compose -f docker compose.prod.yml exec -T web python manage.py migrate --noinput

# Compress CSS/JS (required because COMPRESS_OFFLINE=True in production)
echo -e "${BLUE}🗜️  Compressing static assets (CSS/JS)...${NC}"
docker compose -f docker compose.prod.yml exec -T web python manage.py compress --force

# Collect static files
echo -e "${BLUE}📦 Collecting static files...${NC}"
docker compose -f docker compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Compile translations
echo -e "${BLUE}🌍 Compiling translations...${NC}"
docker compose -f docker compose.prod.yml exec -T web python manage.py compilemessages || true

# Clear cache
echo -e "${BLUE}🗑️  Clearing cache...${NC}"
docker compose -f docker compose.prod.yml exec -T web python manage.py shell -c "from django.core.cache import cache; cache.clear()" || true

# Restart services
echo -e "${BLUE}🔄 Restarting services...${NC}"
docker compose -f docker compose.prod.yml restart

# Final status
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Deployment Complete! ✅                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Service Status:${NC}"
docker compose -f docker compose.prod.yml ps

echo ""
echo -e "${GREEN}🌐 Application URLs:${NC}"
echo -e "   - Main: http://$(hostname -I | awk '{print $1}')"
echo -e "   - Admin: http://$(hostname -I | awk '{print $1}')/admin/"

echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "   View logs:     docker compose -f docker compose.prod.yml logs -f"
echo -e "   Stop:          docker compose -f docker compose.prod.yml down"
echo -e "   Restart:       docker compose -f docker compose.prod.yml restart"
echo -e "   Shell:         docker compose -f docker compose.prod.yml exec web python manage.py shell"
echo -e "   Django Q:      docker compose -f docker compose.prod.yml logs -f qcluster"

echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo -e "   1. Update .env with production values"
echo -e "   2. Configure SSL certificates in docker/nginx/ssl/"
echo -e "   3. Update nginx config for your domain"
echo -e "   4. Set up automated backups"
echo -e "   5. Configure firewall rules"
