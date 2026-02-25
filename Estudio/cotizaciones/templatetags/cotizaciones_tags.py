from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from django import template

register = template.Library()

TZ_AR = ZoneInfo("America/Argentina/Buenos_Aires")

_FORMATOS_UTC = (
    '%Y-%m-%dT%H:%M:%S.%fZ',
    '%Y-%m-%dT%H:%M:%SZ',
)

_FORMATOS_NAIVE = (
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%S',
)


@register.filter(name='formato_fecha_iso')
def formato_fecha_iso(valor):
    if not valor:
        return valor
    try:
        valor_str = str(valor).strip()
        for fmt in _FORMATOS_UTC:
            try:
                dt = datetime.strptime(valor_str, fmt).replace(tzinfo=timezone.utc)
                dt_ar = dt.astimezone(TZ_AR)
                return dt_ar.strftime('%d/%m/%Y %H:%M hs')
            except ValueError:
                continue
        for fmt in _FORMATOS_NAIVE:
            try:
                dt = datetime.strptime(valor_str, fmt)
                return dt.strftime('%d/%m/%Y %H:%M hs')
            except ValueError:
                continue
        dt = datetime.strptime(valor_str, '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')

    except Exception:
        return valor
