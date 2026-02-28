# Django Settings Configuration Guide

## Overview

This project uses multiple Django settings files to support different environments:
- Native local development (without Docker)
- Docker-based development (dev containers)
- Production deployment

## Settings Files Structure

```
idrissimart/settings/
├── __init__.py
├── common.py            # Shared base settings
├── local.py             # Native local development
├── docker_local.py      # Docker development (NEW)
└── docker.py            # Production
```

## Settings Files Explained

### 1. `common.py` - Base Settings

Contains shared configuration for all environments:
- Installed apps
- Middleware configuration
- Template settings
- Authentication backends
- Static/media file settings
- Social auth configuration
- Internationalization

**Do not run with this directly** - always use one of the environment-specific files.

### 2. `local.py` - Native Local Development

**Use when:** Running Django directly on your machine without Docker

```bash
# Activate virtual environment
source .venv/bin/activate

# Run Django
python manage.py runserver
```

**Configuration:**
- ✅ Debug mode: ON
- ✅ Database: SQLite (`db.sqlite3`)
- ✅ Redis: localhost:6379 (requires local Redis installation)
- ✅ Email: SMTP4Dev on localhost:2525 (if running)
- ✅ Allowed hosts: 127.0.0.1, localhost

**When to use:**
- Quick local testing without Docker
- Working on frontend/templates
- Simple debugging
- When Docker isn't available

**Setup:**
```bash
# Install Redis locally (macOS)
brew install redis
brew services start redis

# Or use Docker just for Redis
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. `docker_local.py` - Docker Development ⭐ RECOMMENDED

**Use when:** Developing with Docker or VS Code Dev Containers

```bash
# Start all services
docker-compose up

# Or with dev containers
code .  # Open in VS Code Dev Containers
```

**Configuration:**
- ✅ Debug mode: ON
- ✅ Database: MariaDB container (`db` service)
- ✅ Redis: Redis container (`redis` service)
- ✅ Email: SMTP4Dev container (`smtp4dev` service)
- ✅ Allowed hosts: *, localhost, web (Docker service names)
- ✅ Auto-reload: Enabled
- ✅ Volume mount: Code changes reflect immediately

**Benefits:**
- 🎯 Closest to production environment
- 🎯 All services containerized and coordinated
- 🎯 No manual service installation needed
- 🎯 Team members get identical environments
- 🎯 Clean isolation from host OS

**Environment Variables:**
```env
DJANGO_SETTINGS_MODULE=idrissimart.settings.docker_local
DB_HOST=db                    # Container service name
DB_NAME=idrissimart
DB_USER=idrissimart_user
DB_PASSWORD=idrissimart_password
REDIS_HOST=redis              # Container service name
REDIS_PASSWORD=redispassword
EMAIL_HOST=smtp4dev           # Container service name
```

**Access Points:**
- Django: http://localhost:8000
- Admin: http://localhost:8000/admin
- WebSockets: http://localhost:8001
- Email UI: http://localhost:3100
- MariaDB: localhost:3306
- Redis: localhost:6379

### 4. `docker.py` - Production

**Use when:** Deploying to production servers

```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Configuration:**
- ❌ Debug mode: OFF
- ✅ Database: Production MariaDB
- ✅ Redis: Production Redis with password
- ✅ Email: Real SMTP server
- ✅ HTTPS: Enforced
- ✅ Security headers: Enabled
- ✅ Static files: Compressed and cached
- ✅ Logging: File-based with filtering

**Security Features:**
- SSL redirect enabled
- Secure cookies
- XSS protection
- Content type sniffing protection
- Invalid host filtering (prevents spam logs)

## Quick Reference

### Starting Development

**With Docker (Recommended):**
```bash
# First time
cp .env.example .env
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Daily use
docker-compose up
```

**Without Docker:**
```bash
# First time
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Daily use
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=idrissimart.settings.local
python manage.py runserver
```

### Switching Settings

**Option 1: Environment Variable**
```bash
export DJANGO_SETTINGS_MODULE=idrissimart.settings.docker_local
python manage.py runserver
```

**Option 2: Command Line**
```bash
python manage.py runserver --settings=idrissimart.settings.local
```

**Option 3: .env File**
```env
DJANGO_SETTINGS_MODULE=idrissimart.settings.docker_local
```

