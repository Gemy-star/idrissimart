"""
Utility functions for the main app
"""

from django.utils import timezone
from django.utils.timesince import timesince
from decimal import Decimal
import re


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
    """
    if not price:
        return "غير محدد"

    # Format with thousands separator
    if price >= 1000000:
        formatted = f"{price/1000000:.1f}M"
    elif price >= 1000:
        formatted = f"{price/1000:.0f}K"
    else:
        formatted = f"{price:,.0f}"

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
            return {"type": "urgent", "text": "عاجل", "class": "urgent-badge"}
        elif is_featured:
            return {"type": "featured", "text": "مميز", "class": "featured-badge"}
        return None

    now = timezone.now()
    hours_diff = (now - created_at).total_seconds() / 3600

    if is_urgent:
        return {"type": "urgent", "text": "عاجل", "class": "urgent-badge"}
    elif hours_diff <= 24:
        return {"type": "new", "text": "جديد", "class": "new-badge"}
    elif is_featured or (
        hasattr(ad, "features") and ad.features.filter(is_active=True).exists()
    ):
        return {"type": "featured", "text": "مميز", "class": "featured-badge"}

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
                return "الآن"
            return f"منذ {minutes} دقيقة"
        return f"منذ {hours} ساعة"
    elif diff.days == 1:
        return "أمس"
    elif diff.days < 7:
        return f"منذ {diff.days} أيام"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"منذ {weeks} أسبوع"
    else:
        return created_at.strftime("%Y-%m-%d")


def truncate_text_smart(text, max_length=120):
    """
    Smart text truncation that respects word boundaries
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
