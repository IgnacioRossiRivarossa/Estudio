import time
import threading
import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings

BASE_URL = settings.IOL_BASE_URL
MAX_WORKERS = getattr(settings, 'IOL_MAX_WORKERS', 10)

class IOLClient:
    def __init__(self):
        self.usuario = settings.IOL_USUARIO
        self.password = settings.IOL_PASSWORD
        self.access_token = None
        self.refresh_token = None
        self.token_expira_en = 0
        self._lock = threading.Lock()

    def login(self):
        resp = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": self.usuario,
                "password": self.password,
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code != 200:
            raise ConnectionError(
                f"Login IOL fallido HTTP {resp.status_code}: {resp.text}"
            )
        self._guardar_tokens(resp.json())

    def _renovar(self):
        resp = requests.post(
            f"{BASE_URL}/token",
            data={
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code == 200:
            self._guardar_tokens(resp.json())
        else:
            self.login()

    def _guardar_tokens(self, data: dict):
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expira_en = time.time() + data.get("expires_in", 1200) - 90

    def _headers(self) -> dict:
        with self._lock:
            if self.access_token is None:
                self.login()
            elif time.time() >= self.token_expira_en:
                self._renovar()
        return {"Authorization": f"Bearer {self.access_token}"}

    def get(self, url: str):
        resp = requests.get(url, headers=self._headers())
        if resp.status_code == 401:
            with self._lock:
                self.login()
            resp = requests.get(url, headers=self._headers())
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        return resp.json()


def consultar_titulo(iol: IOLClient, simbolo: str) -> dict:
    try:
        d = iol.get(
            f"{BASE_URL}/api/v2/bCBA/Titulos/{quote(simbolo)}/Cotizacion"
        )
        cierre = d.get("ultimoCierre", d.get("cierreAnterior", None))
        return {"simbolo": simbolo, "ok": True, "cierre": cierre, "error": None}
    except Exception as e:
        return {
            "simbolo": simbolo,
            "ok": False,
            "cierre": None,
            "error": "no encontrado (404)" if "404" in str(e) else str(e),
        }


def consultar_titulos_paralelo(iol: IOLClient, simbolos: list) -> dict:
    resultados = {}
    errores = []
    workers = min(MAX_WORKERS, len(simbolos)) if simbolos else 1

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futuros = {executor.submit(consultar_titulo, iol, s): s for s in simbolos}
        for futuro in as_completed(futuros):
            r = futuro.result()
            if r["ok"] and r["cierre"] is not None:
                resultados[r["simbolo"]] = r["cierre"]
            else:
                errores.append(f"{r['simbolo']}: {r['error']}")

    return {"cierres": resultados, "errores": errores}