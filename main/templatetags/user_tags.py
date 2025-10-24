from django import template

register = template.Library()


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
