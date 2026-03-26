"""
Data migration: for CustomField and CustomFieldOption records where label_en is empty,
copy label_ar into label_en so existing English-labelled fields display correctly
on the English version of the site. The admin can then update label_ar with proper Arabic text.
"""

from django.db import migrations


def copy_label_ar_to_label_en(apps, schema_editor):
    CustomField = apps.get_model("main", "CustomField")
    CustomFieldOption = apps.get_model("main", "CustomFieldOption")

    # For CustomField records where label_en is blank, copy label_ar to label_en
    fields_to_fix = CustomField.objects.filter(label_en="")
    for field in fields_to_fix:
        field.label_en = field.label_ar
        field.save(update_fields=["label_en"])

    # Same for CustomFieldOption
    options_to_fix = CustomFieldOption.objects.filter(label_en="")
    for option in options_to_fix:
        option.label_en = option.label_ar
        option.save(update_fields=["label_en"])


def reverse_migration(apps, schema_editor):
    pass  # Non-destructive — no need to reverse


class Migration(migrations.Migration):

    dependencies = [
        ("main", "1002_add_auto_refresh_and_video_pricing"),
    ]

    operations = [
        migrations.RunPython(copy_label_ar_to_label_en, reverse_migration),
    ]
