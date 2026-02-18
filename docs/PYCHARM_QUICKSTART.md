# Quick Start Guide - PyCharm Run Configurations

## 🚀 Getting Started in 3 Steps

### Step 1: Restart PyCharm
After adding the configuration files, restart PyCharm to load them.

### Step 2: Select a Configuration
Look at the top-right corner of PyCharm. You should see a dropdown menu with these options:

1. **Django Runserver** - Standard Django development (port 8000)
2. **Daphne ASGI Server** - WebSocket support (port 8001)
3. **Django Q Cluster** - Background tasks worker
4. **All Services (Compound)** - Daphne + Django Q together
5. **Full Dev Stack (Runserver + Q)** - Django Runserver + Django Q

### Step 3: Run!
Click the green ▶️ play button (or press Shift+F10)

---

## 📋 Which Configuration Should I Use?

### For Most Development Work:
**→ Use "Django Runserver"**
- Simple HTTP development
- Quick testing
- No WebSocket features needed

### For WebSocket/Real-time Features:
**→ Use "All Services (Compound)"**
- Includes Daphne (WebSockets) on port 8001
- Includes Django Q (background tasks)
- Full production-like environment

### For Background Task Development:
**→ Use "Full Dev Stack (Runserver + Q)"**
- Django on port 8000
- Django Q for async tasks
- No WebSocket overhead

### Individual Services:
- **Daphne ASGI Server** - Only WebSocket server
- **Django Q Cluster** - Only background tasks

---

## ⚙️ Prerequisites

### 1. Verify Python Interpreter
**File → Settings → Project: idrissimart → Python Interpreter**
- Should point to: `.venv/bin/python`
- If not, click gear icon → Add → Existing Environment → Select `.venv/bin/python`

### 2. Install Dependencies
```bash
# Activate virtual environment
source .venv/bin/activate  # On Linux/WSL
# or
.venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt
```

### 3. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional
```

### 4. For Django Q (Optional)
Django Q in your project uses Django ORM as the broker, so no Redis needed for basic functionality. However, for Channels (WebSockets), you'll need Redis:

```bash
# Using Docker (recommended)
docker-compose up redis -d

# Or install Redis locally
sudo apt install redis-server
sudo service redis-server start
```

---

## 🐛 Debugging

### To Debug Any Configuration:
1. Set breakpoints (click left margin next to line numbers)
2. Click the debug icon 🐞 instead of play button
3. Or press Shift+F9

### Debug Multiple Services:
When using compound configurations (All Services, Full Dev Stack):
- Each service runs in a separate tab
- You can debug each service independently
- Set breakpoints in any service

---

## 🔥 Hot Tips

### 1. Quick Switch Between Configurations
**Ctrl+Shift+A** → Type "Run" → Select configuration

### 2. Stop All Services
**Ctrl+F2** - Stops all running processes

### 3. View Logs
The Run tool window (bottom) shows logs for each service in tabs

### 4. Edit Configurations
**Run → Edit Configurations** to customize:
- Port numbers
- Environment variables
- Command-line arguments

### 5. Default Browser
Configurations will open your browser automatically
- Django Runserver: http://127.0.0.1:8000
- Daphne: http://127.0.0.1:8001

---

## 🆘 Troubleshooting

### "No module named 'django'"
→ Wrong Python interpreter selected. Check Settings → Project → Python Interpreter

### "Port already in use"
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Configurations Don't Appear
1. Restart PyCharm
2. Check `.idea/runConfigurations/` folder exists
3. File → Invalidate Caches → Invalidate and Restart

### Django Q Won't Start
Check if migrations are applied:
```bash
python manage.py migrate
```

---

## 📚 More Information

See **PYCHARM_RUN_CONFIGURATIONS.md** for detailed documentation.

---

## 🎯 Summary

| Configuration | Ports | Best For |
|--------------|-------|----------|
| Django Runserver | 8000 | General development |
| Daphne ASGI Server | 8001 | WebSocket testing |
| Django Q Cluster | - | Task development |
| **All Services** | 8001 | **Full stack (recommended)** |
| **Full Dev Stack** | 8000 | **Standard + tasks** |

**Recommendation**: Start with **"Django Runserver"** for basic work, switch to **"All Services (Compound)"** when you need WebSockets or background tasks.

