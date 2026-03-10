# API Documentation Index

Welcome to the Idrissimart API documentation! This folder contains comprehensive guides for setting up and using the API.

## 📚 Quick Navigation

### Getting Started
1. **[API_SETUP_GUIDE.md](./API_SETUP_GUIDE.md)** - Complete setup instructions
2. **[API_SETUP_CHECKLIST.md](./API_SETUP_CHECKLIST.md)** - Step-by-step checklist
3. **[MOBILE_API_QUICKSTART.md](./MOBILE_API_QUICKSTART.md)** - Quick start for React Native

### API Documentation
4. **[SWAGGER_REDOC_GUIDE.md](./SWAGGER_REDOC_GUIDE.md)** - Swagger UI & ReDoc usage
5. **[SWAGGER_IMPLEMENTATION_SUMMARY.md](./SWAGGER_IMPLEMENTATION_SUMMARY.md)** - Implementation details
6. **[API_IMPLEMENTATION_SUMMARY.md](./API_IMPLEMENTATION_SUMMARY.md)** - Complete API overview

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/api/swagger/ 🔥
- **ReDoc:** http://localhost:8000/api/redoc/ 📖
- **DRF Browsable API:** http://localhost:8000/api/

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements_api.txt

# 2. Run migrations
python manage.py migrate

# 3. Start server
python manage.py runserver

