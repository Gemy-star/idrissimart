# Z-Index Hierarchy Reference

This document defines the z-index scale used throughout the IdrissiMart application to ensure proper layering of UI elements.

## Z-Index Scale (from lowest to highest)

### Layer 0-9: Base Content
- **0-9**: Default content, page elements
- Used for: Regular page content, text, images

### Layer 10: Navigation Tabs
- **10**: Tab navigation (`.nav-tabs`, `.admin-tabs`)
- Used for: Tab navigation controls
- Files: `static/css/admin-dashboard.css`

### Layer 100-999: Interactive Elements
- **100-999**: Dropdowns, tooltips, popovers
- Used for: Bootstrap dropdowns, tooltips, and popovers

### Layer 1000: Fixed Headers
- **1000**: Fixed headers, sticky elements
- Used for: Sticky navigation, fixed headers

### Layer 10000: Slide Panels
- **10000**: Slide panels (categories, custom fields, etc.)
- Used for: Admin slide-out panels
- Files: Template-specific `<style>` blocks

### Layer 10050: Slide Panel Overlays
- **10050**: Slide panel overlays/backdrops
- Used for: Dark overlay behind slide panels

### Layer 10100: Admin Toggle
- **10100**: Admin sidebar toggle button
- Files: `templates/admin_dashboard/base.html`

### Layer 10200: Admin Overlay
- **10200**: Admin sidebar overlay
- Files: `templates/admin_dashboard/base.html`

### Layer 10300: Admin Sidebar
- **10300**: Admin sidebar panel
- Files: `templates/admin_dashboard/base.html`

### Layer 10500-10700: **GLOBAL MODALS (CRITICAL)**
- **10500**: Modal backdrops (`.modal-backdrop`)
- **10600**: Modal containers (`.modal`)
- **10700**: Modal dialogs (`.modal .modal-dialog`)
- **Purpose**: Ensures ALL modals appear above admin sidebar and other fixed elements
- **Files**: `static/css/admin-dashboard.css` (GLOBAL)
- **⚠️ DO NOT OVERRIDE**: These values are set globally and should NEVER be overridden in individual templates

### Layer 10800+: Notifications & Alerts
- **10800**: Toast notifications, alert boxes
- Used for: Success/error messages that should appear above everything
- Files: Template-specific notification functions

## Implementation Guidelines

### ✅ DO:
1. **Always use the global modal z-index** defined in `admin-dashboard.css`
2. **Reference this document** when adding new positioned elements
3. **Use z-index values within the defined ranges** for the element type
4. **Add comments** referencing this document when setting z-index

### ❌ DON'T:
1. **Never override modal z-index** in individual templates
2. **Don't use arbitrary z-index values** like 9999 or 99999
3. **Don't set z-index without checking** this hierarchy first
4. **Don't create z-index values** that conflict with existing layers

## Common Patterns

### Bootstrap Modals (Recommended)
```html
<!-- No custom z-index needed - uses global values -->
<div class="modal fade" id="myModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <!-- Content -->
        </div>
    </div>
</div>
```

### Custom Modals (If needed)
```css
/* Custom modal - should match global modal z-index */
.my-custom-modal {
    z-index: 10600; /* Same as global .modal */
}

.my-custom-modal-backdrop {
    z-index: 10500; /* Same as global .modal-backdrop */
}
```

### Notifications
```javascript
// Notifications should appear above modals
box.style.zIndex = '10800';
```

## Files to Update When Changing Z-Index

If you need to adjust the z-index hierarchy:

1. **Update this document** with the new values
2. **Update `static/css/admin-dashboard.css`** (Global modal styles)
3. **Update `templates/admin_dashboard/base.html`** (Admin sidebar values)
4. **Search and update** any template-specific overrides
5. **Test all modals** across the application

## Testing Checklist

When making z-index changes, test:

- [ ] Bootstrap modals on all admin pages
- [ ] Admin sidebar opens/closes correctly
- [ ] Slide panels (categories, custom fields)
- [ ] Dropdown menus in modals
- [ ] Toast notifications
- [ ] Mobile responsive behavior

## Current Implementation

### Global CSS (`static/css/admin-dashboard.css`)
```css
/* Modal backdrop */
.modal-backdrop {
    z-index: 10500 !important;
}

/* Modal container */
.modal {
    z-index: 10600 !important;
}

/* Modal dialog */
.modal .modal-dialog {
    z-index: 10700 !important;
}
```

### Admin Base Template (`templates/admin_dashboard/base.html`)
```css
.admin-sidebar-toggle { z-index: 10100; }
.admin-sidebar-overlay { z-index: 10200; }
.admin-sidebar { z-index: 10300; }
```

## Troubleshooting

### Modal appears behind sidebar
- **Cause**: Custom z-index override in template
- **Solution**: Remove the override, use global values

### Element not visible
- **Cause**: z-index too low for its purpose
- **Solution**: Check this hierarchy and use appropriate layer

### Conflicting layers
- **Cause**: Multiple elements with same z-index
- **Solution**: Use the defined ranges to separate layers

## Version History

- **2025-11-19**: Initial hierarchy established
  - Defined 10500-10700 range for global modals
  - Standardized admin sidebar values (10100-10300)
  - Documented all z-index layers
