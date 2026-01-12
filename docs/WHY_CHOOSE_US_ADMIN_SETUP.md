# Why Choose Us Section - Admin Configuration

## Overview
The "Why Choose Us" section on the homepage is now fully manageable through the Django admin interface. This allows non-technical users to easily update the features displayed on the homepage without modifying code.

## Features

### 1. Dynamic Content Management
- Add, edit, or remove features from the admin panel
- Control the order of features
- Enable/disable individual features
- Show/hide the entire section

### 2. Multilingual Support
- English and Arabic translations for all fields
- Automatic fallback to English if Arabic is not provided

### 3. Customizable Icons
- Use any FontAwesome icon for each feature
- Icons are displayed with the feature title

## Admin Interface

### Accessing the Admin
1. Go to Django Admin: `/admin/`
2. Navigate to **Content** → **Home Page Content**
3. Scroll to the **"Why Choose Us"** section

### Configuration Options

#### Section Settings
- **Show Why Choose Us**: Toggle to show/hide the entire section
- **Why Choose Us Title**: Main title for the section (e.g., "Why Choose Idrissimart?")
- **Why Choose Us Subtitle**: Optional subtitle text below the title

#### Managing Features
Features can be managed in two ways:

**Option 1: Inline Editor (Quick)**
- Edit features directly within the Home Page admin
- Add new features using the inline form at the bottom
- Fields: Title, Title (Arabic), Description (Arabic), Icon, Order, Active status

**Option 2: Detailed Editor**
- Go to **Content** → **Why Choose Us Features**
- Full editing interface for each feature
- Better for detailed content editing

### Feature Fields
- **Title**: Feature title in English (e.g., "High Accuracy")
- **Title (Arabic)**: Feature title in Arabic (e.g., "دقة عالية")
- **Description**: Feature description in English
- **Description (Arabic)**: Feature description in Arabic
- **Icon**: FontAwesome icon class (e.g., "fas fa-crosshairs", "fas fa-satellite")
- **Order**: Display order (lower numbers appear first)
- **Active**: Whether to display this feature

## Database Models

### HomePage Model
Located in: `content/site_config.py`

Fields:
```python
show_why_choose_us = BooleanField(default=True)
why_choose_us_title = CharField(max_length=200)
why_choose_us_title_ar = CharField(max_length=200)
why_choose_us_subtitle = TextField(blank=True)
why_choose_us_subtitle_ar = TextField(blank=True)
```

### WhyChooseUsFeature Model
Located in: `content/site_config.py`

Fields:
```python
home_page = ForeignKey(HomePage, related_name='why_choose_us_features')
title = CharField(max_length=200)
title_ar = CharField(max_length=200)
description = TextField()
description_ar = TextField()
icon = CharField(max_length=50, default='fas fa-check-circle')
order = IntegerField(default=0)
is_active = BooleanField(default=True)
```

## Template Integration

### Template Location
`templates/pages/home.html`

### Template Code
```django
{% if home_page.show_why_choose_us %}
<section class="features-section py-3" id="about">
    <div class="container">
        <h2 class="section-title text-white">{{ home_page.why_choose_us_title_ar|default:home_page.why_choose_us_title }}</h2>
        {% if home_page.why_choose_us_subtitle_ar or home_page.why_choose_us_subtitle %}
        <p class="text-center text-white mb-4">{{ home_page.why_choose_us_subtitle_ar|default:home_page.why_choose_us_subtitle }}</p>
        {% endif %}
        <div class="row g-4">
            {% for feature in home_page.why_choose_us_features.all %}
                {% if feature.is_active %}
                <div class="col-lg-3 col-md-6">
                    <div class="feature-box">
                        <div class="feature-icon">
                            <i class="{{ feature.icon }}"></i>
                        </div>
                        <h4 class="feature-title">{{ feature.title_ar|default:feature.title }}</h4>
                        <p>{{ feature.description_ar|default:feature.description }}</p>
                    </div>
                </div>
                {% endif %}
            {% endfor %}
        </div>
    </div>
</section>
{% endif %}
```

## Management Command

### populate_why_choose_us
A management command is provided to populate the section with default data.

**Usage:**
```bash
python manage.py populate_why_choose_us
```

**Default Features:**
1. High Accuracy (دقة عالية) - Icon: fas fa-crosshairs
2. Advanced Technology (تقنية متطورة) - Icon: fas fa-satellite
3. Certified Expertise (خبرة معتمدة) - Icon: fas fa-certificate
4. Fast Delivery (تسليم سريع) - Icon: fas fa-clock

**Location:** `content/management/commands/populate_why_choose_us.py`

## Migration

The feature was added via migration: `content/migrations/0028_homepage_show_why_choose_us_and_more.py`

## Icons Reference

### Common FontAwesome Icons
You can use any FontAwesome 5 icon. Here are some popular choices:

**General:**
- `fas fa-check-circle` - Check mark
- `fas fa-star` - Star
- `fas fa-award` - Award/Medal
- `fas fa-shield-alt` - Shield
- `fas fa-heart` - Heart

**Technology:**
- `fas fa-laptop-code` - Laptop with code
- `fas fa-microchip` - Microchip
- `fas fa-satellite` - Satellite
- `fas fa-cogs` - Gears/Settings
- `fas fa-database` - Database

**Business:**
- `fas fa-handshake` - Handshake
- `fas fa-certificate` - Certificate
- `fas fa-chart-line` - Chart/Growth
- `fas fa-users` - Users/Team
- `fas fa-briefcase` - Briefcase

**Speed/Time:**
- `fas fa-clock` - Clock
- `fas fa-bolt` - Lightning bolt
- `fas fa-shipping-fast` - Fast delivery
- `fas fa-stopwatch` - Stopwatch

**Quality:**
- `fas fa-thumbs-up` - Thumbs up
- `fas fa-medal` - Medal
- `fas fa-crosshairs` - Precision/Target
- `fas fa-gem` - Diamond/Quality

**Support:**
- `fas fa-headset` - Headset/Support
- `fas fa-comments` - Chat/Comments
- `fas fa-phone` - Phone
- `fas fa-envelope` - Email

## Best Practices

1. **Feature Count**: Keep 3-6 features for optimal visual balance
2. **Title Length**: Keep titles concise (2-5 words)
3. **Description Length**: Keep descriptions short (one sentence)
4. **Icon Selection**: Choose icons that visually represent the feature
5. **Order**: Arrange features in order of importance
6. **Active Status**: Use to temporarily hide features without deleting them

## Troubleshooting

### Features Not Showing
1. Check if `show_why_choose_us` is enabled in HomePage admin
2. Ensure features are marked as `is_active=True`
3. Verify features exist: Go to admin → Why Choose Us Features
4. Run the populate command if no features exist: `python manage.py populate_why_choose_us`

### Icons Not Displaying
1. Verify the icon class name is correct (e.g., "fas fa-star")
2. Ensure FontAwesome is loaded in the template (check base.html)
3. Try a different icon to test

### Wrong Language Showing
1. Check if the Arabic field has content
2. Template uses `title_ar|default:title` which falls back to English if Arabic is empty
3. Language is determined by the session/middleware settings

## Future Enhancements

Potential improvements:
- Add color customization per feature
- Add optional images/photos per feature
- Add link URL per feature
- Add animation effects options
- Export/import feature sets
