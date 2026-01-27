# Country Selection Synchronization Feature

## Overview
This feature ensures that when a user selects a country in the ad creation form, the selection is automatically synchronized with:
1. The header country dropdown display
2. The user's session (server-side)
3. The browser's localStorage (client-side)

## Implementation Details

### 1. Modified Files

#### `templates/classifieds/ad_form.html`
- **Added helper function** `getCookie()` to retrieve CSRF token for API calls
- **Added sync function** `syncCountryToHeader(countryCode)` that:
  - Makes POST request to `/api/set-country/` endpoint
  - Saves country to session on the server
  - Updates localStorage with the selected country code
  - Calls the global `window.updateCountryUI()` to update header display

- **Enhanced country select event handler** (around line 2094):
  - Created country ID to code mapping using Django template loop
  - Extracts country code when user selects a country
  - Calls `syncCountryToHeader()` to synchronize the selection
  - Continues with existing city loading functionality

#### `static/js/main.js`
- **Made country data global**:
  - `window.countryFlags` - Emoji flags for each country
  - `window.countryNames` - Arabic names for each country

- **Made updateCountryUI global**:
  - Changed from local function to `window.updateCountryUI()`
  - Updates desktop dropdown current country display
  - Updates mobile country display
  - Updates active states and check icons
  - Can now be called from any page (including ad form)

- **Updated references**:
  - Changed `countryFlags[code]` to `window.countryFlags[code]`
  - Changed `countryNames[code]` to `window.countryNames[code]`
  - Changed `updateUI(code)` to `window.updateCountryUI(code)` in handleCountryChange

### 2. Flow Diagram

```
User selects country in ad form
         ↓
Country change event triggered
         ↓
Extract country ID from select value
         ↓
Map country ID to country code (SA, EG, etc.)
         ↓
Call syncCountryToHeader(countryCode)
         ↓
    ┌────────────────────┐
    │  Async API Call    │
    │  POST /api/set-    │
    │  country/          │
    └────────────────────┘
         ↓
    ┌────────────────────┐
    │  Server saves to   │
    │  session           │
    └────────────────────┘
         ↓
    ┌────────────────────┐
    │  Update localStorage│
    │  selectedCountry   │
    └────────────────────┘
         ↓
    ┌────────────────────┐
    │  Call              │
    │  updateCountryUI() │
    └────────────────────┘
         ↓
Header dropdown updates visually
```

### 3. API Endpoint

**Endpoint:** `/api/set-country/`
**Method:** POST
**Parameters:**
- `country_code` (required): Two-letter country code (e.g., 'SA', 'EG', 'AE')

**Response:**
```json
{
  "success": true,
  "message": "تم تغيير البلد بنجاح"
}
```

**Implementation in views.py:**
```python
@require_http_methods(["POST"])
def set_country(request):
    country_code = request.POST.get('country_code')
    if country_code:
        request.session['selected_country'] = country_code
        return JsonResponse({'success': True, 'message': 'تم تغيير البلد بنجاح'})
    return JsonResponse({'success': False, 'message': 'خطأ في البيانات'})
```

### 4. Country Code Mapping

The ad form uses country database IDs (integer values), while the header uses country codes (2-letter strings). The mapping is dynamically generated in the template:

```javascript
const countryData = {
    {% for country in countries %}
    '{{ country.id }}': '{{ country.code }}',
    {% endfor %}
};
```

Example output:
```javascript
const countryData = {
    '1': 'SA',
    '2': 'EG',
    '3': 'AE',
    // ...
};
```

### 5. Benefits

1. **Consistent User Experience**: Country selection is consistent across the entire site
2. **Session Persistence**: Selected country persists across page refreshes via session
3. **Local Storage Backup**: Client-side storage provides instant feedback
4. **Visual Feedback**: Header immediately reflects the selection without page reload
5. **Multi-step Forms**: Ad creation maintains country context throughout the process

### 6. Testing Instructions

1. **Navigate to Ad Creation Form**:
   - Go to `/classifieds/new/` or edit existing ad

2. **Select a Country**:
   - In Step 1, select a different country from the dropdown

3. **Verify Synchronization**:
   - Check header country dropdown - should update immediately
   - Open browser console and check: `localStorage.getItem('selectedCountry')`
   - Navigate to another page - country should persist

4. **Test Session Persistence**:
   - Refresh the page
   - Check if selected country is still active in header
   - Create a new ad - country should default to your selection

### 7. Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Uses Fetch API (supported in all modern browsers)
- Uses localStorage (supported in all modern browsers)

### 8. Error Handling

- If API call fails, error is logged to console
- User can continue using the form (non-blocking)
- City loading continues independently
- Graceful degradation if `updateCountryUI` function not available

### 9. Future Enhancements

Possible improvements:
- Add loading indicator during sync
- Show success/error toast notification
- Retry logic for failed API calls
- Sync on page load (read from localStorage and set in header)
- Batch multiple country changes if user changes rapidly

## Code Locations

- **Ad Form Template**: `templates/classifieds/ad_form.html` (lines 1277-1330, 2094-2130)
- **Main JavaScript**: `static/js/main.js` (lines 230-290)
- **Backend View**: `main/views.py` (set_country function)
- **URL Configuration**: `main/urls.py` or `content/urls.py` (api/set-country/ route)

## Related Documentation

- [AD_FEATURES_SYSTEM.md](AD_FEATURES_SYSTEM.md)
- [ADMIN_COUNTRIES_MANAGEMENT.md](ADMIN_COUNTRIES_MANAGEMENT.md)
- [02_ajax.md](02_ajax.md)
