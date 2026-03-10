# Mobile API Documentation

## Overview

This API provides comprehensive REST endpoints for the Idrissimart classified ads platform, designed to support React Native mobile applications.

## Interactive API Documentation

The API now includes interactive documentation powered by **Swagger UI** and **ReDoc**:

### Swagger UI (Interactive)
**URL:** `http://your-domain.com/api/swagger/`

Features:
- Interactive API exploration
- Try out endpoints directly from the browser
- Live request/response testing
- JWT authentication support
- Request/response examples

### ReDoc (Clean Documentation)
**URL:** `http://your-domain.com/api/redoc/`

Features:
- Clean, readable API documentation
- Search functionality
- Code samples in multiple languages
- Detailed schema information
- Mobile-friendly interface

### OpenAPI Schema
**JSON:** `http://your-domain.com/api/swagger.json`
**YAML:** `http://your-domain.com/api/swagger.yaml`

## Authentication

The API uses JWT (JSON Web Token) authentication.

### Obtain Token
```bash
POST /api/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
```bash
POST /api/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

### Using Token in Swagger UI

1. Click the **"Authorize"** button at the top of Swagger UI
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click **"Authorize"**
4. Now you can test authenticated endpoints

### Using Token in Requests
Include the token in the Authorization header:
```
Authorization: Bearer your_access_token
```

## Base URL

```
http://your-domain.com/api/
```

## Quick Start

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "mobile": "+966501234567",
    "country": 1
  }'
```

### 2. Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'
```

### 3. Access Protected Endpoints
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Main Endpoints

For a complete list of endpoints with detailed documentation, parameters, and examples, visit:
- **Swagger UI:** `/api/swagger/`
- **ReDoc:** `/api/redoc/`

### Quick Reference

#### Authentication & Users
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh token
- `GET/POST /api/users/` - List/Register users
- `GET /api/users/me/` - Current user profile
- `PATCH /api/users/update_profile/` - Update profile

#### Classified Ads
- `GET /api/ads/` - List all ads (with filters)
- `POST /api/ads/` - Create new ad
- `GET /api/ads/{id}/` - Ad details
- `PATCH /api/ads/{id}/` - Update ad
- `DELETE /api/ads/{id}/` - Delete ad
- `GET /api/ads/featured/` - Featured ads
- `GET /api/ads/urgent/` - Urgent ads
- `POST /api/ads/{id}/toggle_favorite/` - Add/remove favorite

#### Categories & Countries
- `GET /api/countries/` - List countries
- `GET /api/categories/` - List categories
- `GET /api/categories/root_categories/` - Root categories only

#### Blog
- `GET /api/blogs/` - List blogs
- `GET /api/blogs/{id}/` - Blog details
- `POST /api/blogs/{id}/like/` - Like/unlike
- `POST /api/blogs/{id}/comment/` - Add comment

#### Chat
- `GET /api/chat-rooms/` - User's chat rooms
- `POST /api/chat-rooms/create_or_get/` - Create/get room
- `POST /api/chat-rooms/{id}/send_message/` - Send message

#### Wishlist & Notifications
- `GET /api/wishlist/items/` - Wishlist items
- `GET /api/notifications/` - User's notifications
- `GET /api/notifications/unread_count/` - Unread count

## Query Parameters

### Filtering
```
GET /api/ads/?category=1&city=Riyadh&min_price=100&max_price=1000
```

### Searching
```
GET /api/ads/?search=laptop
```

### Ordering
```
GET /api/ads/?ordering=-created_at  # Descending
GET /api/ads/?ordering=price        # Ascending
```

### Pagination
```
GET /api/ads/?page=2&page_size=20
```

## Response Format

### Success Response (List)
```json
{
    "count": 100,
    "next": "http://api.example.com/api/ads/?page=2",
    "previous": null,
    "results": [...]
}
```

### Success Response (Detail)
```json
{
    "id": 1,
    "title": "Used Laptop",
    "price": 2000,
    ...
}
```

### Error Response
```json
{
    "error": "Error message",
    "detail": "Detailed error information"
}
```

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

Default limits:
- **100 requests/minute** for authenticated users
- **20 requests/minute** for unauthenticated users

## Testing the API

### Using Swagger UI (Recommended)
1. Visit `/api/swagger/`
2. Click "Authorize" and enter your JWT token
3. Try out any endpoint interactively

### Using Postman
1. Import the OpenAPI schema from `/api/swagger.json`
2. Add Bearer token to Authorization header
3. Test endpoints

### Using cURL
See examples above

## React Native Integration

Example code for React Native is provided in the Quick Start Guide.
For complete examples, see: `/docs/MOBILE_API_QUICKSTART.md`

## Support

- **Interactive Docs:** `/api/swagger/` or `/api/redoc/`
- **Setup Guide:** `/docs/API_SETUP_GUIDE.md`
- **Quick Start:** `/docs/MOBILE_API_QUICKSTART.md`
- **Email:** support@idrissimart.com

## Version

**API Version:** v1
**Last Updated:** March 10, 2026
