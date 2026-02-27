# VS Code Dev Container Setup

## Prerequisites

1. **Install VS Code Extensions:**
   - [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)

2. **Install Docker:**
   - Docker Desktop for Mac/Windows
   - Docker Engine for Linux

## Quick Start

### Method 1: Open in Container (Recommended)

1. Open VS Code
2. Press `Cmd/Ctrl + Shift + P`
3. Type: **"Dev Containers: Open Folder in Container"**
4. Select the `idrissimart` folder
5. Wait for container to build (first time takes a few minutes)
6. VS Code will reopen inside the container

### Method 2: Reopen in Container

1. Open the project folder in VS Code normally
2. VS Code will detect `.devcontainer/devcontainer.json`
3. Click **"Reopen in Container"** in the notification
4. Wait for container to build

### Method 3: Command Palette

1. Open project in VS Code
2. Press `Cmd/Ctrl + Shift + P`
3. Type: **"Dev Containers: Rebuild and Reopen in Container"**

## What Happens?

When you open in container, VS Code will:
- Build the Docker containers using `docker-compose.yml`
- Attach to the `web` service container
- Install recommended extensions inside the container
- Set up Python environment and linting
- Run migrations and collect static files
- Forward ports (8000, 8001, 3306, 6379, 3100)

## Features

### Automatic Port Forwarding

- **Port 8000** - Django web server
- **Port 8001** - WebSocket server (Daphne)
- **Port 3100** - Email testing UI (SMTP4Dev)
- **Port 3306** - MariaDB database
- **Port 6379** - Redis

Access them on your local machine at `http://localhost:PORT`

### Pre-installed Extensions

- Python language support
- Django syntax highlighting
- Code formatting (Black)
- Import sorting (isort)
- Linting (flake8)
- SQL tools for database access
- GitLens for Git integration
- And more...

### Code Quality Tools

- **Black** - Auto-formatting on save
- **isort** - Import organization on save
- **flake8** - Linting and error detection
- **Pylance** - IntelliSense and type checking

## Running the Development Server

The container doesn't auto-start Django. To run:

```bash
# In VS Code terminal (inside container)
python manage.py runserver 0.0.0.0:8000
```

Or use the integrated terminal:
1. Press `` Ctrl + ` `` to open terminal
2. Run: `python manage.py runserver 0.0.0.0:8000`
3. Access at http://localhost:8000

## Common Commands

All these run **inside** the container:

```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check
```

## Database Access

### Using VS Code SQLTools Extension

1. Open SQL Tools panel (sidebar icon)
2. Add new connection:
   - **Driver**: MySQL
   - **Host**: `db`
   - **Port**: `3306`
   - **Database**: `idrissimart`
   - **Username**: `idrissimart_user`
   - **Password**: `idrissimart_password`

### Using Terminal

```bash
# Django dbshell
python manage.py dbshell

# Direct MySQL
mysql -h db -u idrissimart_user -pidrissimart_password idrissimart
```

## Debugging

### Python Debugging

1. Set breakpoints in your code (click left of line number)
2. Press `F5` or go to Run and Debug panel
3. Select "Python: Django" configuration
4. Start debugging

### View Logs

```bash
# Django logs
docker-compose logs -f web

# All services
docker-compose logs -f
```

## Working with Other Services

Even though VS Code attaches to the `web` container, all services are running:

```bash
# Check running containers
docker-compose ps

# View qcluster logs
docker-compose logs -f qcluster

# Redis CLI
docker-compose exec redis redis-cli -a redispassword

# Access database
docker-compose exec db mysql -u idrissimart_user -pidrissimart_password
```

## Customization

Edit `.devcontainer/devcontainer.json` to:
- Add more VS Code extensions
- Change settings
- Modify post-create commands
- Add environment variables

## Troubleshooting

### Container Build Fails

```bash
# Rebuild without cache
docker-compose build --no-cache web
```

### Extensions Not Installing

1. Press `Cmd/Ctrl + Shift + P`
2. Type: **"Dev Containers: Rebuild Container"**

### Port Already in Use

Stop any local services using ports 8000, 3306, 6379, etc.

```bash
# Check what's using a port
lsof -i :8000
```

### Can't Connect to Database

Ensure database service is running:
```bash
docker-compose ps db
docker-compose logs db
```

### File Changes Not Reflecting

Volume mounting should be automatic. If issues persist:
```bash
# Restart container
docker-compose restart web
```

## Exiting Dev Container

To return to local VS Code:
1. Press `Cmd/Ctrl + Shift + P`
2. Type: **"Dev Containers: Reopen Folder Locally"**

Or simply close VS Code and reopen normally.

## Benefits

✅ **Consistent Environment** - Everyone uses the same setup  
✅ **No Local Installation** - All dependencies in container  
✅ **IntelliSense** - Full code completion and navigation  
✅ **Debugging** - Built-in Python debugger  
✅ **Extensions** - All tools pre-configured  
✅ **Terminal Access** - Direct access to container  
✅ **Port Forwarding** - Access services on localhost  

## Resources

- [VS Code Dev Containers Docs](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Django Documentation](https://docs.djangoproject.com/)
