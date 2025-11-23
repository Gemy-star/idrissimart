# Django Channels Chat Implementation - Production Deployment Guide

## Overview
This implementation adds real-time WebSocket chat functionality between:
- **Publisher ↔ Client**: Chat about specific ads
- **Publisher ↔ Admin**: Support/help chat

## Architecture

```
Client Browser
    ↓ (WebSocket)
Nginx (Port 443/80)
    ├── /ws/* → Daphne (Port 8001) - WebSocket/ASGI
    └── /* → Gunicorn (Port 8000) - HTTP/WSGI

Both connect to:
    - PostgreSQL/MySQL (Database)
    - Redis (Channel Layer)
```

## Installation Steps

### 1. Install Dependencies

```bash
cd /path/to/idrissimart
source venv/bin/activate

# Install Channels and Redis
pip install -r requirements_channels.txt

# Or install individually
pip install channels==4.0.0 channels-redis==4.2.0 daphne==4.1.0 redis==5.0.1 hiredis==2.3.2
```

### 2. Install and Configure Redis

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Test Redis
redis-cli ping
# Should return: PONG
```

### 3. Update Production Settings

Edit `idrissimart/settings/settings_production.py`:

```python
# Add Channels configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            # For production with password:
            # "hosts": [f"redis://:{REDIS_PASSWORD}@127.0.0.1:6379/0"],
        },
    },
}
```

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx_channels.conf /etc/nginx/sites-available/idrissimart

# Update paths in the file
sudo nano /etc/nginx/sites-available/idrissimart

# Enable site
sudo ln -s /etc/nginx/sites-available/idrissimart /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 6. Setup Systemd Services

```bash
# Copy service files
sudo cp daphne.service /etc/systemd/system/
sudo cp gunicorn.service /etc/systemd/system/

# Update paths in both files
sudo nano /etc/systemd/system/daphne.service
sudo nano /etc/systemd/system/gunicorn.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable daphne gunicorn
sudo systemctl start daphne gunicorn

# Check status
sudo systemctl status daphne
sudo systemctl status gunicorn
```

## Usage

### Publisher-Client Chat

**URL Pattern**: `/ws/chat/ad/<ad_id>/`

**JavaScript Client Example**:
```javascript
const adId = 123;
const chatSocket = new WebSocket(
    `wss://${window.location.host}/ws/chat/ad/${adId}/`
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === 'history') {
        // Display chat history
        console.log('Chat history:', data.messages);
    } else if (data.type === 'message') {
        // New message received
        console.log('New message from:', data.sender_name);
        console.log('Message:', data.message);
    } else if (data.type === 'typing') {
        // User is typing
        console.log(data.user_name + ' is typing...');
    }
};

// Send message
function sendMessage(message) {
    chatSocket.send(JSON.stringify({
        'type': 'message',
        'message': message
    }));
}

// Send typing indicator
function sendTyping() {
    chatSocket.send(JSON.stringify({
        'type': 'typing'
    }));
}
```

### Publisher-Admin Chat

**URL Pattern**: `/ws/chat/support/<room_name>/`

Room name format: `publisher_<publisher_id>`

**JavaScript Client Example**:
```javascript
const publisherId = 456;
const supportSocket = new WebSocket(
    `wss://${window.location.host}/ws/chat/support/publisher_${publisherId}/`
);

supportSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === 'message') {
        console.log(`${data.sender_role}: ${data.message}`);
    }
};

// Send support message
function sendSupportMessage(message) {
    supportSocket.send(JSON.stringify({
        'type': 'message',
        'message': message
    }));
}
```

## Testing

### 1. Test WebSocket Connection

```bash
# Install wscat for testing
npm install -g wscat

# Test publisher-client chat
wscat -c "ws://localhost:8001/ws/chat/ad/1/"

# Test publisher-admin chat
wscat -c "ws://localhost:8001/ws/chat/support/publisher_1/"
```

### 2. Monitor Logs

```bash
# Daphne logs
sudo journalctl -u daphne -f

# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx logs
sudo tail -f /var/log/nginx/idrissimart_error.log
sudo tail -f /var/log/nginx/idrissimart_access.log
```

### 3. Check Redis

```bash
# Monitor Redis
redis-cli monitor

# Check connected clients
redis-cli CLIENT LIST

# Check channel subscriptions
redis-cli PUBSUB CHANNELS
```

## Troubleshooting

### WebSocket Connection Failed

1. **Check Daphne is running**:
```bash
sudo systemctl status daphne
```

2. **Check Nginx WebSocket config**:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

3. **Check firewall**:
```bash
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
```

### Messages Not Being Received

1. **Check Redis is running**:
```bash
sudo systemctl status redis
```

2. **Test Redis connection**:
```python
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> await channel_layer.send("test", {"type": "test.message"})
```

### High Memory Usage

1. **Adjust Daphne workers** in `daphne.service`:
```ini
ExecStart=/path/to/venv/bin/daphne ... --workers 2
```

2. **Configure Redis maxmemory**:
```bash
sudo nano /etc/redis/redis.conf
# Add: maxmemory 256mb
# Add: maxmemory-policy allkeys-lru
sudo systemctl restart redis
```

## Security Considerations

1. **Use SSL/TLS**: Always use `wss://` in production
2. **Authentication**: WebSocket connections are authenticated via Django sessions
3. **Rate Limiting**: Consider implementing rate limiting for messages
4. **Input Validation**: All messages are validated before processing
5. **CORS**: Configured via `AllowedHostsOriginValidator`

## Performance Optimization

1. **Redis Configuration**:
```conf
# /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
tcp-backlog 511
timeout 300
```

2. **Nginx Tuning**:
```nginx
worker_processes auto;
worker_connections 1024;
```

3. **Monitor with**:
- `htop` - CPU/Memory usage
- `redis-cli --stat` - Redis stats
- `nginx -V` - Nginx version and modules

## Maintenance

### Restart Services After Code Updates

```bash
# Restart Daphne
sudo systemctl restart daphne

# Restart Gunicorn
sudo systemctl restart gunicorn

# Reload Nginx (zero downtime)
sudo systemctl reload nginx
```

### Clear Redis Cache

```bash
redis-cli FLUSHALL
```

### Backup Chat Messages

```bash
python manage.py dumpdata main.ChatRoom main.ChatMessage > chat_backup.json
```

## Next Steps

1. Create frontend chat UI components
2. Add typing indicators
3. Implement read receipts
4. Add file sharing in chat
5. Implement chat notifications
6. Add chat search functionality
