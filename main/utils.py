"""
Utility functions for the main app
"""

from django.utils.translation import gettext as _

from django.utils import timezone
from django.utils.timesince import timesince
from decimal import Decimal
import re
import random
import string
from datetime import timedelta


def get_selected_country_from_request(request, default="EG"):
    """
    Get the selected country from request (middleware sets it) or session as fallback
    """
    return getattr(
        request, "selected_country", request.session.get("selected_country", default)
    )


def get_country_filtered_ads(request, queryset):
    """
    Apply country filtering to a ClassifiedAd queryset based on selected country
    """
    selected_country = get_selected_country_from_request(request)
    return queryset.filter(country__code=selected_country)


def format_ad_price(price, currency_symbol=None):
    """
    Format ad price with proper number formatting and currency symbol
    Shows full price with thousands separator to display decimals
    """
    if not price:
        return ""

    # Format with thousands separator and 2 decimal places
    # This shows full price including fractions (e.g., 1,234.56)
    formatted = f"{float(price):,.2f}"

    if currency_symbol:
        return f"{formatted} {currency_symbol}"
    return formatted


def get_ad_urgency_badge(ad):
    """
    Determine the urgency badge for an ad based on creation date and features
    """
    # Handle missing attributes gracefully
    created_at = getattr(ad, "created_at", None)
    is_urgent = getattr(ad, "is_urgent", False)
    is_featured = getattr(ad, "is_featured", False)

    if not created_at:
        # If no creation date, just check if urgent or featured
        if is_urgent:
            return {"type": "urgent", "text": _("عاجل"), "class": "urgent-badge"}
        elif is_featured:
            return {"type": "featured", "text": _("مميز"), "class": "featured-badge"}
        return None

    now = timezone.now()
    hours_diff = (now - created_at).total_seconds() / 3600

    if is_urgent:
        return {"type": "urgent", "text": _("عاجل"), "class": "urgent-badge"}
    elif hours_diff <= 24:
        return {"type": "new", "text": _("جديد"), "class": "new-badge"}
    elif is_featured or (
        hasattr(ad, "features") and ad.features.filter(is_active=True).exists()
    ):
        return {"type": "featured", "text": _("مميز"), "class": "featured-badge"}

    return None


def get_ad_time_display(created_at):
    """
    Get a human-friendly time display for ads
    """
    now = timezone.now()
    diff = now - created_at

    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            if minutes < 5:
                return _("الآن")
            return _("منذ {minutes} دقيقة").format(minutes=minutes)
        return _("منذ {hours} ساعة").format(hours=hours)
    elif diff.days == 1:
        return _("أمس")
    elif diff.days < 7:
        return _("منذ {days} أيام").format(days=diff.days)
    elif diff.days < 30:
        weeks = diff.days // 7
        return _("منذ {weeks} أسبوع").format(weeks=weeks)
    else:
        return created_at.strftime("%Y-%m-%d")


def truncate_text_smart(text, max_length=120):
    """
    Truncates text at word boundaries
    """
    if not text or len(text) <= max_length:
        return text
    # Find the last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")

    if last_space != -1:
        truncated = truncated[:last_space]

    return truncated + "..."


def get_ad_image_url(ad, size="medium"):
    """
    Get optimized image URL for ad with fallback
    """
    if hasattr(ad, "images") and ad.images.exists():
        image = ad.images.first().image
        if image:
            return image.url

    # Return category-specific placeholder or default
    category_placeholders = {
        "vehicles": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=400&h=300&fit=crop",
        "electronics": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=300&fit=crop",
        "real-estate": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop",
        "fashion": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop",
    }

    # Try to match category
    if hasattr(ad, "category") and ad.category:
        category_name = ad.category.name.lower()
        for key, url in category_placeholders.items():
            if key in category_name:
                return url

    return "https://images.unsplash.com/photo-1586953983027-d7508abb5014?w=400&h=300&fit=crop"


