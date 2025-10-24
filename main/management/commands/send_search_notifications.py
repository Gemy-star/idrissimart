import urllib.parse

from constance import config
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from main.filters import ClassifiedAdFilter
from main.models import ClassifiedAd, SavedSearch


class Command(BaseCommand):
    help = "Sends email notifications for new ads matching saved searches."

    def handle(self, *args, **options):
        if not config.ENABLE_SAVED_SEARCH_NOTIFICATIONS:
            self.stdout.write(
                self.style.WARNING("Saved search notifications are disabled globally.")
            )
            return

        # Get all saved searches with notifications enabled
        saved_searches = SavedSearch.objects.filter(
            email_notifications=True
        ).select_related("user")

        if not saved_searches.exists():
            self.stdout.write("No active saved searches found.")
            return

        self.stdout.write(
            f"Processing {saved_searches.count()} active saved searches..."
        )

        for search in saved_searches:
            # Determine the time window for new ads for this specific search
            # If never notified, use the search creation date. Otherwise, use the last notification date.
            time_threshold = search.last_notified_at or search.created_at

            # Find new ads since the last notification
            new_ads_for_search = ClassifiedAd.objects.filter(
                created_at__gt=time_threshold, status=ClassifiedAd.AdStatus.ACTIVE
            )

            if not new_ads_for_search.exists():
                continue

            query_dict = urllib.parse.parse_qs(search.query_params)

            # Use the filterset to find matching ads from the new ads queryset
            filterset = ClassifiedAdFilter(query_dict, queryset=new_ads_for_search)
            matching_ads = filterset.qs

            if matching_ads.exists():
                self.send_notification_email(search, matching_ads)

        self.stdout.write(self.style.SUCCESS("Finished sending notifications."))

    def send_notification_email(self, search, ads):
        user = search.user
        if not user.email:
            self.stdout.write(
                self.style.ERROR(
                    f"User {user.username} has no email address. Skipping."
                )
            )
            return

        subject = config.SAVED_SEARCH_EMAIL_SUBJECT.format(search_name=search.name)

        current_site = Site.objects.get_current()

        context = {
            "user": user,
            "search": search,
            "ads": ads,
            "site_url": f"https://{current_site.domain}",
        }

        html_message = render_to_string(
            "emails/saved_search_notification.html", context
        )

        try:
            send_mail(
                subject=subject,
                message="",  # Plain text version can be added here
                from_email=config.SAVED_SEARCH_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sent notification to {user.email} for search '{search.name}' with {ads.count()} new ads."
                )
            )

            # Update the last_notified_at timestamp to now
            search.last_notified_at = timezone.now()
            search.save(update_fields=["last_notified_at"])
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to send email to {user.email}: {e}")
            )
