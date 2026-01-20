# Homepage Statistics Management Command

## Overview
This management command sets up the homepage statistics section with predefined values.

## Command
```bash
python manage.py setup_homepage_statistics
```

## What it does
Sets up 4 statistics cards on the homepage with the following values:

### Statistic 1 - معلنين نشطين (Active Advertisers)
- **Value:** 15
- **Title (EN):** Active Advertisers
- **Title (AR):** معلنين نشطين
- **Subtitle (EN):** Offices, Engineers & Companies
- **Subtitle (AR):** مكاتب، مهندسين، وشركات
- **Icon:** fas fa-user-friends

### Statistic 2 - إعلانات منشورة (Published Ads)
- **Value:** 150
- **Title (EN):** Published Ads
- **Title (AR):** إعلانات منشورة
- **Subtitle (EN):** Services, Equipment & Job Opportunities
- **Subtitle (AR):** خدمات، معدات، وفرص عمل
- **Icon:** fas fa-bullhorn

### Statistic 3 - زيارات شهرية (Monthly Visits)
- **Value:** 500
- **Title (EN):** Monthly Visits
- **Title (AR):** زيارات شهرية
- **Subtitle (EN):** Interested in Surveying Field
- **Subtitle (AR):** مهتمون بالمجال المساحي
- **Icon:** fas fa-chart-line

### Statistic 4 - تخصصات مدعومة (Supported Specializations)
- **Value:** 250
- **Title (EN):** Supported Specializations
- **Title (AR):** تخصصات مدعومة
- **Subtitle (EN):** Surveying - Engineering - GIS
- **Subtitle (AR):** مساحة – هندسة – GIS
- **Icon:** fas fa-th-large

## Usage
Run this command after deploying to setup or reset the homepage statistics:

```bash
python manage.py setup_homepage_statistics
```

The command will:
1. ✅ Enable the statistics section (`show_statistics = True`)
2. ✅ Set all 4 statistics with values, titles, subtitles, and icons
3. ✅ Display a success message with the configured values

## Location
- Command file: `content/management/commands/setup_homepage_statistics.py`
- Model: `content.site_config.HomePage`
- Template: `templates/pages/home.html`

## Notes
- This command is idempotent - you can run it multiple times safely
- All values can be edited later via Django Admin or Super Admin Dashboard
- Changes take effect immediately on the homepage
