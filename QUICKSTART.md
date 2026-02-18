# 🚀 Quick Reference: Poetry + WSL + PyCharm

## Run Configurations (Fixed! ✅)

### Select from dropdown (top-right):
- **Django Runserver** - Port 8000
- **Daphne ASGI Server** - Port 8001  
- **Django Q Cluster** - Background tasks
- **All Services** - Daphne + Django Q
- **Full Dev Stack** - Runserver + Django Q

### Click green ▶️ button to run!

---

## Poetry Commands (WSL Terminal)

```bash
# Navigate to project
cd /opt/WORK/idrissimart

# Install dependencies
poetry install

# Run Django commands
poetry run python manage.py runserver
poetry run python manage.py migrate
poetry run python manage.py createsuperuser

# Add packages
poetry add <package>              # Production
poetry add --group dev <package>  # Development

# Update packages
poetry update

# Show installed
poetry show
```

---

## Your Environment

- 🐧 WSL: Ubuntu-24.04
- 📦 Poetry: 2.3.2
- 🐍 Python: 3.12.3
- 📁 VirtualEnv: `/opt/WORK/idrissimart/.venv/`
- 🔴 Redis: Local server on port 6379

---

## Redis Setup (Required for Django Q & Channels)

```bash
# Install Redis
sudo apt install redis-server -y

# Start Redis
sudo service redis-server start

# Verify
redis-cli ping  # Should return: PONG
```

**See REDIS_LOCAL_SETUP.md for complete setup guide**

---

## Status: ✅ Ready to Go!

**Fixed:** PyCharm run configurations now use WSL Python interpreter  
**Verified:** Poetry virtual environment is working  
**Documented:** See PYCHARM_WSL_FIX.md for details

---

## Need Help?

See full documentation:
- **PYCHARM_POETRY_WSL_SETUP.md** - Complete setup guide
- **PYCHARM_WSL_FIX.md** - What was fixed
- **POETRY_GUIDE.md** - Poetry commands & usage

