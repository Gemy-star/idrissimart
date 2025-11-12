"""
Consolidated template tags for IdrissiMart
"""

import re
from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()

# ======================
# USER TAGS
# ======================


@register.inclusion_tag("partials/_avatar_display.html")
def user_avatar(user, size=30, css_class=""):
    """
    Renders a user's avatar image or a default placeholder.
    Usage: {% user_avatar user=request.user size=50 css_class="rounded-circle" %}
    """
    return {
        "user": user,
        "size": size,
        "css_class": css_class,
    }


# ======================
# CURRENCY TAGS
# ======================


@register.simple_tag
def get_currency(ad):
    """
    Returns the currency code for the ad based on its country.
    Falls back to 'SAR' if no country or currency is set.
    """
    if ad and hasattr(ad, "country") and ad.country:
        return ad.country.currency or "SAR"
    return "SAR"


@register.simple_tag
def get_currency_symbol(ad):
    """
    Returns the currency symbol for the ad based on its country.
    """
    currency_symbols = {
        "SAR": "ر.س",  # Saudi Riyal
        "EGP": "ج.م",  # Egyptian Pound
        "AED": "د.إ",  # UAE Dirham
        "KWD": "د.ك",  # Kuwaiti Dinar
        "QAR": "ر.ق",  # Qatari Riyal
        "BHD": "د.ب",  # Bahraini Dinar
        "OMR": "ر.ع",  # Omani Rial
        "JOD": "د.أ",  # Jordanian Dinar
    }

    currency_code = get_currency(ad)
    return currency_symbols.get(currency_code, currency_code)


@register.filter
def format_price_with_currency(price, ad):
    """
    Formats price with the appropriate currency.
    Usage: {{ ad.price|format_price_with_currency:ad }}
    """
    if price is None:
        return ""

    currency = get_currency(ad)
    formatted_price = f"{float(price):,.2f}"
    return f"{formatted_price} {currency}"


# ======================
# FORMAT TAGS
# ======================


@register.filter(name="phone_format")
def phone_format(phone_number):
    """
    Formats a phone number into a more readable international format.
    Example: +966501234567 -> +966 50 123 4567
    """
    if not phone_number or not isinstance(phone_number, str):
        return phone_number

    # Remove all non-digit characters except for a leading '+'
    cleaned_number = re.sub(r"[^\d+]", "", phone_number)

    # Common country codes to detect
    country_codes = {
        "966": 4,  # Saudi Arabia
        "20": 3,  # Egypt
        "971": 3,  # UAE
    }

    for code, split_pos in country_codes.items():
        if cleaned_number.startswith(f"+{code}"):
            # Format: +CCC XX XXX XXXX
            part1 = cleaned_number[1:split_pos]
            part2 = cleaned_number[split_pos : split_pos + 2]
            part3 = cleaned_number[split_pos + 2 : split_pos + 5]
            part4 = cleaned_number[split_pos + 5 :]
            return f"+{part1} {part2} {part3} {part4}"

    return phone_number


# ======================
# AD TAGS
# ======================


@register.simple_tag
def ad_price_formatted(ad):
    """Format ad price with currency symbol"""
    if not ad or not hasattr(ad, "price"):
        return "غير محدد"

    try:
        from main.utils import format_ad_price

        currency_symbol = get_currency_symbol(ad)
        return format_ad_price(ad.price, currency_symbol)
    except Exception:
        # Fallback formatting
        return f"{ad.price:,.0f} ر.س"


@register.simple_tag
def ad_urgency_badge(ad):
    """Get urgency badge for ad"""
    try:
        from main.utils import get_ad_urgency_badge

        badge = get_ad_urgency_badge(ad)
        if not badge:
            return ""

        return mark_safe(
            f"""
            <span class="ad-badge {badge['class']}">
                <i class="fas fa-bolt"></i>
                <span>{badge['text']}</span>
            </span>
        """
        )
    except Exception:
        return ""


@register.simple_tag
def ad_time_friendly(ad):
    """Get friendly time display for ad"""
    if not ad or not hasattr(ad, "created_at"):
        return ""

    try:
        from main.utils import get_ad_time_display

        return get_ad_time_display(ad.created_at)
    except Exception:
        return ad.created_at.strftime("%Y-%m-%d") if ad.created_at else ""


