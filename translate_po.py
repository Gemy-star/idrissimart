#!/usr/bin/env python
"""
Translates all Arabic msgid entries in locale/en/LC_MESSAGES/django.po to English.
- Empty msgstr: translate from Arabic
- Fuzzy with wrong msgstr: translate from Arabic
- English msgid with empty msgstr: copy msgid to msgstr
- Removes fuzzy flags after applying translation
"""
import sys
import time
import polib
from deep_translator import GoogleTranslator

PO_FILE = "locale/en/LC_MESSAGES/django.po"
BATCH_SIZE = 50   # Translate in batches to reduce API calls
SLEEP_BETWEEN_BATCHES = 1.0  # seconds


def is_arabic(text):
    return any('\u0600' <= c <= '\u06ff' for c in text)


def needs_translation(entry):
    """Return True if the entry needs a new translation."""
    if not is_arabic(entry.msgid):
        return False
    # Needs work if empty or if it has a fuzzy flag (likely wrong)
    return not entry.msgstr or 'fuzzy' in entry.flags


def translate_batch(texts, translator):
    """Translate a list of texts, returning a list of translations."""
    results = []
    for text in texts:
        try:
            # GoogleTranslator has a 5000 char limit per request
            if len(text) > 4900:
                text = text[:4900]
            translated = translator.translate(text)
            results.append(translated if translated else text)
        except Exception as e:
            print(f"  Warning: translation failed for '{text[:60]}...': {e}", file=sys.stderr)
            results.append(text)  # fall back to original
    return results


def main():
    print(f"Loading {PO_FILE} ...")
    po = polib.pofile(PO_FILE)

    translator = GoogleTranslator(source='ar', target='en')

    # Collect all entries that need translation
    to_translate = [e for e in po if needs_translation(e)]
    print(f"Entries needing Arabic→English translation: {len(to_translate)}")

    # Also handle English msgid with empty msgstr
    eng_empty = [e for e in po if not is_arabic(e.msgid) and not e.msgstr]
    print(f"English msgid with empty msgstr (will copy): {len(eng_empty)}")

    # Copy English msgids to msgstr
    for entry in eng_empty:
        entry.msgstr = entry.msgid
        if 'fuzzy' in entry.flags:
            entry.flags.remove('fuzzy')

    # Translate Arabic entries in batches
    total = len(to_translate)
    done = 0
    errors = 0

    for i in range(0, total, BATCH_SIZE):
        batch = to_translate[i:i + BATCH_SIZE]
        msgids = [e.msgid for e in batch]

        print(f"  Translating batch {i // BATCH_SIZE + 1}/{(total + BATCH_SIZE - 1) // BATCH_SIZE} "
              f"({i + 1}–{min(i + len(batch), total)} of {total}) ...", end=' ', flush=True)

        translations = translate_batch(msgids, translator)

        for entry, translation in zip(batch, translations):
            if translation:
                entry.msgstr = translation
                if 'fuzzy' in entry.flags:
                    entry.flags.remove('fuzzy')
                done += 1
            else:
                errors += 1

        print(f"done ({done} translated, {errors} errors so far)")

        if i + BATCH_SIZE < total:
            time.sleep(SLEEP_BETWEEN_BATCHES)

    print(f"\nSaving {PO_FILE} ...")
    po.save(PO_FILE)
    print(f"Done. Translated {done} entries, {errors} errors.")
    print(f"Run: cd /Users/kriko/works/idrissimart && .venv/bin/python -m django compilemessages")


if __name__ == '__main__':
    main()
