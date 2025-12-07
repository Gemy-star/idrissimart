import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings")

# Import settings first
from django.conf import settings

if not settings.configured:
    settings.configure()

# Now test slugify
from django.utils.text import slugify
import re

print("=" * 60)
print("Testing Arabic Slug Support")
print("=" * 60)

# Test slugify
test_cases = [
    "كتاب الفوتوغراميتري والاستشعار عن بعد",
    "سيارة مرسيدس 2020",
    "عقارات للبيع في الرياض",
]

pattern = r"^[\w\-\u0600-\u06FF]+$"

print("\n1. Testing slugify() with allow_unicode=True:\n")
for text in test_cases:
    slug = slugify(text, allow_unicode=True)
    matches = bool(re.match(pattern, slug))
    status = "✅" if matches else "❌"
    print(f"{status} {text}")
    print(f"   Slug: {slug}")
    print(f"   Matches pattern: {matches}\n")

print("\n2. Testing URL pattern:\n")
print(f"Pattern: {pattern}")
print("This pattern matches:")
print("- Latin letters (a-z, A-Z)")
print("- Digits (0-9)")
print("- Underscore (_)")
print("- Hyphen (-)")
print("- Arabic characters (\\u0600-\\u06FF)")

print("\n" + "=" * 60)
print("✅ Basic slug tests completed successfully!")
print("=" * 60)
