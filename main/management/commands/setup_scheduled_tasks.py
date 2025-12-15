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

    def handle(self, *args, **options):
        reset = options["reset"]

        if reset:
            self.stdout.write(
                self.style.WARNING("🗑️  Deleting all existing scheduled tasks...")
            )
            deleted_count = Schedule.objects.all().delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f"✅ Deleted {deleted_count} existing tasks")
            )

        self.stdout.write(self.style.WARNING("📝 Setting up scheduled tasks..."))

        tasks = [
            {
                "func": "main.scheduled_tasks.expire_ads_task",
                "name": "Expire Ads Daily",
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": timezone.now().replace(
                    hour=2, minute=0, second=0, microsecond=0
                ),
            },
            {
                "func": "main.scheduled_tasks.send_expiration_notifications_task",
                "name": "Send 3-Day Expiration Notifications",
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": timezone.now().replace(
                    hour=10, minute=0, second=0, microsecond=0
                ),
                "kwargs": '{"days": 3}',
            },
            {
                "func": "main.scheduled_tasks.send_7day_expiration_notifications_task",
                "name": "Send 7-Day Expiration Notifications",
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": timezone.now().replace(
                    hour=11, minute=0, second=0, microsecond=0
                ),
            },
            {
                "func": "main.scheduled_tasks.cleanup_old_notifications_task",
                "name": "Cleanup Old Notifications Weekly",
                "schedule_type": Schedule.WEEKLY,
                "repeats": -1,
                "next_run": timezone.now().replace(
                    hour=3, minute=0, second=0, microsecond=0
                ),
            },
            {
                "func": "main.scheduled_tasks.check_upgrade_expiry_task",
                "name": "Check Upgrade Expiry Every 6 Hours",
                "schedule_type": Schedule.HOURLY,
                "repeats": -1,
                "minutes": 360,  # Every 6 hours
            },
        ]

        created_count = 0
        updated_count = 0

        for task_config in tasks:
            # Check if task already exists
            existing = Schedule.objects.filter(func=task_config["func"]).first()

            if existing:
                self.stdout.write(f"  ⚙️  Updating task: {task_config['name']}")
                for key, value in task_config.items():
                    if key != "func":
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
            self.stdout.write(
                f"  • {task.name}"
                f"\n    Function: {task.func}"
                f"\n    Schedule: {schedule_info}"
                f'\n    Next run: {task.next_run.strftime("%Y-%m-%d %H:%M:%S")}'
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
            if task.minutes:
                hours = task.minutes // 60
                return f"Every {hours} hours"
            return "Hourly"
        elif task.schedule_type == Schedule.MINUTES:
            return f"Every {task.minutes} minutes"
        else:
            return task.schedule_type
