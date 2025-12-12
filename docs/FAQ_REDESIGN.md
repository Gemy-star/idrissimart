# FAQ Page Redesign Documentation

## Overview
The FAQ page has been redesigned with a modern sidebar navigation layout and CKEditor5 rich text support for better content management.

## Features Implemented

### 1. Sidebar Navigation Layout

#### Design Pattern
- **Sidebar**: Fixed category navigation on the left (3 columns on large screens)
- **Content Area**: Dynamic FAQ content on the right (9 columns on large screens)
- **Sticky Navigation**: Sidebar stays visible while scrolling (position: sticky, top: 100px)

#### Visual Elements
- **Category Icons**: FontAwesome icons for each category
- **Active States**: Gradient background for selected category
- **Animations**: FadeIn animation when switching categories
- **Responsive**: Sidebar stacks on top for mobile devices

### 2. Category Switching Functionality

#### JavaScript Implementation
```javascript
function showCategory(event, categoryId) {
    // Hide all categories
    // Remove all active states
    // Show selected category
    // Add active state to clicked link
    // Auto-scroll on mobile
}
```

#### User Experience
- Click category in sidebar to view its FAQs
- First category shown by default
- Smooth transitions between categories
- Auto-scroll to content on mobile devices

### 3. CKEditor5 Rich Text Support

#### Model Updates
- **FAQ Model**: Changed `answer` and `answer_ar` from TextField to CKEditor5Field
- **Configuration**: Using 'extends' config for full feature set
- **Migration**: `0029_faq_ckeditor5_fields.py`

#### Admin Interface
- **Create FAQ**: CKEditor5 for both Arabic and English answers
- **Edit FAQ**: CKEditor5 with existing content
- **Toolbar**: Heading, bold, italic, link, lists, blockquote, table, undo/redo

#### Frontend Display
- Answers rendered with `{{ faq.answer_ar|safe }}` to preserve HTML formatting
- Rich text content: headings, bold, italic, links, lists, tables, blockquotes

## File Changes

### Templates

#### `templates/pages/faq.html`
**CSS Additions:**
```css
.faq-sidebar {
    background: white;
    border-radius: 15px;
    padding: 25px;
    position: sticky;
    top: 100px;
}

.faq-category-nav-item a.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.faq-category-section {
    display: none;
}

.faq-category-section.active {
    display: block;
    animation: fadeIn 0.3s ease-in;
}
```

**HTML Structure:**
```html
<div class="row">
    <!-- Sidebar -->
    <div class="col-lg-3 col-md-4">
        <div class="faq-sidebar">
            <ul class="faq-category-nav">
                <!-- Category links -->
            </ul>
        </div>
    </div>

    <!-- Content Area -->
    <div class="col-lg-9 col-md-8">
        <div class="faq-content-area">
            <!-- FAQ sections by category -->
        </div>
    </div>
</div>
```

**JavaScript:**
- Category switching function
- Active state management
- Mobile auto-scroll

#### `templates/admin_dashboard/faqs/create.html`
- Added CKEditor5 CDN script
- Added `ckeditor5` class to textareas
- Initialized CKEditor for Arabic (ar) and English (en)
- Custom toolbar configuration

#### `templates/admin_dashboard/faqs/edit.html`
- Same CKEditor5 integration as create template
- Preserves existing content in editor

### Models

#### `main/models.py`
**Before:**
```python
answer = models.TextField(verbose_name=_("الإجابة - Answer"))
answer_ar = models.TextField(verbose_name=_("الإجابة بالعربية"), blank=True)
```

**After:**
```python
answer = CKEditor5Field(
    verbose_name=_("الإجابة - Answer"),
    config_name='extends',
    blank=True
)
answer_ar = CKEditor5Field(
    verbose_name=_("الإجابة بالعربية"),
    config_name='extends',
    blank=True
)
```

### Migrations
- **File**: `main/migrations/0029_faq_ckeditor5_fields.py`
- **Changes**: Altered `answer` and `answer_ar` fields to CKEditor5Field

## Responsive Design

### Desktop (≥992px)
- Sidebar: 3 columns, sticky position
- Content: 9 columns
- Category icons: 35px

### Tablet (768px - 991px)
- Sidebar: 4 columns
- Content: 8 columns
- Icons slightly smaller

### Mobile (<768px)
- Sidebar stacks on top
- Full width layout
- Larger touch targets (45px icons)
- Auto-scroll to content when category selected

## Dark Mode Support

All components have dark mode styles:
```css
body.dark-mode .faq-sidebar {
    background: #2d3748;
    border-color: #4a5568;
}

body.dark-mode .faq-category-link {
    color: #e2e8f0;
}
```

## CKEditor5 Configuration

