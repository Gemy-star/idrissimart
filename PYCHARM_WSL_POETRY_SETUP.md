# PyCharm WSL + Poetry Setup Guide

## Fixed Issues

### Problem
PyCharm was trying to use a Windows path for Python interpreter:
```
C:\WORK\idrissimart\.venv\Scripts\python.exe
```

But you're running in WSL with path:
```
/opt/WORK/idrissimart/.venv/bin/python
```

Also, the interpreter path was corrupted with:
```
/opt/WORK/idrissimart/.venv/bin/pytho/bin/python
```

### Solution Applied
1. Fixed `.idea/misc.xml` to use Poetry interpreter correctly
2. Verified all dependencies are installed via Poetry
3. Confirmed Redis configuration for local development

## PyCharm Configuration Steps

### 1. Configure Python Interpreter

1. Open PyCharm Settings: `File` → `Settings` (or `Ctrl+Alt+S`)
2. Navigate to: `Project: idrissimart` → `Python Interpreter`
3. Click the gear icon ⚙️ → `Add...`
4. Select `WSL` from the left sidebar
5. Choose `Poetry Environment`
6. Select the existing environment at: `/opt/WORK/idrissimart/.venv`
7. Click `OK`

**Important:** The interpreter should be named `Poetry (idrissimart)` and point to:
```
/opt/WORK/idrissimart/.venv/bin/python
```

### 2. Verify Poetry Integration

In the terminal within PyCharm, verify:

```bash
# Check Poetry environment
poetry env info

# Should show:
# Virtualenv
# Python:         3.12.3
# Implementation: CPython
# Path:           /opt/WORK/idrissimart/.venv
# Executable:     /opt/WORK/idrissimart/.venv/bin/python
```

### 3. Redis Setup for Local Development

The project is configured to use a local Redis server on `127.0.0.1:6379`.

#### Install and Start Redis (if not already running):

```bash
# Install Redis
sudo apt update
sudo apt install redis-server -y

# Start Redis
sudo service redis-server start

# Verify Redis is running
redis-cli ping
# Should return: PONG

# Check Redis status
sudo service redis-server status
```

#### Alternative: Start Redis without sudo

If you want to run Redis in the current terminal:

```bash
redis-server
```

### 4. Run Configurations

The following run configurations are set up:

#### Django Runserver
- **Command:** `manage.py runserver 127.0.0.1:8000`
- **Settings:** `idrissimart.settings.local`
- **URL:** http://127.0.0.1:8000

#### Daphne ASGI Server (Channels)
- **Command:** `python -m daphne -b 127.0.0.1 -p 8001 --verbosity 2 idrissimart.asgi:application`
- **Settings:** `idrissimart.settings.local`
- **Port:** 8001
- **Purpose:** WebSocket support for real-time features

#### Django Q Cluster (Task Queue)
- **Command:** `manage.py qcluster`
- **Settings:** `idrissimart.settings.local`
- **Purpose:** Async task processing

#### Full Dev Stack
- **Compound configuration** that runs:
  - Django Runserver (HTTP)
  - Django Q Cluster (Tasks)

### 5. Running the Application

#### Option A: Using PyCharm Run Configurations

1. Select a run configuration from the dropdown (top-right)
2. Click the green play button ▶️

#### Option B: Using Terminal Commands

```bash
# Activate Poetry environment
poetry shell

# Or run commands with poetry run
poetry run python manage.py runserver

# Run Daphne
poetry run daphne -b 127.0.0.1 -p 8001 idrissimart.asgi:application

# Run Django Q cluster
poetry run python manage.py qcluster
```

### 6. Verify Installation

Test that everything is working:

```bash
# Verify Django can be imported
poetry run python -c "import django; print(django.get_version())"

# Verify Daphne is installed
poetry run python -m daphne --version

# Verify Channels is installed
poetry run python -c "import channels; print(channels.__version__)"

# Check Redis connection
poetry run python manage.py shell -c "from django_q.conf import redis_client; print('Redis OK' if redis_client.ping() else 'Redis Failed')"
```

## Common Issues and Solutions

### Issue 1: "Couldn't import Django"
**Cause:** Python interpreter not set correctly or virtual environment not activated.

**Solution:**
1. Verify interpreter in PyCharm settings
2. Restart PyCharm
3. Rebuild project indexes: `File` → `Invalidate Caches / Restart`

### Issue 2: "No module named daphne"
**Cause:** Dependencies not installed or wrong Python interpreter.

**Solution:**
```bash
# Install dependencies
poetry install

# Verify daphne is installed
poetry run python -m daphne --version
```

### Issue 3: Redis Connection Error
**Cause:** Redis server not running.

**Solution:**
```bash
# Start Redis
sudo service redis-server start

# Verify
redis-cli ping
```

### Issue 4: PyCharm Not Detecting WSL Changes
**Solution:**
1. `File` → `Invalidate Caches / Restart`
2. Restart PyCharm
3. Reopen project from WSL path: `\\wsl.localhost\Ubuntu-24.04\opt\WORK\idrissimart`

## Project Structure

```
idrissimart/
├── .venv/                      # Poetry virtual environment
│   └── bin/python              # Python interpreter
├── .idea/                      # PyCharm configuration
│   ├── misc.xml                # Interpreter settings
│   └── runConfigurations/      # Run configurations
├── idrissimart/
│   └── settings/
│       ├── local.py            # Local development settings (uses local Redis)
│       ├── docker.py           # Docker settings
│       └── common.py           # Common settings
├── pyproject.toml              # Poetry dependencies
├── poetry.lock                 # Locked dependencies
└── manage.py                   # Django management script
```

## Environment Settings

The project uses `idrissimart.settings.local` for local development, which includes:

- **Database:** SQLite (`db.sqlite3`)
- **Redis:** Local Redis at `127.0.0.1:6379`
- **Email:** smtp4dev (for testing)
- **Debug:** Enabled
- **Channels:** WebSocket support via Redis
- **Django-Q:** Task queue via Redis

## Next Steps

1. ✅ Python interpreter configured
2. ✅ Poetry environment verified
3. ✅ Dependencies installed
4. ⬜ Start Redis server
5. ⬜ Run migrations: `poetry run python manage.py migrate`
6. ⬜ Create superuser: `poetry run python manage.py createsuperuser`
7. ⬜ Start development server

## Quick Start Commands

```bash
# Start Redis (one-time per reboot)
sudo service redis-server start

# Run migrations
poetry run python manage.py migrate

# Create superuser (if needed)
poetry run python manage.py createsuperuser

# Run development server
poetry run python manage.py runserver

# In a separate terminal: Run Django Q cluster
poetry run python manage.py qcluster
```

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [PyCharm WSL Support](https://www.jetbrains.com/help/pycharm/using-wsl-as-a-remote-interpreter.html)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Django-Q2 Documentation](https://django-q2.readthedocs.io/)

