"""
Management command to setup Django Q scheduled tasks
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.models import Schedule
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "إعداد المهام المجدولة لـ Django Q - Setup Django Q scheduled tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="حذف المهام الموجودة وإعادة إنشائها - Delete existing tasks and recreate them",
        )
        parser.add_argument(
            "--settings",
            type=str,
            default=None,
            help="Django settings module to use for scheduled tasks (e.g., 'idrissimart.settings.production')",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        settings_module = options.get("settings")

        if reset:
            self.stdout.write(
                self.style.WARNING("🗑️  Deleting all existing scheduled tasks...")
            )
            deleted_count = Schedule.objects.all().delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f"✅ Deleted {deleted_count} existing tasks")
            )

        self.stdout.write(self.style.WARNING("📝 Setting up scheduled tasks..."))

        if settings_module:
            self.stdout.write(
                self.style.NOTICE(f"📌 Using settings module: {settings_module}")
            )

        # Get tomorrow at 2 AM for initial run
        next_day_2am = timezone.now().replace(
            hour=2, minute=0, second=0, microsecond=0
        )
        if next_day_2am < timezone.now():
            next_day_2am = next_day_2am + timezone.timedelta(days=1)

        # Helper function to add settings argument if provided
        def format_args(command_args):
            if settings_module:
                return f"{command_args},--settings,{settings_module}"
            return command_args

        tasks = [
            # === CORE EXPIRATION COMMANDS (Daily) ===
            {
                "func": "django.core.management.call_command",
                "name": "Daily Expired Ads Check",
                "args": format_args("check_expired_ads"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am,
            },
            {
                "func": "django.core.management.call_command",
                "name": "Daily Subscription Check",
                "args": format_args("check_expired_subscriptions"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am.replace(minute=10),
            },
            {
                "func": "django.core.management.call_command",
                "name": "Daily Package Check",
                "args": format_args("check_expired_packages"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am.replace(minute=20),
            },
            {
                "func": "django.core.management.call_command",
                "name": "Hourly Order Expiration Check",
                "args": format_args("check_expired_orders"),
                "schedule_type": Schedule.HOURLY,
                "repeats": -1,
                "minutes": 60,
            },
            {
                "func": "django.core.management.call_command",
                "name": "Daily Expired Features Cleanup",
                "args": format_args("clear_expired_features"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am.replace(hour=3, minute=0),
            },
            {
                "func": "django.core.management.call_command",
                "name": "Daily Session Cleanup",
                "args": format_args("clearsessions"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am.replace(hour=4, minute=0),
            },
            # === DATABASE MAINTENANCE COMMANDS ===
            {
                "func": "django.core.management.call_command",
                "name": "Weekly Notification Cleanup",
                "args": format_args("cleanup_old_notifications"),
                "schedule_type": Schedule.WEEKLY,
                "repeats": -1,
                "next_run": next_day_2am.replace(hour=3, minute=0),
            },
            {
                "func": "django.core.management.call_command",
                "name": "Daily Payment Timeout Check",
                "args": format_args("check_pending_payments"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am.replace(minute=30),
            },
            # === NOTIFICATION COMMANDS ===
            {
                "func": "django.core.management.call_command",
                "name": "Daily Expiration Reminders (3 days)",
                "args": format_args("send_expiration_notifications"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am.replace(hour=9, minute=0),
            },
            {
                "func": "django.core.management.call_command",
                "name": "Daily Facebook Request Processing",
                "args": format_args("process_facebook_share_requests,--notify-admins"),
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_day_2am.replace(hour=10, minute=0),
            },
        ]

        created_count = 0
        updated_count = 0

        for task_config in tasks:
            # Check if task already exists by name
            existing = Schedule.objects.filter(name=task_config["name"]).first()

            if existing:
                self.stdout.write(f"  ⚙️  Updating task: {task_config['name']}")
                for key, value in task_config.items():
                    setattr(existing, key, value)
                existing.save()
                updated_count += 1
            else:
                self.stdout.write(f"  ➕ Creating task: {task_config['name']}")
                Schedule.objects.create(**task_config)
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Setup complete!"
                f"\n   Created: {created_count} tasks"
                f"\n   Updated: {updated_count} tasks"
            )
        )

        # Display summary
        self.stdout.write(self.style.WARNING("\n📋 Scheduled Tasks Summary:"))

        all_tasks = Schedule.objects.all().order_by("name")
        for task in all_tasks:
            schedule_info = self._get_schedule_info(task)
            next_run_str = task.next_run.strftime("%Y-%m-%d %H:%M:%S") if task.next_run else "Not set"
            self.stdout.write(
                f"  • {task.name}"
                f"\n    Schedule: {schedule_info}"
                f'\n    Next run: {next_run_str}'
                f"\n"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "\n💡 To start the Django Q worker, run:"
                "\n   python manage.py qcluster"
            )
        )

    def _get_schedule_info(self, task):
        """Get human-readable schedule information"""
        if task.schedule_type == Schedule.DAILY:
            return f'Daily at {task.next_run.strftime("%H:%M")}'
        elif task.schedule_type == Schedule.WEEKLY:
            return f'Weekly on {task.next_run.strftime("%A at %H:%M")}'
        elif task.schedule_type == Schedule.HOURLY:
            if hasattr(task, 'minutes') and task.minutes:
                hours = task.minutes // 60
                return f"Every {hours} hours"
            return "Hourly"
        elif task.schedule_type == Schedule.MINUTES:
            return f"Every {task.minutes} minutes"
        else:
            return task.schedule_type

