# Smart Login Redirect System - Documentation

## Overview
The system automatically redirects users to their appropriate dashboards after login based on their role and activity.

## Implementation Details

### 1. Custom Login View (`main/auth_views.py`)

**Location:** `c:\WORK\idrissimart\main\auth_views.py`

**Key Method:** `get_success_url()`

```python
def get_success_url(self):
    """
    Determine the redirect URL based on user role:
    - Superusers/Staff -> Admin Dashboard
    - Publishers (users with ads) -> Publisher Dashboard
    - Regular users -> Home page
    """
    user = self.request.user

    # Check if user is superuser/admin
    if user.is_superuser or user.is_staff:
        return reverse_lazy('main:admin_dashboard')

    # Check if user has posted any ads (publisher)
    from .models import ClassifiedAd
    user_has_ads = ClassifiedAd.objects.filter(user=user).exists()

    if user_has_ads:
        return reverse_lazy('main:my_ads')

    # Default redirect for regular users
    return reverse_lazy('main:home')
```

**Welcome Messages:**
- Admins: "مرحباً بك في لوحة الإدارة، {name}! 👨‍💼"
- Regular Users: "مرحباً بك {name}! 🎉"

### 2. Dashboard Redirect View (`main/views.py`)

**Location:** `c:\WORK\idrissimart\main\views.py`

**Function:** `dashboard_redirect(request)`

**URL Pattern:** `/dashboard/`

```python
@login_required
def dashboard_redirect(request):
    """
    Smart dashboard redirect for logged-in users.
    Can be used as a general "My Dashboard" link.
    """
    if user.is_superuser or user.is_staff:
        return redirect('main:admin_dashboard')

    user_has_ads = ClassifiedAd.objects.filter(user=user).exists()
    if user_has_ads:
        return redirect('main:my_ads')

    return redirect('main:home')
```

### 3. URL Routes

**Location:** `c:\WORK\idrissimart\main\urls.py`

```python
urlpatterns = [
    # General dashboard redirect
    path("dashboard/", views.dashboard_redirect, name="dashboard"),

    # Admin dashboard (superusers only)
    path("admin/classifieds/dashboard/",
         classifieds_views.AdminDashboardView.as_view(),
         name="admin_dashboard"),

    # Publisher dashboard (users with ads)
    path("classifieds/my-ads/",
         classifieds_views.MyClassifiedAdsView.as_view(),
         name="my_ads"),
]
```

## User Flow Diagrams

### Login Flow
```
User Logs In
    ↓
Check User Role
    ↓
├─→ Is Superuser/Staff? → Admin Dashboard (/admin/classifieds/dashboard/)
├─→ Has Posted Ads? → Publisher Dashboard (/classifieds/my-ads/)
└─→ Regular User → Home Page (/)
```

### Dashboard Access Flow
```
User Clicks "Dashboard" Link (/dashboard/)
    ↓
Requires Login (@login_required)
    ↓
Check User Type
    ↓
├─→ Superuser/Staff → Admin Dashboard
├─→ Has Ads → My Ads (Publisher View)
└─→ No Ads → Home Page
```

## Dashboard URLs

| User Type | Dashboard URL | Template | View |
|-----------|--------------|----------|------|
| **Superadmin** | `/admin/classifieds/dashboard/` | `admin/dashboard_main.html` | `AdminDashboardView` |
| **Admin** | `/admin/classifieds/dashboard/` | `admin/dashboard_main.html` | `AdminDashboardView` |
| **Publisher** | `/classifieds/my-ads/` | `classifieds/my_ads_list.html` | `MyClassifiedAdsView` |
| **Regular User** | `/` | `pages/home.html` | `HomeView` |

## Features

### Admin Dashboard Features
- ✅ View all advertisements (active, pending, hidden, expired)
- ✅ Statistics cards with counts
- ✅ Advanced filtering and search
- ✅ Hide/Unhide ads (AJAX)
- ✅ Enable cart for ads (AJAX)
- ✅ Delete ads (AJAX)
- ✅ Manage categories
- ✅ Navigate to custom fields, users, packages, transactions

### Publisher Dashboard Features
- ✅ View own advertisements
- ✅ Edit ads
- ✅ Delete ads
- ✅ View ad statistics
- ✅ Create new ads

