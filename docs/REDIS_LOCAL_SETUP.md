# Redis Setup for Local Development (WSL)

## 📦 Installing Redis on WSL Ubuntu

### Step 1: Install Redis Server

```bash
# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server -y

# Verify installation
redis-server --version
```

### Step 2: Configure Redis

Edit the Redis configuration file:
```bash
sudo nano /etc/redis/redis.conf
```

**Optional Configuration Changes:**
- Set `supervised systemd` for better systemd integration
- Keep `bind 127.0.0.1` for local-only access (secure)
- Keep `port 6379` (default)
- No password needed for local development

### Step 3: Start Redis

```bash
# Start Redis service
sudo service redis-server start

# Enable Redis to start on boot (optional)
sudo systemctl enable redis-server

# Check status
sudo service redis-server status

# Test connection
redis-cli ping
# Should output: PONG
```

---

## ✅ Verification

### Test Redis Connection:
```bash
# Connect to Redis CLI
redis-cli

# Inside Redis CLI:
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> set test "Hello Redis"
OK
127.0.0.1:6379> get test
"Hello Redis"
127.0.0.1:6379> exit
```

### Check Redis from Python:
```bash
cd /opt/WORK/idrissimart

# Test Redis connection with Python
poetry run python -c "import redis; r = redis.Redis(host='127.0.0.1', port=6379, db=0); print('Redis version:', r.info()['redis_version']); print('Connection:', r.ping())"
```

---

## 🔧 Configuration in Django

### Settings Updated: ✅

**File:** `idrissimart/settings/local.py`

**Django-Q2 Configuration:**
```python
Q_CLUSTER = {
    "name": "idrissimart_local",
    "workers": 2,
    "redis": {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 0,
        "password": None,
    },
    # ... other settings
}
```

**Channels Configuration:**
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

---

## 🚀 Usage with PyCharm

### Running Services with Redis:

1. **Start Redis First:**
   ```bash
   sudo service redis-server start
   ```

2. **Run Django Services:**
   - **Django Runserver** - Main web server
   - **Django Q Cluster** - Background tasks (needs Redis)
   - **Daphne ASGI Server** - WebSocket/Channels (needs Redis)

3. **Or use Compound Configurations:**
   - **Full Dev Stack** - Runserver + Django Q
   - **All Services** - Daphne + Django Q

---

## 🛠️ Common Redis Commands

### Service Management:
```bash
# Start Redis
sudo service redis-server start

# Stop Redis
sudo service redis-server stop

# Restart Redis
sudo service redis-server restart

# Check status
sudo service redis-server status

# View Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Redis CLI Commands:
```bash
# Connect to Redis
redis-cli

# Get all keys
KEYS *

# Clear all data
FLUSHALL

# Monitor Redis commands in real-time
MONITOR

# Get Redis info
INFO

# Check memory usage
INFO memory

# Exit
exit
```

---

## 📊 Monitoring Redis

### Check Redis Memory Usage:
```bash
redis-cli INFO memory | grep used_memory_human
```

### Monitor Redis Activity:
```bash
# Terminal 1: Monitor commands
redis-cli MONITOR

# Terminal 2: Run Django Q or Daphne
poetry run python manage.py qcluster
```

### View Django Q Tasks:
```bash
# In Django shell
poetry run python manage.py shell

>>> from django_q.models import Task, Schedule
>>> Task.objects.all().count()  # View tasks
>>> Schedule.objects.all()      # View scheduled tasks
```

---

## 🔍 Troubleshooting

### Redis Not Starting:
```bash
# Check if port 6379 is already in use
sudo netstat -tlnp | grep 6379

# Check Redis logs
sudo tail -50 /var/log/redis/redis-server.log

# Try starting manually
redis-server
```

### Connection Refused:
```bash
# Make sure Redis is running
sudo service redis-server status

# Test connection
redis-cli ping

# Check firewall (usually not needed for localhost)
sudo ufw status
```

### Django-Q Not Working:
```bash
# Check Redis connection from Django
poetry run python manage.py shell
>>> import redis
>>> r = redis.Redis(host='127.0.0.1', port=6379)
>>> r.ping()
True

# Run Django Q in verbose mode
poetry run python manage.py qcluster --pythonpath=. --verbosity=3
```

### Channels/Daphne Not Working:
```bash
# Test channels connection
poetry run python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> import asyncio
>>> asyncio.run(channel_layer.send('test', {'type': 'test.message'}))

# Run Daphne in verbose mode
poetry run daphne -v 2 idrissimart.asgi:application
```

---

## 🧹 Maintenance

### Clear Redis Data:
```bash
# Connect to Redis
redis-cli

# Clear all data
FLUSHALL

# Or clear specific database
SELECT 0
FLUSHDB
```

### Backup Redis Data:
```bash
# Redis saves data to dump.rdb by default
# Location: /var/lib/redis/dump.rdb

# Manual backup
sudo cp /var/lib/redis/dump.rdb /var/lib/redis/dump.rdb.backup

# Trigger save
redis-cli SAVE
```

---

## 📝 Quick Reference

### Installation:
```bash
sudo apt install redis-server -y
sudo service redis-server start
redis-cli ping  # Should return PONG
```

### Start Services (in order):
```bash
# 1. Start Redis
sudo service redis-server start

# 2. Run Django (choose one)
poetry run python manage.py runserver           # Web server
poetry run python manage.py qcluster            # Background tasks
poetry run daphne idrissimart.asgi:application  # WebSockets/Channels
```

### Or Use PyCharm Run Configurations:
- Select configuration from dropdown
- Click green ▶️ button
- All services automatically connect to local Redis

---

## 🎯 What Uses Redis?

1. **Django-Q2** - Background task queue
   - Scheduled tasks (periodic jobs)
   - Async task execution
   - Email sending
   - Ad expiration checks
   
2. **Django Channels** - WebSocket/Real-time
   - WebSocket connections
   - Real-time notifications
   - Chat features (if implemented)
   - Live updates

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Redis installed: `redis-server --version`
- [ ] Redis running: `sudo service redis-server status`
- [ ] Redis responding: `redis-cli ping` returns `PONG`
- [ ] Python can connect: `poetry run python -c "import redis; redis.Redis().ping()"`
- [ ] Django can connect: Run `manage.py qcluster` without errors
- [ ] Channels work: Run Daphne without errors

---

## 📚 Related Documentation

- **QUICKSTART.md** - Quick reference for Poetry + WSL + PyCharm
- **PYCHARM_WSL_FIX.md** - PyCharm configuration details
- **POETRY_GUIDE.md** - Poetry commands and usage

---

## Date: February 16, 2026

