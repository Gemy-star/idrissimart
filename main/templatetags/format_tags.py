import re

from django import template

register = template.Library()


@register.filter(name="phone_format")
def phone_format(phone_number):
    """
    Formats a phone number into a more readable international format.
    Example: +966501234567 -> +966 50 123 4567

    Usage: {{ user.phone|phone_format }}
    """
    if not phone_number or not isinstance(phone_number, str):
        return phone_number

    # Remove all non-digit characters except for a leading '+'
    cleaned_number = re.sub(r"[^\d+]", "", phone_number)

    # Common country codes to detect
    country_codes = {
        "966": 4,  # Saudi Arabia (e.g., +966 5x xxx xxxx)
        "20": 3,  # Egypt (e.g., +20 1xx xxx xxxx)
        "971": 3,  # UAE (e.g., +971 5x xxx xxxx)
    }

    for code, split_pos in country_codes.items():
        if cleaned_number.startswith(f"+{code}"):
            # Format: +CCC XX XXX XXXX
            part1 = cleaned_number[1:split_pos]
            part2 = cleaned_number[split_pos : split_pos + 2]
            part3 = cleaned_number[split_pos + 2 : split_pos + 5]
            part4 = cleaned_number[split_pos + 5 :]
            return f"+{part1} {part2} {part3} {part4}"

    # Fallback for other numbers
    return phone_number
