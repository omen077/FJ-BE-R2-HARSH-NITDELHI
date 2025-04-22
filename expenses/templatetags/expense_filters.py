from django import template

register = template.Library()

@register.filter
def divided_by(value, arg):
    """Divides the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def times(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def split(value, arg):
    """Splits a string by the provided delimiter"""
    return value.split(arg)

@register.filter
def get_item(list_obj, index):
    """Gets an item from a list by index, with index wrapping if needed"""
    try:
        index = int(index)
        if list_obj and len(list_obj) > 0:
            # Use modulo to wrap around if index exceeds list length
            return list_obj[index % len(list_obj)]
        return ""
    except (ValueError, TypeError):
        return ""

@register.filter
def floatformat(value, arg=None):
    """Format a float to a specified number of decimal places"""
    try:
        value = float(value)
        if arg is not None:
            decimals = int(arg)
            return round(value, decimals)
        else:
            return round(value)
    except (ValueError, TypeError):
        return value 