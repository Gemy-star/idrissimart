import os
import polib

# Direct path without Django
locale_path = r"c:\WORK\idrissimart\locale"

print(f"Locale path: {locale_path}")
print(f"Locale path exists: {os.path.exists(locale_path)}")

if os.path.exists(locale_path):
    print(f"\nLanguage directories:")
    for lang_code in os.listdir(locale_path):
        lang_dir = os.path.join(locale_path, lang_code)
        if not os.path.isdir(lang_dir):
            continue

        po_file = os.path.join(lang_dir, "LC_MESSAGES", "django.po")
        print(f"\n- {lang_code}:")
        print(f"  PO file path: {po_file}")
        print(f"  PO file exists: {os.path.exists(po_file)}")

        if os.path.exists(po_file):
            try:
                po = polib.pofile(po_file)
                total = len(po)
                translated = len(po.translated_entries())
                untranslated = len(po.untranslated_entries())
                fuzzy = len(po.fuzzy_entries())
                percent = po.percent_translated()

                print(f"  Total entries: {total}")
                print(f"  Translated: {translated}")
                print(f"  Untranslated: {untranslated}")
                print(f"  Fuzzy: {fuzzy}")
                print(f"  Percent: {percent}%")
            except Exception as e:
                print(f"  Error: {e}")
                import traceback

                print(traceback.format_exc())