# 4. Visit Swagger UI
# http://localhost:8000/api/swagger/
```

## 📖 Documentation Files

### Setup & Installation
- **API_SETUP_GUIDE.md** (Updated)
  - Installation instructions
  - Configuration steps
  - Testing procedures
  - React Native integration examples

- **API_SETUP_CHECKLIST.md** (New)
  - Complete setup checklist
  - Verification steps
  - Common issues and solutions
  - Success criteria

### API Usage
- **SWAGGER_REDOC_GUIDE.md** (New)
  - How to use Swagger UI
  - How to use ReDoc
  - Authentication in Swagger
  - Testing endpoints
  - Export to Postman

- **MOBILE_API_QUICKSTART.md** (Existing)
  - React Native setup
  - API service examples
  - Authentication flow
  - Common queries

### Technical Details
- **SWAGGER_IMPLEMENTATION_SUMMARY.md** (New)
  - What was implemented
  - Dependencies added
  - Configuration details
  - Package information

- **API_IMPLEMENTATION_SUMMARY.md** (Existing)
  - Complete API overview
  - All endpoints listed
  - Models covered
  - Features implemented

## 🎯 For Different Users

### For New Developers
Start here:
1. [API_SETUP_CHECKLIST.md](./API_SETUP_CHECKLIST.md) - Follow the checklist
2. [SWAGGER_REDOC_GUIDE.md](./SWAGGER_REDOC_GUIDE.md) - Learn to use Swagger
3. http://localhost:8000/api/swagger/ - Start testing!

### For Mobile App Developers
Start here:
1. [MOBILE_API_QUICKSTART.md](./MOBILE_API_QUICKSTART.md) - React Native guide
2. http://localhost:8000/api/swagger/ - Explore endpoints
3. http://localhost:8000/api/swagger.json - Import to Postman

### For Team Leads
Start here:
1. [SWAGGER_IMPLEMENTATION_SUMMARY.md](./SWAGGER_IMPLEMENTATION_SUMMARY.md) - What was built
2. [API_IMPLEMENTATION_SUMMARY.md](./API_IMPLEMENTATION_SUMMARY.md) - Complete overview
3. http://localhost:8000/api/redoc/ - Clean documentation

### For Backend Developers
Start here:
1. [API_SETUP_GUIDE.md](./API_SETUP_GUIDE.md) - Technical setup
2. [API_IMPLEMENTATION_SUMMARY.md](./API_IMPLEMENTATION_SUMMARY.md) - Architecture
3. Review serializers and viewsets in `/api/` folder

## 🔥 Interactive Features

### Swagger UI (`/api/swagger/`)
- ✅ Interactive API testing
- ✅ Try out endpoints
- ✅ JWT authentication
- ✅ Real-time responses
- ✅ Request validation
- ✅ Export as cURL

### ReDoc (`/api/redoc/`)
- ✅ Clean documentation
- ✅ Search functionality
- ✅ Mobile-friendly
- ✅ Code examples
- ✅ Schema visualization
- ✅ One-page view

### OpenAPI Schema
- ✅ JSON format: `/api/swagger.json`
- ✅ YAML format: `/api/swagger.yaml`
- ✅ Import to Postman
- ✅ Generate SDKs
- ✅ API versioning

## 📦 What's Included

### 50+ API Endpoints
- User authentication & management
- Classified ads CRUD
- Categories & countries
- Blog posts & comments
- Real-time chat
- Wishlist/favorites
- Notifications
- Packages & payments
- FAQ & support
- Static pages

### Complete Documentation
- ✅ Request/response examples
- ✅ Authentication requirements
- ✅ Query parameters
- ✅ Error codes
- ✅ Rate limiting info
- ✅ Best practices

### Mobile-Ready
- ✅ React Native examples
- ✅ Authentication flow
- ✅ Image upload support
- ✅ Real-time features
- ✅ CORS configured

## 🛠️ Tools & Scripts

### Installation Script
```bash
./scripts/install_api.sh
```
Automatically installs all dependencies and verifies installation.

### Requirements Files
- `requirements_api.txt` - API-specific dependencies
- `pyproject.toml` - Poetry configuration

## 📝 Additional Resources

### External Links
- **Django REST Framework:** https://www.django-rest-framework.org/
- **drf-yasg:** https://drf-yasg.readthedocs.io/
- **OpenAPI Spec:** https://swagger.io/specification/
- **React Native:** https://reactnative.dev/

### Internal Files
- `/api/README.md` - API app documentation
- `/api/serializers.py` - All serializers
- `/api/views.py` - All viewsets
- `/api/urls.py` - URL routing

## 🔍 Common Tasks

### View All Endpoints
Visit: http://localhost:8000/api/swagger/

### Test Authentication
```bash
# Get token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Use token in Swagger:
# 1. Click "Authorize"
# 2. Enter: Bearer YOUR_TOKEN
```

### Export to Postman
1. Copy: http://localhost:8000/api/swagger.json
2. Postman → Import → Link
3. Paste and import

### Generate Client SDK
Use the OpenAPI schema with tools like:
- Swagger Codegen
- OpenAPI Generator
- Postman's SDK generation

## 💡 Tips

1. **Use Swagger UI for testing** - It's faster than Postman for quick tests
2. **Bookmark `/api/swagger/`** - You'll use it often
3. **Share ReDoc with team** - Clean documentation for everyone
4. **Import to Postman** - For advanced testing scenarios
5. **Read the guides** - They have detailed examples
6. **Check the checklist** - Ensure everything is configured

## 🐛 Troubleshooting

### Can't access Swagger?
- Check server is running: `python manage.py runserver`
- Visit: http://localhost:8000/api/swagger/
- Clear browser cache

### Import errors?
- Run: `pip install -r requirements_api.txt`
- Check: `python -c "import drf_yasg; print('OK')"`

### Authentication not working?
- Get JWT token from `/api/auth/token/`
- Click "Authorize" in Swagger
- Enter: `Bearer YOUR_TOKEN` (include "Bearer ")

### More issues?
See [API_SETUP_CHECKLIST.md](./API_SETUP_CHECKLIST.md) for common issues and solutions.

## 📞 Support

- **Interactive Docs:** http://localhost:8000/api/swagger/
- **Email:** support@idrissimart.com
- **Issues:** Check GitHub issues
- **Slack:** #api-development channel

## ✅ Status

- ✅ API fully implemented
- ✅ Swagger UI configured
- ✅ ReDoc configured
- ✅ Documentation complete
- ✅ Examples provided
- ✅ Mobile-ready
- ✅ Production-ready

---

**Last Updated:** March 10, 2026
**Version:** 1.0.0
**Maintainer:** Idrissimart Team

**Happy Coding! 🚀**
