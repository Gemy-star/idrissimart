# Docker Development Environment Guide

## Overview

This guide covers the development environment setup for Idrissimart using Docker.

## Quick Start

### 1. Initial Setup

```bash
# Copy the development environment file
cp .env.development .env

# Edit .env if needed (optional for development)
nano .env

# Build and start services
make -f Makefile.dev setup
```

### 2. Create Superuser

```bash
make -f Makefile.dev createsuperuser
```

### 3. Access the Application

- **Web Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Email Testing UI**: http://localhost:3100 (SMTP4Dev)

## Available Commands

Use the Makefile for convenient development commands:

```bash
# Show all available commands
make -f Makefile.dev help

# Start services
make -f Makefile.dev up

# Stop services
make -f Makefile.dev down

# View logs
make -f Makefile.dev logs
make -f Makefile.dev logs-web
make -f Makefile.dev logs-qcluster

# Run migrations
make -f Makefile.dev migrate
make -f Makefile.dev makemigrations

# Django shell
make -f Makefile.dev shell

# Bash shell in container
make -f Makefile.dev bash

# Run tests
make -f Makefile.dev test

# Fresh restart (clean slate)
make -f Makefile.dev fresh
```

## Service Architecture

### Development Services

1. **db** (MariaDB 11.2)
   - Port: 3306
   - Database: idrissimart
   - User: idrissimart_user
   - Password: idrissimart_password

2. **redis** (Redis 7)
   - Port: 6379
   - Password: redispassword

3. **web** (Django Development Server)
   - Port: 8000
   - Auto-reload enabled
   - Debug mode ON

4. **daphne** (WebSocket Server)
   - Port: 8001
   - For Django Channels

5. **qcluster** (Django-Q Task Queue)
   - Background task processor

6. **nginx** (Reverse Proxy)
   - Port: 80, 443

7. **smtp4dev** (Email Testing)
   - Web UI: Port 3100
   - SMTP: Port 2525

## Key Differences from Production

| Feature | Development | Production |
|---------|-------------|------------|
| Server | Django runserver | Gunicorn |
| Debug Mode | ON | OFF |
| Hot Reload | Yes | No |
| Code Mounting | Volume mount (editable) | Copied (read-only) |
| Dependencies | All (including dev) | Production only |
| Email | SMTP4Dev (testing) | Real SMTP server |
| SSL | Disabled | Enabled |
| Resource Limits | None | Configured |
| User | root | appuser |

## Development Workflow

### Making Code Changes

1. Edit files locally - changes are immediately reflected in containers
2. Django's auto-reload will restart the server automatically
3. For structural changes, restart services:
   ```bash
   make -f Makefile.dev restart
   ```

### Database Operations

```bash
# Create migrations
make -f Makefile.dev makemigrations

# Apply migrations
make -f Makefile.dev migrate

# Access database shell
make -f Makefile.dev db-shell

# Backup database
make -f Makefile.dev backup-db

# Restore database
make -f Makefile.dev restore-db FILE=backup_20240101_120000.sql
```

### Working with Dependencies

```bash
# Install new packages
make -f Makefile.dev install-packages PACKAGES="requests beautifulsoup4"

# Update all packages
make -f Makefile.dev update-packages

# Rebuild after dependency changes
make -f Makefile.dev build
make -f Makefile.dev up
```

### Testing Email

1. Send emails from your application
2. View them in SMTP4Dev UI: http://localhost:3100
3. No actual emails are sent externally

### Debugging

```bash
# View live logs
make -f Makefile.dev logs

# View specific service logs
make -f Makefile.dev logs-web
make -f Makefile.dev logs-qcluster

# Interactive debugging with ipdb
# Add this to your code:
import ipdb; ipdb.set_trace()

# Access shell
make -f Makefile.dev shell
```

### Background Tasks (Django-Q)

```bash
# View Django-Q logs
make -f Makefile.dev logs-qcluster

# Schedule tasks (if you have setup script)
docker-compose exec web python manage.py setup_scheduled_tasks

# Check scheduled tasks
docker-compose exec web python manage.py qinfo
```

## Troubleshooting

### Services Won't Start

```bash
# Check service status
make -f Makefile.dev ps

# View logs for errors
make -f Makefile.dev logs

# Try a fresh restart
make -f Makefile.dev fresh
```

### Database Connection Errors

```bash
# Check database is running
docker-compose ps db

# Check database logs
make -f Makefile.dev logs-db

# Restart database
docker-compose restart db
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000

# Stop conflicting services or change port in docker-compose.yml
```

### Volume Permission Issues

```bash
# If you get permission errors, check volume ownership
ls -la media/ staticfiles/

# Fix permissions if needed
sudo chown -R $USER:$USER media/ staticfiles/
```

### Clear Everything and Start Fresh

```bash
# Nuclear option - removes all containers, volumes, and images
make -f Makefile.dev clean

# Rebuild from scratch
make -f Makefile.dev setup
```

## Performance Tips

1. **Use volume mounts for code** (already configured)
2. **Keep containers running** - don't stop/start frequently
3. **Use `make restart`** for quick restarts
4. **Monitor resources**: `make -f Makefile.dev stats`

## Environment Variables

Key development environment variables in `.env`:

```env
DEBUG=True
DJANGO_SETTINGS_MODULE=idrissimart.settings.development
DB_HOST=db
REDIS_HOST=redis
EMAIL_HOST=smtp4dev
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web
```

## Switching to Production

To deploy to production:

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Or use the deployment script
./docker-deploy-prod.sh
```

## Additional Resources

- [Docker Documentation](DOCKER_GUIDE.md)
- [Production Setup](DOCKER_SETUP_SUMMARY.md)
- [Testing Services](TEST_SERVICES_GUIDE.md)

## Support

If you encounter issues:

1. Check logs: `make -f Makefile.dev logs`
2. Verify services are running: `make -f Makefile.dev ps`
3. Try fresh restart: `make -f Makefile.dev fresh`
4. Check this guide's troubleshooting section
