#!/bin/bash

# =============================================================================
# Docker Backup Script for Idrissimart
# Schedule this with cron for automated backups
# =============================================================================

set -e

# Configuration
BACKUP_DIR="/opt/WORK/idrissimart/backups"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="docker compose.prod.yml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting backup process...${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Database backup
echo -e "${YELLOW}Backing up database...${NC}"
DB_BACKUP_FILE="$BACKUP_DIR/db_${DATE}.sql"

if docker compose -f $COMPOSE_FILE exec -T db mysqldump \
    -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} > "$DB_BACKUP_FILE" 2>/dev/null; then

    # Compress backup
    gzip "$DB_BACKUP_FILE"
    echo -e "${GREEN}✓ Database backup: $DB_BACKUP_FILE.gz${NC}"
else
    echo -e "${RED}✗ Database backup failed${NC}"
fi

# Media files backup (optional - uncomment if needed)
# echo -e "${YELLOW}Backing up media files...${NC}"
# MEDIA_BACKUP_FILE="$BACKUP_DIR/media_${DATE}.tar.gz"
# tar -czf "$MEDIA_BACKUP_FILE" ./media/
# echo -e "${GREEN}✓ Media backup: $MEDIA_BACKUP_FILE${NC}"

# Clean old backups
echo -e "${YELLOW}Cleaning old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# List recent backups
echo -e "${GREEN}Recent backups:${NC}"
ls -lh "$BACKUP_DIR" | tail -n 10

echo -e "${GREEN}Backup process complete!${NC}"

# Optional: Upload to remote storage (S3, etc.)
# aws s3 cp "$DB_BACKUP_FILE.gz" s3://your-bucket/backups/
