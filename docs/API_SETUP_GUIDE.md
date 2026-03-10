# API App Installation and Setup Guide

## Overview

This document provides instructions for setting up and using the API app for the Idrissimart React Native mobile application.

## Interactive API Documentation 🎉

The API includes **Swagger UI** and **ReDoc** for interactive testing and documentation:

- **Swagger UI:** `http://localhost:8000/api/swagger/` - Interactive API testing
- **ReDoc:** `http://localhost:8000/api/redoc/` - Beautiful, clean documentation
- **OpenAPI Schema:** `http://localhost:8000/api/swagger.json` - For imports

See [SWAGGER_REDOC_GUIDE.md](./SWAGGER_REDOC_GUIDE.md) for detailed usage instructions.

## Installation

### 1. Install Required Packages

```bash
pip install -r requirements_api.txt
```

Or using Poetry:

```bash
poetry install
```

Or install individually:

```bash
pip install djangorestframework>=3.16.1
pip install djangorestframework-simplejwt>=5.3.0
pip install django-cors-headers>=4.9.0
pip install django-filter>=25.1
pip install markdown>=3.9
pip install drf-yasg[validation]>=1.21.11
```

### 2. Run Migrations

The API app doesn't have its own models, but ensure all migrations are up to date:

```bash
python manage.py migrate
```

### 3. Create a Superuser (if not exists)

```bash
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

### 5. Test the API

Visit any of these URLs:
- **DRF Browsable API:** `http://localhost:8000/api/`
- **Swagger UI:** `http://localhost:8000/api/swagger/` ⭐ Recommended
- **ReDoc:** `http://localhost:8000/api/redoc/`

## Quick Start with Swagger UI

1. Navigate to `http://localhost:8000/api/swagger/`
2. Click "Authorize" button at the top
3. Get JWT token from `/api/auth/token/` endpoint
4. Enter `Bearer YOUR_TOKEN` in the authorization dialog
5. Start testing endpoints interactively!

For detailed Swagger/ReDoc usage, see [SWAGGER_REDOC_GUIDE.md](./SWAGGER_REDOC_GUIDE.md)

## API Endpoints

### Authentication

#### Obtain JWT Token
```
POST /api/auth/token/
Body: {
    "username": "your_username",
    "password": "your_password"
}
```

#### Refresh JWT Token
```
POST /api/auth/token/refresh/
Body: {
    "refresh": "your_refresh_token"
}
```

### Main Endpoints

#### Users
- `GET /api/users/` - List users
- `POST /api/users/` - Register new user
- `GET /api/users/me/` - Get current user profile
- `PATCH /api/users/update_profile/` - Update current user
- `GET /api/users/{id}/` - Get user details
- `GET /api/users/{id}/ads/` - Get user's ads
- `GET /api/users/{id}/reviews/` - Get user's reviews

#### Countries
- `GET /api/countries/` - List countries

#### Categories
- `GET /api/categories/` - List categories
- `GET /api/categories/{id}/` - Category details
- `GET /api/categories/{id}/ads/` - Ads in category
- `GET /api/categories/root_categories/` - Root categories only

#### Classified Ads
- `GET /api/ads/` - List ads
- `POST /api/ads/` - Create ad (auth required)
- `GET /api/ads/{id}/` - Ad details
- `PATCH /api/ads/{id}/` - Update ad (owner only)
- `DELETE /api/ads/{id}/` - Delete ad (owner only)
- `GET /api/ads/featured/` - Featured ads
- `GET /api/ads/urgent/` - Urgent ads
- `GET /api/ads/recent/` - Recent ads
- `GET /api/ads/my_ads/` - Current user's ads
- `POST /api/ads/{id}/toggle_favorite/` - Add/remove favorite
- `POST /api/ads/{id}/review/` - Add review

#### Blogs
- `GET /api/blog-categories/` - Blog categories
- `GET /api/blogs/` - List blogs
- `GET /api/blogs/{id}/` - Blog details
- `POST /api/blogs/{id}/like/` - Like/unlike blog
- `POST /api/blogs/{id}/comment/` - Add comment

#### Chat
- `GET /api/chat-rooms/` - User's chat rooms
- `GET /api/chat-rooms/{id}/` - Chat room details
- `POST /api/chat-rooms/create_or_get/` - Create/get chat room
- `POST /api/chat-rooms/{id}/send_message/` - Send message
- `POST /api/chat-rooms/{id}/mark_read/` - Mark as read

