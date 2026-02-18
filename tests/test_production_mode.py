#!/usr/bin/env python
"""
Test Production Services using Production Settings
This script uses docker settings which loads from environment.production
"""

import os
import sys

# Load production environment variables
print("Loading production environment from environment.production...")
env_file = os.path.join(os.path.dirname(__file__), "environment.production")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value
    print("✓ Production environment loaded")
else:
    print("⚠️  environment.production not found, using system environment")

# Now run the test script
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.docker")
django.setup()

# Import and run tests
from test_production_services import main

if __name__ == "__main__":
    sys.exit(main())
