from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def formato_ar(value, decimals=2):
    if value is None or value == '':
        return '-'
    try:
        d = Decimal(str(value))
        formatted = f"{d:,.{int(decimals)}f}"
        # Convierte formato US (1,234,567.89) → AR (1.234.567,89)
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except (InvalidOperation, ValueError, TypeError):
        return value
