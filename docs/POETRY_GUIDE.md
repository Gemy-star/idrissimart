# Poetry Usage Guide for Idrissimart

## 📦 Why Poetry?

Poetry provides:
- ✅ Better dependency resolution
- ✅ Automatic lock file management
- ✅ Virtual environment management
- ✅ Cleaner dependency declarations
- ✅ Built-in packaging and publishing

## 🚀 Quick Start

### Installation

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### Basic Commands

```bash
# Install all dependencies
poetry install

# Install only production dependencies
poetry install --only main

# Add a new dependency
poetry add django

# Add a development dependency
poetry add --group dev pytest

# Update dependencies
poetry update

# Update specific package
poetry update django

# Show installed packages
poetry show

# Show dependency tree
poetry show --tree
```

## 🐳 Docker Integration

### Dockerfile Usage

The Dockerfile now uses Poetry exclusively:

```dockerfile
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root --no-interaction
```

### Building Images

```bash
# Build with Poetry
docker compose build

# Build without cache
docker compose build --no-cache
```

## 📝 Managing Dependencies

### Adding Dependencies

```bash
# Production dependency
poetry add requests
poetry add django>=4.2

# Development dependency
poetry add --group dev pytest black ruff

# Optional dependency
poetry add --optional sphinx

# From specific source
poetry add --source pypi django
```

### Removing Dependencies

```bash
# Remove a package
poetry remove requests

# Remove dev dependency
poetry remove --group dev pytest
```

### Updating pyproject.toml

Edit `pyproject.toml` manually for complex changes:

```toml
[tool.poetry.dependencies]
python = "^3.11"
django = "^5.2.7"
mysqlclient = "^2.2.7"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
black = "^25.0.0"
ruff = "^0.14.0"
```

Then run:
```bash
poetry lock
poetry install
```

## 🔧 Local Development

### Setup Virtual Environment

```bash
# Create virtual environment
poetry install

# Activate virtual environment
poetry shell

# Or run commands directly
poetry run python manage.py runserver
poetry run python manage.py migrate
```

### Using with Docker

```bash
# Build with Poetry dependencies
docker compose build

# Start services
docker compose up -d

# Run migrations (uses Poetry-installed packages)
docker compose exec web python manage.py migrate

# Add new dependency and rebuild
poetry add package-name
poetry lock
docker compose build web
docker compose up -d
```

## 📊 Dependency Groups

### Main Dependencies (Production)
```bash
poetry install --only main
```

### Development Dependencies
```bash
poetry install --with dev
```

### All Dependencies
```bash
poetry install
```

## 🔄 Migration from pip/requirements.txt

If you have `requirements.txt`:

```bash
# Install from requirements.txt
poetry add $(cat requirements.txt)

# Or use Poetry's import
poetry add `cat requirements.txt`

# Generate lock file
poetry lock
```

## ⚡ Performance Tips

### Faster Installation
```bash
# Use parallel installation
poetry config installer.parallel true

# Use system site packages if needed
poetry config virtualenvs.options.system-site-packages true

# Disable virtualenv creation in Docker
poetry config virtualenvs.create false
```

### Caching
```bash
# Clear cache
poetry cache clear pypi --all

# List cache
poetry cache list
```

## 🐛 Troubleshooting

### Lock File Issues
```bash
# Regenerate lock file
poetry lock --no-update

# Force update
poetry lock
```

### Dependency Conflicts
```bash
# Show why package is installed
poetry show --why package-name

# Verbose dependency resolution
poetry install -vvv
```

### Virtual Environment Issues
```bash
# Remove and recreate venv
poetry env remove python
poetry install

# List virtual environments
poetry env list

# Use specific Python version
poetry env use python3.11
```

## 📚 Common Workflows

### Adding a Feature with New Dependencies

```bash
# 1. Add dependency
poetry add new-package

# 2. Test locally
poetry run python manage.py test

# 3. Commit changes
git add pyproject.toml poetry.lock
git commit -m "Add new-package dependency"

# 4. Rebuild Docker
docker compose build
docker compose up -d
```

### Updating All Dependencies

```bash
# 1. Update dependencies
poetry update

# 2. Test
poetry run python manage.py test

# 3. Rebuild Docker
docker compose build --no-cache
docker compose up -d
```

## 🔐 Production Deployment

### Export Requirements (if needed)

```bash
# Export to requirements.txt format
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Export only production
poetry export -f requirements.txt --output requirements.txt --only main --without-hashes
```

### Docker Production Build

```bash
# Build production image
docker compose -f docker-compose.prod.yml build

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

## 📖 Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry CLI Reference](https://python-poetry.org/docs/cli/)
- [Dependency Management](https://python-poetry.org/docs/dependency-specification/)
- [Configuration](https://python-poetry.org/docs/configuration/)

## ✅ Best Practices

1. **Always commit both `pyproject.toml` and `poetry.lock`**
2. **Use `poetry lock --no-update` to update lock file without changing versions**
3. **Use `poetry show --outdated` to check for updates**
4. **Pin critical dependencies with exact versions**
5. **Use dependency groups for organization**
6. **Test after updating dependencies**
7. **Keep Poetry version consistent across team**

## 🎯 Quick Reference

```bash
# Installation
poetry install                 # Install all deps
poetry install --only main     # Production only

# Adding packages
poetry add <package>           # Add to main
poetry add --group dev <pkg>   # Add to dev

# Updates
poetry update                  # Update all
poetry update <package>        # Update specific

# Information
poetry show                    # List packages
poetry show <package>          # Package details
poetry check                   # Validate config

# Environment
poetry shell                   # Activate venv
poetry env info                # Show venv info
poetry run <command>           # Run in venv

# Lock file
poetry lock                    # Update lock file
poetry lock --no-update        # Lock without updating
```

## 🔧 IDE Integration

### PyCharm + WSL + Poetry

**Important:** When using PyCharm with WSL and Poetry, make sure your run configurations use the project interpreter.

See **PYCHARM_WSL_FIX.md** for details on configuring PyCharm to work with Poetry's in-project virtual environment in WSL.

**Quick Check:**
- Python Interpreter: `3.12 WSL (Ubuntu-24.04): (/opt/WORK/idrissimart/.venv/bin/python)`
- Run configurations should have `IS_MODULE_SDK="true"`
- Virtual environment created by Poetry at: `/opt/WORK/idrissimart/.venv/`

### VS Code + Poetry

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

