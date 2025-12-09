# Dynamic City Selection System

## Overview
This document describes the implementation of a dynamic city selection system that displays cities based on the selected country in forms throughout the application.

## Implementation Details

### 1. Database Schema
**File**: `content/models.py`

Added a `cities` JSONField to the `Country` model to store city lists for each country:

```python
cities = models.JSONField(
    default=list, blank=True, verbose_name=_("المدن")
)
```

**Migration**: `content/migrations/0013_add_cities_to_country.py`

### 2. City Data Population
**File**: `content/management/commands/populate_cities.py`

Created a management command that populates comprehensive city lists for all supported countries:

**Countries Covered**:
- **Saudi Arabia (SA)**: 50 cities
- **Egypt (EG)**: 79 cities
- **UAE (AE)**: 45 cities
- **Kuwait (KW)**: 60 cities
- **Qatar (QA)**: 69 cities
- **Bahrain (BH)**: 67 cities

**Total**: 370 cities across 6 countries

**Usage**:
```bash
python manage.py populate_cities
```

### 3. API Endpoint
**File**: `content/views.py`

Created an AJAX endpoint to fetch cities for a specific country:

```python
def get_cities(request, country_code):
    """
    AJAX endpoint to get cities for a specific country
    Returns JSON with city list
    """
```

**URL**: `content/urls.py`
```python
path("api/cities/<str:country_code>/", get_cities, name="get_cities")
```

**Endpoint**: `/content/api/cities/{country_code}/`

**Response Format**:
```json
{
    "success": true,
    "cities": ["المدينة 1", "المدينة 2", ...],
    "country_name": "اسم الدولة"
}
```

### 4. Form Updates
**File**: `main/forms.py`

Updated the following forms to use dynamic city dropdowns:

#### ClassifiedAdForm
- Changed city widget from `TextInput` to `Select`
- Added dynamic city population in `__init__` method based on selected country
- City field is populated with cities from the selected country

#### SimpleEnhancedAdForm
- Same updates as ClassifiedAdForm
- Ensures consistent behavior across all ad creation forms

**Key Changes**:
```python
# City field widget changed to Select
"city": forms.Select(attrs={"class": "form-select", "id": "id_city"})

# Dynamic population in __init__
self.fields["city"] = forms.ChoiceField(
    required=True,
    label=_("المدينة"),
    widget=forms.Select(attrs={"class": "form-select", "id": "id_city"}),
    choices=[("", _("اختر المدينة"))]
)
```

### 5. JavaScript Implementation
**File**: `static/js/dynamic-cities.js`

Created a JavaScript module that:
- Monitors country selection changes
- Fetches cities via AJAX when country changes
- Dynamically populates the city dropdown
- Preserves selected city on form validation errors
- Automatically infers country codes from select options using emojis/text

**Key Features**:
- Automatic initialization on page load
- Loading states for better UX
- Error handling and fallbacks
- Country code inference from option text (supports Arabic/English/Emojis)
- Preserves user's city selection during form resubmission

**Usage**:
Include the script in templates that have country/city fields:
```html
<script src="{% static 'js/dynamic-cities.js' %}"></script>
```

## Form Field Behavior

### Initial Page Load
1. City dropdown is disabled if no country is selected
2. If a country is already selected (edit form), cities are loaded automatically
3. Previously selected city is preserved

### Country Selection
1. User selects a country
2. JavaScript detects the change
3. API call is made to `/content/api/cities/{country_code}/`
4. City dropdown is populated with relevant cities
5. City dropdown is enabled for selection

### Form Validation
If form validation fails:
1. Selected country is preserved
2. Cities for that country are loaded again
3. Previously selected city is re-selected

## Benefits

### User Experience
✅ Only shows relevant cities for the selected country
✅ Prevents manual city entry errors
✅ Consistent city names across the platform
✅ Faster form completion with dropdown selection
✅ Better data quality and standardization

### Development
✅ Easy to maintain city lists via management command
✅ Centralized city data in database
✅ Reusable across all forms with city fields
✅ Simple API for future mobile app integration
✅ No hardcoded city lists in templates or forms

### Data Quality
✅ Standardized city names
✅ No typos or variations in city spellings
✅ Better search and filter capabilities
✅ Improved analytics and reporting
✅ Consistent data across the platform

## Updating City Lists

To update or add cities for a country:

1. Edit `content/management/commands/populate_cities.py`
2. Update the city list for the desired country in the `cities_data` dictionary
3. Run the command:
   ```bash
   python manage.py populate_cities
   ```

## Future Enhancements

Potential improvements for the future:

1. **Admin Interface**: Add ability to manage cities via Django admin
2. **Multi-language Support**: Store city names in both Arabic and English
3. **City Hierarchy**: Support for regions/governorates → cities structure
4. **Auto-complete**: Add search/filter functionality for large city lists
5. **Geolocation**: Auto-select country/city based on user's IP address
6. **Postal Codes**: Add postal/zip code data for cities
7. **Caching**: Cache city lists in browser localStorage for better performance

## Testing

### Manual Testing Checklist
- [ ] Create new ad - verify city dropdown updates when country changes
- [ ] Edit existing ad - verify correct cities are shown
- [ ] Form validation error - verify city selection is preserved
- [ ] Different countries - verify each country shows its cities
- [ ] API endpoint - test direct access to `/content/api/cities/SA/`
- [ ] Empty country selection - verify city dropdown is disabled
- [ ] Browser console - check for JavaScript errors

### Files to Test
- Ad creation forms
- Ad edit forms
- User registration/profile forms (if they have city fields)
- Checkout/order forms
- Any custom forms with city fields

## Troubleshooting

### Cities not loading
1. Check browser console for JavaScript errors
2. Verify API endpoint is accessible: `/content/api/cities/SA/`
3. Ensure `populate_cities` command was run
4. Check if countries have `is_active=True`

### Wrong cities showing
1. Verify country code mapping in JavaScript
2. Check database - ensure country has cities populated
3. Clear browser cache

### Form submission issues
1. Ensure city value exists in the cities list for selected country
2. Check form validation in browser console
3. Verify city field is not still using old TextInput widget

## Migration Path

If you have existing data with free-text city entries:

1. Run migration to add cities field
2. Run `populate_cities` command
3. Update forms (already done)
4. Create a data migration script to map existing cities to standardized ones
5. Test thoroughly before deploying to production

## Support

For issues or questions:
- Check this documentation
- Review the code comments in the files mentioned above
- Check browser console for JavaScript errors
- Verify database has city data populated
