from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from main.models import User


@receiver(post_save, sender=User)
def assign_user_permissions(sender, instance, created, **kwargs):
    """
    Automatically assign permissions based on user profile type
    """
    if created or instance.profile_type:
        # Remove all previous permissions
        instance.user_permissions.clear()

        # Assign permissions based on profile type
        if instance.profile_type == User.ProfileType.DEFAULT:
            perms = [
                "can_post_classified_ads",
                "can_request_services",
                "can_apply_jobs",
                "can_enroll_courses",
            ]
        elif instance.profile_type == User.ProfileType.SERVICE:
            perms = [
                "can_offer_services",
                "can_bid_on_services",
                "can_post_classified_ads",
            ]
        elif instance.profile_type == User.ProfileType.MERCHANT:
            perms = [
                "can_sell_products",
                "can_manage_store",
                "can_view_sales_reports",
                "can_post_classified_ads",
                "can_post_jobs",
            ]
        elif instance.profile_type == User.ProfileType.EDUCATIONAL:
            perms = [
                "can_create_courses",
                "can_manage_courses",
                "can_post_jobs",
            ]
        else:
            perms = []

        # All verified users can leave reviews
        status = instance.verification_status
        if status == User.VerificationStatus.VERIFIED:
            perms.extend(
                [
                    "can_review_products",
                    "can_review_services",
                    "can_review_courses",
                    "can_review_users",
                ]
            )

        # Premium users get additional permissions
        if instance.is_premium and instance.has_premium_access():
            perms.extend(
                [
                    "can_access_premium_features",
                    "can_boost_listings",
                    "can_feature_classified_ads",
                ]
            )

        # Get content type and add permissions
        content_type = ContentType.objects.get_for_model(User)
        for perm_codename in perms:
            try:
                permission = Permission.objects.get(
                    content_type=content_type,
                    codename=perm_codename,
                )
                instance.user_permissions.add(permission)
            except Permission.DoesNotExist:
                pass
