# Admin Country Management System

## Overview

Complete CRUD (Create, Read, Update, Delete) interface for managing countries in the admin dashboard with modern UX patterns including Bootstrap modals, toast notifications, and theme-compatible styling.

## Implementation Date
**Added:** December 2024

## Features

### 1. **Country CRUD Operations**
- ✅ Create new countries with full details
- ✅ Edit existing countries
- ✅ Delete countries (with validation)
- ✅ Toggle active/inactive status
- ✅ Reorder countries
- ✅ Populate cities from management command

### 2. **Modal Dialogs**
- **Add/Edit Modal**: Bootstrap 5 modal with form validation
- **Delete Confirmation Modal**: Red-themed danger modal with warning
- Smooth animations and theme-compatible styling

### 3. **Toast Notifications**
- Success messages (green)
- Error messages (red)
- Info messages (blue)
- Warning messages (yellow)
- Auto-dismiss after 5 seconds
- Icon indicators for each type

### 4. **Theme Compatibility**
- CSS variables for light/dark theme support
- Automatic theme switching with `[data-theme='dark']`
- Consistent with existing admin dashboard styling

### 5. **User Experience**
- Real-time form validation
- JSON validation for cities field
- Auto-uppercase for country codes
- Tooltips for action buttons
- Responsive table design
- Empty state when no countries exist

## Files Modified/Created

### Backend Files

#### 1. **main/views.py**
Added 6 new view functions (Lines 2740-2891):

```python
# Class-based view for list page
class AdminCountriesView(SuperadminRequiredMixin, TemplateView):
    template_name = "admin_dashboard/countries.html"
    # Returns all countries ordered by order, name

# AJAX endpoints
@superadmin_required
def admin_country_get(request, country_id):
    # Returns country data as JSON for editing

@superadmin_required
@require_http_methods(["POST"])
def admin_country_save(request):
    # Create or update country, validates code uniqueness

@superadmin_required
@require_http_methods(["POST"])
def admin_country_delete(request, country_id):
    # Deletes country after checking if used in ads

@superadmin_required
@require_http_methods(["POST"])
def admin_country_toggle_active(request, country_id):
    # Toggles is_active status

@superadmin_required
@require_http_methods(["POST"])
def admin_country_populate_cities(request, country_id):
    # Runs populate_cities management command for specific country
```

**Key Validation:**
- Checks if country code already exists (on save)
- Prevents deletion if country has associated ads
- Validates JSON format for cities field
- Superadmin access only

#### 2. **main/urls.py**
Added 6 URL patterns (after line 909):

```python
# Admin Countries Management
path("admin/countries/", AdminCountriesView.as_view(), name="admin_countries"),
path("admin/countries/<int:country_id>/", admin_country_get, name="admin_country_get"),
path("admin/countries/save/", admin_country_save, name="admin_country_save"),
path("admin/countries/<int:country_id>/delete/", admin_country_delete, name="admin_country_delete"),
path("admin/countries/<int:country_id>/toggle-active/", admin_country_toggle_active, name="admin_country_toggle_active"),
path("admin/countries/<int:country_id>/populate-cities/", admin_country_populate_cities, name="admin_country_populate_cities"),
```

### Frontend Files

#### 3. **templates/admin_dashboard/countries.html** (NEW)
Complete admin interface with:

**Template Structure:**
- Extends `admin_dashboard/base.html`
- Uses Django i18n for translations
- Includes modals block for proper z-index

**CSS Variables (Theme-aware):**
```css
:root {
    --countries-modal-bg: #ffffff;
    --countries-text-primary: #1a202c;
    --countries-accent: #4b315e;
    /* ... more variables */
}

[data-theme='dark'] {
    --countries-modal-bg: #2d3748;
    --countries-text-primary: #f7fafc;
    --countries-accent: #a78bbd;
    /* ... dark theme overrides */
}
```

**Main Features:**
1. **Countries Table**: Displays all countries with flag, name, code, phone code, currency, cities count, status
2. **Action Buttons**: Edit, Toggle Active, Populate Cities, Delete
3. **Add/Edit Modal**: Full form with bilingual fields, cities JSON textarea, validation
4. **Delete Confirmation**: Separate modal with danger styling
5. **Toast Notifications**: Auto-generated at bottom-right corner

**JavaScript Functions:**
- `showToast(message, type, duration)` - Display notification
- `openAddModal()` - Show modal for new country
- `openEditModal(countryId)` - Fetch and show country data for editing
- `openDeleteModal(countryId, countryName)` - Show delete confirmation
- `saveCountry()` - AJAX POST to save/update
- `deleteCountry()` - AJAX POST to delete
- `toggleActive(countryId)` - AJAX POST to toggle status
- `populateCities(countryId)` - AJAX POST to run populate command

#### 4. **templates/admin_dashboard/partials/_admin_nav.html**
Added navigation link (after Categories):