## Comparison Matrix

| Feature | local.py | docker_local.py | docker.py |
|---------|----------|-----------------|-----------|
| **Environment** | Native | Docker Dev | Production |
| **Debug Mode** | ✅ ON | ✅ ON | ❌ OFF |
| **Database** | SQLite | MariaDB | MariaDB |
| **Redis** | localhost | Container | Container |
| **Email** | Console/SMTP4Dev | SMTP4Dev | Real SMTP |
| **Auto-reload** | ✅ Yes | ✅ Yes | ❌ No |
| **HTTPS** | ❌ No | ❌ No | ✅ Required |
| **Performance** | Fast | Good | Optimized |
| **Setup** | Simple | Medium | Complex |
| **Team Consistency** | ❌ Variable | ✅ Identical | ✅ Identical |

## Troubleshooting

### "Can't connect to database"

**If using `docker_local.py`:**
- Verify database container is running: `docker-compose ps db`
- Check connection: `docker-compose logs db`
- Ensure DB_HOST=db in .env

**If using `local.py`:**
- SQLite should work out of the box
- Check file permissions on `db.sqlite3`

### "Redis connection failed"

**If using `docker_local.py`:**
- Verify Redis container: `docker-compose ps redis`
- Check logs: `docker-compose logs redis`
- Ensure REDIS_HOST=redis in .env

**If using `local.py`:**
- Install Redis: `brew install redis` (macOS)
- Start Redis: `brew services start redis`
- Or use Docker: `docker run -d -p 6379:6379 redis`

### "Wrong settings being loaded"

Check which settings are active:
```python
# In Django shell
python manage.py shell
>>> from django.conf import settings
>>> print(settings.SETTINGS_MODULE)
>>> print(settings.DEBUG)
>>> print(settings.DATABASES)
```

Or check environment:
```bash
echo $DJANGO_SETTINGS_MODULE
```

### "Static files not loading"

```bash
# Collect static files
python manage.py collectstatic --noinput

# In Docker
docker-compose exec web python manage.py collectstatic --noinput
```

## Best Practices

### ✅ DO

1. **Use `docker_local.py` for team development** - ensures consistency
2. **Keep secrets in environment variables** - never hardcode passwords
3. **Use `.env` file** - don't pass secrets via command line
4. **Document any setting changes** - update this guide
5. **Test with production-like settings** before deployment

### ❌ DON'T

1. **Don't commit `.env` files** - they contain secrets
2. **Don't mix settings** - use one environment at a time
3. **Don't override settings in random places** - modify the settings files properly
4. **Don't use DEBUG=True in production** - serious security risk
5. **Don't hardcode database credentials** - use environment variables

## Migration Guide

### From `local.py` to `docker_local.py`

If you've been using native local development and want to switch to Docker:

1. **Update your .env:**
   ```env
   DJANGO_SETTINGS_MODULE=idrissimart.settings.docker_local
   DB_HOST=db
   REDIS_HOST=redis
   EMAIL_HOST=smtp4dev
   ```

2. **Start Docker services:**
   ```bash
   docker-compose up -d
   ```

3. **Migrate your database:**
   ```bash
   # Export from SQLite (if needed)
   python manage.py dumpdata > data.json
   
   # Import to MariaDB
   docker-compose exec web python manage.py loaddata data.json
   ```

4. **Verify everything works:**
   ```bash
   docker-compose logs -f
   ```

## VS Code Dev Containers

The project includes a `.devcontainer/devcontainer.json` configuration:

```jsonc
{
  "name": "Idrissimart Development",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "web",
  "remoteEnv": {
    "DJANGO_SETTINGS_MODULE": "idrissimart.settings.docker_local"
  }
}
```

To use:
1. Install "Dev Containers" extension in VS Code
2. Open project folder
3. Click "Reopen in Container" when prompted
4. VS Code will use `docker_local.py` automatically

## Additional Resources

- [Docker Development Guide](../DOCKER_DEV_GUIDE.md)
- [Production Deployment](../docker-compose.prod.yml)
- [Environment Variables](./.env.example)

## Support

If you have questions about settings configuration:
1. Check this guide first
2. Review the settings file comments
3. Check Docker logs: `docker-compose logs`
4. Consult team documentation

---

**Last Updated:** 2026-02-28
**Maintainer:** Development Team
