# main/ad_features_models.py
"""Models for new ad features and requests"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class FacebookShareRequest(models.Model):
    """Model to track Facebook share requests for admin review"""

    class Status(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار - Pending")
        IN_PROGRESS = "in_progress", _("جاري التنفيذ - In Progress")
        COMPLETED = "completed", _("تم التنفيذ - Completed")
        REJECTED = "rejected", _("مرفوض - Rejected")

    ad = models.ForeignKey(
        "ClassifiedAd",
        on_delete=models.CASCADE,
        related_name="facebook_share_requests",
        verbose_name=_("الإعلان"),
    )
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="facebook_share_requests",
        verbose_name=_("المستخدم"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("الحالة"),
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الطلب"),
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التنفيذ"),
    )
    processed_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_facebook_requests",
        verbose_name=_("تم التنفيذ بواسطة"),
    )
    facebook_post_url = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("رابط المنشور على فيسبوك"),
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name=_("ملاحظات الإدارة"),
    )
    payment_confirmed = models.BooleanField(
        default=False,
        verbose_name=_("تم تأكيد الدفع"),
    )
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("مبلغ الدفع"),
    )

    class Meta:
        db_table = "facebook_share_requests"
        verbose_name = _("Facebook Share Request")
        verbose_name_plural = _("Facebook Share Requests")
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["status", "-requested_at"]),
            models.Index(fields=["ad", "status"]),
        ]

    def __str__(self):
        return f"طلب نشر على فيسبوك - {self.ad.title} ({self.get_status_display()})"

    def mark_as_completed(self, facebook_post_url=None, admin=None):
        """Mark the request as completed"""
        self.status = self.Status.COMPLETED
        self.processed_at = timezone.now()
        self.processed_by = admin
        if facebook_post_url:
            self.facebook_post_url = facebook_post_url
            # Update the ad
            self.ad.facebook_share_completed = True
            self.ad.facebook_shared_at = timezone.now()
            self.ad.facebook_post_url = facebook_post_url
            self.ad.save(
                update_fields=[
                    "facebook_share_completed",
                    "facebook_shared_at",
                    "facebook_post_url",
                ]
            )
        self.save()

    def mark_as_rejected(self, reason="", admin=None):
        """Mark the request as rejected"""
        self.status = self.Status.REJECTED
        self.processed_at = timezone.now()
        self.processed_by = admin
        self.admin_notes = reason
        # Update the ad
        self.ad.share_on_facebook = False
        self.ad.facebook_share_requested = False
        self.ad.save(update_fields=["share_on_facebook", "facebook_share_requested"])
        self.save()