```html
<a href="{% url 'main:admin_countries' %}" class="nav-link-item {% if active_nav == 'countries' %}active{% endif %}">
    <i class="fas fa-globe"></i>
    <span>{% trans "الدول" %}</span>
</a>
```

## API Endpoints

### 1. GET /admin/countries/
**Description**: List all countries (HTML page)
**Access**: Superadmin only
**Returns**: Rendered template with countries context

### 2. GET /admin/countries/<id>/
**Description**: Get single country data
**Access**: Superadmin only
**Returns**:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "السعودية",
        "name_en": "Saudi Arabia",
        "code": "SA",
        "phone_code": "+966",
        "currency": "SAR",
        "flag_emoji": "🇸🇦",
        "cities": ["الرياض", "جدة", "مكة المكرمة"],
        "is_active": true,
        "order": 0
    }
}
```

### 3. POST /admin/countries/save/
**Description**: Create or update country
**Access**: Superadmin only
**Request Body**:
```json
{
    "id": 1,  // Optional, omit for create
    "name": "السعودية",
    "name_en": "Saudi Arabia",
    "code": "SA",
    "phone_code": "+966",
    "currency": "SAR",
    "flag_emoji": "🇸🇦",
    "cities": ["الرياض", "جدة"],
    "is_active": true,
    "order": 0
}
```
**Returns**:
```json
{
    "success": true,
    "message": "تم حفظ الدولة بنجاح"
}
```

**Validation:**
- Code must be unique (unless updating same country)
- Cities must be valid JSON array

### 4. POST /admin/countries/<id>/delete/
**Description**: Delete country
**Access**: Superadmin only
**Returns**:
```json
{
    "success": true,
    "message": "تم حذف الدولة بنجاح"
}
```

**Error Response** (if country has ads):
```json
{
    "success": false,
    "message": "لا يمكن حذف الدولة لوجود إعلانات مرتبطة بها (5 إعلانات)"
}
```

### 5. POST /admin/countries/<id>/toggle-active/
**Description**: Toggle country active status
**Access**: Superadmin only
**Returns**:
```json
{
    "success": true,
    "message": "تم تغيير حالة الدولة بنجاح",
    "is_active": true
}
```

### 6. POST /admin/countries/<id>/populate-cities/
**Description**: Run populate_cities command for specific country
**Access**: Superadmin only
**Returns**:
```json
{
    "success": true,
    "message": "تم تحميل 50 مدينة للسعودية"
}
```

## Database Schema

Uses existing `Country` model from `content.models`:

```python
class Country(models.Model):
    name = models.CharField(max_length=100)  # Arabic name
    name_en = models.CharField(max_length=100)  # English name
    code = models.CharField(max_length=3, unique=True)  # ISO code
    phone_code = models.CharField(max_length=10)
    currency = models.CharField(max_length=10)
    flag_emoji = models.CharField(max_length=10, blank=True)
    cities = models.JSONField(default=list, blank=True)  # JSON array
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
```

## Usage Guide

### For Admins

#### Adding a New Country

1. Navigate to **Admin Dashboard → الدول (Countries)**
2. Click **"إضافة دولة جديدة"** (Add New Country)
3. Fill in the form:
   - **Arabic Name**: اسم الدولة بالعربي
   - **English Name**: Country name in English
   - **Code**: 2-letter ISO code (auto-uppercase)
   - **Phone Code**: e.g., +966
   - **Currency**: 3-letter code (auto-uppercase)
   - **Flag Emoji**: 🇸🇦 (optional)
   - **Order**: Sorting order (default: 0)
   - **Cities**: JSON array, e.g., `["الرياض", "جدة"]` (optional)
   - **Active**: Check to make country visible
4. Click **"حفظ"** (Save)
5. Success toast appears, page reloads

#### Editing a Country

1. Find the country in the table
2. Click the **Edit** button (pencil icon)
3. Modal opens with pre-filled data
4. Make changes
5. Click **"حفظ"** (Save)
6. Success toast appears, page reloads

#### Deleting a Country

1. Find the country in the table
2. Click the **Delete** button (trash icon)
3. Confirmation modal appears with country name
4. Click **"حذف"** (Delete) to confirm
5. If country has no ads: deleted successfully
6. If country has ads: error message shows count

#### Toggle Active/Inactive

1. Find the country in the table
2. Click the **Toggle** button (check/ban icon)
3. Status changes immediately
4. Success toast appears, page reloads

#### Populate Cities

1. Find a country in the table
2. Click the **Sync** button (refresh icon)
3. Runs management command to add predefined cities
4. Success toast shows number of cities added
5. Page reloads with updated cities count

### For Developers

#### Adding New Countries Programmatically

```python
from content.models import Country