### Features Enabled
- **Headings**: H1, H2, H3, H4, H5, H6, Paragraph
- **Text Formatting**: Bold, Italic
- **Links**: Insert/edit hyperlinks
- **Lists**: Bulleted and numbered lists
- **Block Elements**: Blockquote
- **Tables**: Insert and edit tables
- **Undo/Redo**: Full history support

### Language Support
- **Arabic Editor**: `language: 'ar'` for RTL support
- **English Editor**: `language: 'en'` for LTR

### CDN Version
- Using CKEditor 5 Classic Editor v40.0.0
- Loaded from: `https://cdn.ckeditor.com/ckeditor5/40.0.0/classic/ckeditor.js`

## Usage Examples

### Admin - Creating FAQ with Rich Text

1. Navigate to Admin Dashboard → FAQs → Create New
2. Fill in question (Arabic/English)
3. Use CKEditor toolbar to format answer:
   - Add headings for structure
   - Bold/italic important text
   - Add links to resources
   - Create lists for steps
   - Insert tables for comparisons
4. Select category, order, and status
5. Click Save

### Frontend - Browsing FAQs

1. Visit FAQ page
2. See categories in left sidebar
3. Click category to view its FAQs
4. First category shown by default
5. FAQs displayed in accordion format
6. Rich text answers with proper formatting

## Performance Considerations

### Sticky Sidebar
- `position: sticky` for better performance than fixed
- No JavaScript scroll listeners needed
- Smooth native scrolling

### Category Switching
- CSS display toggle (no DOM manipulation)
- Lightweight animation (opacity/transform)
- Event delegation possible for future enhancements

### CKEditor Loading
- CDN delivery for fast loading
- Lazy initialization on DOMContentLoaded
- Minimal toolbar for faster startup

## Future Enhancements

### Potential Features
1. Search within FAQs
2. Print-friendly version
3. FAQ analytics (popular questions)
4. User feedback (helpful/not helpful)
5. Share individual FAQ
6. Jump to specific FAQ from sidebar
7. Collapsible sidebar on mobile
8. FAQ categories as dropdown on mobile

### SEO Improvements
1. Schema.org FAQ markup
2. Individual FAQ permalinks
3. FAQ breadcrumbs
4. Meta descriptions per category

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **CKEditor5**: Requires modern JavaScript (ES6+)
- **CSS Features**: Flexbox, Grid, CSS Variables, position: sticky
- **Fallbacks**: Graceful degradation for older browsers

## Accessibility

### Implemented
- Semantic HTML structure (`<nav>`, `<section>`, `<article>`)
- ARIA labels for navigation
- Keyboard navigation support
- Focus indicators on links
- High contrast in dark mode

### To Consider
- Screen reader announcements for category changes
- Skip navigation link
- Keyboard shortcuts for category switching
- Focus trap in FAQ sections

## Testing Checklist

- [x] Sidebar navigation displays correctly
- [x] Category switching works smoothly
- [x] Active states update properly
- [x] Responsive design on all screen sizes
- [x] CKEditor loads in admin create/edit
- [x] Rich text renders correctly on frontend
- [x] Migration applied successfully
- [x] Dark mode styles work
- [x] Accordion functionality preserved
- [x] Mobile auto-scroll works
- [ ] Test with large number of categories (10+)
- [ ] Test with long FAQ content
- [ ] Test CKEditor with various content types
- [ ] Browser compatibility testing
- [ ] Performance testing with many FAQs

## Troubleshooting

### CKEditor Not Loading
**Issue**: Editor doesn't initialize
**Solution**:
- Check browser console for errors
- Verify CDN script loaded
- Ensure DOMContentLoaded fires
- Check for JavaScript conflicts

### Sidebar Not Sticky
**Issue**: Sidebar scrolls with content
**Solution**:
- Verify `position: sticky` support
- Check `top` value (should be > navbar height)
- Ensure parent has sufficient height
- Check for conflicting CSS

### Category Not Switching
**Issue**: Clicking category doesn't change content
**Solution**:
- Check JavaScript console for errors
- Verify `showCategory` function exists
- Check `data-category` attributes match IDs
- Ensure active class toggling works

### Rich Text Not Displaying
**Issue**: HTML shows as plain text
**Solution**:
- Use `|safe` filter in templates
- Check for `escape` filter conflicts
- Verify CKEditor saved HTML properly
- Check Content Security Policy headers

## Maintenance

### Regular Tasks
1. Update CKEditor CDN version periodically
2. Review and optimize FAQ content
3. Monitor category usage analytics
4. Update documentation as features change
5. Test responsive design on new devices

### Content Guidelines
1. Keep answers concise and structured
2. Use headings for long answers
3. Include links to related resources
4. Use lists for step-by-step guides
5. Add tables for comparisons
6. Keep consistent tone and style

## Related Documentation
- [CKEditor5 Official Docs](https://ckeditor.com/docs/ckeditor5/latest/)
- Django CKEditor 5 Package
- Bootstrap 5 Grid System
- CSS Sticky Positioning
