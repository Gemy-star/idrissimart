# =============================================================================
# Docker Deployment and Management Guide for Idrissimart
# =============================================================================

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- 10GB disk space

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Make start script executable
chmod +x docker-start.sh

# Run the setup
./docker-start.sh
```

### 2. Manual Setup (Alternative)

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Create superuser
docker compose exec web python manage.py createsuperuser
```

## 🔧 Common Commands

### Service Management

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart web
docker compose restart daphne
docker compose restart qcluster

# View logs
docker compose logs -f
docker compose logs -f web
docker compose logs -f daphne
docker compose logs -f qcluster

# View service status
docker compose ps
```

### Django Commands

```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Django shell
docker compose exec web python manage.py shell

# Run custom management command
docker compose exec web python manage.py your_command

# Django Q cluster monitor
docker compose exec qcluster python manage.py qmonitor
```

### Database Management

```bash
# Access MariaDB CLI
docker compose exec db mysql -u root -p

# Backup database
docker compose exec db mysqldump -u root -p idrissimart > backup.sql

# Restore database
docker compose exec -T db mysql -u root -p idrissimart < backup.sql

# Import SQL file
docker compose exec -T db mysql -u root -p idrissimart < /path/to/file.sql
```

### Redis Management

```bash
# Access Redis CLI
docker compose exec redis redis-cli -a your_redis_password

# Clear Redis cache
docker compose exec redis redis-cli -a your_redis_password FLUSHALL
```

### Email Testing (smtp4dev)

```bash
# Start smtp4dev service
docker compose up -d smtp4dev

# View Web UI (see all emails sent by the application)
# Open browser: http://localhost:3100

# Test email functionality (from host)
python test_email.py

# Test email from Django shell (inside container)
docker compose exec web python manage.py shell
# Then run:
# from django.core.mail import send_mail
# send_mail('Test', 'Message', 'from@test.com', ['to@test.com'])

# Stop smtp4dev
docker compose stop smtp4dev

# View logs
docker compose logs -f smtp4dev
```

**Features:**
- All emails sent by Django appear in the web interface
- No real emails are sent (safe for testing)
- View HTML/text content, attachments, headers
- No authentication required for local development
- Configured in `idrissimart/settings/local.py`

## 📁 File Structure

```
idrissimart/
├── Dockerfile                          # Main application Dockerfile
├── docker compose.yml                  # Docker Compose configuration
├── .dockerignore                       # Files to exclude from build
├── .env                               # Environment variables (create from .env.example)
├── .env.example                       # Example environment file
├── pyproject.toml                     # Poetry dependencies
├── poetry.lock                        # Poetry lock file
├── docker-start.sh                    # Quick start script
├── docker/
│   ├── nginx/
│   │   ├── nginx.conf                # Main Nginx config
│   │   ├── conf.d/
│   │   │   └── idrissimart.conf     # Site-specific config
│   │   └── ssl/                      # SSL certificates
│   │       ├── certificate.crt
│   │       └── private.key
│   └── mariadb/
│       └── conf.d/
│           └── custom.cnf            # MariaDB custom config
```

## 🔒 SSL/HTTPS Setup

### 1. Add SSL Certificates

```bash
# Copy your certificates
cp your_certificate.crt docker/nginx/ssl/certificate.crt
cp your_private.key docker/nginx/ssl/private.key

# Set proper permissions
chmod 644 docker/nginx/ssl/certificate.crt
chmod 600 docker/nginx/ssl/private.key
```

### 2. Update Nginx Configuration

Uncomment SSL-related lines in `docker/nginx/conf.d/idrissimart.conf`:
- SSL listen directives
- SSL certificate paths
- SSL parameters
- HTTPS redirect server block

### 3. Update Environment Variables

```bash
# In .env file
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### 4. Restart Nginx

```bash
docker compose restart nginx
```

## 📊 Monitoring and Logs

### View Logs

```bash
# All services
docker compose logs -f

# Specific service with tail
docker compose logs -f --tail=100 web

# Save logs to file
docker compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
```

### Monitor Resources

```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Service health
docker compose ps
```

## 🔄 Updates and Maintenance

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose build
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate

# Collect static files
docker compose exec web python manage.py collectstatic --noinput
```

### Update Dependencies

```bash
# Update dependencies in pyproject.toml
# Edit pyproject.toml file

# Rebuild images
docker compose build --no-cache

# Restart services
docker compose up -d
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs service_name

# Check if ports are in use
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# Remove and recreate
docker compose down
docker compose up -d
```

### Database connection issues

```bash
# Check database status
docker compose exec db mysqladmin -u root -p ping

# Check if migrations ran
docker compose exec web python manage.py showmigrations

# Reset and migrate
docker compose exec web python manage.py migrate
```

### Static files not loading

```bash
# Collect static files again
docker compose exec web python manage.py collectstatic --noinput --clear

# Check volume permissions
docker compose exec web ls -la /app/staticfiles/

# Restart nginx
docker compose restart nginx
```

### WebSocket not working

```bash
# Check Daphne logs
docker compose logs -f daphne

# Check Redis connection
docker compose exec web python -c "import redis; r=redis.Redis(host='redis', port=6379); print(r.ping())"

# Restart Daphne
docker compose restart daphne
```

## 🗑️ Cleanup

### Remove Everything

```bash
# Stop and remove containers, networks
docker compose down

# Remove volumes (⚠️ This deletes data!)
docker compose down -v

# Remove images
docker compose down --rmi all
```

### Clean Docker System

```bash
# Remove unused containers, networks, images
docker system prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

## 🔐 Production Considerations

1. **Environment Variables**: Never commit `.env` file
2. **Secret Keys**: Use strong, random secret keys
3. **Database Passwords**: Use complex passwords
4. **SSL Certificates**: Use valid SSL certificates
5. **Backup Strategy**: Regular database and media backups
6. **Monitoring**: Set up monitoring and alerting
7. **Resource Limits**: Configure container resource limits
8. **Logging**: Configure log rotation
9. **Updates**: Keep Docker images updated
10. **Security**: Regular security audits

## 📞 Support

For issues and questions:
- Check logs: `docker compose logs -f`
- Review configuration files
- Check environment variables in `.env`
- Verify service health: `docker compose ps`
