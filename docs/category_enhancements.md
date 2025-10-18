# Category Model Enhancements

## Overview

The Category model has been enhanced with company relationships and country-based filtering to support multi-country operations and company-managed categories.

## New Features

### 1. Company Relationship

- **Field**: `company` (ForeignKey to User)
- **Purpose**: Allow companies (merchants, service providers, educational institutions) to manage their own categories
- **Usage**: Categories can be owned and managed by specific companies
- **Access**: `category.company` or `user.managed_categories.all()`

### 2. Country Filtering

- **Single Country**: `country` (ForeignKey to Country)
- **Multiple Countries**: `countries` (ManyToManyField to Country)
- **Purpose**: Filter categories by country availability
- **Auto-filter**: Categories without country assignment are available in all countries

### 3. Subcategory Management

#### Instance Methods

**`get_full_name()`**

```python
category.get_full_name()
# Returns: "Parent Category > Subcategory"
```

**`get_all_subcategories()`**

```python
category.get_all_subcategories()
# Returns all subcategories recursively
```

**`is_subcategory()`**

```python
category.is_subcategory()
# Returns True if category has a parent
```

**`get_root_category()`**

```python
category.get_root_category()
# Returns the top-level parent category
```

#### Class Methods

**`get_by_country(country_code)`**

```python
Category.get_by_country('SA')
# Returns categories available in Saudi Arabia
```

**`get_by_section_and_country(section_type, country_code)`**

```python
Category.get_by_section_and_country('product', 'SA')
# Returns product categories in Saudi Arabia
```

**`get_by_company(company)`**

```python
Category.get_by_company(user)
# Returns categories managed by specific company
```

**`get_root_categories(section_type=None, country_code=None)`**

```python
Category.get_root_categories('service', 'AE')
# Returns root service categories in UAE
```

## Usage Examples

### 1. Get Categories for Current Country

```python
from django.shortcuts import render
from main.models import Category

def category_list(request):
    country_code = request.session.get('selected_country', 'SA')
    categories = Category.get_by_country(country_code)
    return render(request, 'categories.html', {'categories': categories})
```

### 2. Get Product Categories for Specific Country

```python
def product_categories(request):
    country = request.session.get('selected_country', 'SA')
    categories = Category.get_by_section_and_country('product', country)
    return render(request, 'products/categories.html', {'categories': categories})
```

### 3. Get Subcategories

```python
def category_detail(request, category_id):
    category = Category.objects.get(id=category_id)
    subcategories = category.subcategories.filter(is_active=True)
    all_subcats = category.get_all_subcategories()
    return render(request, 'category_detail.html', {
        'category': category,
        'subcategories': subcategories,
        'all_subcategories': all_subcats
    })
```

### 4. Company-Managed Categories

```python
def company_dashboard(request):
    company = request.user
    managed_categories = Category.get_by_company(company)
    return render(request, 'dashboard.html', {'categories': managed_categories})
```

### 5. Filter by Multiple Countries

```python
# Get categories available in multiple countries
from content.models import Country

gcc_countries = Country.objects.filter(code__in=['SA', 'AE', 'KW', 'QA', 'BH', 'OM'])
categories = Category.objects.filter(countries__in=gcc_countries).distinct()
```

## View Integration Example

### Context Processor Update

```python
# main/context_processors.py
from main.models import Category

def global_context(request):
    country_code = request.session.get('selected_country', 'SA')

    return {
        'product_categories': Category.get_by_section_and_country('product', country_code),
        'service_categories': Category.get_by_section_and_country('service', country_code),
        'job_categories': Category.get_by_section_and_country('job', country_code),
        'course_categories': Category.get_by_section_and_country('course', country_code),
        'classified_categories': Category.get_by_section_and_country('classified', country_code),
    }
```

## Admin Integration

### Admin Configuration

```python
# main/admin.py
from django.contrib import admin
from main.models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'section_type', 'parent', 'company', 'country', 'is_active']
    list_filter = ['section_type', 'is_active', 'country', 'company']
    search_fields = ['name', 'name_ar', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['countries']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is a company, show only their categories
        if not request.user.is_superuser and request.user.profile_type in ['merchant', 'service', 'educational']:
            qs = qs.filter(company=request.user)
        return qs
```

## Migration

Run the migration to apply these changes:

```bash
python manage.py migrate main
```

## Notes

- Categories without country assignment are available globally
- Categories can belong to one primary country and multiple additional countries
- Company relationship is optional - admin can manage global categories
- Subcategories inherit availability from parent categories
- All querysets automatically filter by country when using class methods
