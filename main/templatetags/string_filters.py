from django import template
import html
import re

register = template.Library()


@register.filter(name="replace")
def replace(value, arg):
    return value.replace(arg, " ")


@register.filter(name="clean_html")
def clean_html(value):
    """
    Remove HTML tags and decode HTML entities like &nbsp;, &lt;, etc.
    """
    if not value:
        return value

    # First decode HTML entities like &nbsp; &lt; &gt;
    value = html.unescape(value)

    # Remove HTML tags
    value = re.sub(r"<[^>]+>", "", value)

    # Replace multiple spaces with single space
    value = re.sub(r"\s+", " ", value)

    # Strip leading/trailing whitespace
    return value.strip()
