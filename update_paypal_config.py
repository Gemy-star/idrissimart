#!/usr/bin/env python
"""
Update PayPal Configuration - Set Constance values from .env
"""

import os
import sys
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test.log")

django.setup()

from constance.models import Constance

# Read from .env
client_id = os.getenv("PAYPAL_CLIENT_ID", "")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "")
mode = os.getenv("PAYPAL_MODE", "sandbox")

print("\n" + "=" * 60)
print("UPDATING PAYPAL CONFIGURATION TO DATABASE")
print("=" * 60)

print(f"\nReading from .env:")
print(f"  Client ID: {client_id[:30] if client_id else 'NOT SET'}...")
print(f"  Client Secret: {client_secret[:30] if client_secret else 'NOT SET'}...")
print(f"  Mode: {mode}")

if not client_id or not client_secret:
    print("\n✗ ERROR: PAYPAL_CLIENT_ID or PAYPAL_CLIENT_SECRET not set in .env")
    sys.exit(1)

# Update Constance with values from .env
# Constance stores values as JSON
config_updates = {
    "PAYPAL_CLIENT_ID": json.dumps(client_id),
    "PAYPAL_CLIENT_SECRET": json.dumps(client_secret),
    "PAYPAL_MODE": json.dumps(mode),
}

print(f"\nUpdating Constance database...")
for key, value in config_updates.items():
    try:
        obj, created = Constance.objects.update_or_create(
            key=key, defaults={"value": value}
        )
        action = "Created" if created else "Updated"
        print(f"  ✓ {action} {key}")
    except Exception as e:
        print(f"  ✗ Error updating {key}: {e}")
        sys.exit(1)

print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

# Verify by reading from Constance
from constance import config

print(f"\nPayPal Configuration (from Constance):")
print(
    f"  Client ID: {config.PAYPAL_CLIENT_ID[:30]}..."
    if config.PAYPAL_CLIENT_ID
    else "  Client ID: NOT SET"
)
print(
    f"  Client Secret: {config.PAYPAL_CLIENT_SECRET[:30]}..."
    if config.PAYPAL_CLIENT_SECRET
    else "  Client Secret: NOT SET"
)
print(f"  Mode: {config.PAYPAL_MODE}")

print("\n✓ Configuration updated! Now test with:")
print("  python test_paypal_simple.py")

print("\n" + "=" * 60)
