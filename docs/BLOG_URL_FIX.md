# Blog URL Reverse Match Error Fix

## Problem
```
django.urls.exceptions.NoReverseMatch: Reverse for 'blog_detail' with keyword arguments
```

## Root Cause
The error occurs when Django tries to reverse the URL for `content:blog_detail` but cannot find the URL pattern. This happens on the production server but not locally.

## Diagnosis Results
Locally, all blog posts have valid slugs and `get_absolute_url()` works correctly:
- 11 blogs in database
- All slugs are valid
- All URLs reverse successfully: `/ar/content/<slug>/`

## Production Issues
The error suggests one of these issues on production:

1. **URL Configuration Not Loaded**
   - The `content.urls` might not be included in production `urls.py`
   - Or the app_name/namespace is missing

2. **Code Not Deployed**
   - The latest `urls.py` changes might not be on production server

3. **Application Not Restarted**
   - Gunicorn workers haven't loaded the new URL configuration

## Solution

### Step 1: Verify Production Files
Check that `/srv/idrissimart/idrissimart/urls.py` contains:

```python
urlpatterns += i18n_patterns(
    path("", include("main.urls", namespace="main")),
    path("super-admin/", admin.site.urls),
    path("content/", include("content.urls", namespace="content")),  # This line must exist
)
```

### Step 2: Verify content/urls.py
Check that `/srv/idrissimart/content/urls.py` contains:

```python
from django.urls import path, re_path
from .views import BlogDetailView, BlogLikeView, BlogListView

app_name = "content"  # This is critical!

urlpatterns = [
    path("", BlogListView.as_view(), name="blog_list"),
    re_path(r"^tag/(?P<tag_slug>[-\w]+)/$", BlogListView.as_view(), name="blog_list_by_tag"),
    path("<slug:slug>/like/", BlogLikeView.as_view(), name="blog_like"),
    path("<slug:slug>/", BlogDetailView.as_view(), name="blog_detail"),
]
```

### Step 3: Run Diagnostic Command on Production
```bash
cd /srv/idrissimart
source .venv/bin/activate
python manage.py check_blog_slugs
```

This will show:
- All blog slugs in database
- Whether get_absolute_url() works for each blog

### Step 4: Restart Gunicorn
```bash
sudo systemctl restart gunicorn
```

### Step 5: Check Application Logs
```bash
sudo journalctl -u gunicorn -n 100 --no-pager
```

## Testing
After applying fixes, test by:
1. Visiting the homepage: `https://idrissimarts.com/ar/`
2. Checking blog list: `https://idrissimarts.com/ar/content/`
3. Checking individual blog: `https://idrissimarts.com/ar/content/test/`

## Prevention
- Always restart Gunicorn after URL configuration changes
- Use `python manage.py check` before deployment
- Test URLs with: `python manage.py check_blog_slugs`
