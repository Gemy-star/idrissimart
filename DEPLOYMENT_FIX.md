# Production Server Fix

The 500 errors on the production server are likely because the gunicorn workers need to be restarted to load the new code changes.

## Commands to run on production server (srv1103414):

```bash
# Restart the gunicorn service
sudo systemctl restart gunicorn

# Check the status
sudo systemctl status gunicorn

# If there are still errors, check the logs
sudo journalctl -u gunicorn -n 50

# If needed, reload nginx
sudo systemctl reload nginx
```

## What was changed:

1. Added translation management endpoints in `main/views.py`:
   - `admin_translations_get(request, lang)` - GET endpoint to load translations
   - `admin_translations_save(request, lang)` - POST endpoint to save translations

2. Added URL routes in `main/urls.py`:
   - `/admin/translations/get/<lang>/`
   - `/admin/translations/save/<lang>/`

3. Updated `templates/admin_dashboard/translations.html`:
   - Inline translation editor
   - AJAX loading and saving

## Verify the fix:

After restarting, the site should load normally. The translation editing feature will work when you:
1. Go to `/admin/translations/`
2. Click "تحرير الترجمات" on any language card
3. Edit translations inline
4. Click "حفظ جميع التغييرات" to save

## If errors persist:

Check Python syntax:
```bash
cd /srv/idrissimart
source .venv/bin/activate
python -m py_compile main/views.py
```

Check for missing imports:
```bash
pip list | grep polib
```

If polib is missing:
```bash
pip install polib==1.2.0
```