## Integration with Templates

### Adding Dashboard Link to Navigation

**Example for header/navbar:**

```django-html
{% if user.is_authenticated %}
    <a href="{% url 'main:dashboard' %}" class="nav-link">
        <i class="fas fa-tachometer-alt"></i>
        {% if user.is_superuser %}
            {% trans "لوحة الإدارة" %}
        {% else %}
            {% trans "لوحة التحكم" %}
        {% endif %}
    </a>
{% endif %}
```

### Conditional Dashboard Links

```django-html
{% if user.is_authenticated %}
    {% if user.is_superuser or user.is_staff %}
        <!-- Admin Dashboard Link -->
        <a href="{% url 'main:admin_dashboard' %}" class="btn btn-primary">
            <i class="fas fa-shield-alt"></i> {% trans "إدارة الموقع" %}
        </a>
    {% else %}
        <!-- User Dashboard Link -->
        <a href="{% url 'main:my_ads' %}" class="btn btn-primary">
            <i class="fas fa-list"></i> {% trans "إعلاناتي" %}
        </a>
    {% endif %}
{% endif %}
```

## Testing

### Test Scenarios

1. **Superuser Login**
   - Login with superuser account
   - Should redirect to `/admin/classifieds/dashboard/`
   - Should see admin navigation menu
   - Should see all ads statistics

2. **Publisher Login**
   - Login with user who has posted ads
   - Should redirect to `/classifieds/my-ads/`
   - Should see only their ads
   - Should have edit/delete options

3. **New User Login**
   - Login with user who hasn't posted ads
   - Should redirect to `/`
   - Should see home page

4. **Dashboard URL Direct Access**
   - Navigate to `/dashboard/`
   - Should redirect based on user role
   - Non-authenticated users redirected to login

## Security

### Access Control

**AdminDashboardView:**
```python
def dispatch(self, request, *args, **kwargs):
    if not request.user.is_superuser:
        messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
        return redirect("main:home")
    return super().dispatch(request, *args, **kwargs)
```

**MyClassifiedAdsView:**
```python
class MyClassifiedAdsView(LoginRequiredMixin, ListView):
    # Only shows ads belonging to the logged-in user
    def get_queryset(self):
        return ClassifiedAd.objects.filter(user=self.request.user)
```

## Customization

### Adding More User Roles

To add more user roles (e.g., Moderator):

1. **Update `get_success_url()` in `auth_views.py`:**
```python
def get_success_url(self):
    user = self.request.user

    if user.is_superuser:
        return reverse_lazy('main:admin_dashboard')
    elif user.is_staff:  # Moderator
        return reverse_lazy('main:moderator_dashboard')
    elif ClassifiedAd.objects.filter(user=user).exists():
        return reverse_lazy('main:my_ads')

    return reverse_lazy('main:home')
```

2. **Create the moderator dashboard view and template**

3. **Add URL pattern**

### Custom Redirect After Login

To redirect to a specific page after login, use the `next` parameter:

```html
<a href="{% url 'main:login' %}?next=/classifieds/create/">Login to Post Ad</a>
```

## Troubleshooting

### Issue: Users Not Redirected Correctly

**Check:**
1. User role (`user.is_superuser`, `user.is_staff`)
2. Ads existence: `ClassifiedAd.objects.filter(user=user).exists()`
3. URL names match in `get_success_url()`

### Issue: Permission Denied

**Check:**
1. `dispatch()` method in dashboard views
2. `LoginRequiredMixin` is applied
3. User has appropriate permissions

### Issue: Infinite Redirect Loop

**Check:**
1. `redirect_authenticated_user = True` in `CustomLoginView`
2. Success URL doesn't point back to login
3. Middleware not interfering with redirects

## Summary

The smart login redirect system provides:
- ✅ **Automatic role-based routing** after login
- ✅ **Centralized dashboard redirect** via `/dashboard/`
- ✅ **Three-tier access levels**: Admin, Publisher, Regular User
- ✅ **Secure access control** with permission checks
- ✅ **Seamless user experience** with personalized greetings
- ✅ **Flexible and extensible** for future roles

Users are automatically taken to the most relevant dashboard for their role, improving UX and reducing confusion.
