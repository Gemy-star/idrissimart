# API Setup Checklist ✅

Use this checklist to ensure everything is properly configured.

## Installation Steps

- [ ] **Install Dependencies**
  ```bash
  pip install -r requirements_api.txt
  # OR
  poetry install
  ```

- [ ] **Verify Installations**
  ```bash
  python -c "import rest_framework; print('DRF OK')"
  python -c "import drf_yasg; print('Swagger OK')"
  python -c "import corsheaders; print('CORS OK')"
  ```

- [ ] **Run Migrations**
  ```bash
  python manage.py migrate
  ```

- [ ] **Create Superuser** (if needed)
  ```bash
  python manage.py createsuperuser
  ```

## Configuration Verification

- [ ] **Check INSTALLED_APPS** in `settings/common.py`:
  - `rest_framework` ✅
  - `rest_framework_simplejwt` ✅
  - `corsheaders` ✅
  - `drf_yasg` ✅
  - `api.apps.ApiConfig` ✅

- [ ] **Check MIDDLEWARE** includes:
  - `corsheaders.middleware.CorsMiddleware` ✅

- [ ] **Check REST_FRAMEWORK settings** configured ✅

- [ ] **Check SWAGGER_SETTINGS** configured ✅

- [ ] **Check CORS_ALLOWED_ORIGINS** configured ✅

- [ ] **Check API URLs** included in main `urls.py`:
  ```python
  path("api/", include("api.urls", namespace="api")),
  ```

## Testing

- [ ] **Start Development Server**
  ```bash
  python manage.py runserver
  ```

- [ ] **Test Basic API**
  - Visit: `http://localhost:8000/api/`
  - Should see: DRF browsable API ✅

- [ ] **Test Swagger UI**
  - Visit: `http://localhost:8000/api/swagger/`
  - Should see: Interactive Swagger documentation ✅

- [ ] **Test ReDoc**
  - Visit: `http://localhost:8000/api/redoc/`
  - Should see: Clean ReDoc documentation ✅

- [ ] **Test OpenAPI Schema**
  - Visit: `http://localhost:8000/api/swagger.json`
  - Should see: JSON schema ✅

- [ ] **Test Registration**
  ```bash
  curl -X POST http://localhost:8000/api/users/ \
    -H "Content-Type: application/json" \
    -d '{
      "username": "testuser",
      "email": "test@example.com",
      "password": "testpass123",
      "password_confirm": "testpass123"
    }'
  ```

- [ ] **Test JWT Authentication**
  ```bash
  curl -X POST http://localhost:8000/api/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{
      "username": "testuser",
      "password": "testpass123"
    }'
  ```

- [ ] **Test Protected Endpoint**
  ```bash
  curl -X GET http://localhost:8000/api/users/me/ \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```

## Swagger UI Testing

- [ ] **Access Swagger UI**
  - Navigate to: `http://localhost:8000/api/swagger/`

- [ ] **Test Authorization**
  - Click "Authorize" button
  - Enter: `Bearer YOUR_ACCESS_TOKEN`
  - Click "Authorize"

- [ ] **Test Endpoints**
  - Expand any endpoint
  - Click "Try it out"
  - Fill parameters
  - Click "Execute"
  - Verify response

- [ ] **Test Different HTTP Methods**
  - GET request ✅
  - POST request ✅
  - PATCH request ✅
  - DELETE request ✅

## pyproject.toml Check

- [ ] **Verify Dependencies Added**
  ```toml
  djangorestframework = "^3.16.1"
  drf-yasg = {extras = ["validation"], version = "^1.21.11"}
  markdown = "^3.9"
  django-cors-headers = "^4.9.0"
  djangorestframework-simplejwt = "^5.3.0"
  ```

- [ ] **Run Poetry Check**
  ```bash
  poetry check
  poetry lock --check
  ```

## Documentation Review

- [ ] **Review API README**
  - File: `api/README.md` ✅

- [ ] **Review Setup Guide**
  - File: `docs/API_SETUP_GUIDE.md` ✅

- [ ] **Review Swagger Guide**
  - File: `docs/SWAGGER_REDOC_GUIDE.md` ✅

- [ ] **Review Quick Start**
  - File: `docs/MOBILE_API_QUICKSTART.md` ✅

## Mobile App Integration

- [ ] **Test CORS Configuration**
  - Add your mobile app URL to CORS_ALLOWED_ORIGINS
  - Test from mobile app/React Native

- [ ] **Test Image Upload**
  - Create ad with images
  - Verify images are uploaded correctly

- [ ] **Test Real-time Features**
  - Chat messaging
  - Notifications

## Production Preparation

- [ ] **Security Review**
  - DEBUG = False in production
  - SECRET_KEY in environment variables
  - ALLOWED_HOSTS configured
  - CORS origins restricted to production domains

- [ ] **Performance**
  - Enable caching
  - Configure pagination appropriately
  - Set up CDN for media files

- [ ] **Monitoring**
  - Set up error tracking (Sentry)
  - Configure logging
  - Monitor API performance

- [ ] **Documentation**
  - Update API documentation URL in mobile app
  - Share Swagger/ReDoc URLs with team
  - Document any custom endpoints

## Common Issues

### Issue: Import errors for rest_framework
**Solution:** Run `pip install -r requirements_api.txt`

### Issue: drf_yasg not found
**Solution:** Run `pip install drf-yasg[validation]>=1.21.11`

### Issue: Swagger UI shows empty
**Solution:** Check that all viewsets are registered in router

### Issue: CORS errors in mobile app
**Solution:** Add mobile app URL to CORS_ALLOWED_ORIGINS

### Issue: 401 Unauthorized in Swagger
**Solution:** Click "Authorize" and enter JWT token with "Bearer " prefix

## Helpful Commands

```bash
# Install dependencies
pip install -r requirements_api.txt

# or with Poetry
poetry install

# Run development server
python manage.py runserver

# Run tests
python manage.py test api

# Check for errors
python manage.py check

# Create superuser
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic

# View all URLs
python manage.py show_urls  # if installed
```

## Resources

- **Swagger UI:** http://localhost:8000/api/swagger/
- **ReDoc:** http://localhost:8000/api/redoc/
- **DRF Docs:** https://www.django-rest-framework.org/
- **drf-yasg Docs:** https://drf-yasg.readthedocs.io/
- **OpenAPI Spec:** https://swagger.io/specification/

## Success! 🎉

If all items are checked, your API is ready to use!

Next steps:
1. Start building your React Native mobile app
2. Import OpenAPI schema to Postman for testing
3. Share Swagger URL with your team
4. Begin implementing mobile app features

---

**Need Help?**
- Check the docs in `/docs/` folder
- Visit Swagger UI for interactive testing
- Email: support@idrissimart.com

**Happy Coding! 🚀**
