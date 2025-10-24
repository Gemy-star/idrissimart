from constance import config
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .models import ClassifiedAd, Notification


@receiver(pre_save, sender=ClassifiedAd)
def send_ad_approval_notification(sender, instance, **kwargs):
    """
    Send a notification and email to the user when their ad is approved.
    """
    if instance.pk:
        try:
            old_instance = ClassifiedAd.objects.get(pk=instance.pk)
            # Check if the status is changing from 'pending' to 'active'
            if (
                old_instance.status == ClassifiedAd.AdStatus.PENDING
                and instance.status == ClassifiedAd.AdStatus.ACTIVE
            ):
                # 1. Create an in-app notification
                Notification.objects.create(
                    user=instance.user,
                    message=_(
                        'تمت الموافقة على إعلانك "{ad_title}" وهو الآن مباشر.'
                    ).format(ad_title=instance.title),
                    link=instance.get_absolute_url(),
                )

                # 2. Send an email notification
                current_site = Site.objects.get_current()
                subject = config.AD_APPROVAL_EMAIL_SUBJECT.format(
                    ad_title=instance.title
                )
                context = {
                    "user": instance.user,
                    "ad": instance,
                    "site_url": f"https://{current_site.domain}",
                }
                html_message = render_to_string(
                    "emails/ad_approval_notification.html", context
                )

                send_mail(
                    subject=subject,
                    message="",
                    from_email=config.AD_APPROVAL_FROM_EMAIL,
                    recipient_list=[instance.user.email],
                    html_message=html_message,
                )
        except ClassifiedAd.DoesNotExist:
            pass  # This is a new ad, so no status change to handle
