"""
Template tags for currency display based on country
"""
from django import template

register = template.Library()


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
