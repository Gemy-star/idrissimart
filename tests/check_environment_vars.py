#!/usr/bin/env python
"""
Check what's actually being loaded from environment
"""
import os
from pathlib import Path

print("\n" + "="*80)
print("ENVIRONMENT VARIABLE CHECK")
print("="*80 + "\n")

# Check .env file directly
env_file = Path("/opt/WORK/idrissimart/.env")
print(f"Checking .env file: {env_file}")
print(f"File exists: {env_file.exists()}")

if env_file.exists():
    with open(env_file) as f:
        lines = f.readlines()

    print("\n[.env file contents - Paymob section]")
    in_paymob = False
    for i, line in enumerate(lines):
        if "PAYMOB" in line:
            in_paymob = True
        if in_paymob:
            if line.strip() and not line.startswith("#"):
                # Show first 50 chars
                val = line[:50] + "..." if len(line) > 50 else line
                print(f"  Line {i+1}: {val.strip()}")
            if "PAYPAL" in line:
                break

print("\n[Environment variables - Current values]")
env_vars = [
    "PAYMOB_API_KEY",
    "PAYMOB_SECRET_KEY",
    "PAYMOB_PUBLIC_KEY",
    "PAYMOB_INTEGRATION_ID",
    "PAYMOB_IFRAME_ID",
    "PAYMOB_HMAC_SECRET",
    "PAYPAL_CLIENT_ID",
    "PAYPAL_CLIENT_SECRET",
]

for var in env_vars:
    val = os.getenv(var, "NOT SET")
    if val and val != "NOT SET":
        # Show first 50 chars
        display = val[:50] + "..." if len(val) > 50 else val
        print(f"  {var}: {display}")
    else:
        print(f"  {var}: NOT SET")

print("\n" + "="*80)
print("To update environment, restart Django or reload .env:")
print("  1. Ctrl + C (stop Django)")
print("  2. poetry run python manage.py runserver")
print("="*80 + "\n")

