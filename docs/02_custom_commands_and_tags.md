# 🧰 Custom Commands & Template Tags

This document provides a guide on how to use the custom management commands and template tags created for the Idrissi Mart project.

---

## ⚙️ Custom Management Commands

These commands are run from your terminal in the project's root directory and help automate common development tasks like populating the database with test data.

### **1. `populate_users`**

This command creates a specified number of dummy users with realistic data using the Faker library.

-   **Purpose**: To quickly add test users to the database for development and testing.
-   **Default Password**: All created users will have the password `admin123456`.

#### Usage

```bash
python manage.py populate_users <number_of_users>
```

#### Example

To create 25 new users:

```bash
python manage.py populate_users 25
```

---

### **2. `populate_ads`**

This command populates the database with a specified number of dummy classified ads for a given country. It generates realistic, category-specific titles, descriptions, prices, and images.

-   **Purpose**: To create a rich set of test data for the classifieds section.
-   **Arguments**:
    -   `total`: The number of ads to create.
    -   `--country_code`: The country code (e.g., `EG`, `SA`) for which to create the ads. Defaults to `EG`.

#### Usage

```bash
python manage.py populate_ads <total> --country_code <CODE>
```

#### Example

To create 50 new ads for Egypt:

```bash
python manage.py populate_ads 50 --country_code EG
```

---

### **3. `clear_expired_features`**

This command cleans the database by deleting `AdFeature` records that have passed their `end_date`.

-   **Purpose**: To perform routine database maintenance and remove outdated records.
-   **Options**:
    -   `--dry-run`: Shows how many records would be deleted without actually deleting them.

#### Usage

To delete expired features:
```bash
python manage.py clear_expired_features
```

To perform a dry run:
```bash
python manage.py clear_expired_features --dry-run
```

---

## 🎨 Custom Template Tags & Filters

These tags and filters simplify rendering complex logic directly in your Django templates.

### **1. `user_avatar`**

-   **File**: `main/templatetags/user_tags.py`
-   **Purpose**: Renders a user's profile image or a default placeholder if no image exists.
-   **Usage**:
    1.  Load the tags in your template: `{% load user_tags %}`
    2.  Use the tag: `{% user_avatar user=<user_object> size=<size_in_px> css_class="<classes>" %}`
-   **Example**:
    ```django-html
    {% user_avatar user=ad.user size=50 css_class="rounded-circle me-3" %}
    ```

### **2. `phone_format`**

-   **File**: `main/templatetags/format_tags.py`
-   **Purpose**: Formats a phone number string into a more readable international format (e.g., `+966 50 123 4567`).
-   **Usage**:
    1.  Load the tags in your template: `{% load format_tags %}`
    2.  Apply the filter: `{{ user.phone|phone_format }}`
-   **Example**:
    ```django-html
    <a href="tel:{{ ad.user.phone|default_if_none:'' }}">{{ ad.user.phone|phone_format }}</a>
    ```

### **3. `get_currency`**

-   **File**: `main/templatetags/currency_tags.py`
-   **Purpose**: Returns the correct currency code (e.g., `EGP`, `SAR`) for an ad based on its country.
-   **Usage**:
    1.  Load the tags in your template: `{% load currency_tags %}`
    2.  Use the tag: `{% get_currency ad %}`
-   **Example**:
    ```django-html
    <span class="ad-price">{{ ad.price|floatformat:2 }} {% get_currency ad %}</span>
    ```
