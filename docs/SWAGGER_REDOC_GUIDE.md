# Swagger & ReDoc API Documentation Setup

## Overview

The Idrissimart API now includes interactive API documentation using:
- **Swagger UI** - Interactive API testing interface
- **ReDoc** - Beautiful, clean API documentation
- **OpenAPI 3.0** - Industry-standard API specification

## Access Documentation

### Swagger UI (Interactive Testing)
**URL:** `http://localhost:8000/api/swagger/`

Perfect for:
- Testing API endpoints interactively
- Trying out requests with different parameters
- Understanding request/response formats
- Debugging API calls

### ReDoc (Clean Documentation)
**URL:** `http://localhost:8000/api/redoc/`

Perfect for:
- Reading comprehensive API documentation
- Understanding API structure
- Searching for specific endpoints
- Sharing with team members

### OpenAPI Schema
- **JSON Format:** `http://localhost:8000/api/swagger.json`
- **YAML Format:** `http://localhost:8000/api/swagger.yaml`

Use these for:
- Importing into Postman
- Generating client SDKs
- API contract validation

## Using Swagger UI

### Step 1: Access Swagger UI
Navigate to: `http://localhost:8000/api/swagger/`

### Step 2: Authenticate (for protected endpoints)

1. **Get JWT Token First:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "your_username",
       "password": "your_password"
     }'
   ```

2. **Copy the Access Token** from the response

3. **Click the "Authorize" button** at the top of Swagger UI

4. **Enter:** `Bearer YOUR_ACCESS_TOKEN` (include "Bearer " prefix)

5. **Click "Authorize"** button

6. **Click "Close"**

Now you can test all authenticated endpoints!

### Step 3: Test an Endpoint

1. **Expand an endpoint** (e.g., GET /api/ads/)

2. **Click "Try it out"**

3. **Fill in parameters** (optional):
   - Query parameters (search, filters)
   - Path parameters (ID)
   - Request body (for POST/PATCH)

4. **Click "Execute"**

5. **View the response:**
   - Response code
   - Response body
   - Response headers
   - cURL command

### Example: Creating an Ad

1. Authorize with JWT token
2. Find `POST /api/ads/` endpoint
3. Click "Try it out"
4. Fill in the request body:
   ```json
   {
     "title": "Used Laptop for Sale",
     "category": 1,
     "description": "Excellent condition laptop",
     "price": 2000,
     "currency": "SAR",
     "country": 1,
     "city": "Riyadh",
     "mobile": "+966501234567"
   }
   ```
5. Click "Execute"
6. Check the response!

## Using ReDoc

### Step 1: Access ReDoc
Navigate to: `http://localhost:8000/api/redoc/`

### Step 2: Browse Documentation

- **Left Sidebar:** Navigate through endpoints
- **Main Panel:** View detailed documentation
- **Search:** Use search bar at top
- **Expand/Collapse:** Click sections to expand/collapse

### Features

#### 1. Search Functionality
- Type in the search box to find endpoints
- Search by endpoint path, method, or description

#### 2. Code Examples
- See request/response examples
- Multiple response code examples
- Schema definitions

#### 3. Authentication Info
- View authentication requirements
- See how to use JWT tokens

#### 4. Request/Response Schemas
- Detailed field descriptions
- Data types and validations
- Required vs optional fields

## Configuration

### Swagger Settings (in settings/common.py)

```python
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': True,
}
```

### ReDoc Settings

```python
REDOC_SETTINGS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': True,
}
```

## Customizing Documentation

### Adding Descriptions to ViewSets

```python
class ClassifiedAdViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing classified ads.

    list:
    Return a list of all classified ads with filtering options.

    create:
    Create a new classified ad.

    retrieve:
    Get details of a specific ad.

    update:
    Update an existing ad (owner only).

    destroy:
    Delete an ad (owner only).
    """
    queryset = ClassifiedAd.objects.all()
    serializer_class = ClassifiedAdSerializer
```

