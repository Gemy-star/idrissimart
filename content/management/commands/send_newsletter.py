# management/commands/send_newsletter.py
"""
Django management command to send newsletters
Usage:
    python manage.py send_newsletter --subject "Newsletter subject" --html-file path/to/template.html
    python manage.py send_newsletter --subject "SMS Newsletter" --sms-message "Your message" --method sms
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send newsletters to all active subscribers via email or SMS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--subject",
            type=str,
            help="Newsletter subject (for email)",
            required=False,
        )
        parser.add_argument(
            "--html-file",
            type=str,
            help="Path to HTML template file",
            required=False,
        )
        parser.add_argument(
            "--text-file",
            type=str,
            help="Path to plain text file",
            required=False,
        )
        parser.add_argument(
            "--sms-message",
            type=str,
            help="SMS message to send",
            required=False,
        )
        parser.add_argument(
            "--method",
            type=str,
            choices=["email", "sms", "both"],
            default="email",
            help="Send method: email, sms, or both (default: email)",
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Send only to admin email for testing",
        )

    def handle(self, *args, **options):
        method = options.get("method", "email")
        is_test = options.get("test", False)

        # Validate inputs
        if method in ["email", "both"]:
            if not options.get("subject"):
                raise CommandError("--subject is required for email newsletters")

            if not options.get("html_file"):
                raise CommandError("--html-file is required for email newsletters")

        if method in ["sms", "both"]:
            if not options.get("sms_message"):
                raise CommandError("--sms-message is required for SMS newsletters")

        # Send email newsletter
        if method in ["email", "both"]:
            self._send_email_newsletter(options)

        # Send SMS newsletter
        if method in ["sms", "both"]:
            self._send_sms_newsletter(options)

        self.stdout.write(
            self.style.SUCCESS("Newsletter dispatch completed successfully!")
        )

    def _send_email_newsletter(self, options):
        """Send email newsletter"""
        from content.tasks import send_newsletter_to_all

        subject = options.get("subject")
        html_file = options.get("html_file")
        text_file = options.get("text_file")
        is_test = options.get("test", False)

        try:
            # Read HTML content
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Read text content if provided, otherwise strip from HTML
            if text_file:
                with open(text_file, "r", encoding="utf-8") as f:
                    text_content = f.read()
            else:
                text_content = strip_tags(html_content)

            if is_test:
                # Send only to admin email
                from django.core.mail import send_mail

                admin_email = getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@idrissimart.com"
                )
                send_mail(
                    subject=f"[TEST] {subject}",
                    message=text_content,
                    from_email=admin_email,
                    recipient_list=[admin_email],
                    html_message=html_content,
                    fail_silently=False,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Test email sent to {admin_email}")
                )
            else:
                # Send to all subscribers
                result = send_newsletter_to_all(
                    content_subject=subject,
                    content_html=html_content,
                    content_plain=text_content,
                )

                if result["success"]:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Email newsletter sent to {result['sent_count']} subscribers"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Error: {result['message']}")
                    )

        except FileNotFoundError as e:
            raise CommandError(f"File not found: {e}")
        except Exception as e:
            raise CommandError(f"Error sending email newsletter: {e}")

    def _send_sms_newsletter(self, options):
        """Send SMS newsletter"""
        from content.tasks import send_sms_newsletter_to_all

        sms_message = options.get("sms_message")
        is_test = options.get("test", False)

        if len(sms_message) > 160:
            self.stdout.write(
                self.style.WARNING(
                    f"Warning: SMS message length is {len(sms_message)} characters. "
                    "Standard SMS is limited to 160 characters."
                )
            )

        if is_test:
            self.stdout.write(
                self.style.SUCCESS("SMS send is available for live mode only.")
            )
        else:
            result = send_sms_newsletter_to_all(content_message=sms_message)

            if result["success"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"SMS newsletter sent to {result['sent_count']} subscribers"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Error: {result['message']}")
                )
