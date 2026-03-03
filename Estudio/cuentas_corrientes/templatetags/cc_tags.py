from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter(name='formato_ar')
def formato_ar(value):
    if value is None:
        return '0,00'
    try:
        num = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    formatted = f'{num:,.2f}'
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return formatted
