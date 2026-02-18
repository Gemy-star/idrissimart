# ✅ Local Settings Updated for Redis

## What Was Changed

**File:** `idrissimart/settings/local.py`

### Added Redis Configuration:

#### 1. Django-Q2 (Background Tasks)
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

#### 2. Django Channels (WebSockets/Real-time)
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

## Quick Setup Guide

### 1. Install Redis
```bash
sudo apt install redis-server -y
```

### 2. Start Redis
```bash
sudo service redis-server start
```

### 3. Verify Redis
```bash
redis-cli ping
# Should output: PONG
```

### 4. Test Configuration
```bash
cd /opt/WORK/idrissimart
poetry run python test_redis.py
```

---

## What Uses Redis?

### Django-Q2 (Background Tasks)
- ✅ Scheduled periodic tasks
- ✅ Async task execution
- ✅ Email queue processing
- ✅ Ad expiration checks
- ✅ Any background job

**Run with:**
```bash
poetry run python manage.py qcluster
```
**Or PyCharm:** Select "Django Q Cluster" configuration

### Django Channels (Real-time)
- ✅ WebSocket connections
- ✅ Real-time notifications
- ✅ Live updates
- ✅ Chat features

**Run with:**
```bash
poetry run daphne idrissimart.asgi:application
```
**Or PyCharm:** Select "Daphne ASGI Server" configuration

---

## PyCharm Run Configurations

All configurations now work with local Redis:

1. **Django Runserver** - Port 8000 (doesn't need Redis)
2. **Django Q Cluster** - Background tasks (needs Redis ✅)
3. **Daphne ASGI Server** - Port 8001 (needs Redis ✅)
4. **All Services (Compound)** - Daphne + Django Q (needs Redis ✅)
5. **Full Dev Stack** - Runserver + Django Q (needs Redis ✅)

---

## Testing

### Quick Test:
```bash
# 1. Make sure Redis is running
redis-cli ping

# 2. Test Redis integration
poetry run python test_redis.py

# 3. Start Django Q
poetry run python manage.py qcluster
```

### Full Test (All Services):
```bash
# Terminal 1: Start Redis
sudo service redis-server start

# Terminal 2: Start Django Runserver
poetry run python manage.py runserver

# Terminal 3: Start Django Q
poetry run python manage.py qcluster

# Terminal 4: Start Daphne
poetry run daphne idrissimart.asgi:application
```

**Or use PyCharm:** Select "All Services (Compound)" and click Run ▶️

---

## Documentation Created

1. ✅ **REDIS_LOCAL_SETUP.md** - Complete Redis setup guide
2. ✅ **test_redis.py** - Redis connectivity test script
3. ✅ **QUICKSTART.md** - Updated with Redis info
4. ✅ **PYCHARM_POETRY_WSL_SETUP.md** - Updated with Redis requirements
5. ✅ **LOCAL_REDIS_SETUP_SUMMARY.md** - This file

---

## Configuration Summary

### Before (No Redis):
- ❌ Django-Q not configured for local
- ❌ Channels using in-memory backend (not persistent)
- ❌ Background tasks wouldn't work locally

### After (With Redis):
- ✅ Django-Q configured with local Redis
- ✅ Channels using Redis backend (persistent)
- ✅ Background tasks work in local development
- ✅ Same configuration as production (but using localhost)

---

## Environment Variables (Optional)

If you want to customize Redis settings, you can use environment variables:

```bash
# .env file (optional)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

Current settings use defaults (no .env needed for local development).

---

## Troubleshooting

### Redis Not Installed?
```bash
sudo apt install redis-server -y
```

### Redis Not Running?
```bash
sudo service redis-server start
sudo service redis-server status
```

### Connection Refused?
```bash
# Check if Redis is listening
sudo netstat -tlnp | grep 6379

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Django-Q Errors?
```bash
# Test Redis connection
poetry run python test_redis.py

# Run Django Q in verbose mode
poetry run python manage.py qcluster --verbosity=3
```

---

## Daily Usage

### Start Your Day:
```bash
# 1. Start Redis (if not running)
sudo service redis-server start

# 2. Use PyCharm run configurations
# Select configuration → Click Run ▶️
```

### Stop Your Day:
```bash
# Optional: Stop Redis to free memory
sudo service redis-server stop
```

---

## Next Steps

1. ✅ Redis installed and configured
2. ✅ Local settings updated
3. ✅ Test scripts created
4. ✅ Documentation updated

**You're ready to use Redis with local development! 🚀**

### Try It:
```bash
# Start Redis
sudo service redis-server start

# Test it
poetry run python test_redis.py

# Run Django Q
poetry run python manage.py qcluster
```

---

## Related Files

- `idrissimart/settings/local.py` - Local settings (updated)
- `idrissimart/settings/docker.py` - Production settings (reference)
- `idrissimart/settings/common.py` - Base settings
- `test_redis.py` - Test script
- `REDIS_LOCAL_SETUP.md` - Complete guide

---

## Date: February 16, 2026

