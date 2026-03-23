"""
Management command to setup Django Q scheduled newsletter tasks.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Setup Django Q schedules for newsletter email/SMS tasks"

    TASK_NAMES = [
        "Weekly Newsletter Email",
        "Weekly Newsletter SMS",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing newsletter schedules before recreating them",
        )
        parser.add_argument(
            "--with-sms",
            action="store_true",
            help="Also schedule weekly SMS newsletter task",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        with_sms = options["with_sms"]

        if reset:
            deleted_count = Schedule.objects.filter(name__in=self.TASK_NAMES).delete()[0]
            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {deleted_count} existing newsletter schedule(s)"
                )
            )

        # Next Monday at 09:00 local time
        now = timezone.localtime()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        days_ahead = (0 - next_run.weekday()) % 7  # Monday=0
        if days_ahead == 0 and next_run <= now:
            days_ahead = 7
        next_run = next_run + timezone.timedelta(days=days_ahead)

        tasks = [
            {
                "func": "content.tasks.send_newsletter_scheduled_task",
                "name": "Weekly Newsletter Email",
                "schedule_type": Schedule.WEEKLY,
                "repeats": -1,
                "next_run": next_run,
            }
        ]

        if with_sms:
            tasks.append(
                {
                    "func": "content.tasks.send_newsletter_sms_scheduled_task",
                    "name": "Weekly Newsletter SMS",
                    "schedule_type": Schedule.WEEKLY,
                    "repeats": -1,
                    "next_run": next_run.replace(hour=10),
                }
            )

        created_count = 0
        updated_count = 0

        for task_config in tasks:
            schedule, created = Schedule.objects.get_or_create(
                name=task_config["name"],
                defaults=task_config,
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {schedule.name}"))
            else:
                for key, value in task_config.items():
                    setattr(schedule, key, value)
                schedule.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated: {schedule.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Newsletter schedules ready. Created={created_count}, Updated={updated_count}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS("Start worker with: python manage.py qcluster")
        )
