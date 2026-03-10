# Mobile API - Quick Start Guide

## 🚀 Quick Installation

```bash
# 1. Install API dependencies
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.0
pip install django-cors-headers==4.3.1
pip install django-filter==23.5

# 2. Run migrations
python manage.py migrate

# 3. Start server
python manage.py runserver

# 4. Test API
curl http://localhost:8000/api/
```

## 🔑 Authentication

### Register User
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "mobile": "+966501234567",
    "country": 1
  }'
```

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Use Token
```bash
curl http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📱 React Native Setup

### Install Dependencies
```bash
npm install axios
npm install @react-native-async-storage/async-storage
```

### API Service (api.js)
```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://YOUR_SERVER_IP:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = await AsyncStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
            refresh,
          });
          await AsyncStorage.setItem('access_token', response.data.access);
          error.config.headers.Authorization = `Bearer ${response.data.access}`;
          return axios(error.config);
        } catch (refreshError) {
          // Redirect to login
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Auth Functions (auth.js)
```javascript
import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const register = async (userData) => {
  const response = await api.post('/users/', userData);
  return response.data;
};

export const login = async (username, password) => {
  const response = await api.post('/auth/token/', { username, password });
  await AsyncStorage.setItem('access_token', response.data.access);
  await AsyncStorage.setItem('refresh_token', response.data.refresh);
  return response.data;
};

export const logout = async () => {
  await AsyncStorage.removeItem('access_token');
  await AsyncStorage.removeItem('refresh_token');
};

export const getCurrentUser = async () => {
  const response = await api.get('/users/me/');
  return response.data;
};
```

### Ads Functions (ads.js)
```javascript
import api from './api';

export const getAds = async (page = 1, filters = {}) => {
  const params = new URLSearchParams({ page, ...filters });
  const response = await api.get(`/ads/?${params}`);
  return response.data;
};

export const getAdDetail = async (id) => {
  const response = await api.get(`/ads/${id}/`);
  return response.data;
};

export const createAd = async (adData) => {
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
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const updateAd = async (id, adData) => {
  const response = await api.patch(`/ads/${id}/`, adData);
  return response.data;
};

export const deleteAd = async (id) => {
  await api.delete(`/ads/${id}/`);
};

export const toggleFavorite = async (id) => {
  const response = await api.post(`/ads/${id}/toggle_favorite/`);
  return response.data;
};
```

### Usage Example (AdsList.js)
```javascript
import React, { useEffect, useState } from 'react';
import { View, FlatList, Text } from 'react-native';
import { getAds } from './services/ads';

const AdsList = () => {
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAds();
  }, []);

  const loadAds = async () => {
    try {
      const data = await getAds(1);
      setAds(data.results);
    } catch (error) {
      console.error('Error loading ads:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      <FlatList
        data={ads}
        renderItem={({ item }) => (
          <View>
            <Text>{item.title}</Text>
            <Text>{item.price} {item.currency}</Text>
          </View>
        )}
        keyExtractor={(item) => item.id.toString()}
      />
    </View>
  );
};

export default AdsList;
```

## 🔍 Common Queries

### Search Ads
```javascript
const searchAds = async (query) => {
  const response = await api.get(`/ads/?search=${query}`);
  return response.data;
};
```

### Filter by Category and Price
```javascript
const filterAds = async (categoryId, minPrice, maxPrice) => {
  const response = await api.get(
    `/ads/?category=${categoryId}&min_price=${minPrice}&max_price=${maxPrice}`
  );
  return response.data;
};
```

### Get Featured Ads
```javascript
const getFeaturedAds = async () => {
  const response = await api.get('/ads/featured/');
  return response.data;
};
```

### Get User's Ads
```javascript
const getMyAds = async () => {
  const response = await api.get('/ads/my_ads/');
  return response.data;
};
```

## 💬 Chat Example

### Create Chat Room
```javascript
const createChatRoom = async (adId) => {
  const response = await api.post('/chat-rooms/create_or_get/', {
    ad_id: adId,
  });
  return response.data;
};
```

### Send Message
```javascript
const sendMessage = async (roomId, message) => {
  const response = await api.post(`/chat-rooms/${roomId}/send_message/`, {
    message,
  });
  return response.data;
};
```

## 🔔 Notifications

### Get Unread Count
```javascript
const getUnreadCount = async () => {
  const response = await api.get('/notifications/unread_count/');
  return response.data.count;
};
```

### Mark All as Read
```javascript
const markAllRead = async () => {
  await api.post('/notifications/mark_all_read/');
};
```

## 📦 Complete Example App Structure

```
mobile-app/
├── src/
│   ├── services/
│   │   ├── api.js          # Axios instance
│   │   ├── auth.js         # Auth functions
│   │   ├── ads.js          # Ads functions
│   │   ├── chat.js         # Chat functions
│   │   └── notifications.js
│   ├── screens/
│   │   ├── LoginScreen.js
│   │   ├── RegisterScreen.js
│   │   ├── HomeScreen.js
│   │   ├── AdsListScreen.js
│   │   ├── AdDetailScreen.js
│   │   ├── CreateAdScreen.js
│   │   └── ProfileScreen.js
│   └── components/
│       ├── AdCard.js
│       ├── SearchBar.js
│       └── FilterModal.js
└── App.js
```

## 🛠️ Troubleshooting

### CORS Error
Add your mobile app's IP to CORS settings in `settings/common.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://192.168.1.100:8081",  # Your local IP
]
```

### Can't connect to localhost
Use your computer's IP address instead of localhost:
```javascript
const API_URL = 'http://192.168.1.100:8000/api';
```

### Token expired
Implement token refresh logic as shown in the interceptors example above.

## 📚 Resources

- Full API Docs: `/api/README.md`
- Setup Guide: `/docs/API_SETUP_GUIDE.md`
- Implementation Summary: `/docs/API_IMPLEMENTATION_SUMMARY.md`
- DRF Docs: https://www.django-rest-framework.org/
- React Native Docs: https://reactnative.dev/

## ✅ Checklist

- [ ] Install API dependencies
- [ ] Run migrations
- [ ] Test API with Postman
- [ ] Configure CORS for your IP
- [ ] Create React Native project
- [ ] Install axios and async-storage
- [ ] Create API service
- [ ] Implement authentication
- [ ] Create screens
- [ ] Test on device

---

**Happy Coding! 🚀**
