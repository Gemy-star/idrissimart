"""
Management command: create_admin_groups

Creates (or updates) all predefined admin permission groups, including the
"super_admin" and "publisher" groups for user assignment.
After creating groups, assigns every existing user:
    - admin/staff users -> super_admin
    - all other users   -> publisher

Safe to run multiple times — uses get_or_create.

Usage:
    python manage.py create_admin_groups
    python manage.py create_admin_groups --list
    python manage.py create_admin_groups --skip-assign
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


ADMIN_GROUP_LABELS = {
    "admin_ads":           "إدارة الإعلانات",
    "admin_users":         "إدارة المستخدمين",
    "admin_accounting":    "المحاسبة والمدفوعات",
    "admin_content":       "إدارة المحتوى",
    "admin_reports":       "التقارير والإحصائيات",
    "admin_reviews":       "التحقق والمراجعات",
    "admin_support":       "الدعم الفني",
    "admin_notifications": "الإشعارات",
}

PROFILE_GROUP_LABELS = {
    "super_admin":   "مشرف عام - Super Admin",
    "publisher":     "ناشر - Publisher",
    "default_users": "مستخدم قياسي - Default User",
}


class Command(BaseCommand):
    help = "Create predefined admin/user permission groups and assign users by role"

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="List existing admin groups and their members",
        )
        parser.add_argument(
            "--skip-assign",
            action="store_true",
            help="Create groups only — skip assigning users to groups",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self._list_groups()
            return

        # --- Create admin groups ---
        self.stdout.write(self.style.MIGRATE_HEADING("Setting up admin groups..."))
        created_count = 0
        for name, label in ADMIN_GROUP_LABELS.items():
            group, created = Group.objects.get_or_create(name=name)
            status = self.style.SUCCESS("created") if created else self.style.WARNING("exists ")
            self.stdout.write(f"  [{status}]  {name:28s}  {label}")
            if created:
                created_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} new group(s) created, "
                f"{len(ADMIN_GROUP_LABELS) - created_count} already existed."
            )
        )

        # --- Create user-facing groups (publisher, default_users) ---
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Setting up user profile groups..."))
        for name, label in PROFILE_GROUP_LABELS.items():
            group, created = Group.objects.get_or_create(name=name)
            status = self.style.SUCCESS("created") if created else self.style.WARNING("exists ")
            self.stdout.write(f"  [{status}]  {name:28s}  {label}")

        if options["skip_assign"]:
            self.stdout.write(self.style.WARNING("\nSkipping user assignment (--skip-assign)."))
            return

        # --- Assign users: admin/staff -> super_admin, others -> publisher ---
        self._assign_users_to_groups()

    def _assign_users_to_groups(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Assigning users to groups by role..."))

        # Pre-fetch groups
        groups = {name: Group.objects.get(name=name) for name in PROFILE_GROUP_LABELS}

        assigned = {"super_admin": 0, "publisher": 0}

        for user in User.objects.all().iterator():
            profile_type = (getattr(user, "profile_type", "default") or "default").lower()

            # Legacy-safe admin detection:
            # - explicit admin profile_type (if present in old data)
            # - Django staff/superuser flags
            is_admin_user = profile_type == "admin" or user.is_staff or user.is_superuser
            group_name = "super_admin" if is_admin_user else "publisher"

            target_group = groups[group_name]
            if not user.groups.filter(pk=target_group.pk).exists():
                user.groups.add(target_group)
                assigned[group_name] += 1

        self.stdout.write("")
        for name in ("super_admin", "publisher"):
            count = assigned[name]
            label = PROFILE_GROUP_LABELS[name]
            self.stdout.write(f"  {self.style.SUCCESS(str(count))} users assigned to '{name}' ({label})")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("User group assignment complete."))

    def _list_groups(self):
        all_groups = {**ADMIN_GROUP_LABELS, **PROFILE_GROUP_LABELS}
        self.stdout.write(self.style.MIGRATE_HEADING("All groups:"))
        for name, label in all_groups.items():
            try:
                group = Group.objects.prefetch_related("user_set").get(name=name)
                members = list(group.user_set.values_list("username", flat=True))
                self.stdout.write(
                    f"\n  {self.style.SUCCESS(name)} — {label}"
                    f"\n    Members ({len(members)}): "
                    + (", ".join(members) if members else "none")
                )
            except Group.DoesNotExist:
                self.stdout.write(f"\n  {self.style.ERROR(name)} — NOT CREATED yet")
        self.stdout.write("")
