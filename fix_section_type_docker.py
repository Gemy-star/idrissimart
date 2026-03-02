#!/usr/bin/env python
"""
Fix subcategory section_type to match their parent categories.
Run on the production server:
    python fix_section_type_docker.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.docker")
django.setup()

from main.models import Category

fixed = 0
for cat in Category.objects.filter(is_active=True).exclude(parent=None):
    if cat.parent and cat.section_type != cat.parent.section_type:
        print(f"Fixing: {cat.name} ({cat.id}): [{cat.section_type}] -> [{cat.parent.section_type}]")
        cat.section_type = cat.parent.section_type
        cat.save(update_fields=["section_type"])
        fixed += 1

print(f"Fixed {fixed} categories")
