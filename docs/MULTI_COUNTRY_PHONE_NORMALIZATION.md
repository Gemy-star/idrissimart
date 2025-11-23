# Multi-Country Phone Number Normalization

## Overview
Updated the phone verification system to support phone number normalization for all 8 supported countries in the platform: Saudi Arabia (SA), UAE (AE), Egypt (EG), Kuwait (KW), Qatar (QA), Bahrain (BH), Oman (OM), and Jordan (JO).

## Changes Made

### 1. Backend Changes

#### `main/utils.py`
- **Added `get_country_phone_patterns(country_code)` function**
  - Returns country-specific configuration including:
    - `phone_code`: International dialing code (+966, +971, etc.)
    - `patterns`: List of regex patterns for validation
    - `normalize`: Lambda function for country-specific normalization

- **Updated `validate_phone_number(phone, country_code='SA')`**
  - Now accepts `country_code` parameter (defaults to 'SA')
  - Uses country-specific patterns from `get_country_phone_patterns()`
  - Supports different phone formats for each country:
    - **SA**: 05xxxxxxxx, 9665xxxxxxxx, +9665xxxxxxxx, 5xxxxxxxx
    - **AE**: 05xxxxxxxx, 9715xxxxxxxx, +9715xxxxxxxx, 5xxxxxxxx
    - **EG**: 01xxxxxxxxx, 201xxxxxxxxx, +201xxxxxxxxx, 1xxxxxxxxx
    - **KW**: xxxxxxxx (8 digits), 965xxxxxxxx, +965xxxxxxxx
    - **QA**: xxxxxxxx (8 digits), 974xxxxxxxx, +974xxxxxxxx
    - **BH**: xxxxxxxx (8 digits), 973xxxxxxxx, +973xxxxxxxx
    - **OM**: xxxxxxxx (8 digits), 968xxxxxxxx, +968xxxxxxxx
    - **JO**: 07xxxxxxxx, 9627xxxxxxxx, +9627xxxxxxxx, 7xxxxxxxx

- **Updated `normalize_phone_number(phone, country_code='SA')`**
  - Now accepts `country_code` parameter (defaults to 'SA')
  - Uses country-specific normalization logic
  - Returns international format with country code (+9665xxxxxxxx, +9715xxxxxxxx, etc.)
  - Includes fallback logic for edge cases

#### `main/auth_views.py`
- **Updated `RegisterView.get()`**
  - Now passes `countries` queryset to template
  - Fetches active countries ordered by `order` field

- **Updated `RegisterView.post()`**
  - Retrieves `country_code` from POST data (defaults to 'SA')
  - Passes `country_code` to `normalize_phone_number()`
  - Includes `countries` in context when rendering errors

- **Updated `send_phone_verification_code()`**
  - Now accepts `country_code` in JSON request body
  - Passes `country_code` to `validate_phone_number()` and `normalize_phone_number()`
  - Updated error message to indicate country-specific validation

- **Updated `verify_phone_code()`**
  - Now accepts `country_code` in JSON request body
  - Passes `country_code` to `normalize_phone_number()`

#### `main/forms.py`
- **Updated `RegistrationForm.clean_phone()`**
  - Retrieves `country_code` from form data (defaults to 'SA')
  - Passes `country_code` to `validate_phone_number()` and `normalize_phone_number()`
  - Updated error message: "رقم الجوال غير صحيح لهذه الدولة"

### 2. Frontend Changes

#### `templates/pages/register.html`
- **Added country selector dropdown**
  - Positioned before phone input field
  - Shows flag emoji, country name, and phone code
  - Default selection: Saudi Arabia (SA)
  - Calls `updatePhonePlaceholder()` on change
  - Required field

- **Added `updatePhonePlaceholder()` JavaScript function**
  - Updates phone input placeholder based on selected country
  - Country-specific placeholders:
    - **SA, AE**: "مثال: 0501234567"
    - **EG**: "مثال: 01012345678"
    - **KW, QA, BH, OM**: "مثال: 12345678"
    - **JO**: "مثال: 0791234567"

- **Updated `sendVerificationCode()` function**
  - Retrieves selected country code from dropdown
  - Sends `country_code` in AJAX request body

- **Updated `verifyPhoneCode()` function**
  - Retrieves selected country code from dropdown
  - Sends `country_code` in AJAX request body
  - Disables country selector after successful verification

## Phone Number Formats by Country

| Country | Code | Phone Code | Format Examples | Pattern |
|---------|------|------------|-----------------|---------|
| Saudi Arabia | SA | +966 | 0501234567, 9665xxxxxxxx | 05xxxxxxxx (10 digits local) |
| UAE | AE | +971 | 0501234567, 9715xxxxxxxx | 05xxxxxxxx (10 digits local) |
| Egypt | EG | +20 | 01012345678, 201xxxxxxxxx | 01xxxxxxxxx (11 digits local) |
| Kuwait | KW | +965 | 12345678, 965xxxxxxxx | xxxxxxxx (8 digits) |
| Qatar | QA | +974 | 12345678, 974xxxxxxxx | xxxxxxxx (8 digits) |
| Bahrain | BH | +973 | 12345678, 973xxxxxxxx | xxxxxxxx (8 digits) |
| Oman | OM | +968 | 12345678, 968xxxxxxxx | xxxxxxxx (8 digits) |
| Jordan | JO | +962 | 0791234567, 9627xxxxxxxx | 07xxxxxxxx (10 digits local) |

## Testing Checklist

- [ ] Test registration with Saudi phone number (05xxxxxxxx)
- [ ] Test registration with UAE phone number (05xxxxxxxx)
- [ ] Test registration with Egyptian phone number (01xxxxxxxxx)
- [ ] Test registration with Kuwait phone number (8 digits)
- [ ] Test registration with Qatar phone number (8 digits)
- [ ] Test registration with Bahrain phone number (8 digits)
- [ ] Test registration with Oman phone number (8 digits)
- [ ] Test registration with Jordan phone number (07xxxxxxxx)
- [ ] Verify phone placeholder updates when country changes
- [ ] Verify error message shows for invalid format
- [ ] Verify phone numbers are normalized correctly in database
- [ ] Test verification code send/verify flow for each country
- [ ] Verify duplicate phone detection works across all formats
- [ ] Test switching countries during registration

## Migration Notes

### Existing Phone Numbers
All existing phone numbers in the database should already be in normalized international format (+9665xxxxxxxx) from the previous implementation. No migration needed.

### Backward Compatibility
The system defaults to 'SA' (Saudi Arabia) if no country code is provided, maintaining backward compatibility with any existing code that doesn't pass the country_code parameter.

## Future Enhancements

1. **Production SMS Gateway Integration**
   - Currently logs to console
   - Need to integrate with SMS provider (e.g., Twilio, Nexmo, local provider)
   - May require different providers for different countries

2. **Country Auto-Detection**
   - Use IP geolocation to pre-select user's country
   - Improve user experience by reducing manual selection

3. **Phone Number Formatting Display**
   - Add JavaScript to format phone input as user types
   - Show country-specific formatting hints

4. **Admin Interface**
   - Add country filter for phone number management
   - Display phone numbers with country flags in admin

## Related Files

- `main/utils.py` - Phone validation and normalization utilities
- `main/auth_views.py` - Registration view and verification endpoints
- `main/forms.py` - Registration form with phone validation
- `templates/pages/register.html` - Registration template with country selector
- `content/models.py` - Country model with phone_code field

## Date
January 2025
