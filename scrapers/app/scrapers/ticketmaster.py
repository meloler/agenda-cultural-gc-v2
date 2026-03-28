"""
Scraper para la API Discovery de Ticketmaster.
Estrategia: Búsqueda secuencial con delays anti-429 y User-Agent real.

IMPORTANTE: La API Key se lee de la variable de entorno TM_API_KEY.
"""

import asyncio
import os

import httpx

from app.models import Evento
from app.utils.text_processing import limpiar_texto

API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "es-ES,es;q=0.9",
}

# Delay entre peticiones (segundos)
DELAY_BETWEEN_CALLS = 1.5
# Espera tras un 429 antes de reintentar
RETRY_WAIT_429 = 5


async def _fetch_with_retry(
    client: httpx.AsyncClient,
    label: str,
    params: dict,
) -> list[dict]:
    """Ejecuta una petición a la API con reintento ante 429.

    Si recibe HTTP 429, espera RETRY_WAIT_429 segundos y reintenta una vez.
    """
    for attempt in range(2):  # máximo 2 intentos
        try:
            response = await client.get(API_URL, params=params, headers=HEADERS)

            if response.status_code == 429:
                if attempt == 0:
                    print(f"   ⏳ [{label}] HTTP 429 – esperando {RETRY_WAIT_429}s antes de reintentar...")
                    await asyncio.sleep(RETRY_WAIT_429)
                    continue
                else:
                    print(f"   ⚠️ [{label}] HTTP 429 persistente. Saltando.")
                    return []

            if response.status_code != 200:
                print(f"   ⚠️ [{label}] HTTP {response.status_code}")
                return []

            data = response.json()
            total = data.get("page", {}).get("totalElements", 0)

            if "_embedded" not in data:
                print(f"   [{label}] Respuesta vacía pero válida (totalElements={total})")
                return []

            items = data["_embedded"].get("events", [])
            print(f"   ✅ [{label}] {len(items)} eventos recibidos (totalElements={total})")
            return items

        except Exception as e:
            print(f"   ⚠️ [{label}] Error: {e}")
            return []

    return []


def _parse_event(item: dict) -> Evento | None:
    """Convierte un dict crudo de la API en un objeto Evento."""
    try:
        event_id = item.get("id")
        nombre = item.get("name", "Evento TM")
        url_venta = item.get("url", "")

        dates = item.get("dates", {}).get("start", {})
        fecha_iso = dates.get("localDate")
        fecha_raw = f"{fecha_iso} {dates.get('localTime', '')}".strip()

        imgs = item.get("images", [])
        img_url = imgs[0]["url"] if imgs else None

        prices = item.get("priceRanges", [])
        precio_num = float(prices[0].get("min")) if prices else None

        lugar = "Gran Canaria"
        try:
            venues = item.get("_embedded", {}).get("venues", [])
            if venues:
                lugar = venues[0].get("name", "Gran Canaria")
        except Exception:
            pass

        # Extraer hora del localTime
        hora = None
        local_time = dates.get("localTime")
        if local_time and ":" in local_time:
            hora = local_time[:5]  # "20:00:00" → "20:00"

        return Evento(
            nombre=limpiar_texto(nombre),
            lugar=limpiar_texto(lugar),
            fecha_raw=fecha_raw,
            fecha_iso=fecha_iso,
            precio_num=precio_num,
            hora=hora,
            organiza="Ticketmaster",
            url_venta=url_venta,
            imagen_url=img_url,
            estilo="Otros",
            source_id=event_id,
        )
    except Exception:
        return None


async def scrape_ticketmaster_api() -> list[Evento]:
    """Ticketmaster API – Búsqueda secuencial con delays anti-429.

    Ejecuta 2 búsquedas de forma serializada con pausa entre ellas
    y unifica resultados por event ID.
    """
    print("🔥 Ticketmaster (API Discovery - Stealth Mode)...")
    eventos: list[Evento] = []

    api_key = os.getenv("TM_API_KEY")
    if not api_key:
        print("   ⚠️ TM_API_KEY no definida. Saltando Ticketmaster.")
        return eventos

    # Parámetros base compartidos
    base = {
        "apikey": api_key,
        "countryCode": "ES",
        "classificationId": "KZFzniwnSyZfZ7v7nJ",  # ID global: Música
        "size": "200",
        "sort": "date,asc",
    }

    # Definición de las búsquedas (secuenciales, no paralelas)
    searches = [
        ("A-City", {**base, "city": "Las Palmas"}),
        ("B-Keyword", {**base, "keyword": "Gran Canaria"}),
    ]

    seen_ids: set[str] = set()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            for i, (label, params) in enumerate(searches):
                # Delay entre llamadas (excepto antes de la primera)
                if i > 0:
                    await asyncio.sleep(DELAY_BETWEEN_CALLS)

                items = await _fetch_with_retry(client, label, params)

                for item in items:
                    event_id = item.get("id")
                    if not event_id or event_id in seen_ids:
                        continue
                    seen_ids.add(event_id)

                    evento = _parse_event(item)
                    if evento:
                        eventos.append(evento)

        print(f"   -> Ticketmaster TOTAL: {len(eventos)} eventos únicos procesados.")

    except Exception as e:
        print(f"   ⚠️ Error Ticketmaster: {e}")

    return eventos
