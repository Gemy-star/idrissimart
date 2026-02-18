#!/usr/bin/env python
"""
Fix PayPal Configuration - Remove old database values
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test.log")

django.setup()

from constance.models import Constance

print("\n" + "=" * 60)
print("FIXING PAYPAL CONFIGURATION")
print("=" * 60)

# Delete old PayPal values from database
keys_to_delete = ["PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET", "PAYPAL_MODE"]

print("\nDeleting old PayPal configuration from database...")
for key in keys_to_delete:
    try:
        deleted_count, _ = Constance.objects.filter(key=key).delete()
        if deleted_count > 0:
            print(f"  ✓ Deleted {key} from database")
        else:
            print(f"  ○ {key} not found in database")
    except Exception as e:
        print(f"  ✗ Error deleting {key}: {e}")

print("\n" + "=" * 60)
print("Verification - Current configuration:")
print("=" * 60)

from constance import config

print(f"\nPayPal Configuration (now using .env):")
print(f"  Client ID: {config.PAYPAL_CLIENT_ID[:30]}...")
print(f"  Client Secret: {config.PAYPAL_CLIENT_SECRET[:30]}...")
print(f"  Mode: {config.PAYPAL_MODE}")

print("\n✓ Configuration fixed! PayPal will now use the .env values.")
print("\nYou can verify this by running:")
print("  python test_paypal_simple.py")

print("\n" + "=" * 60)
