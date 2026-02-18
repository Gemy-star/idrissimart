# PyCharm Run Configurations Guide

This project includes pre-configured PyCharm run configurations for easy development with Django, Daphne (ASGI), and Django Q.

## Available Configurations

### 1. Django Runserver
**Purpose**: Standard Django development server for HTTP requests (no WebSocket support)

**Configuration Details:**
- Port: 8000
- Host: 127.0.0.1
- Settings: `idrissimart.settings.local`
- Auto-opens browser at: http://127.0.0.1:8000

**When to use:**
- Regular Django development without WebSocket/Channels features
- Testing basic HTTP endpoints
- Simple debugging sessions

**How to run:**
1. Open PyCharm
2. Select "Django Runserver" from the run configuration dropdown (top right)
3. Click the green play button

---

### 2. Daphne ASGI Server
**Purpose**: ASGI server with full support for Django Channels and WebSockets

**Configuration Details:**
- Port: 8001
- Host: 127.0.0.1
- Settings: `idrissimart.settings.local`
- Verbosity: 2 (detailed logging)
- Module: Uses `idrissimart.asgi:application`

**Features:**
- Full WebSocket support via Django Channels
- Handles both HTTP and WebSocket protocols
- Real-time communication support

**When to use:**
- Testing WebSocket connections
- Real-time features (chat, notifications, live updates)
- Production-like ASGI environment

**How to run:**
1. Select "Daphne ASGI Server" from the run configuration dropdown
2. Click the green play button
3. Access your app at: http://127.0.0.1:8001

---

### 3. Django Q Cluster
**Purpose**: Background task worker for async/scheduled tasks

**Configuration Details:**
- Command: `manage.py qcluster`
- Settings: `idrissimart.settings.local`
- Requires: Redis server running

**Features:**
- Processes background tasks asynchronously
- Handles scheduled/cron jobs
- Task queue management

**When to use:**
- Testing scheduled tasks
- Processing background jobs
- Email sending, data processing, etc.

**Prerequisites:**
- Redis must be running (check docker-compose.yml)
- Django Q configuration in settings

**How to run:**
1. Ensure Redis is running: `docker-compose up redis -d`
2. Select "Django Q Cluster" from the run configuration dropdown
3. Click the green play button

---

### 4. All Services (Compound)
**Purpose**: Runs Daphne + Django Q simultaneously

**Components:**
- Daphne ASGI Server (port 8001)
- Django Q Cluster

**When to use:**
- Full-stack development with real-time and background features
- Testing complete application workflow
- Production-like environment

**How to run:**
1. Ensure Redis is running
2. Select "All Services (Compound)" from the run configuration dropdown
3. Click the green play button
4. Both services will start in separate tabs within the Run tool window

---

## Setup Instructions

### 1. Virtual Environment
Ensure your Python virtual environment is configured:
```bash
# The configurations expect: .venv/bin/python
python -m venv .venv
source .venv/bin/activate  # On Windows WSL: source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Python Interpreter in PyCharm
1. Go to: **File → Settings → Project → Python Interpreter**
2. Click the gear icon → **Add Interpreter → Add Local Interpreter**
3. Select **Existing Environment**
4. Choose: `<project_dir>/.venv/bin/python`

### 3. Django Settings
The run configurations use `idrissimart.settings.local` by default.
To change this, edit the XML files in `.idea/runConfigurations/` or modify via PyCharm UI:
1. **Run → Edit Configurations**
2. Select a configuration
3. Modify environment variables (e.g., `DJANGO_SETTINGS_MODULE`)

### 4. Redis Requirement (for Django Q)
Django Q requires Redis to be running. Start Redis via Docker:
```bash
docker-compose up redis -d
```

Or install locally:
```bash
# Ubuntu/WSL
sudo apt install redis-server
sudo service redis-server start
```

---

## Debugging

All configurations support PyCharm's debugger:

1. Set breakpoints in your code (click in the gutter next to line numbers)
2. Click the debug icon (bug symbol) instead of the play button
3. The application will pause at your breakpoints

### Debugging Tips:
- **Daphne**: Set breakpoints in views, WebSocket consumers
- **Django Q**: Set breakpoints in task functions
- **Multiple services**: Each service runs in a separate debug session

---

## Troubleshooting

### Configuration not found
If run configurations don't appear:
1. Restart PyCharm
2. Check `.idea/runConfigurations/` folder exists
3. Try: **Run → Edit Configurations → + → Import from File**

### "Module not found" errors
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python interpreter settings in PyCharm

### Daphne won't start
- Check if port 8001 is already in use
- Verify `idrissimart.asgi` module exists
- Check ASGI configuration in settings

### Django Q errors
- Ensure Redis is running: `redis-cli ping` (should return PONG)
- Check Django Q configuration in settings
- Verify `DJANGO_Q` settings in `settings/common.py` or `settings/local.py`

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

---

## Customization

### Changing Ports
Edit the configuration files in `.idea/runConfigurations/`:
- **Django Runserver**: Change `<option name="port" value="8000" />`
- **Daphne**: Change `-p 8001` in PARAMETERS

### Different Settings Module
Change the environment variable:
```xml
<env name="DJANGO_SETTINGS_MODULE" value="idrissimart.settings.docker" />
```

### Additional Django Q Options
Modify the PARAMETERS in `Django_Q_Cluster.xml`:
```xml
<option name="PARAMETERS" value="qcluster --verbosity 2" />
```

---

## Production Deployment

These configurations are for **development only**. For production:
- Use the systemd service files (`daphne.service`, `gunicorn.service`)
- Configure proper process managers (systemd, supervisor)
- Use production settings (`idrissimart.settings.docker`)
- Deploy with Docker (see `docker-compose.prod.yml`)

---

## Additional Resources

- **Django Channels**: https://channels.readthedocs.io/
- **Daphne**: https://github.com/django/daphne
- **Django Q2**: https://django-q2.readthedocs.io/
- **PyCharm Run Configurations**: https://www.jetbrains.com/help/pycharm/run-debug-configuration.html

---

## Quick Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Django Runserver | 8000 | HTTP | Basic development |
| Daphne | 8001 | HTTP + WS | ASGI + WebSockets |
| Django Q | - | - | Background tasks |
| Redis | 6379 | Redis | Task queue backend |

---

## Need Help?

Check the project documentation in `/docs/` or refer to:
- `DOCKER_GUIDE.md` for Docker setup
- `TEST_SERVICES_GUIDE.md` for testing services
- Project-specific docs in `/docs/` folder

