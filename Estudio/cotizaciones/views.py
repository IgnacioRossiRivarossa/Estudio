import json
import logging
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .services import get_dashboard_data

logger = logging.getLogger(__name__)

ROLES_PERMITIDOS = ('Administrador', 'Colaborador')

@login_required
def dashboard_economico_view(request):
    if request.user.rol not in ROLES_PERMITIDOS:
        raise PermissionDenied

    data = get_dashboard_data()

    # Preparar datos de dólares para las cards
    dolares = data.get("dolares") or []

    # Preparar cotizaciones de otras monedas
    cotizaciones = data.get("cotizaciones") or []

    # Últimos valores de inflación mensual e interanual
    inflacion_lista = data.get("inflacion") or []
    inflacion_ia_lista = data.get("inflacion_ia") or []
    uva_lista = data.get("uva") or []
    riesgo_pais_lista = data.get("riesgo_pais") or []
    riesgo_ultimo = data.get("riesgo_ultimo")

    # Obtener últimos valores para las cards de resumen
    ultima_inflacion = inflacion_lista[-1] if inflacion_lista else None
    ultima_inflacion_ia = inflacion_ia_lista[-1] if inflacion_ia_lista else None
    ultimo_uva = uva_lista[-1] if uva_lista else None

    # Datos para gráficos: últimos 24 meses (inflación), últimos 60 (UVA y riesgo)
    inflacion_chart = inflacion_lista[-24:] if inflacion_lista else []
    inflacion_ia_chart = inflacion_ia_lista[-24:] if inflacion_ia_lista else []
    uva_chart = uva_lista[-60:] if uva_lista else []
    riesgo_chart = riesgo_pais_lista[-60:] if riesgo_pais_lista else []

    # Serializar datos de gráficos a JSON para Chart.js
    def extraer_labels_valores(datos):
        """Extrae listas de fechas y valores de una lista de dicts."""
        labels = [item.get("fecha", "") for item in datos]
        valores = [item.get("valor", 0) for item in datos]
        return labels, valores

    infl_labels, infl_valores = extraer_labels_valores(inflacion_chart)
    infl_ia_labels, infl_ia_valores = extraer_labels_valores(inflacion_ia_chart)
    uva_labels, uva_valores = extraer_labels_valores(uva_chart)
    riesgo_labels, riesgo_valores = extraer_labels_valores(riesgo_chart)

    contexto = {
        "dolares": dolares,
        "cotizaciones": cotizaciones,
        "ultima_inflacion": ultima_inflacion,
        "ultima_inflacion_ia": ultima_inflacion_ia,
        "ultimo_uva": ultimo_uva,
        "riesgo_ultimo": riesgo_ultimo,
        # Datos JSON para Chart.js
        "infl_labels": json.dumps(infl_labels),
        "infl_valores": json.dumps(infl_valores),
        "infl_ia_labels": json.dumps(infl_ia_labels),
        "infl_ia_valores": json.dumps(infl_ia_valores),
        "uva_labels": json.dumps(uva_labels),
        "uva_valores": json.dumps(uva_valores),
        "riesgo_labels": json.dumps(riesgo_labels),
        "riesgo_valores": json.dumps(riesgo_valores),
    }

    return render(request, "cotizaciones/dashboard.html", contexto)