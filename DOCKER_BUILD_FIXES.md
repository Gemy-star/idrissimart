# Docker Build Fixes Applied

## 🔧 Issues Fixed

### 1. Missing `pkg-config` Package ✅
**Problem**: `mysqlclient` couldn't build because `pkg-config` was missing
```
/bin/sh: 1: pkg-config: not found
Exception: Can not find valid pkg-config name.
```

**Solution**: Added `pkg-config` to system dependencies in Dockerfile

### 2. Dockerfile Casing Warnings ✅
**Problem**: Docker warned about inconsistent `FROM ... as` casing
```
WARN: FromAsCasing: 'as' and 'FROM' keywords' casing do not match
```

**Solution**: Changed all `FROM ... as` to `FROM ... AS` (uppercase)

### 3. Switched to Poetry for Dependency Management ✅
**Problem**: Using pip with multiple requirements files was complex and error-prone

**Solution**:
- ✅ Installed Poetry 1.8.0 in Docker image
- ✅ Using `pyproject.toml` and `poetry.lock` for all dependencies
- ✅ Removed pip fallback - Poetry only
- ✅ Simplified dependency installation process

### Dependencies Now Managed by Poetry:
- Production dependencies in `[tool.poetry.dependencies]`
- Development dependencies in `[tool.poetry.group.dev.dependencies]`
- Single source of truth for all packages
- Automatic lock file management
- ✅ `pkg-config` - Required for building mysqlclient
- ✅ Poetry 1.8.0 - Modern Python dependency manager

### Build Process:
1. **Base Stage**: Install system packages + Poetry
2. **Builder Stage**: Install Python dependencies via Poetry
3. **Production Stage**: Copy virtual environment and app code

### 4. Missing GLib/Cairo Libraries (libgobject-2.0-0) ✅
**Problem**: Python packages failed with missing shared library error
```
OSError: cannot load library 'libgobject-2.0-0': libgobject-2.0-0:
cannot open shared object file: No such file or directory
```

**Root Cause**:
- Python packages like WeasyPrint, cairocffi require GLib/Cairo system libraries
- These were not installed in the base Docker image

**Solution**: Added required system libraries to Dockerfile
```dockerfile
libglib2.0-0          # GLib library (provides libgobject-2.0-0)
libcairo2             # Cairo 2D graphics library
libpango-1.0-0        # Pango text layout library
libpangocairo-1.0-0   # Pango Cairo bindings
libgdk-pixbuf-2.0-0   # GDK Pixbuf image loading
```

**Note**: Initially had wrong package name `libgdk-pixbuf2.0-0` (dot instead of hyphen), which was corrected to `libgdk-pixbuf-2.0-0`.

**Verification**:
```bash
docker compose exec web ldconfig -p | grep libgobject
docker compose exec web ldconfig -p | grep libcairo
```

### 5. Container Naming Issue (trophy vs idrissimart) ✅
**Problem**: Containers were created with wrong project name
```
host not found in upstream "web:8000" in /etc/nginx/conf.d/trophy.conf:2
Container names: trophy_web, trophy_nginx, trophy_db instead of idrissimart_*
```

**Root Cause**:
- Docker Compose derives project name from directory or COMPOSE_PROJECT_NAME
- Old containers from previous project still running
- Project name wasn't explicitly set in .env

**Solution**:
1. Stopped and removed all `trophy_*` containers
2. Added `COMPOSE_PROJECT_NAME=idrissimart` to `.env` file
3. Rebuilt images with correct project name

**Commands Used**:
```bash
# Remove old containers
docker stop trophy_web trophy_daphne trophy_qcluster trophy_nginx trophy_redis trophy_db
docker rm trophy_web trophy_daphne trophy_qcluster trophy_nginx trophy_redis trophy_db

# Set project name in .env
echo "COMPOSE_PROJECT_NAME=idrissimart" >> .env

# Rebuild with correct name
docker compose build
```

**Verification**:
```bash
docker compose ps
# Should show: idrissimart_web, idrissimart_nginx, etc.
```

## 🚀 Build Command

Current build running with:
```bash
docker compose build --no-cache
```

This will take 3-5 minutes on first build.

## ✅ After Build Completes

Run these commands:

```bash
# 1. Start services
docker compose up -d

# 2. Check status
docker compose ps

# 3. Run migrations
docker compose exec web python manage.py migrate

# 4. Collect static files
docker compose exec web python manage.py collectstatic --noinput

# 5. Create superuser
docker compose exec web python manage.py createsuperuser

# 6. Access application
# http://localhost
```

## 📊 Monitor Build Progress

```bash
# Check if build is complete
docker compose ps

# View build logs
docker compose logs -f

# Check images
docker images | grep idrissimart
```

## 🐛 If Build Fails

```bash
# Check logs
docker compose build 2>&1 | tee build.log

# Clean and rebuild
docker compose down -v
docker system prune -f
docker compose build --no-cache
```

---

**Status**: ✅ All fixes applied, build in progress
**Next**: Wait for build to complete, then start services
