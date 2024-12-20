from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """
    Calculate percentage
    """
    try:
        return float(value) * 100 / float(total)
    except (ValueError, ZeroDivisionError):
        return 0
