import os

import django
from django.utils.translation import activate
from django.utils.translation import gettext as _


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    print("\n=== اختبار الترجمات ===\n")

    # Arabic
    activate("ar")
    print("العربية (ar):")
    print(f"  - {_('Item added to cart')}")
    print(f"  - {_('Item removed from cart')}")
    print(f"  - {_('Country updated successfully')}")

    # English
    activate("en")
    print("\nEnglish (en):")
    print(f"  - {_('Item added to cart')}")
    print(f"  - {_('Item removed from cart')}")
    print(f"  - {_('Country updated successfully')}")


if __name__ == "__main__":
    main()