### Adding Parameter Descriptions

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ClassifiedAdViewSet(viewsets.ModelViewSet):

    @swagger_auto_schema(
        operation_description="Search ads by keyword",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search keyword",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'min_price',
                openapi.IN_QUERY,
                description="Minimum price filter",
                type=openapi.TYPE_NUMBER
            ),
        ],
        responses={200: ClassifiedAdSerializer(many=True)}
    )
    def list(self, request):
        # Your implementation
        pass
```

## Common Tasks

### 1. Test Registration Flow

**Swagger UI Steps:**
1. Go to POST /api/users/
2. Click "Try it out"
3. Fill user data
4. Execute
5. Check response for user ID

### 2. Test Authentication Flow

**Swagger UI Steps:**
1. Go to POST /api/auth/token/
2. Click "Try it out"
3. Enter username and password
4. Execute
5. Copy the access token
6. Click "Authorize" at top
7. Paste token with "Bearer " prefix
8. Now test protected endpoints!

### 3. Test File Upload (Ad with Images)

**Note:** File upload testing in Swagger UI has limitations. Better to use:
- Postman
- cURL
- Your mobile app

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/ads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Laptop" \
  -F "category=1" \
  -F "description=Great laptop" \
  -F "price=2000" \
  -F "currency=SAR" \
  -F "country=1" \
  -F "city=Riyadh" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"
```

## Exporting to Postman

### Step 1: Get OpenAPI Schema
Visit: `http://localhost:8000/api/swagger.json`

### Step 2: Import to Postman
1. Open Postman
2. Click "Import"
3. Choose "Link"
4. Paste: `http://localhost:8000/api/swagger.json`
5. Click "Continue"
6. Click "Import"

### Step 3: Configure Authentication
1. Select the imported collection
2. Go to "Authorization" tab
3. Type: "Bearer Token"
4. Token: YOUR_ACCESS_TOKEN

Now all endpoints are available in Postman!

## Production Deployment

### Security Considerations

1. **Disable Swagger in Production** (optional):
   ```python
   # In production settings
   if not DEBUG:
       SWAGGER_SETTINGS['USE_SESSION_AUTH'] = False
       # Or completely disable:
       # Remove swagger URLs from urlpatterns
   ```

2. **Restrict Access:**
   ```python
   # Only allow authenticated users
   schema_view = get_schema_view(
       ...
       permission_classes=(permissions.IsAuthenticated,),
   )
   ```

3. **Use HTTPS:**
   - Always use HTTPS in production
   - Update SWAGGER_SETTINGS with your domain

### Performance

- Swagger UI and ReDoc are cached
- Schema generation is optimized
- No performance impact on API endpoints

## Troubleshooting

### Swagger UI not loading
**Solution:** Check browser console for errors, ensure all dependencies are installed

### Authentication not working
**Solution:** Make sure to include "Bearer " prefix in authorization

### Endpoints not showing
**Solution:** Check that viewsets are registered in router

### Schema validation errors
**Solution:** Ensure serializers have proper field definitions

## Additional Resources

- **drf-yasg Documentation:** https://drf-yasg.readthedocs.io/
- **OpenAPI Specification:** https://swagger.io/specification/
- **Swagger UI Guide:** https://swagger.io/docs/open-source-tools/swagger-ui/
- **ReDoc Documentation:** https://redocly.com/docs/redoc/

## Tips & Best Practices

1. **Always authorize in Swagger UI** before testing protected endpoints
2. **Use ReDoc for reading**, Swagger UI for testing
3. **Export to Postman** for advanced testing scenarios
4. **Add docstrings** to your viewsets for better documentation
5. **Use swagger_auto_schema** decorator for custom endpoint docs
6. **Test file uploads** using cURL or Postman, not Swagger UI
7. **Keep schemas updated** by documenting serializer fields properly

## Support

For questions or issues:
- Check the troubleshooting section above
- Visit `/api/swagger/` for interactive testing
- Visit `/api/redoc/` for clean documentation
- Email: support@idrissimart.com

---

**Happy API Testing! 🚀**