def calculate_ad_score(ad):
    """
    Calculate a relevance/quality score for ad ranking
    """
    score = 0

    # Base score
    score += 10

    # Views boost
    if hasattr(ad, "views_count"):
        score += min(ad.views_count * 0.1, 20)

    # Recent ads boost
    hours_since_creation = (timezone.now() - ad.created_at).total_seconds() / 3600
    if hours_since_creation <= 24:
        score += 15
    elif hours_since_creation <= 168:  # 1 week
        score += 10

    # Features boost
    if hasattr(ad, "features") and ad.features.filter(is_active=True).exists():
        score += 25

    # Complete profile boost
    if hasattr(ad, "user") and ad.user:
        if ad.user.verification_status == "verified":
            score += 15
        if ad.user.profile_image:
            score += 5

    # Price reasonableness (basic check)
    if hasattr(ad, "price") and ad.price:
        if 100 <= ad.price <= 100000:  # Reasonable price range
            score += 5

    return min(score, 100)  # Cap at 100


def get_similar_ads(ad, limit=4):
    """
    Get similar ads based on category, price range, and location
    """
    from .models import ClassifiedAd

    if not ad:
        return ClassifiedAd.objects.none()

    # Price range (±50%)
    price_min = ad.price * Decimal("0.5") if ad.price else 0
    price_max = ad.price * Decimal("1.5") if ad.price else 999999999

    similar = (
        ClassifiedAd.objects.filter(category=ad.category, status="active")
        .exclude(pk=ad.pk)
        .filter(price__gte=price_min, price__lte=price_max)
    )

    # Boost same city
    if ad.city:
        same_city = similar.filter(city__iexact=ad.city)[: limit // 2]
        other_city = similar.exclude(city__iexact=ad.city)[: limit // 2]
        return list(same_city) + list(other_city)

    return similar[:limit]


def get_ad_contact_info(ad):
    """
    Get formatted contact information for an ad
    """
    contact_info = {}

    if hasattr(ad, "user") and ad.user:
        user = ad.user

        # Phone number
        if hasattr(user, "phone") and user.phone:
            # Format phone number (basic formatting)
            phone = re.sub(r"[^\d+]", "", user.phone)
            if phone.startswith("966"):
                phone = "+" + phone
            elif phone.startswith("05"):
                phone = "+966" + phone[1:]
            contact_info["phone"] = phone

        # WhatsApp
        if hasattr(user, "whatsapp") and user.whatsapp:
            whatsapp = re.sub(r"[^\d+]", "", user.whatsapp)
            if whatsapp.startswith("966"):
                whatsapp = "+" + whatsapp
            elif whatsapp.startswith("05"):
                whatsapp = "+966" + whatsapp[1:]
            contact_info["whatsapp"] = whatsapp

        # Display name
        contact_info["name"] = user.get_full_name() or user.username

        # Verification status
        if hasattr(user, "verification_status"):
            contact_info["verified"] = user.verification_status == "verified"

    return contact_info


def generate_verification_code(length=6):
    """
    Generate a random numeric verification code
    """
    return "".join(random.choices(string.digits, k=length))


def send_sms_verification_code(phone_number, code):
    """
    Send SMS verification code to phone number.

    In production, integrate with SMS gateway like:
    - Twilio
    - Nexmo/Vonage
    - AWS SNS
    - MSG91
    - Uniform

    For now, this is a placeholder that logs the code.
    """
    try:
        # TODO: Integrate with actual SMS service
        # Example for Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f"Your verification code is: {code}",
        #     from_=twilio_number,
        #     to=phone_number
        # )

        # For development/testing, just log it
        print(f"[SMS] Verification code for {phone_number}: {code}")
        print(f"[SMS] Code expires in 10 minutes")

        return True
    except Exception as e:
        print(f"[SMS ERROR] Failed to send code to {phone_number}: {str(e)}")
        return False


def get_country_phone_patterns(country_code):
    """
    Get phone validation patterns for different countries
    """
    patterns = {
        "SA": {  # Saudi Arabia
            "phone_code": "+966",
            "patterns": [
                r"^05\d{8}$",  # 05xxxxxxxx
                r"^9665\d{8}$",  # 9665xxxxxxxx
                r"^\+9665\d{8}$",  # +9665xxxxxxxx
                r"^5\d{8}$",  # 5xxxxxxxx
            ],
            "normalize": lambda p: (
                "+966" + p[1:]
                if p.startswith("05")
                else (
                    "+966" + p
                    if p.startswith("5") and len(p) == 9
                    else ("+" + p if p.startswith("966") else p)
                )
            ),
        },
        "AE": {  # UAE
            "phone_code": "+971",
            "patterns": [
                r"^05\d{8}$",  # 05xxxxxxxx
                r"^9715\d{8}$",  # 9715xxxxxxxx
                r"^\+9715\d{8}$",  # +9715xxxxxxxx
                r"^5\d{8}$",  # 5xxxxxxxx
            ],
            "normalize": lambda p: (
                "+971" + p[1:]
                if p.startswith("05")
                else (
                    "+971" + p
                    if p.startswith("5") and len(p) == 9
                    else ("+" + p if p.startswith("971") else p)
                )
            ),
        },
        "EG": {  # Egypt
            "phone_code": "+20",
            "patterns": [
                r"^01\d{9}$",  # 01xxxxxxxxx
                r"^201\d{9}$",  # 201xxxxxxxxx
                r"^\+201\d{9}$",  # +201xxxxxxxxx
                r"^1\d{9}$",  # 1xxxxxxxxx
            ],
            "normalize": lambda p: (
                "+20" + p
                if p.startswith("01")
                else (
                    "+20" + p
                    if p.startswith("1") and len(p) == 10
                    else ("+" + p if p.startswith("20") else p)
                )
            ),
        },
        "KW": {  # Kuwait
            "phone_code": "+965",
            "patterns": [
                r"^\d{8}$",  # xxxxxxxx (8 digits)
                r"^965\d{8}$",  # 965xxxxxxxx
                r"^\+965\d{8}$",  # +965xxxxxxxx
            ],
            "normalize": lambda p: (
                "+965" + p if len(p) == 8 else ("+" + p if p.startswith("965") else p)
            ),
        },
        "QA": {  # Qatar
            "phone_code": "+974",
            "patterns": [
                r"^\d{8}$",  # xxxxxxxx (8 digits)
                r"^974\d{8}$",  # 974xxxxxxxx
                r"^\+974\d{8}$",  # +974xxxxxxxx
            ],
            "normalize": lambda p: (
                "+974" + p if len(p) == 8 else ("+" + p if p.startswith("974") else p)
            ),
        },
        "BH": {  # Bahrain
            "phone_code": "+973",
            "patterns": [
                r"^\d{8}$",  # xxxxxxxx (8 digits)
                r"^973\d{8}$",  # 973xxxxxxxx
                r"^\+973\d{8}$",  # +973xxxxxxxx
            ],
            "normalize": lambda p: (
                "+973" + p if len(p) == 8 else ("+" + p if p.startswith("973") else p)
            ),
        },
        "OM": {  # Oman
            "phone_code": "+968",
            "patterns": [
                r"^\d{8}$",  # xxxxxxxx (8 digits)
                r"^968\d{8}$",  # 968xxxxxxxx
                r"^\+968\d{8}$",  # +968xxxxxxxx
            ],
            "normalize": lambda p: (
                "+968" + p if len(p) == 8 else ("+" + p if p.startswith("968") else p)
            ),
        },
        "JO": {  # Jordan
            "phone_code": "+962",
            "patterns": [
                r"^07\d{8}$",  # 07xxxxxxxx
                r"^9627\d{8}$",  # 9627xxxxxxxx
                r"^\+9627\d{8}$",  # +9627xxxxxxxx
                r"^7\d{8}$",  # 7xxxxxxxx
            ],
            "normalize": lambda p: (
                "+962" + p[1:]
                if p.startswith("07")
                else (
                    "+962" + p
                    if p.startswith("7") and len(p) == 9
                    else ("+" + p if p.startswith("962") else p)
                )
            ),
        },
    }

    return patterns.get(country_code, patterns["SA"])  # Default to SA


def validate_phone_number(phone, country_code="SA"):
    """
    Validate phone number format based on country
    """
    if not phone:
        return False

    # Remove spaces, dashes, and parentheses
    phone = re.sub(r"[\s\-\(\)]", "", phone)

    # Get country-specific patterns
    country_config = get_country_phone_patterns(country_code)
    patterns = country_config["patterns"]

    return any(re.match(pattern, phone) for pattern in patterns)


def normalize_phone_number(phone, country_code="SA"):
    """
    Normalize phone number to international format based on country
    """
    if not phone:
        return None

    # Remove spaces, dashes, and parentheses
    phone = re.sub(r"[\s\-\(\)]", "", phone)

    # Get country-specific configuration
    country_config = get_country_phone_patterns(country_code)

    # Apply country-specific normalization
    try:
        normalized = country_config["normalize"](phone)
        # Ensure it starts with +
        if not normalized.startswith("+"):
            normalized = country_config["phone_code"] + normalized
        return normalized
    except:
        # Fallback: if already has +, return as-is
        if phone.startswith("+"):
            return phone
        # Otherwise, prepend country code
        return country_config["phone_code"] + phone


# Image processing utilities
def add_watermark_to_image(
    image_field, watermark_path=None, opacity=128, position="bottom-right", scale=0.15
):
    """
    Add watermark to an uploaded image

    Args:
        image_field: Django ImageField instance
        watermark_path: Path to watermark image (defaults to mini-logo-dark-theme.png)
        opacity: Watermark opacity (0-255)
        position: Watermark position ('bottom-right', 'bottom-left', 'top-right', 'top-left', 'center')
        scale: Watermark scale relative to image width (0.0-1.0)

    Returns:
        InMemoryUploadedFile: Watermarked image file
    """
    import os
    from io import BytesIO
    from PIL import Image
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.conf import settings
    import logging

    logger = logging.getLogger(__name__)

    if not watermark_path:
        watermark_path = os.path.join(
            settings.STATIC_ROOT or settings.BASE_DIR / "static",
            "images/logos/mini-logo-dark-theme.png",
        )

    # If STATIC_ROOT doesn't exist (development), try STATICFILES_DIRS
    if not os.path.exists(watermark_path) and hasattr(settings, "STATICFILES_DIRS"):
        for static_dir in settings.STATICFILES_DIRS:
            alt_path = os.path.join(static_dir, "images/logos/mini-logo-dark-theme.png")
            if os.path.exists(alt_path):
                watermark_path = alt_path
                break

    try:
        # Open the original image
        image = Image.open(image_field)

        # Convert to RGBA if needed
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Check if watermark file exists
        if not os.path.exists(watermark_path):
            logger.warning(f"Watermark file not found: {watermark_path}")
            return None

        # Open watermark
        watermark = Image.open(watermark_path)
        if watermark.mode != "RGBA":
            watermark = watermark.convert("RGBA")

        # Calculate watermark size (scale relative to image width)
        img_width, img_height = image.size
        wm_width = int(img_width * scale)
        wm_height = int(watermark.size[1] * (wm_width / watermark.size[0]))
        watermark = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)

        # Apply opacity to watermark
        alpha = watermark.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity / 255))
        watermark.putalpha(alpha)

        # Calculate position
        padding = 20  # pixels from edge
        positions = {
            "bottom-right": (
                img_width - wm_width - padding,
                img_height - wm_height - padding,
            ),
            "bottom-left": (padding, img_height - wm_height - padding),
            "top-right": (img_width - wm_width - padding, padding),
            "top-left": (padding, padding),
            "center": ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
        }

        watermark_position = positions.get(position, positions["bottom-right"])

        # Create a transparent layer for the watermark
        transparent = Image.new("RGBA", image.size, (0, 0, 0, 0))
        transparent.paste(watermark, watermark_position, watermark)

        # Composite the watermark onto the image
        watermarked = Image.alpha_composite(image, transparent)

        # Convert back to RGB if original was not RGBA
        if hasattr(image_field, "file") and hasattr(image_field.file, "content_type"):
            if image_field.file.content_type in ["image/jpeg", "image/jpg"]:
                watermarked = watermarked.convert("RGB")

        # Save to BytesIO
        output = BytesIO()
        image_format = "PNG" if image_field.name.lower().endswith(".png") else "JPEG"
        watermarked.save(output, format=image_format, quality=95)
        output.seek(0)

        # Create InMemoryUploadedFile
        watermarked_file = InMemoryUploadedFile(
            output,
            "ImageField",
            image_field.name,
            f"image/{image_format.lower()}",
            output.getbuffer().nbytes,
            None,
        )

        return watermarked_file

    except Exception as e:
        logger.error(f"Error adding watermark to image: {str(e)}")
        return None
