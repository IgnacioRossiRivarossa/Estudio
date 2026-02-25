import logging
import requests

logger = logging.getLogger(__name__)

BASE_DOLAR = "https://dolarapi.com/v1"
BASE_ARGDATOS = "https://api.argentinadatos.com/v1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 compatible",
}

TIMEOUT = 12  # segundos

def _get_json(url, fallback=None):
    if fallback is None:
        fallback = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.warning("Timeout al consultar %s", url)
    except requests.exceptions.ConnectionError:
        logger.warning("Error de conexión al consultar %s", url)
    except requests.exceptions.HTTPError as exc:
        logger.warning("Error HTTP %s al consultar %s", exc.response.status_code, url)
    except Exception:
        logger.exception("Error inesperado al consultar %s", url)
    return fallback

def get_dolares():
    return _get_json(f"{BASE_DOLAR}/dolares", fallback=[])

def get_cotizaciones():
    return _get_json(f"{BASE_DOLAR}/cotizaciones", fallback=[])

def get_inflacion():
    return _get_json(f"{BASE_ARGDATOS}/finanzas/indices/inflacion", fallback=[])

def get_inflacion_interanual():
    return _get_json(f"{BASE_ARGDATOS}/finanzas/indices/inflacionInteranual", fallback=[])

def get_uva():
    return _get_json(f"{BASE_ARGDATOS}/finanzas/indices/uva", fallback=[])

def get_riesgo_pais():
    return _get_json(f"{BASE_ARGDATOS}/finanzas/indices/riesgo-pais", fallback=[])


def get_riesgo_pais_ultimo():
    return _get_json(f"{BASE_ARGDATOS}/finanzas/indices/riesgo-pais/ultimo", fallback=None)

def get_dashboard_data():
    return {
        "dolares": get_dolares(),
        "cotizaciones": get_cotizaciones(),
        "inflacion": get_inflacion(),
        "inflacion_ia": get_inflacion_interanual(),
        "uva": get_uva(),
        "riesgo_pais": get_riesgo_pais(),
        "riesgo_ultimo": get_riesgo_pais_ultimo(),
    }
