#!/usr/bin/env python
"""
Check what PayPal credentials are being used
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test.log")

django.setup()

from constance import config
from constance.models import Constance

print("\n" + "=" * 60)
print("CURRENT PAYPAL CONFIGURATION - DEBUG")
print("=" * 60)

# Check what's in constance config right now
print(f"\nVia config object (what Django uses):")
print(f"  PAYPAL_CLIENT_ID: {config.PAYPAL_CLIENT_ID[:30]}...")
print(f"  PAYPAL_CLIENT_SECRET: {config.PAYPAL_CLIENT_SECRET[:30]}...")
print(f"  PAYPAL_MODE: {config.PAYPAL_MODE}")

# Check what's in database
print(f"\nIn database (Constance table):")
try:
    for key in ["PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET", "PAYPAL_MODE"]:
        try:
            db_value = Constance.objects.get(key=key)
            print(
                f"  {key}: {db_value.value[:30]}..."
                if len(str(db_value.value)) > 30
                else f"  {key}: {db_value.value}"
            )
        except Constance.DoesNotExist:
            print(f"  {key}: NOT IN DATABASE (will use .env)")
except Exception as e:
    print(f"  Error querying database: {e}")

# Check environment
print(f"\nIn .env file (environment variables):")
env_client_id = os.getenv("PAYPAL_CLIENT_ID", "NOT SET")
env_secret = os.getenv("PAYPAL_CLIENT_SECRET", "NOT SET")
env_mode = os.getenv("PAYPAL_MODE", "NOT SET")

print(
    f"  PAYPAL_CLIENT_ID: {env_client_id[:30]}..."
    if len(env_client_id) > 30
    else f"  PAYPAL_CLIENT_ID: {env_client_id}"
)
print(
    f"  PAYPAL_CLIENT_SECRET: {env_secret[:30]}..."
    if len(env_secret) > 30
    else f"  PAYPAL_CLIENT_SECRET: {env_secret}"
)
print(f"  PAYPAL_MODE: {env_mode}")

print("\n" + "=" * 60)
print("SOLUTION:")
print("=" * 60)

# Check if they differ
if config.PAYPAL_CLIENT_ID != env_client_id:
    print("\n⚠️  DATABASE and .ENV have DIFFERENT values!")
    print("\nTo fix this, delete the old values from the database:")
    print("  python manage.py shell")
    print("  >>> from constance.models import Constance")
    print("  >>> Constance.objects.filter(key='PAYPAL_CLIENT_ID').delete()")
    print("  >>> Constance.objects.filter(key='PAYPAL_CLIENT_SECRET').delete()")
    print("  >>> Constance.objects.filter(key='PAYPAL_MODE').delete()")
    print("  >>> exit()")
    print("\nThen restart Django to use .env values")
else:
    print("\n✓ Database and .env values match")

print("\n" + "=" * 60)
