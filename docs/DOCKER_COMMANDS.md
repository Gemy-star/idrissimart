# Quick Docker Commands Reference - Fixed for Docker Compose V2

## ✅ All Fixed - Use these commands now

### Dependency Management
```bash
# Using Poetry (recommended)
poetry install              # Install all dependencies
poetry add package-name     # Add new package
poetry update               # Update dependencies

# Inside Docker container
docker compose exec web poetry show  # List installed packages
```

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f db
docker compose logs -f daphne
docker compose logs -f qcluster
```

### Django Management Commands
```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Django shell
docker compose exec web python manage.py shell

# Show migrations
docker compose exec web python manage.py showmigrations
```

### Database Commands
```bash
# Access MariaDB
docker compose exec db mysql -u root -p

# Backup database
docker compose exec db mysqldump -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} > backup.sql

# Restore database
docker compose exec -T db mysql -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} < backup.sql
```

###Redis Commands
```bash
# Access Redis CLI
docker compose exec redis redis-cli -a ${REDIS_PASSWORD}

# Clear cache
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} FLUSHALL
```

### Service Management
```bash
# Check status
docker compose ps

# Restart specific service
docker compose restart web
docker compose restart nginx

# Rebuild and restart
docker compose build
docker compose up -d
```

### Troubleshooting
```bash
# Stop all containers
docker compose down

# Remove volumes (⚠️ deletes data)
docker compose down -v

# Remove everything and start fresh
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## 🔧 First Time Setup

Wait for build to complete, then:

```bash
# 1. Wait for all containers to be "Up (healthy)"
docker compose ps

# 2. Run migrations
docker compose exec web python manage.py migrate

# 3. Collect static files
docker compose exec web python manage.py collectstatic --noinput

# 4. Create superuser
docker compose exec web python manage.py createsuperuser

# 5. Access application
# http://localhost
```

## ⚠️  Common Issues

### "docker-compose: command not found"
✅ FIXED - Use `docker compose` (with space) instead

### "Cannot connect to database"
```bash
# Check db is running
docker compose ps db

# Check logs
docker compose logs db

# Restart database
docker compose restart db
```

### Build taking too long
The first build can take 5-10 minutes. Subsequent builds are cached and much faster.

### Container keeps restarting
```bash
# Check logs to see the error
docker compose logs -f web
```
