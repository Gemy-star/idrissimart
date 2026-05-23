from django.db import migrations

VALID_PROFILE_TYPES = {"default", "publisher"}


def fix_invalid_profile_types(apps, schema_editor):
    User = apps.get_model("main", "User")
    updated = User.objects.exclude(profile_type__in=VALID_PROFILE_TYPES).update(
        profile_type="default"
    )
    if updated:
        print(f"\nFixed {updated} users with invalid profile_type → 'default'")


class Migration(migrations.Migration):

    dependencies = [
        ("main", "1018_add_urgent_auto_refresh_to_feature_type"),
    ]

    operations = [
        migrations.RunPython(fix_invalid_profile_types, migrations.RunPython.noop),
    ]