@register.filter
def smart_truncate(text, max_length=120):
    """Smart text truncation filter"""
    if not text:
        return ""

    try:
        from main.utils import truncate_text_smart

        return truncate_text_smart(text, max_length)
    except Exception:
        # Fallback truncation
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."


@register.simple_tag
def ad_image_optimized(ad, size="medium"):
    """Get optimized image URL for ad"""
    try:
        from main.utils import get_ad_image_url

        return get_ad_image_url(ad, size)
    except Exception:
        # Fallback to first image or placeholder
        if hasattr(ad, "images") and ad.images.exists():
            return ad.images.first().image.url
        return "/static/images/placeholder-ad.jpg"


@register.simple_tag
def ad_quality_score(ad):
    """Calculate ad quality score"""
    try:
        from main.utils import calculate_ad_score

        return calculate_ad_score(ad)
    except Exception:
        return 75  # Default score


@register.inclusion_tag("partials/_ad_badges.html")
def render_ad_badges(ad):
    """Render all badges for an ad"""
    badges = []

    try:
        from main.utils import get_ad_urgency_badge

        # Urgency badge
        urgency = get_ad_urgency_badge(ad)
        if urgency:
            badges.append(urgency)

        # Delivery badge
        if hasattr(ad, "is_delivery_available") and ad.is_delivery_available:
            badges.append(
                {"type": "delivery", "text": "توصيل", "class": "delivery-badge"}
            )

        # Negotiable badge
        if hasattr(ad, "is_negotiable") and ad.is_negotiable:
            badges.append(
                {
                    "type": "negotiable",
                    "text": "قابل للتفاوض",
                    "class": "negotiable-badge",
                }
            )
    except Exception:
        pass  # Return empty badges if there's an error

    return {"badges": badges}


@register.inclusion_tag("partials/_ad_stats.html")
def render_ad_stats(ad):
    """Render ad statistics"""
    stats = []

    try:
        from main.utils import calculate_ad_score

        # Views
        if hasattr(ad, "views_count") and ad.views_count:
            stats.append(
                {"icon": "fas fa-eye", "value": ad.views_count, "label": "مشاهدة"}
            )

        # Quality score
        score = calculate_ad_score(ad)
        if score > 70:
            stats.append({"icon": "fas fa-star", "value": f"{score}%", "label": "جودة"})
    except Exception:
        pass  # Return empty stats if there's an error

    return {"stats": stats}


@register.simple_tag
def ad_verification_status(user):
    """Get verification status display for user"""
    if not user or not hasattr(user, "verification_status"):
        return ""

    if user.verification_status == "verified":
        if user.is_company:
            return {
                "status": "verified_company",
                "text": "شركة موثقة",
                "icon": "fas fa-building",
                "class": "verified-company-badge",
            }
        else:
            return {
                "status": "verified_person",
                "text": "عضو موثق",
                "icon": "fas fa-user-check",
                "class": "verified-person-badge",
            }

    return ""


@register.simple_tag
def render_verification_badge(user, location="overlay"):
    """
    Render verification badge for different locations (overlay, card, footer)
    """
    if not user or not user.is_verified:
        return ""

    badge_data = {
        "is_verified": True,
        "is_company": user.is_company,
        "location": location,
    }

    if user.is_company:
        badge_data.update(
            {
                "text": "شركة موثقة",
                "icon": "fas fa-building",
                "class": "verified-company-badge",
            }
        )
    else:
        badge_data.update(
            {
                "text": "عضو موثق",
                "icon": "fas fa-user-check",
                "class": "verified-person-badge",
            }
        )

    return badge_data


@register.inclusion_tag("partials/_verification_badge.html")
def verification_badge(user, location="overlay"):
    """Render verification badge with template"""
    return render_verification_badge(user, location)


# ======================
# Utility Filters
# ======================


@register.filter(name="get_item")
def get_item(mapping, key):
    """
    Safely get a key from a dict-like object in templates.
    Usage: {{ my_dict|get_item:key }}
    """
    try:
        if mapping is None:
            return ""
        # Support dict and Django QueryDict-like objects
        return mapping.get(key, "")
    except Exception:
        return ""
