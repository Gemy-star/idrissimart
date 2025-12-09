# Dynamic Cities - Quick Start Guide

## For Developers: Adding Dynamic Cities to Your Forms

### Step 1: Include the JavaScript
Add this to your template's extra scripts block:

```html
{% block extra_scripts %}
<script src="{% static 'js/dynamic-cities.js' %}"></script>
{% endblock %}
```

### Step 2: Ensure Form Fields Have Correct IDs
Make sure your country and city fields have these IDs:
- Country field: `id="id_country"`
- City field: `id="id_city"`

The JavaScript will automatically detect these fields and set up the dynamic loading.

### Step 3: That's It!
The system works automatically. The JavaScript will:
1. Detect the country field
2. Listen for changes
3. Load cities when country changes
4. Populate the city dropdown

## Example Form Template

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<form method="post">
    {% csrf_token %}

    <!-- Country field -->
    <div class="mb-3">
        <label for="id_country">{{ form.country.label }}</label>
        {{ form.country }}
    </div>

    <!-- City field - will be populated dynamically -->
    <div class="mb-3">
        <label for="id_city">{{ form.city.label }}</label>
        {{ form.city }}
    </div>

    <button type="submit" class="btn btn-primary">Submit</button>
</form>
{% endblock %}

{% block extra_scripts %}
<script src="{% static 'js/dynamic-cities.js' %}"></script>
{% endblock %}
```

## Manual Initialization

If you need to manually trigger city loading:

```javascript
// Load cities for a specific country
window.dynamicCities.loadCities(countryId, 'id_city', selectedCity);

// Re-initialize the listener
window.dynamicCities.setupCountryListener();
```

## Custom Field IDs

If your form uses different field IDs, you can manually initialize:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const countryField = document.getElementById('your_country_id');
    const cityField = document.getElementById('your_city_id');

    if (countryField && cityField) {
        countryField.addEventListener('change', function() {
            if (this.value) {
                window.dynamicCities.loadCities(this.value, 'your_city_id');
            }
        });

        // Load on page load if country selected
        if (countryField.value) {
            window.dynamicCities.loadCities(countryField.value, 'your_city_id', cityField.value);
        }
    }
});
```

## API Direct Usage

You can also use the API directly:

```javascript
fetch('/content/api/cities/SA/')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Cities:', data.cities);
            console.log('Country:', data.country_name);
        }
    });
```

## Supported Countries

- 🇸🇦 Saudi Arabia (SA) - 50 cities
- 🇪🇬 Egypt (EG) - 79 cities
- 🇦🇪 UAE (AE) - 45 cities
- 🇰🇼 Kuwait (KW) - 60 cities
- 🇶🇦 Qatar (QA) - 69 cities
- 🇧🇭 Bahrain (BH) - 67 cities

## Troubleshooting

### Cities not loading?
1. Check browser console for errors
2. Verify script is included: `<script src="{% static 'js/dynamic-cities.js' %}"></script>`
3. Ensure field IDs are correct
4. Test API directly: `/content/api/cities/SA/`

### Need to add more cities?
Edit and run the management command:
```bash
python manage.py populate_cities
```