country = Country.objects.create(
    name="السعودية",
    name_en="Saudi Arabia",
    code="SA",
    phone_code="+966",
    currency="SAR",
    flag_emoji="🇸🇦",
    cities=["الرياض", "جدة", "مكة المكرمة"],
    is_active=True,
    order=0
)
```

#### Extending the System

To add new fields:

1. Update `Country` model in `content/models.py`
2. Create migration: `python manage.py makemigrations`
3. Run migration: `python manage.py migrate`
4. Update `admin_country_save` view to handle new field
5. Update `admin_country_get` to return new field
6. Add input field to `countries.html` modal
7. Update JavaScript `saveCountry()` to send new field

## Security

### Access Control
- All views protected with `@superadmin_required` decorator
- Class view uses `SuperadminRequiredMixin`
- Only users with `is_staff=True` and `is_superuser=True` can access

### CSRF Protection
- All POST requests require CSRF token
- JavaScript uses `getCookie('csrftoken')` helper
- Token sent in `X-CSRFToken` header

### Input Validation
- Country code uniqueness check
- JSON validation for cities field
- HTTP method restrictions (`@require_http_methods(["POST"])`)
- Foreign key integrity (prevent delete if country has ads)

## Styling Guide

### Theme Variables

Both light and dark themes supported via CSS variables:

**Light Theme:**
- Background: `#ffffff`
- Text: `#1a202c`
- Accent: `#4b315e` (purple)
- Borders: `#f3f4f6`

**Dark Theme:**
- Background: `#2d3748`
- Text: `#f7fafc`
- Accent: `#a78bbd` (light purple)
- Borders: `rgba(255, 255, 255, 0.1)`

### Button Colors
- **Primary**: Purple accent color
- **Success**: Green (#28a745)
- **Danger**: Red (#dc3545)
- **Warning**: Yellow (#ffc107)
- **Info**: Blue (#17a2b8)
- **Secondary**: Gray (#6c757d)

### Modal Styling
- Border radius: `16px`
- Box shadow: `0 20px 60px` with theme-aware opacity
- Padding: `1.5rem`
- Smooth fade-in animation

### Toast Styling
- Position: Top-right corner
- Z-index: `11000`
- Border radius: `12px`
- Auto-dismiss: 5 seconds
- Icons: Font Awesome (check-circle, exclamation-circle, info-circle)

## Troubleshooting

### Issue: Modal doesn't close after save
**Solution**: Check that `countryModal.hide()` is called in `saveCountry()` success callback

### Issue: Countries not loading
**Solution**:
1. Check superadmin permissions
2. Verify URL pattern in `urls.py`
3. Check `AdminCountriesView` returns correct context

### Issue: Delete fails with "Country has ads"
**Solution**: This is expected behavior. Either:
1. Delete/reassign all ads from this country first
2. Or keep the country but set `is_active=False`

### Issue: Cities JSON validation error
**Solution**: Ensure cities are in valid JSON array format:
```json
["الرياض", "جدة", "مكة المكرمة"]
```
Not:
```
الرياض, جدة, مكة المكرمة
```

### Issue: Toast notifications don't appear
**Solution**:
1. Check that `toastContainer` div exists in template
2. Verify Bootstrap is loaded
3. Check browser console for JavaScript errors

## Future Enhancements

### Potential Features
- [ ] Bulk import countries from CSV
- [ ] Drag-and-drop reordering
- [ ] Country flag image upload (instead of emoji)
- [ ] Map integration for country selection
- [ ] Multi-language support (more than Arabic/English)
- [ ] Country statistics (ad count, user count)
- [ ] Export countries to JSON/CSV
- [ ] Audit log for country changes

### Performance Optimizations
- [ ] Pagination for large country lists
- [ ] AJAX table refresh (without full page reload)
- [ ] Debounced search filter
- [ ] Lazy loading for cities dropdown

## Related Documentation

- [Dynamic City Selection System](DYNAMIC_CITIES_QUICK_START.md)
- [Country Filtering Implementation](country_filtering_implementation.md)
- [Admin Dashboard Updates](ADMIN_DASHBOARD_UPDATES.md)
- [Multi-Country Phone Normalization](MULTI_COUNTRY_PHONE_NORMALIZATION.md)

## Testing Checklist

### Manual Testing
- [ ] Create new country with all fields
- [ ] Create country with minimal fields (only required)
- [ ] Edit existing country
- [ ] Delete country with no ads
- [ ] Try to delete country with ads (should fail)
- [ ] Toggle active/inactive status
- [ ] Populate cities for existing country
- [ ] Test JSON validation (valid and invalid)
- [ ] Test duplicate code prevention
- [ ] Verify theme switching (light/dark)
- [ ] Check responsive design on mobile
- [ ] Verify toast notifications appear and dismiss
- [ ] Test navigation tab highlighting

### Browser Testing
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (iOS/Android)

## Conclusion

This implementation provides a complete, production-ready country management interface for the admin dashboard with:

✅ Full CRUD operations
✅ Modern UX with modals and toasts
✅ Theme-compatible styling
✅ Security and validation
✅ Comprehensive documentation
✅ Bilingual support (Arabic/English)

The system integrates seamlessly with the existing admin dashboard and follows established patterns for consistency and maintainability.