#### Wishlist
- `GET /api/wishlist/` - User's wishlist
- `GET /api/wishlist/items/` - Wishlist items

#### Notifications
- `GET /api/notifications/` - User's notifications
- `POST /api/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/mark_all_read/` - Mark all as read
- `GET /api/notifications/unread_count/` - Unread count

#### Packages & Payments
- `GET /api/ad-features/` - List features
- `GET /api/ad-packages/` - List packages
- `GET /api/payments/` - User's payments
- `GET /api/user-packages/` - User's packages

#### FAQ & Support
- `GET /api/faq-categories/` - FAQ categories
- `GET /api/faqs/` - List FAQs
- `GET /api/safety-tips/` - Safety tips
- `POST /api/contact-messages/` - Send message

#### Home & Static Pages
- `GET /api/home-sliders/` - Home sliders
- `GET /api/why-choose-us/` - Features
- `GET /api/site-config/` - Site config
- `GET /api/about-page/` - About page
- `GET /api/contact-page/` - Contact page
- `GET /api/terms-page/` - Terms & conditions
- `GET /api/privacy-page/` - Privacy policy

#### Custom Fields
- `GET /api/custom-fields/` - List custom fields
- `GET /api/custom-fields/by_category/?category_id={id}` - Fields by category

## Filtering and Search

### Search
Add `?search=keyword` to search endpoints:
```
GET /api/ads/?search=laptop
```

### Filtering
Add filter parameters:
```
GET /api/ads/?category=1&city=Riyadh&min_price=100&max_price=1000
```

### Ordering
Add `?ordering=field` or `?ordering=-field` (descending):
```
GET /api/ads/?ordering=-created_at
GET /api/ads/?ordering=price
```

### Pagination
Use `?page=N&page_size=N`:
```
GET /api/ads/?page=2&page_size=20
```

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React Native web)
- `http://localhost:8081` (Expo default)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8081`

To add more origins, edit `idrissimart/settings/common.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://your-mobile-app-url",
    # Add more origins here
]
```

## React Native Usage Example

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://your-server.com/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Login
const login = async (username, password) => {
  const response = await api.post('/auth/token/', {
    username,
    password,
  });
  await AsyncStorage.setItem('access_token', response.data.access);
  await AsyncStorage.setItem('refresh_token', response.data.refresh);
  return response.data;
};

// Get ads
const getAds = async (page = 1) => {
  const response = await api.get(`/ads/?page=${page}`);
  return response.data;
};

// Create ad
const createAd = async (adData) => {
  const formData = new FormData();
  Object.keys(adData).forEach(key => {
    if (key === 'images') {
      adData[key].forEach((image, index) => {
        formData.append('images', {
          uri: image.uri,
          type: 'image/jpeg',
          name: `image_${index}.jpg`,
        });
      });
    } else {
      formData.append(key, adData[key]);
    }
  });

  const response = await api.post('/ads/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export { login, getAds, createAd };
```

## Testing

Run API tests:

```bash
python manage.py test api
```

## Security Considerations

1. **JWT Tokens**: Access tokens expire after 1 day, refresh tokens after 7 days
2. **CORS**: Only allowed origins can access the API
3. **Permissions**: Most write operations require authentication
4. **Rate Limiting**: Consider adding rate limiting in production
5. **HTTPS**: Always use HTTPS in production

## Troubleshooting

### Issue: "Import 'rest_framework' could not be resolved"
**Solution**: Install djangorestframework: `pip install djangorestframework`

### Issue: CORS errors in mobile app
**Solution**: Add your app's URL to `CORS_ALLOWED_ORIGINS` in settings

### Issue: 401 Unauthorized
**Solution**: Ensure JWT token is being sent in Authorization header

### Issue: 404 Not Found on API endpoints
**Solution**: Check that `/api/` is in your URL path

## Production Deployment

1. Set `DEBUG = False` in production settings
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Enable HTTPS
5. Set up proper CORS origins
6. Consider adding rate limiting
7. Use production-ready database (PostgreSQL)
8. Configure media file storage (S3, etc.)

## Additional Resources

- Django REST Framework documentation: https://www.django-rest-framework.org/
- Django REST Framework JWT: https://django-rest-framework-simplejwt.readthedocs.io/
- React Native documentation: https://reactnative.dev/

## Support

For questions or issues:
- Create an issue in the project repository
- Contact: support@idrissimart.com
