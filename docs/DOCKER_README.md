# 🐳 Docker Setup for Idrissimart

Complete Docker containerization for the Idrissimart Django application with production-ready configuration.

## 📦 What's Included

### Services
- **MariaDB** - Database server
- **Redis** - Cache and message broker
- **Gunicorn** - WSGI HTTP server for Django
- **Daphne** - ASGI WebSocket server for Django Channels
- **Django-Q** - Asynchronous task queue
- **Nginx** - Reverse proxy and static file server

### Configuration Files

```
.
├── Dockerfile                       # Multi-stage production image
├── docker compose.yml              # Development/testing setup
├── docker compose.prod.yml         # Production setup with resource limits
├── .dockerignore                   # Files excluded from build
├── .env.example                    # Environment variables template
├── docker-start.sh                 # Quick start script
├── docker-deploy-prod.sh           # Production deployment script
├── Makefile.docker                 # Shortcut commands
├── DOCKER_GUIDE.md                 # Detailed documentation
└── docker/
    ├── nginx/
    │   ├── nginx.conf              # Main Nginx configuration
    │   └── conf.d/
    │       └── idrissimart.conf    # Site-specific configuration
    └── mariadb/
        └── conf.d/
            └── custom.cnf          # MariaDB optimization
```

## 🚀 Quick Start

### Development Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your settings
nano .env

# 3. Start all services
./docker-start.sh

# Or manually:
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
```

Access your application:
- **Main site**: http://localhost
- **Admin**: http://localhost/admin/
- **WebSocket**: ws://localhost/ws/

### Production Deployment

```bash
# 1. Configure .env with production values
cp .env.example .env
nano .env

# 2. Deploy
sudo ./docker-deploy-prod.sh

# Or use docker compose directly:
docker compose -f docker compose.prod.yml up -d
```

## 🛠️ Using Makefile Commands

```bash
# View all available commands
make -f Makefile.docker help

# Quick setup
make -f Makefile.docker init

# Build and start
make -f Makefile.docker build
make -f Makefile.docker up

# View logs
make -f Makefile.docker logs
make -f Makefile.docker logs-web

# Django commands
make -f Makefile.docker migrate
make -f Makefile.docker collectstatic
make -f Makefile.docker createsuperuser
make -f Makefile.docker shell

# Restart services
make -f Makefile.docker restart
make -f Makefile.docker restart-web

# Backup database
make -f Makefile.docker backup

# Stop services
make -f Makefile.docker down
```

## 📋 Common Commands

### Service Management

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View status
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f web
docker compose logs -f daphne
docker compose logs -f qcluster

# Restart service
docker compose restart web
```

### Django Management

```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic

# Django shell
docker compose exec web python manage.py shell

# Create migrations
docker compose exec web python manage.py makemigrations

# Run tests
docker compose exec web python manage.py test
```

### Database Management

```bash
# Access MariaDB shell
docker compose exec db mysql -u root -p

# Backup database
docker compose exec db mysqldump -u root -p idrissimart > backup.sql

# Restore database
docker compose exec -T db mysql -u root -p idrissimart < backup.sql

# View database logs
docker compose logs -f db
```

### Redis Management

```bash
# Access Redis CLI
docker compose exec redis redis-cli -a your_redis_password

# Clear cache
docker compose exec redis redis-cli -a your_redis_password FLUSHALL

# Monitor Redis
docker compose exec redis redis-cli -a your_redis_password MONITOR
```

## 🔧 Configuration

### Environment Variables (.env)

Required variables:
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,your-domain.com

# Database
DB_NAME=idrissimart
DB_USER=idrissimart_user
DB_PASSWORD=strong_password
DB_ROOT_PASSWORD=strong_root_password

# Redis
REDIS_PASSWORD=redis_password

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Payment
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-secret
```

See [.env.example](.env.example) for complete list.

### SSL/HTTPS Setup

1. Place SSL certificates in `docker/nginx/ssl/`:
   ```bash
   cp certificate.crt docker/nginx/ssl/
   cp private.key docker/nginx/ssl/
   chmod 644 docker/nginx/ssl/certificate.crt
   chmod 600 docker/nginx/ssl/private.key
   ```

2. Uncomment SSL configuration in [docker/nginx/conf.d/idrissimart.conf](docker/nginx/conf.d/idrissimart.conf)

3. Update .env:
   ```bash
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

4. Restart Nginx:
   ```bash
   docker compose restart nginx
   ```

## 📊 Monitoring

### Service Health

```bash
# Check all services
docker compose ps

# Check resource usage
docker stats

# Health check
curl http://localhost/health/
```

### Logs

```bash
# All services
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100

# Specific service
docker compose logs -f web
docker compose logs -f daphne
docker compose logs -f qcluster
docker compose logs -f nginx

# Save logs to file
docker compose logs > logs_$(date +%Y%m%d).txt
```

## 🔄 Updates and Maintenance

### Update Application

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

# Or use the shortcut:
make -f Makefile.docker update
```

### Backup Strategy

```bash
# Automated backup script (add to crontab)
# Run daily at 2 AM
0 2 * * * cd /path/to/idrissimart && make -f Makefile.docker backup

# Manual backup
make -f Makefile.docker backup

# Or:
docker compose exec -T db mysqldump -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} > backups/backup_$(date +%Y%m%d).sql
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs service_name

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Port already in use
```bash
# Find process using port
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# Kill process or change port in docker compose.yml
```

### Static files not loading
```bash
# Recollect static files
docker compose exec web python manage.py collectstatic --noinput --clear

# Restart nginx
docker compose restart nginx
```

### Database connection issues
```bash
# Check database health
docker compose exec db mysqladmin -u root -p ping

# Check migrations
docker compose exec web python manage.py showmigrations

# Restart database
docker compose restart db
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

```bash
# Stop and remove containers
docker compose down

# Remove volumes (⚠️  deletes data!)
docker compose down -v

# Remove all Docker resources
docker system prune -af --volumes

# Or use Makefile:
make -f Makefile.docker clean
make -f Makefile.docker clean-all  # ⚠️  removes everything
```

## 📚 Additional Resources

- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Detailed documentation
- [docker compose.yml](docker compose.yml) - Development configuration
- [docker compose.prod.yml](docker compose.prod.yml) - Production configuration
- [Dockerfile](Dockerfile) - Image definition

## 🔐 Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Use strong `SECRET_KEY`
- [ ] Set `DEBUG=False` in production
- [ ] Configure SSL certificates
- [ ] Enable `SECURE_SSL_REDIRECT` with HTTPS
- [ ] Restrict `ALLOWED_HOSTS`
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Enable log monitoring
- [ ] Configure proper file permissions
- [ ] Use Docker secrets for sensitive data (optional)

## 📞 Support

For detailed documentation, see [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

For issues:
1. Check logs: `docker compose logs -f`
2. Verify configuration in `.env`
3. Check service health: `docker compose ps`
4. Review [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

## 📝 License

Same as main project.
