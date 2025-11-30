# Site Content Seeding Documentation

## Overview

The `seed_site_content` management command populates all singleton site configuration models with default bilingual content based on the static data previously in templates.

## Usage

### Basic Seeding (Skip Existing Content)

```bash
python manage.py seed_site_content
```

This will populate only empty fields, preserving any existing content.

### Reset All Content

```bash
python manage.py seed_site_content --reset
```

⚠️ **Warning**: This will overwrite ALL existing content with default values.

## Models Populated

### 1. HomePage
- **Hero Section**
  - Title (EN/AR)
  - Subtitle (EN/AR) - Rich text
  - Hero image
  - Button text and URL

- **Modal/Announcement**
  - Modal title (EN/AR)
  - Modal content (EN/AR) - Rich text
  - Modal image
  - Button text and URL

- **Feature Toggles**
  - Show featured categories
  - Show featured ads

### 2. AboutPage
- Title (EN/AR)
- Content (EN/AR) - Rich text
- Vision (EN/AR) - Rich text
- Mission (EN/AR) - Rich text
- Values (EN/AR) - Rich text with HTML grid structure
- Featured image

### 3. ContactPage
- Title (EN/AR)
- Description (EN/AR) - Rich text
- Office hours (EN/AR) - Rich text
- Map embed code (Google Maps iframe)
- Enable contact form toggle
- Notification email

### 4. TermsPage
- Title (EN/AR)
- Content (EN/AR) - Full terms and conditions with sections:
  - Introduction
  - Account Terms
  - User Obligations
  - Prohibited Activities
  - Payment Terms
  - Intellectual Property
  - Limitation of Liability
  - Changes to Terms
- Last updated (auto-managed)

### 5. PrivacyPage
- Title (EN/AR)
- Content (EN/AR) - Full privacy policy with sections:
  - Introduction
  - Information We Collect
  - How We Use Your Information
  - Data Security
  - Sharing Your Information
  - Your Rights
  - Cookies
  - Changes to This Policy
- Last updated (auto-managed)

### 6. SiteConfiguration
- Meta keywords (EN/AR)
- Footer text (EN/AR) - Rich text
- Copyright text

## Admin Interface

### Accessing Content

#### Via Custom Admin Dashboard
Navigate to: `/admin-dashboard/site-content/`

This shows cards for all content models with quick edit links:
- **HomePage**: Edit button → Custom form with CKEditor5
- **AboutPage**: Edit button → Custom form with CKEditor5
- **ContactPage**: Edit button → Custom form with CKEditor5
- **TermsPage**: Edit button → Django admin (SingletonModelAdmin)
- **PrivacyPage**: Edit button → Django admin (SingletonModelAdmin)

#### Via Django Admin
Navigate to: `/admin/content/`

All models are registered with `SingletonModelAdmin` which:
- Prevents creating multiple instances
- Auto-creates single instance if none exists
- Provides clean editing interface

## Content Structure

### Rich Text Fields
All content fields use CKEditor5 with support for:
- Bold, italic, underline formatting
- Headings (H1-H6)
- Lists (ordered/unordered)
- Links
- Images
- Code blocks
- Tables

### Bilingual Support
All text fields have both English (`field_name`) and Arabic (`field_name_ar`) versions.

Templates automatically select the correct version based on `LANGUAGE_CODE`:
```django
{% if LANGUAGE_CODE == 'ar' and page.title_ar %}
    {{ page.title_ar }}
{% elif page.title %}
    {{ page.title }}
{% else %}
    {% trans "Default Fallback Text" %}
{% endif %}
```

## Default Content Source

The seed command uses content extracted from:
- `templates/pages/home.html` → HomePage
- `templates/pages/about.html` → AboutPage
- `templates/pages/contact.html` → ContactPage
- `templates/pages/terms.html` → TermsPage
- `templates/pages/privacy.html` → PrivacyPage

## Template Integration

All frontend templates now use database content instead of hardcoded text:

### Home Page
```django
{{ home_page.hero_title_ar }}
{{ home_page.hero_subtitle_ar|safe }}
```

### About Page
```django
{{ about_page.title_ar }}
{{ about_page.content_ar|safe }}
{{ about_page.vision_ar|safe }}
{{ about_page.mission_ar|safe }}
{{ about_page.values_ar|safe }}
```

### Contact Page
```django
{{ contact_page.title_ar }}
{{ contact_page.description_ar|safe }}
{{ contact_page.office_hours_ar|safe }}
{{ contact_page.map_embed_code_ar|safe }}
```

### Terms Page
```django
{{ terms_page.title_ar }}
{{ terms_page.content_ar|safe }}
{{ terms_page.last_updated|date:"d F Y" }}
```

### Privacy Page
```django
{{ privacy_page.title_ar }}
{{ privacy_page.content_ar|safe }}
{{ privacy_page.last_updated|date:"d F Y" }}
```

## Workflow

### Initial Setup
1. Run migrations: `python manage.py migrate content`
2. Seed content: `python manage.py seed_site_content`
3. Access admin: Visit `/admin-dashboard/site-content/`
4. Edit content as needed

### Updating Content
1. Navigate to admin dashboard or Django admin
2. Edit the specific page content
3. Save changes
4. Content immediately appears on frontend (no cache clearing needed)

### Resetting to Defaults
```bash
python manage.py seed_site_content --reset
```

## Notes

- All rich text fields use `|safe` filter in templates to render HTML
- Images are optional and have fallbacks
- Last updated dates are auto-managed for Terms and Privacy pages
- Content is cached at the view level (solo instances are cached)
- No page refresh needed after editing content

## Related Files

- **Models**: `content/site_config.py`
- **Admin**: `content/admin.py`
- **Views**: `main/enhanced_views.py`, `main/views.py`
- **Templates**:
  - Admin: `templates/admin_dashboard/site_content.html`
  - Edit forms: `templates/admin_dashboard/edit_*.html`
  - Frontend: `templates/pages/*.html`
- **Management Command**: `content/management/commands/seed_site_content.py`
